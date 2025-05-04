"""
This module provides functions to read NetCDF files,
process wind data, and perform various analyses related to wind energy.
"""

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from scipy.stats import weibull_min
from scipy.integrate import quad
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



def wind_speed_df(df2):
    """
    calculates wind speed and direction from u and v components at 10m and 100m height.
    """
    df2["wind_speed_10m [m/s]"] = np.sqrt(df2["u10"]**2 + df2["v10"]**2)

    df2["wind_speed_100m [m/s]"] = np.sqrt(df2["u100"]**2 + df2["v100"]**2)

    df2["wind_direction_10m [degrees]"] = np.arctan2(df2["u10"], df2["v10"]) * 180 / np.pi + 180

    df2["wind_direction_100m [degrees]"] = np.arctan2(df2["u100"], df2["v100"]) * 180 / np.pi + 180

    df = df2[["valid_time", "latitude", "longitude", "wind_speed_10m [m/s]",
              "wind_speed_100m [m/s]", "wind_direction_10m [degrees]",
              "wind_direction_100m [degrees]"]]

    return df



def nc_sorter(df):
    """
    sorts the DataFrame by latitude and longitude,
    and creates separate tables for each unique coordinate.
    """
    # Sortér først
    df_sorted = df.sort_values(by=["latitude", "longitude", "valid_time"]).reset_index(drop=True)

    # Find unikke koordinater
    coords = df_sorted[["latitude", "longitude"]].drop_duplicates()

    # Opret separate tabeller
    tables = {}
    for i, row in coords.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        key = f"lat_{lat}_lon_{lon}"
        tables[key] = df_sorted[(df_sorted["latitude"] == lat)
        & (df_sorted["longitude"] == lon)].reset_index(drop=True)


    return tables



def interpolation(lat, lon, tables):
    #This only works for kordinates in the sqare
    """
    Interpoler vindhastighed og retning for givet latitude og longitude.
    """
    xpercent = (lat-7.75)/0.25
    ypercent = (lon-55.5)/0.25

    lat_8_lon_55_5 = tables["lat_8.0_lon_55.5"]
    lat_8_lon_55_75 = tables["lat_8.0_lon_55.75"]
    lat_7_75_lon_55_5 = tables["lat_7.75_lon_55.5"]
    lat_7_75_lon_55_75 = tables["lat_7.75_lon_55.75"]

    inter = {}

    inter["latTop10Speed"] = lat_7_75_lon_55_5["wind_speed_10m [m/s]"] + (lat_8_lon_55_5["wind_speed_10m [m/s]"] - lat_7_75_lon_55_5["wind_speed_10m [m/s]"]) * xpercent
    inter["latBottom10Speed"] = lat_7_75_lon_55_75["wind_speed_10m [m/s]"] + (lat_8_lon_55_75["wind_speed_10m [m/s]"] - lat_7_75_lon_55_75["wind_speed_10m [m/s]"]) * xpercent

    inter["interValue10Speed"] =  inter["latBottom10Speed"] + (inter["latTop10Speed"] - inter["latBottom10Speed"]) * ypercent



    inter["latTop100Speed"] = lat_7_75_lon_55_5["wind_speed_100m [m/s]"] + (lat_8_lon_55_5["wind_speed_100m [m/s]"] - lat_7_75_lon_55_5["wind_speed_100m [m/s]"]) * xpercent
    inter["latBottom100Speed"] = lat_7_75_lon_55_75["wind_speed_100m [m/s]"] + (lat_8_lon_55_75["wind_speed_100m [m/s]"] - lat_7_75_lon_55_75["wind_speed_100m [m/s]"]) * xpercent

    inter["interValue100Speed"] =  inter["latBottom100Speed"] + (inter["latTop100Speed"] - inter["latBottom100Speed"]) * ypercent



    inter["latTop10Direction"] = lat_7_75_lon_55_75["wind_direction_10m [degrees]"] + (lat_8_lon_55_75["wind_direction_10m [degrees]"] - lat_7_75_lon_55_75["wind_direction_10m [degrees]"]) * xpercent
    inter["latBottom10Direction"] = lat_7_75_lon_55_5["wind_direction_10m [degrees]"] + (lat_8_lon_55_5["wind_direction_10m [degrees]"] - lat_7_75_lon_55_5["wind_direction_10m [degrees]"]) * xpercent

    inter["interValue10Direction"] =  inter["latBottom10Direction"] + (inter["latTop10Direction"] - inter["latBottom10Direction"]) * ypercent



    inter["latTop100Direction"] = lat_7_75_lon_55_75["wind_direction_100m [degrees]"] + (lat_8_lon_55_75["wind_direction_100m [degrees]"] - lat_7_75_lon_55_75["wind_direction_100m [degrees]"]) * xpercent
    inter["latBottom100Direction"] = lat_7_75_lon_55_5["wind_direction_100m [degrees]"] + (lat_8_lon_55_5["wind_direction_100m [degrees]"] - lat_7_75_lon_55_5["wind_direction_100m [degrees]"]) * xpercent

    inter["interValue100Direction"] =  inter["latBottom100Direction"] + (inter["latTop100Direction"] - inter["latBottom100Direction"]) * ypercent



    interpolated_table = pd.DataFrame({
        "valid_time": lat_7_75_lon_55_5["valid_time"],
        "wind_speed_10m [m/s]": inter["interValue10Speed"],
        "wind_speed_100m [m/s]": inter["interValue100Speed"],
        "wind_direction_10m [degrees]": inter["interValue10Direction"],
        "wind_direction_100m [degrees]": inter["interValue100Direction"]
    })


    return interpolated_table



