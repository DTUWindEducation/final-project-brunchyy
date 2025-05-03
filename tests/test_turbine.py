# tests/test_turbine.py

import sys, os
import numpy as np
import pandas as pd
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import GeneralWindTurbine, WindTurbine, TurbineParameters, plot_power_curve, compute_aep


def test_general_turbine_get_power():
    gt = GeneralWindTurbine(100, 90, 1000, v_in=3, v_rated=12, v_out=25)
    assert gt.get_power(2.0) == 0
    # partial region
    expected = 1000*(6/12)**3
    assert pytest.approx(expected, rel=1e-6) == gt.get_power(6.0)
    assert gt.get_power(15.0) == 1000
    assert gt.get_power(30.0) == 0


def test_wind_turbine_interpolation():
    curve = np.array([[0,0],[10,100],[20,200]])
    wt = WindTurbine(100, 90, 200, v_in=0, v_rated=10, v_out=20, power_curve_data=curve)
    out = wt.get_power([5,15,25])
    assert out[0] == 50
    assert out[1] == 150
    assert out[2] == 200


def test_turbine_parameters_and_csv(tmp_path, capfd):
    tp = TurbineParameters(100, 90, 1500, v_in=3, v_rated=12, v_out=25, name="T1")
    tp.showcase()
    captured = capfd.readouterr()
    assert "Rotor Diameter: 100 m" in captured.out

    # CSV reader
    df1 = pd.DataFrame({"a":[1,2],"b":[3,4]})
    f1 = tmp_path/"one.csv"; df1.to_csv(f1, index=False)
    df2 = pd.DataFrame({"x":[5,6],"y":[7,8]})
    f2 = tmp_path/"two.csv"; df2.to_csv(f2, index=False)

    loaded = tp.csv_reader([str(f1), str(f2)])
    assert isinstance(loaded, list) and len(loaded)==2

    pc = tp.power_curve(loaded)
    assert isinstance(pc, list) and pc[0].shape == (2,2)


def test_plot_power_curve_and_aep():
    # plot_power_curve smoke test
    speeds = np.linspace(0,20,5)
    pc = [np.column_stack((speeds, speeds*2)), np.column_stack((speeds, speeds*3))]
    plot_power_curve(speeds, rotor_diameter=100, hub_height=90,
                     rated_power=5000, v_in=3, v_rated=12, v_out=25,
                     power_curve=pc)

    # compute_aep with constant turbine
    class Const:
        def get_power(self,u): return 1.0

    aep = compute_aep(Const(), k=2.0, a=8.0, u_in=0.0, u_out=np.inf)
    assert pytest.approx(8760, rel=1e-6) == aep
