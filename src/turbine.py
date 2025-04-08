import numpy as np

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
        v = np.array(v)
        power = np.zeros_like(v)
        # Region 2 (below rated)
        mask = (v >= self.v_in) & (v < self.v_rated)
        power[mask] = self.rated_power * (v[mask] / self.v_rated)**3
        # Region 3 (rated to cut-out)
        mask = (v >= self.v_rated) & (v <= self.v_out)
        power[mask] = self.rated_power
        return power


class WindTurbine(GeneralWindTurbine):
    """
    Wind turbine with actual power curve data for interpolation.
    """
    def __init__(self, rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, power_curve_data, name=None):
        super().__init__(rotor_diameter, hub_height, rated_power, v_in, v_rated, v_out, name)
        self.power_curve_data = power_curve_data

    def get_power(self, v):
        v = np.array(v)
        wind_speeds = self.power_curve_data[:, 0]
        powers = self.power_curve_data[:, 1]
        return np.interp(v, wind_speeds, powers, left=0, right=0)
