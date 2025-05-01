# tests/test_turbine.py

import numpy as np
import pytest
from your_package import GeneralWindTurbine, WindTurbine, TurbineParameters

def test_general_turbine_power():
    gt = GeneralWindTurbine(100, 90, rated_power=1000, v_in=3, v_rated=12, v_out=25)
    # below cut-in
    assert gt.get_power(2.0) == 0
    # between v_in and v_rated: P ∝ v³
    p = gt.get_power(6.0)
    assert pytest.approx(p, rel=1e-3) == 1000*(6/12)**3
    # above rated but below cut-out: constant
    assert gt.get_power(15.0) == 1000
    # above cut-out
    assert gt.get_power(30.0) == 0

def test_wind_turbine_interpolation():
    # simple power curve: (v,p): (0,0),(10,100),(20,200)
    curve = np.array([[0,0],[10,100],[20,200]])
    wt = WindTurbine(100, 90, 200, 0, 10, 20, power_curve_data=curve)
    # test interpolation
    vs = [0,5,10,15,20,25]
    out = wt.get_power(vs)
    # at 5 m/s → half of 100
    assert out[1] == 50
    # above cut-out returns 0
    assert out[-1] == 0

def test_turbine_parameters_methods(capfd):
    tp = TurbineParameters(100, 90, 1000, 3, 12, 25, name="TestTurbine")
    # showcase prints lines
    tp.showcase()
    captured = capfd.readouterr()
    assert "Rotor Diameter: 100 m" in captured.out
    # csvReader & power_curve
    # create two small CSVs
    import pandas as pd
    df1 = pd.DataFrame({"a":[1,2],"b":[3,4]})
    path1 = "temp1.csv"; df1.to_csv(path1,index=False)
    df2 = pd.DataFrame({"x":[5,6],"y":[7,8]})
    path2 = "temp2.csv"; df2.to_csv(path2,index=False)
    loaded = tp.csvReader([path1,path2])
    assert all(isinstance(df, pd.DataFrame) for df in loaded)
    pc = tp.power_curve(loaded)
    assert isinstance(pc, list) and pc[0].shape==(2,2)
    # cleanup
    import os; os.remove(path1); os.remove(path2)
