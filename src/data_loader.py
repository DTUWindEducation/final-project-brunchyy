import xarray as xr
import numpy as np
import os

# Define the 4 fixed ERA5 grid points
LOCATIONS = [
    (55.5, 7.75),
    (55.5, 8.0),
    (55.75, 7.75),
    (55.75, 8.0)
]

# Load the dataset
def load_dataset(filepaths):
    """
    Load and concatenate multiple ERA5 NetCDF files into a single xarray Dataset.

    Parameters:
    - filepaths (list of str): list of NetCDF file paths

    Returns:
    - xarray.Dataset: combined dataset
    """
    datasets = [xr.open_dataset(fp) for fp in filepaths]
    combined = xr.concat(datasets, dim='valid_time')  # adjust dim to match your file
    return combined

# Compute wind speed at each location
def compute_wind_speed_at_locations(ds, height='10'):
    """
    Compute wind speed time series for fixed locations at given height.

    Parameters:
    - ds (xarray.Dataset): ERA5 dataset
    - height (str): height in meters as string, e.g., '10' or '100'

    Returns:
    - dict: {(lat, lon): wind_speed_time_series}
    """
    wind_speeds = {}
    for lat, lon in LOCATIONS:
        point_data = ds.sel(latitude=lat, longitude=lon, method='nearest')

        u = point_data[f'u{height}']
        v = point_data[f'v{height}']
        speed = np.sqrt(u**2 + v**2)

        wind_speeds[(lat, lon)] = speed

    return wind_speeds
