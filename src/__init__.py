import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from stats import fit_weibull, plot_weibull #to import q5 and q6 solved in stats.py

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
    
    



file_path = ["inputs/1997-1999.nc", "inputs/2000-2002.nc", "inputs/2003-2005.nc", "inputs/2006-2008.nc", "inputs/2009-2011.nc", "inputs/2012-2014.nc", "inputs/2015-2017.nc", "inputs/2018-2020.nc"]

df2 = nc_reader(file_path)

df = wind_speed(df2)

#print(df)

lat_8_lon_55_5, lat_8_lon_55_75, lat_7_75_lon_55_5, lat_7_75_lon_55_75 = nc_sorter(df)

#print(lat_8_lon_55_5)
#print(lat_8_lon_55_75)
#print(lat_7_75_lon_55_5)
#print(lat_7_75_lon_55_75)

#plot = lat_8_lon_55_5.plot(x="valid_time", y="wind_direction_10m [degrees]", title="Wind Speed at 10m Height (Latitude: 8.0, Longitude: 55.5)", figsize=(12, 6))
#plt.xlabel("Valid Time")   
#plt.ylabel("wind_direction_10m [degrees]")
#plt.grid(True)
#plt.show()

#a = {}

#a["Test"] = df["wind_speed_10m [m/s]"]

#print(a)

interpolatedTable = interpolation(7.93, 55.65, lat_8_lon_55_5, lat_8_lon_55_75, lat_7_75_lon_55_5, lat_7_75_lon_55_75)
print(interpolatedTable)

#######snippet code to make stats work

# Choose which height to analyze: 10 or 100?
height = 100  
col_name = f"wind_speed_{height}m [m/s]"

# 1) extract a clean 1-D numpy array
speed_array = interpolatedTable[col_name].to_numpy()
speed_array = speed_array[~np.isnan(speed_array)]

# 2) fit the Weibull distribution
k, A = fit_weibull(speed_array)
print(f"Fitted Weibull at {height} m: k = {k:.2f}, A = {A:.2f}")

# 3) plot the histogram vs. the fitted PDF
plot_weibull(speed_array, k, A, bins=40)
