import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt


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

    df2["wind_direction_10m [degrees]"] = np.arctan2(df2["u10"], df2["v10"]) * 180 / np.pi

    df2["wind_direction_100m [degrees]"] = np.arctan2(df2["u100"], df2["v100"]) * 180 / np.pi

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




file_path = ["inputs/1997-1999.nc", "inputs/2000-2002.nc", "inputs/2003-2005.nc", "inputs/2006-2008.nc", "inputs/2009-2011.nc", "inputs/2012-2014.nc", "inputs/2015-2017.nc", "inputs/2018-2020.nc"]

df2 = nc_reader(file_path)

df = wind_speed(df2)

lat_8_lon_55_5, lat_8_lon_55_75, lat_7_5_lon_55_5, lat_7_5_lon_55_75 = nc_sorter(df)

print(lat_8_lon_55_5)
print(lat_8_lon_55_75)
print(lat_7_5_lon_55_5)
print(lat_7_5_lon_55_75)

plot = lat_8_lon_55_5.plot(x="valid_time", y="wind_direction_10m [degrees]", title="Wind Speed at 10m Height (Latitude: 8.0, Longitude: 55.5)", figsize=(12, 6))
plt.xlabel("Valid Time")   
plt.ylabel("wind_direction_10m [degrees]")
plt.grid(True)
plt.show()