def compute_power_law(interpolated_table, height, z1=10, z2=100):
    """
    Compute wind speed at a given height using the power law.
    interpolatedTable: DataFrame with wind data for one location.
    z1: Height corresponding to U1 [m].
    z2: Height corresponding to U2 [m].
    height: Target height at which wind speed is computed [m].
    """
    # Extract the known wind speeds
    u1 = interpolated_table["wind_speed_10m [m/s]"]
    u2 = interpolated_table["wind_speed_100m [m/s]"]

    # Calculate the shear exponent alpha
    alpha = np.log(u2 / u1) / np.log(z2 / z1)

    # Compute the wind speed at the new height
    u_z = u2 * (height / z2) ** alpha

    # Computing the interpolated direction
    y_percent = (height - z1) / (z2 - z1)
    if height <= 100:
        direction_z = interpolated_table["wind_direction_10m [degrees]"] + (interpolated_table["wind_direction_100m [degrees]"] - interpolated_table["wind_direction_10m [degrees]"]) * y_percent
    else:
        direction_z = interpolated_table["wind_direction_100m [degrees]"]

    interpolated_table_height = pd.DataFrame({
        "valid_time": interpolated_table["valid_time"],
        f"wind_speed_at_{height}[m/s]": u_z,
        f"direction_at_{height}[degrees]": direction_z
    })

    return interpolated_table_height

def fit_weibull(speed_data):
    """
    Fit a 2-parameter Weibull to the input wind-speed array.
    Returns: k (shape), A (scale).
    """
    k, loc, a = weibull_min.fit(speed_data, floc=0)
    return k, a

def plot_weibull(speed_data, k, a, height, bins=30):
    """
    Plot the observed wind-speed histogram (density) and overlay the
    fitted Weibull PDF with parameters k, a.
    """
    counts, edges = np.histogram(speed_data, bins=bins, density=True)
    centers = 0.5*(edges[:-1] + edges[1:])
    pdf = weibull_min.pdf(centers, k, loc=0, scale=a)

    plt.figure()
    plt.bar(centers, counts,
            width=(edges[1]-edges[0]),
            alpha=0.6,
            label='Observed')
    plt.plot(centers, pdf, lw=2,
            label=f'Weibull k={k:.2f}, A={a:.2f}')
    plt.title(f"Weibull Distribution Fit at {height} m")
    plt.xlabel('Wind Speed [m/s]')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.grid(True)
    plt.show()

def wind_rose(height_speed, height):
    """
    Create a wind rose plot for the given height and wind speed data.
    """

    # Extract wind direction and speed at given height [m]
    wind_speed = height_speed[f"wind_speed_at_{height}[m/s]"]
    wind_dir = height_speed[f"direction_at_{height}[degrees]"]

    # Create a windrose plot
    plt.figure(figsize=(8, 8))
    ax = WindroseAxes.from_ax()
    ax.bar(wind_dir, wind_speed, normed=True, opening=0.8,
           edgecolor='white', bins=np.arange(0, 30, 5))
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
        """
        Calculate the power output of the turbine based on wind speed.
        """
        if v < self.v_in or v > self.v_out:
            p = 0
        elif self.v_in <= v < self.v_rated:
            p =self.rated_power * (v/self.v_rated) ** 3
        elif self.v_rated <= v < self.v_out:
            p = self.rated_power
        return p


