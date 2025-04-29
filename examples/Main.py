import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.__init__ as init
from windrose import WindroseAxes
from scipy.integrate import quad


# Defining data file paths
# this makes path in [0] the MW5 and [1] the MW8
MW5 = "inputs/NREL_Reference_5MW_126.csv"
MW15 = "inputs/NREL_Reference_15MW_240.csv"
filePath = np.array([MW5, MW15])

# Parameters are taken from:
# https://nrel.github.io/turbine-models/LEANWIND_8MW_164_RWT.html
rotor_diameter = 126   # meters
hub_height = 90        # meters
rated_power = 5000     # kW
v_in = 3.0             # cut-in wind speed in m/s
v_rated = 11.4         # rated wind speed in m/s
v_out = 25.0           # cut-out wind speed in m/s
name = "Lets see"

# Defining the objekt
turbineParams = init.TurbineParameters(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name)

# Showcasing the parameters
turbineParams.showcase()



MW = turbineParams.csvReader(filePath)
power_curve = turbineParams.power_curve(MW)


general_turbine = init.GeneralWindTurbine(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, "LEANWIND_5MW_126_General")

detailed_turbine_5MW = init.WindTurbine(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve[0], "LEANWIND_5MW_126_Detailed")

detailed_turbine_15MW = init.WindTurbine(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve[1], "LEANWIND_15MW_240_Detailed")




wind_speeds = np.linspace(0, 30, 300)



# Compute power outputs for each wind speed using both turbine models
power_general = np.array([general_turbine.get_power(v) for v in wind_speeds])
power_detailed_5MW = np.array([detailed_turbine_5MW.get_power(v) for v in wind_speeds])
power_detailed_15MW = np.array([detailed_turbine_15MW.get_power(v) for v in wind_speeds])

# Plot the power curves
plt.figure(figsize=(10, 6))
plt.plot(wind_speeds, power_general, label="GeneralWindTurbine", lw=2)
plt.plot(wind_speeds, power_detailed_5MW, label="WindTurbine (Interpolated) 5MW", lw=2, linestyle='--')
plt.plot(wind_speeds, power_detailed_15MW, label="WindTurbine (Interpolated) 15MW", lw=2, linestyle=':')
plt.xlabel("Wind Speed (m/s)")
plt.ylabel("Power Output (kW)")
plt.title("Comparison of Wind Turbine Power Curves")
plt.legend()
plt.grid(True)
plt.show()


file_path = ["inputs/1997-1999.nc", "inputs/2000-2002.nc", "inputs/2003-2005.nc", "inputs/2006-2008.nc", "inputs/2009-2011.nc", "inputs/2012-2014.nc", "inputs/2015-2017.nc", "inputs/2018-2020.nc"]

df2 = init.nc_reader(file_path)

df = init.wind_speed(df2)

lat_8_lon_55_5, lat_8_lon_55_75, lat_7_75_lon_55_5, lat_7_75_lon_55_75 = init.nc_sorter(df)



interpolatedTable = init.interpolation(7.93, 55.65, lat_8_lon_55_5, lat_8_lon_55_75, lat_7_75_lon_55_5, lat_7_75_lon_55_75)
print(interpolatedTable)

height = 90
height_speed = init.compute_power_law(interpolatedTable, height) 
print(height_speed)
#######snippet code to make stats work

# Choose which height to analyze: 10 or 100?
 
col_name = f"wind_speed_at_{height}[m/s]"

# 1) extract a clean 1-D numpy array
speed_array = height_speed[col_name].to_numpy()
speed_array = speed_array[~np.isnan(speed_array)]

# 2) fit the Weibull distribution
k, A = init.fit_weibull(speed_array)
print(f"Fitted Weibull at {height} m: k = {k:.2f}, A = {A:.2f}")

# 3) plot the histogram vs. the fitted PDF
init.plot_weibull(speed_array, k, A, height)

# wind rose diagram
init.wind_rose(height_speed, height) # IMPORTANT add in README.md "pip install windrose" so people run it #################################################


# AEP
# Choose a turbine to evaluate
chosen_turbine = detailed_turbine_5MW  # or detailed_turbine_15MW

# Use the fitted Weibull parameters
aep = init.compute_aep(chosen_turbine, k, A, chosen_turbine.v_in, chosen_turbine.v_out)

print(f"AEP for {chosen_turbine.name} at {height} m = {aep/1e6:.2f} MWh/year")


