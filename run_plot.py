import matplotlib.pyplot as plt
import os
from src.data_loader import load_dataset, compute_wind_speed_at_locations, plot_wind_speed, plot_wind_speed_at_different_heights
import numpy as np


# Collect all .nc file paths from the inputs folder
input_folder = "inputs"
nc_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".nc")]

# Load and combine all NetCDF files
ds = load_dataset(nc_files)



#plot_wind_speed(ds, '10')

#plot_wind_speed(ds, '100')



plot_wind_speed_at_different_heights(ds, heights=['10', '100'])



