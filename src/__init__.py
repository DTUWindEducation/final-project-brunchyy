import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from scipy.stats import weibull_min
from windrose import WindroseAxes


def nc_reader(file_paths):
    """
    Læser én eller flere NetCDF-filer og returnerer en samlet pandas DataFrame.
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]  # Hvis kun én fil er givet

    datasets = [xr.open_dataset(path) for path in file_paths]
    combined = xr.concat(datasets, dim="valid_time")
    df2 = combined.to_dataframe().reset_index()
    return df2



def wind_speed(df2):
    df2["wind_speed_10m [m/s]"] = np.sqrt(df2["u10"]**2 + df2["v10"]**2)

    df2["wind_speed_100m [m/s]"] = np.sqrt(df2["u100"]**2 + df2["v100"]**2)

    df2["wind_direction_10m [degrees]"] = np.arctan2(df2["u10"], df2["v10"]) * 180 / np.pi + 180

    df2["wind_direction_100m [degrees]"] = np.arctan2(df2["u100"], df2["v100"]) * 180 / np.pi + 180

    df = df2[["valid_time", "latitude", "longitude", "wind_speed_10m [m/s]", "wind_speed_100m [m/s]","wind_direction_10m [degrees]", "wind_direction_100m [degrees]"]]

    return df



def nc_sorter(df):
    # Sortér først
    df_sorted = df.sort_values(by=["latitude", "longitude", "valid_time"]).reset_index(drop=True)

    # Find unikke koordinater
    coords = df_sorted[["latitude", "longitude"]].drop_duplicates()

    # Opret separate tabeller
    tables = {}
    for i, row in coords.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        key = f"lat_{lat}_lon_{lon}"
        tables[key] = df_sorted[(df_sorted["latitude"] == lat) & (df_sorted["longitude"] == lon)].reset_index(drop=True)
        
    lat_8_lon_55_5 = tables["lat_8.0_lon_55.5"]
    lat_8_lon_55_75 = tables["lat_8.0_lon_55.75"]
    lat_7_75_lon_55_5 = tables["lat_7.75_lon_55.5"]
    lat_7_75_lon_55_75 = tables["lat_7.75_lon_55.75"]
    return lat_8_lon_55_5, lat_8_lon_55_75, lat_7_75_lon_55_5, lat_7_75_lon_55_75



def interpolation(lat, lon, lat_8_lon_55_5, lat_8_lon_55_75, lat_7_75_lon_55_5, lat_7_75_lon_55_75):   #This only works for kordinates in the sqare
    """
    Interpoler vindhastighed og retning for givet latitude og longitude.
    """
    xpercent = (lat-7.75)/0.25
    ypercent = (lon-55.5)/0.25


    inter = {}

    inter["latTop10Speed"] = lat_7_75_lon_55_5["wind_speed_10m [m/s]"] + (lat_8_lon_55_5["wind_speed_10m [m/s]"]-lat_7_75_lon_55_5["wind_speed_10m [m/s]"])*xpercent
    inter["latBottom10Speed"] = lat_7_75_lon_55_75["wind_speed_10m [m/s]"] + (lat_8_lon_55_75["wind_speed_10m [m/s]"]-lat_7_75_lon_55_75["wind_speed_10m [m/s]"])*xpercent

    inter["interValue10Speed"] =  inter["latBottom10Speed"] + (inter["latTop10Speed"] - inter["latBottom10Speed"]) * ypercent



    inter["latTop100Speed"] = lat_7_75_lon_55_5["wind_speed_100m [m/s]"] + (lat_8_lon_55_5["wind_speed_100m [m/s]"]-lat_7_75_lon_55_5["wind_speed_100m [m/s]"])*xpercent
    inter["latBottom100Speed"] = lat_7_75_lon_55_75["wind_speed_100m [m/s]"] + (lat_8_lon_55_75["wind_speed_100m [m/s]"]-lat_7_75_lon_55_75["wind_speed_100m [m/s]"])*xpercent

    inter["interValue100Speed"] =  inter["latBottom100Speed"] + (inter["latTop100Speed"] - inter["latBottom100Speed"]) * ypercent



    inter["latTop10Direction"] = lat_7_75_lon_55_75["wind_direction_10m [degrees]"] + (lat_8_lon_55_75["wind_direction_10m [degrees]"]-lat_7_75_lon_55_75["wind_direction_10m [degrees]"])*xpercent
    inter["latBottom10Direction"] = lat_7_75_lon_55_5["wind_direction_10m [degrees]"] + (lat_8_lon_55_5["wind_direction_10m [degrees]"]-lat_7_75_lon_55_5["wind_direction_10m [degrees]"])*xpercent

    inter["interValue10Direction"] =  inter["latBottom10Direction"] + (inter["latTop10Direction"] - inter["latBottom10Direction"]) * ypercent



    inter["latTop100Direction"] = lat_7_75_lon_55_75["wind_direction_100m [degrees]"] + (lat_8_lon_55_75["wind_direction_100m [degrees]"]-lat_7_75_lon_55_75["wind_direction_100m [degrees]"])*xpercent
    inter["latBottom100Direction"] = lat_7_75_lon_55_5["wind_direction_100m [degrees]"] + (lat_8_lon_55_5["wind_direction_100m [degrees]"]-lat_7_75_lon_55_5["wind_direction_100m [degrees]"])*xpercent

    inter["interValue100Direction"] =  inter["latBottom100Direction"] + (inter["latTop100Direction"] - inter["latBottom100Direction"]) * ypercent



    interpolatedTable = pd.DataFrame({
        "valid_time": lat_7_75_lon_55_5["valid_time"],
        "wind_speed_10m [m/s]": inter["interValue10Speed"],
        "wind_speed_100m [m/s]": inter["interValue100Speed"],
        "wind_direction_10m [degrees]": inter["interValue10Direction"],
        "wind_direction_100m [degrees]": inter["interValue100Direction"]
    })
    

    return interpolatedTable
    


def compute_power_law(interpolatedTable, height, z1=10, z2=100):
    """
    Compute wind speed at a given height using the power law.
    interpolatedTable: DataFrame with wind data for one location.
    z1: Height corresponding to U1 [m].
    z2: Height corresponding to U2 [m].
    height: Target height at which wind speed is computed [m].
    """
    # Extract the known wind speeds
    U1 = interpolatedTable["wind_speed_10m [m/s]"]
    U2 = interpolatedTable["wind_speed_100m [m/s]"]
    
    # Calculate the shear exponent alpha
    alpha = np.log(U2 / U1) / np.log(z2 / z1)
    
    # Compute the wind speed at the new height
    U_z = U2 * (height / z2) ** alpha

    # Computing the interpolated direction
    y_percent = (height - z1) / (z2 - z1)
    if height <= 100: 
        direction_z = interpolatedTable["wind_direction_10m [degrees]"]+ (interpolatedTable["wind_direction_100m [degrees]"] - interpolatedTable["wind_direction_10m [degrees]"]) * y_percent
    else:
        direction_z = interpolatedTable["wind_direction_100m [degrees]"]

    interpolatedTable_height = pd.DataFrame({
        "valid_time": interpolatedTable["valid_time"],
        f"wind_speed_at_{height}[m/s]": U_z,
        f"direction_at_{height}[degrees]": direction_z
    })

    return interpolatedTable_height

def fit_weibull(speed_data):
    """
    Fit a 2-parameter Weibull to the input wind-speed array.
    Returns: k (shape), A (scale).
    """
    k, loc, A = weibull_min.fit(speed_data, floc=0)
    return k, A

def plot_weibull(speed_data, k, A, height, bins=30):
    """
    Plot the observed wind-speed histogram (density) and overlay the
    fitted Weibull PDF with parameters k, A.
    """
    counts, edges = np.histogram(speed_data, bins=bins, density=True)
    centers = 0.5*(edges[:-1] + edges[1:])
    pdf = weibull_min.pdf(centers, k, loc=0, scale=A)

    plt.figure()
    plt.bar(centers, counts,
            width=(edges[1]-edges[0]),
            alpha=0.6,
            label='Observed')
    plt.plot(centers, pdf, lw=2,
            label=f'Weibull k={k:.2f}, A={A:.2f}')
    plt.title(f"Weibull Distribution Fit at {height} m")
    plt.xlabel('Wind Speed [m/s]')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.grid(True)
    plt.show()

def wind_rose(height_speed, height):
    
    # Extract wind direction and speed at given height [m]
    wind_speed = height_speed[f"wind_speed_at_{height}[m/s]"]
    wind_dir = height_speed[f"direction_at_{height}[degrees]"]

    # Create a windrose plot
    plt.figure(figsize=(8, 8))
    ax = WindroseAxes.from_ax()
    ax.bar(wind_dir, wind_speed, normed=True, opening=0.8, edgecolor='white', bins=np.arange(0, 30, 5))
    ax.set_legend()
    plt.title(f"Wind Rose at {height} m")
    plt.show()



class GeneralWindTurbine:
    """
    Represents a general wind turbine using analytical equations.
    """
    def __init__(self, rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name=None):
        self.rotor_diameter = rotor_diameter
        self.hub_height = hub_height
        self.rated_power = rated_power
        self.v_in = v_in
        self.v_rated = v_rated
        self.v_out = v_out
        self.name = name

    def get_power(self, v):
        if v < self.v_in or v > self.v_out:
            P = 0
        elif self.v_in <= v < self.v_rated:
            P =self.rated_power * (v/self.v_rated) ** 3
        elif self.v_rated <= v < self.v_out:
            P = self.rated_power
        return P


class WindTurbine(GeneralWindTurbine):
    """
    Wind turbine with actual power curve data for interpolation.
    """
    def __init__(self, rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve_data, name=None):
        # Using the parent class __init__ to get the self values 
        super().__init__(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name)
        
        self.power_curve_data = np.array(power_curve_data)

    def get_power(self, v):
        v = np.array(v)
        wind_speed = self.power_curve_data[:, 0]
        power_value = self.power_curve_data[:, 1]

        return np.interp(v, wind_speed, power_value)


class TurbineParameters:
    """
    Parameters for the wind turbine.
    """
    def __init__(self, rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name=None):
        self.rotor_diameter = rotor_diameter
        self.hub_height = hub_height
        self.rated_power = rated_power
        self.v_in = v_in
        self.v_rated = v_rated
        self.v_out = v_out
        self.name = name

    def showcase(self):
        print(f"Rotor Diameter: {self.rotor_diameter} m")
        print(f"Hub Height: {self.hub_height} m")
        print(f"Rated Power: {self.rated_power} kW")
        print(f"Cut-in Wind Speed: {self.v_in} m/s")
        print(f"Rated Wind Speed: {self.v_rated} m/s")
        print(f"Cut-out Wind Speed: {self.v_out} m/s")
        if self.name:
            print(f"Turbine Name: {self.name}")
    
    def csvReader(self, filePath):
        MW = []
        for path in filePath:
            df = pd.read_csv(path)
            MW.append(df)
        return MW
    
    def power_curve(self, MW):
        power_curve = []
        for i in range(len(MW)):
            power_curve.append(MW[i].iloc[:, :2].values)
        return power_curve


