# tests/test_core.py

import numpy as np
import pandas as pd
import xarray as xr
import pytest
import sys
import os
# import everything from your src/__init__.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.__init__ import (
    nc_reader, wind_speed, nc_sorter, interpolation,
    compute_power_law, fit_weibull, plot_weibull, wind_rose
)


@pytest.fixture
def sample_nc(tmp_path):
    # create two tiny xarray datasets and save as netCDF
    times = pd.date_range("2000-01-01", periods=3, freq="H")
    ds1 = xr.Dataset({
        "u10": (("valid_time","latitude","longitude"), np.ones((3,1,1))*2),
        "v10": (("valid_time","latitude","longitude"), np.ones((3,1,1))*3),
        "u100": (("valid_time","latitude","longitude"), np.ones((3,1,1))*4),
        "v100": (("valid_time","latitude","longitude"), np.ones((3,1,1))*5),
    }, coords={"valid_time": times, "latitude":[55.5], "longitude":[7.75]})
    f1 = tmp_path/"a.nc"; ds1.to_netcdf(f1)
    ds2 = ds1.copy(deep=True)
    ds2["u10"].values[:] = 3; ds2["v10"].values[:] = 4
    f2 = tmp_path/"b.nc"; ds2.to_netcdf(f2)
    return [str(f1), str(f2)]


def test_nc_reader_and_wind_speed(sample_nc):
    df = nc_reader(sample_nc)
    # expect 6 rows (3 times × 2 files)
    assert len(df) == 6
    df_ws = wind_speed(df)
    # check new columns exist
    for col in ["wind_speed_10m [m/s]","wind_speed_100m [m/s]",
                "wind_direction_10m [degrees]","wind_direction_100m [degrees]"]:
        assert col in df_ws.columns
    # check first row speed: sqrt(2²+3²)=√13
    assert pytest.approx(np.sqrt(13)) == df_ws["wind_speed_10m [m/s]"].iloc[0]


def test_nc_sorter_and_interpolation():
    times = pd.date_range("2000-01-01", periods=2, freq="H")
    rows = []
    for lat in [55.5,55.75]:
        for lon in [7.75,8.0]:
            for t in times:
                rows.append({
                    "valid_time":t, "latitude":lat, "longitude":lon,
                    "wind_speed_10m [m/s]":lon+lat,
                    "wind_speed_100m [m/s]":2*(lon+lat),
                    "wind_direction_10m [degrees]":10,
                    "wind_direction_100m [degrees]":20
                })
    df = pd.DataFrame(rows)
    c1,c2,c3,c4 = nc_sorter(df)
    assert len(c1)==2 and len(c4)==2

    mid = interpolation(55.625,7.875,c1,c2,c3,c4)
    assert len(mid)==2
    expected = np.mean([55.5+7.75,55.5+8.0,55.75+7.75,55.75+8.0])
    assert np.allclose(mid["wind_speed_10m [m/s]"], expected)


def test_compute_power_law():
    df = pd.DataFrame({
        "valid_time":[0,1],
        "wind_speed_10m":[2,4],
        "wind_speed_100m":[4,8]
    })
    out = compute_power_law(df.copy(), height=50, z1=10, z2=100)
    assert "wind_speed_50m" in out.columns
    assert (out["wind_speed_50m"] > df["wind_speed_10m"]).all()


def test_fit_weibull_and_plot(capsys):
    rng = np.random.default_rng(0)
    data = rng.weibull(2.0, size=500)*8.0
    k,A = fit_weibull(data)
    assert 1.5 < k < 2.5
    assert 5.0 < A < 11.0
    # should not raise
    plot_weibull(data, k, A, height=50, bins=10)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_wind_rose_smoke():
    directions = np.linspace(0,360,36)
    speeds = np.abs(np.sin(np.deg2rad(directions)))
    df = pd.DataFrame({
        "wind_speed_at_50[m/s]":speeds,
        "direction_at_50[degrees]":directions
    })
    # should run without error
    wind_rose(df, height=50)
