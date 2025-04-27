import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from src.__init__ import GeneralWindTurbine, WindTurbine

# Load power curve from CSV
df = pd.read_csv("inputs/NREL_Reference_5MW_126.csv")
power_curve = df[["Wind Speed [m/s]", "Power [kW]"]].to_numpy()

# Specs from the NREL data
rotor_diameter = 126
hub_height = 90
rated_power = 5000
v_in = 3
v_rated = 11.4
v_out = 25

# Initialize both turbines
turbine_analytical = GeneralWindTurbine(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name="Analytical")
turbine_curve = WindTurbine(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve, name="Interpolated")

# Test and plot
v_range = np.linspace(0, 26, 300)
power_analytical = turbine_analytical.get_power(v_range)
power_interpolated = turbine_curve.get_power(v_range)

plt.plot(v_range, power_analytical, label="General (Analytical)", linestyle="--")
plt.plot(v_range, power_interpolated, label="WindTurbine (Interpolated)", alpha=0.8)
plt.xlabel("Wind Speed [m/s]")
plt.ylabel("Power Output [kW]")
plt.title("Power Curve Comparison - NREL 5MW")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
