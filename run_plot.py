import matplotlib.pyplot as plt
import os
from src.data_loader import load_dataset, compute_wind_speed_at_locations

# Collect all .nc file paths from the inputs folder
input_folder = "inputs"
nc_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".nc")]

# Load and combine all NetCDF files
ds = load_dataset(nc_files)

# Compute wind speed at 10 m height
wind_speeds = compute_wind_speed_at_locations(ds, '100')

# Plot wind speed time series for each location
for (lat, lon), speed in wind_speeds.items():
    plt.figure(figsize=(15, 4))
    speed.plot()
    plt.title(f"Wind Speed at 100 m ({lat}°N, {lon}°E)")
    plt.ylabel("Wind Speed [m/s]")
    plt.xlabel("Time")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
