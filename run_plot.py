from src.data_loader import load_dataset, plot_wind_timeseries
import os

# Step 1: Load data once (slow step)
data_dir = "inputs"
print(1)
files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".nc")]
print(2)
ds = load_dataset(files)
print(3)
print(ds)

# Step 2: Plot whatever you want (fast)
plot_wind_timeseries(ds, plot_speed=True, plot_direction=False)