# tests/test_core.py

import numpy as np
import pandas as pd
import xarray as xr
import pytest

# import everything from your src/__init__.py
from src import (
    nc_reader, wind_speed, nc_sorter, interpolation,
    compute_power_law, fit_weibull, plot_weibull, wind_rose
)


@pytest.fixture
def sample_nc(tmp_path):
    # create two tiny xarray datasets and save as netCDF
    times = pd.date_range("2000-01-01", periods=3, freq="H")
    ds1 = xr.Dataset({
        "u10": (("valid_time","latitude","longitude"), np.ones((3,1,1))*2),
        "v10": (("valid_time","latitude","longitude"), np.ones((3,1,1))*3),
        "u100": (("valid_time","latitude","longitude"), np.ones((3,1,1))*4),
        "v100": (("valid_time","latitude","longitude"), np.ones((3,1,1))*5),
    }, coords={"valid_time": times, "latitude":[55.5], "longitude":[7.75]})
    f1 = tmp_path/"a.nc"; ds1.to_netcdf(f1)
    ds2 = ds1.copy(deep=True)
    ds2["u10"].values[:] = 3; ds2["v10"].values[:] = 4
    f2 = tmp_path/"b.nc"; ds2.to_netcdf(f2)
    return [str(f1), str(f2)]


def test_nc_reader_and_wind_speed(sample_nc):
    df = nc_reader(sample_nc)
    # expect 6 rows (3 times × 2 files)
    assert len(df) == 6
    df_ws = wind_speed(df)
    # check new columns exist
    for col in ["wind_speed_10m [m/s]","wind_speed_100m [m/s]",
                "wind_direction_10m [degrees]","wind_direction_100m [degrees]"]:
        assert col in df_ws.columns
    # check first row speed: sqrt(2²+3²)=√13
    assert pytest.approx(np.sqrt(13)) == df_ws["wind_speed_10m [m/s]"].iloc[0]


def test_nc_sorter_and_interpolation():
    times = pd.date_range("2000-01-01", periods=2, freq="H")
    rows = []
    for lat in [55.5,55.75]:
        for lon in [7.75,8.0]:
            for t in times:
                rows.append({
                    "valid_time":t, "latitude":lat, "longitude":lon,
                    "wind_speed_10m [m/s]":lon+lat,
                    "wind_speed_100m [m/s]":2*(lon+lat),
                    "wind_direction_10m [degrees]":10,
                    "wind_direction_100m [degrees]":20
                })
    df = pd.DataFrame(rows)
    c1,c2,c3,c4 = nc_sorter(df)
    assert len(c1)==2 and len(c4)==2

    mid = interpolation(55.625,7.875,c1,c2,c3,c4)
    assert len(mid)==2
    expected = np.mean([55.5+7.75,55.5+8.0,55.75+7.75,55.75+8.0])
    assert np.allclose(mid["wind_speed_10m [m/s]"], expected)


def test_compute_power_law():
    df = pd.DataFrame({
        "valid_time":[0,1],
        "wind_speed_10m":[2,4],
        "wind_speed_100m":[4,8]
    })
    out = compute_power_law(df.copy(), height=50, z1=10, z2=100)
    assert "wind_speed_50m" in out.columns
    assert (out["wind_speed_50m"] > df["wind_speed_10m"]).all()


def test_fit_weibull_and_plot(capsys):
    rng = np.random.default_rng(0)
    data = rng.weibull(2.0, size=500)*8.0
    k,A = fit_weibull(data)
    assert 1.5 < k < 2.5
    assert 5.0 < A < 11.0
    # should not raise
    plot_weibull(data, k, A, height=50, bins=10)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_wind_rose_smoke():
    directions = np.linspace(0,360,36)
    speeds = np.abs(np.sin(np.deg2rad(directions)))
    df = pd.DataFrame({
        "wind_speed_at_50[m/s]":speeds,
        "direction_at_50[degrees]":directions
    })
    # should run without error
    wind_rose(df, height=50)