class WindTurbine(GeneralWindTurbine):
    """
    Wind turbine with actual power curve data for interpolation.
    """
    def __init__(self, rotor_diameter, hub_height, rated_power,
                 v_in, v_rated, v_out, power_curve_data, name=None):
        # Using the parent class __init__ to get the self values
        super().__init__(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name)

        self.power_curve_data = np.array(power_curve_data)

    def get_power(self, v):
        """
        Calculate the power output of the turbine based on wind speed using interpolation.
        """
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
        """
        Showcase the turbine parameters.
        """
        print(f"Rotor Diameter: {self.rotor_diameter} m")
        print(f"Hub Height: {self.hub_height} m")
        print(f"Rated Power: {self.rated_power} kW")
        print(f"Cut-in Wind Speed: {self.v_in} m/s")
        print(f"Rated Wind Speed: {self.v_rated} m/s")
        print(f"Cut-out Wind Speed: {self.v_out} m/s")
        if self.name:
            print(f"Turbine Name: {self.name}")

    def csv_reader(self, filePath):
        """
        Reads the CSV files and returns a list of DataFrames.
        """
        mw = []
        for path in filePath:
            df = pd.read_csv(path)
            mw.append(df)
        return mw

    def power_curve(self, mw):
        """
        Extracts the power curve data from the DataFrames.
        """
        power_curve = []
        for i in range(len(mw)):
            power_curve.append(mw[i].iloc[:, :2].values)
        return power_curve


def plot_power_curve(wind_speeds, rotor_diameter, hub_height,
    rated_power, v_in, v_rated, v_out, power_curve):
    """
    Plot the power curve of the wind turbine using both general and detailed models.
    """

    general_turbine = GeneralWindTurbine(rotor_diameter, hub_height,
    rated_power, v_in, v_rated, v_out, "LEANWIND_5MW_126_General")

    detailed_turbine_5mw = WindTurbine(rotor_diameter, hub_height, rated_power,
    v_in, v_rated, v_out, power_curve[0], "LEANWIND_5MW_126_Detailed")

    detailed_turbine_15mw = WindTurbine(rotor_diameter, hub_height,
    rated_power, v_in, v_rated, v_out, power_curve[1], "LEANWIND_15MW_240_Detailed")

    # Compute power outputs for each wind speed using both turbine models
    power_general = np.array([general_turbine.get_power(v) for v in wind_speeds])
    power_detailed_5mw = np.array([detailed_turbine_5mw.get_power(v) for v in wind_speeds])
    power_detailed_15mw = np.array([detailed_turbine_15mw.get_power(v) for v in wind_speeds])

    # Plot the power curves
    plt.figure(figsize=(10, 6))
    plt.plot(wind_speeds, power_general, label="GeneralWindTurbine", lw=2)
    plt.plot(wind_speeds, power_detailed_5mw,
    label="WindTurbine (Interpolated) 5MW", lw=2, linestyle='--')
    plt.plot(wind_speeds, power_detailed_15mw,
    label="WindTurbine (Interpolated) 15MW", lw=2, linestyle=':')
    plt.xlabel("Wind Speed (m/s)")
    plt.ylabel("Power Output (kW)")
    plt.title("Comparison of Wind Turbine Power Curves")
    plt.legend()
    plt.grid(True)
    plt.show()



def compute_aep(turbine, k, a, u_in, u_out, availability=1.0):
    """
    Compute the Annual Energy Production (AEP) in kWh.
    - turbine: an object with a .get_power(u) method (like WindTurbine)
    - k, A: Weibull parameters (shape, scale)
    - u_in, u_out: cut-in and cut-out speeds
    - availability: assumed 1.0 unless stated otherwise
    """

    def integrand(u):
        return turbine.get_power(u) * weibull_min.pdf(u, k, scale=a)

    energy_per_year, _ = quad(integrand, u_in, u_out)
    aep = availability * 8760 * energy_per_year  # kWh/year
    return aep
