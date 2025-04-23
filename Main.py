import src.turbine as turbine
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Defining data file paths
# this makes path in [0] the MW5 and [1] the MW8
MW5 = "inputs/NREL_Reference_5MW_126.csv"
MW15 = "inputs/NREL_Reference_15MW_240.csv"
filePath = np.array([MW5, MW15])

# Parameters are taken from:
# https://nrel.github.io/turbine-models/LEANWIND_8MW_164_RWT.html
rotor_diameter = 164   # meters
hub_height = 110       # meters
rated_power = 8000     # kW
v_in = 4.0             # cut-in wind speed in m/s
v_rated = 12.5         # rated wind speed in m/s
v_out = 25.0           # cut-out wind speed in m/s
name = "Lets see"

# Defining the objekt
turbineParams = turbine.TurbineParameters(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name)

# Showcasing the parameters
turbineParams.showcase()



MW = turbineParams.csvReader(filePath)
power_curve = turbineParams.power_curve(MW)


general_turbine = turbine.GeneralWindTurbine(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, "LEANWIND_5MW_126_General")

detailed_turbine_5MW = turbine.WindTurbine(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve[0], "LEANWIND_5MW_126_Detailed")

detailed_turbine_8MW = turbine.WindTurbine(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve[1], "LEANWIND_5MW_126_Detailed")




wind_speeds = np.linspace(0, 30, 300)



# Compute power outputs for each wind speed using both turbine models
power_general = np.array([general_turbine.get_power(v) for v in wind_speeds])
power_detailed_5MW = np.array([detailed_turbine_5MW.get_power(v) for v in wind_speeds])
power_detailed_8MW = np.array([detailed_turbine_8MW.get_power(v) for v in wind_speeds])

# Plot the power curves
plt.figure(figsize=(10, 6))
plt.plot(wind_speeds, power_general, label="GeneralWindTurbine", lw=2)
plt.plot(wind_speeds, power_detailed_5MW, label="WindTurbine (Interpolated) 5MW", lw=2, linestyle='--')
plt.plot(wind_speeds, power_detailed_8MW, label="WindTurbine (Interpolated) 8MW", lw=2, linestyle=':')
plt.xlabel("Wind Speed (m/s)")
plt.ylabel("Power Output (kW)")
plt.title("Comparison of Wind Turbine Power Curves")
plt.legend()
plt.grid(True)
plt.show()