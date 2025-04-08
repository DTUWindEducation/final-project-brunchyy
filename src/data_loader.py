import xarray as xr
import numpy as np
import os
import matplotlib.pyplot as plt

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


def plot_wind_speed(ds,height='10'):
    wind_speeds = compute_wind_speed_at_locations(ds, height)


    for (lat, lon), speed in wind_speeds.items():
        plt.figure(figsize=(15, 4))
        speed.plot()
        plt.title(f"Wind Speed at {height} m ({lat}°N, {lon}°E)")
        plt.ylabel("Wind Speed [m/s]")
        plt.xlabel("Time")
        plt.grid(True)
        plt.tight_layout()
        plt.show()



# Not done
#def plot_wind_speed_at_different_heights(ds,heights=['10', '100']): 
#    
#    wind_speeds = {}
#
#    for i in range(len(heights)):
#        wind_speeds[i] = compute_wind_speed_at_locations(ds, heights[i])
#
#
#    for (lat, lon), speed in wind_speeds[i].items():
#        for i in range(len(heights)):    
#            plt.figure(figsize=(15, 4))
#            if i == 0:
#                speed.plot(color='blue')
#            else:
#                speed.plot(color='green')
#            
#        plt.title(f"Wind Speed at {heights[i]} m ({lat}°N, {lon}°E)")
#        plt.ylabel("Wind Speed [m/s]")
#        plt.xlabel("Time")
#        plt.grid(True)
#        plt.tight_layout()
#        plt.show()

def plot_wind_speed_at_different_heights(ds, heights=['10', '100']):
    wind_speeds = {}

    # Beregn vindhastighed for hver højde og gem resultaterne i en ordbog
    for i in range(len(heights)):
        wind_speeds[i] = compute_wind_speed_at_locations(ds, heights[i])

    # Plot vindhastighederne for hver kombination af lat og lon
    for (lat, lon), speed_dict in wind_speeds[0].items():
        plt.figure(figsize=(15, 4))  # Opret en ny figur pr. (lat, lon) kombination
        for i in range(len(heights)):
            # Plot alle værdier af højden (forskellige farver for hver højde)
            speed = wind_speeds[i].get((lat, lon), [])
            if speed.size > 0:  # Hvis der er data for den pågældende lat/lon
                label = f"Height {heights[i]} m"
                color = 'blue' if i == 0 else 'green'  # Skift farve for forskellige højder
                speed.plot(color=color, label=label)

        # Tilføj plotdetaljer
        plt.title(f"Wind Speed at different heights ({lat}°N, {lon}°E)")
        plt.ylabel("Wind Speed [m/s]")
        plt.xlabel("Time")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
    

