import numpy as np
import pandas as pd

class GeneralWindTurbine:
    """
    Represents a general wind turbine using analytical equations.
    """
    def __init__(self, rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name=None):
        self.rotor_diameter = rotor_diameter
        self.hub_height = hub_height
        self.rated_power = rated_power
        self.v_in = v_in
        self.v_rated = v_rated
        self.v_out = v_out
        self.name = name

    def get_power(self, v):
        if v < self.v_in or v > self.v_out:
            P = 0
        elif self.v_in <= v < self.v_rated:
            P =self.rated_power * (v/self.v_rated) ** 3
        elif self.v_rated <= v < self.v_out:
            P = self.rated_power
        return P


class WindTurbine(GeneralWindTurbine):
    """
    Wind turbine with actual power curve data for interpolation.
    """
    def __init__(self, rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve_data, name=None):
        # Using the parent class __init__ to get the self values 
        super().__init__(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name)
        
        self.power_curve_data = np.array(power_curve_data)

    def get_power(self, v):
        v = np.array(v)
        wind_speed = self.power_curve_data[:, 0]
        power_value = self.power_curve_data[:, 1]

        print("wind_speed:", type(wind_speed), wind_speed.shape)
        print("power_value:", type(power_value), power_value.shape)
        print("v:", v)
        return np.interp(v, wind_speed, power_value)


class TurbineParameters:
    """
    Parameters for the wind turbine.
    """
    def __init__(self, rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name=None):
        self.rotor_diameter = rotor_diameter
        self.hub_height = hub_height
        self.rated_power = rated_power
        self.v_in = v_in
        self.v_rated = v_rated
        self.v_out = v_out
        self.name = name

    def showcase(self):
        print(f"Rotor Diameter: {self.rotor_diameter} m")
        print(f"Hub Height: {self.hub_height} m")
        print(f"Rated Power: {self.rated_power} kW")
        print(f"Cut-in Wind Speed: {self.v_in} m/s")
        print(f"Rated Wind Speed: {self.v_rated} m/s")
        print(f"Cut-out Wind Speed: {self.v_out} m/s")
        if self.name:
            print(f"Turbine Name: {self.name}")
    
    def csvReader(self, filePath):
        MW = []
        for path in filePath:
            df = pd.read_csv(path)
            MW.append(df)
        return MW
    
    def power_curve(self, MW):
        power_curve = []
        for i in range(len(MW)):
            power_curve.append(MW[i].iloc[:, :2].values)
        return power_curve



