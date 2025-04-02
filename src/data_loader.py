import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Load the dataset
def load_dataset(filepaths):
    """
    Load and concatenate multiple ERA5 NetCDF files into a single xarray Dataset.

    Parameters:
    - filepaths (list of str): list of NetCDF file paths

    Returns:
    - xarray.Dataset: combined dataset
    """
    datasets = [xr.open_dataset(fp) for fp in filepaths]
    combined = xr.concat(datasets, dim='time')
    return combined

# Step 2: Compute wind speed & direction and plot it
def plot_wind_timeseries(dataset, plot_speed=True, plot_direction=False):
    """
    Extract and plot wind speed and/or direction at 10m and 100m for 4 locations.

    Parameters:
    - dataset (xarray.Dataset): loaded dataset
    - plot_speed (bool): whether to plot wind speed
    - plot_direction (bool): whether to plot wind direction
    """
    # Locations of interest
    locations = [
        (55.5, 7.75),
        (55.5, 8.0),
        (55.75, 7.75),
        (55.75, 8.0)
    ]

    for height in [10, 100]:
        u = dataset[f"u{height}"]
        v = dataset[f"v{height}"]

        if plot_speed:
            plt.figure(figsize=(12, 5))
            for lat, lon in locations:
                u_point = u.sel(latitude=lat, longitude=lon, method="nearest")
                v_point = v.sel(latitude=lat, longitude=lon, method="nearest")
                speed = np.sqrt(u_point**2 + v_point**2)
                plt.plot(speed["time"], speed, label=f"{lat}°N, {lon}°E")
            plt.title(f"Wind Speed Time Series at {height}m")
            plt.xlabel("Time")
            plt.ylabel("Wind Speed (m/s)")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        if plot_direction:
            plt.figure(figsize=(12, 5))
            for lat, lon in locations:
                u_point = u.sel(latitude=lat, longitude=lon, method="nearest")
                v_point = v.sel(latitude=lat, longitude=lon, method="nearest")
                direction_rad = np.arctan2(u_point, v_point)
                direction_deg = (np.degrees(direction_rad) + 360) % 360
                plt.plot(direction_deg["time"], direction_deg, label=f"{lat}°N, {lon}°E")
            plt.title(f"Wind Direction Time Series at {height}m")
            plt.xlabel("Time")
            plt.ylabel("Direction (° from North)")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()
