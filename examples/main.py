import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.__init__ as init
from windrose import WindroseAxes
from scipy.integrate import quad

# Create outputs/ folder if it doesn't exist
os.makedirs("outputs", exist_ok=True)

# Defining data file paths
# this makes path in [0] the MW5 and [1] the MW8
MW5 = "inputs/NREL_Reference_5MW_126.csv"
MW15 = "inputs/NREL_Reference_15MW_240.csv"
filePath = np.array([MW5, MW15])

# Parameters are taken from:
# NREL 5 MW reference turbine:
rotor_diameter = 126   # meters
hub_height = 90        # meters
rated_power = 5000     # kW
v_in = 3.0             # cut-in wind speed in m/s
v_rated = 11.4         # rated wind speed in m/s
v_out = 25.0           # cut-out wind speed in m/s
name = "Lets see"

# Defining the object
turbineParams = init.TurbineParameters(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name)

# Showcasing the parameters
turbineParams.showcase()

# Read the turbine data from the CSV file and create a power curve
MW = turbineParams.csv_reader(filePath)
power_curve = turbineParams.power_curve(MW)

wind_speeds = np.linspace(0, 30, 300)

# Plot the power curve
init.plot_power_curve(wind_speeds, rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve)

# Defining the file paths for the wind data
file_path = ["inputs/1997-1999.nc", "inputs/2000-2002.nc", "inputs/2003-2005.nc", "inputs/2006-2008.nc"]

df2 = init.nc_reader(file_path)

df = init.wind_speed_df(df2)

tables = init.nc_sorter(df)

interpolated_table = init.interpolation(7.93, 55.65, tables)
print(interpolated_table)

# Give the height to be computed
height = 90
height_speed = init.compute_power_law(interpolated_table, height) 
print(height_speed)

col_name = f"wind_speed_at_{height}[m/s]"

# Weibull
# 1) extract a clean 1-D numpy array
speed_array = height_speed[col_name].to_numpy()
speed_array = speed_array[~np.isnan(speed_array)]

# 2) fit the Weibull distribution
k, A = init.fit_weibull(speed_array)
print(f"Fitted Weibull at {height} m: k = {k:.2f}, A = {A:.2f}")

# 3) plot the histogram vs. the fitted PDF
init.plot_weibull(speed_array, k, A, height)

# Wind rose diagram
init.wind_rose(height_speed, height)

# AEP
# Choose a turbine to evaluate
chosen_turbine = init.WindTurbine(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve[0], "LEANWIND_5MW_126_Detailed")  # or detailed_turbine_15MW

# Use the fitted Weibull parameters
aep = init.compute_aep(chosen_turbine, k, A, chosen_turbine.v_in, chosen_turbine.v_out)

print(f"AEP for {chosen_turbine.name} at {height} m = {aep/1e6:.2f} MWh/year")


# Save in the outputs folder the results
# Save the interpolated data and height-adjusted speeds
interpolated_table.to_csv("outputs/interpolated_data.csv", index=False)
height_speed.to_csv(f"outputs/wind_data_{height}m.csv", index=False)

# Save AEP result to a text file
with open("outputs/aep_result.txt", "w") as f:
    f.write(f"AEP for {chosen_turbine.name} at {height} m = {aep/1e6:.2f} MWh/year\n")
