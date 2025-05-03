# tests/test_core.py

import sys, os
import numpy as np
import pandas as pd
import xarray as xr
import pytest

# ensure project root is on the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    nc_reader,
    wind_speed_df,
    nc_sorter,
    interpolation,
    compute_power_law,
    fit_weibull,
    plot_weibull,
    wind_rose,
)


@pytest.fixture
def sample_nc(tmp_path):
    # two tiny ERA5‐like files
    times = pd.date_range("2000-01-01", periods=3, freq="h")
    
    ds1 = xr.Dataset(
        {
            "u10": (("valid_time","latitude","longitude"), np.ones((3,1,1))*2),
            "v10": (("valid_time","latitude","longitude"), np.ones((3,1,1))*3),
            "u100": (("valid_time","latitude","longitude"), np.ones((3,1,1))*4),
            "v100": (("valid_time","latitude","longitude"), np.ones((3,1,1))*5),
        },
        coords={"valid_time": times, "latitude":[55.5], "longitude":[7.75]}
    )
    f1 = tmp_path/"a.nc"; ds1.to_netcdf(f1)
    ds2 = ds1.copy(deep=True)
    ds2["u10"].values[:] = 3; ds2["v10"].values[:] = 4
    f2 = tmp_path/"b.nc"; ds2.to_netcdf(f2)
    return [str(f1), str(f2)]


def test_nc_reader_and_wind_speed(sample_nc):
    df = nc_reader(sample_nc)
    assert len(df) == 6
    df_ws = wind_speed_df(df)
    # new columns exist
    for col in [
        "wind_speed_10m [m/s]", "wind_speed_100m [m/s]",
        "wind_direction_10m [degrees]", "wind_direction_100m [degrees]"
    ]:
        assert col in df_ws.columns
    # first wind_speed_10m = sqrt(2²+3²)
    assert pytest.approx(np.sqrt(13)) == df_ws["wind_speed_10m [m/s]"].iloc[0]


def test_nc_sorter_and_interpolation():
    times = pd.date_range("2000-01-01", periods=2, freq="h")  # fixed warning
    rows = []
    for lat in [55.5, 55.75]:
        for lon in [7.75, 8.0]:
            for t in times:
                rows.append({
                    "valid_time": t,
                    "latitude": lat,
                    "longitude": lon,
                    "wind_speed_10m [m/s]": lat + lon,
                    "wind_speed_100m [m/s]": 2 * (lat + lon),
                    "wind_direction_10m [degrees]": 10,
                    "wind_direction_100m [degrees]": 20
                })
    df = pd.DataFrame(rows)
    tables = nc_sorter(df)

    # Adapted key format to your interpolation function
    assert set(tables.keys()) == {
        "lat_7.75_lon_55.5", "lat_8.0_lon_55.5",
        "lat_7.75_lon_55.75", "lat_8.0_lon_55.75"
    }

    # Run interpolation without errors
    mid = interpolation(55.625, 7.875, tables)

    # Optionally check that the result has expected structure
    assert "wind_speed_10m [m/s]" in mid.columns



def test_compute_power_law():
    df = pd.DataFrame({
        "valid_time":[0,1],
        "wind_speed_10m [m/s]":[2,4],
        "wind_speed_100m [m/s]":[4,8],
        "wind_direction_10m [degrees]":[0,10],
        "wind_direction_100m [degrees]":[20,30]
    })
    out = compute_power_law(df.copy(), height=50, z1=10, z2=100)
    # new columns
    assert "wind_speed_at_50[m/s]" in out.columns
    assert "direction_at_50[degrees]" in out.columns
    # speeds lie between
    assert (out["wind_speed_at_50[m/s]"] > df["wind_speed_10m [m/s]"]).all()
    assert (out["wind_speed_at_50[m/s]"] < df["wind_speed_100m [m/s]"]).all()


def test_fit_weibull_and_plot(capsys):
    rng = np.random.default_rng(0)
    data = rng.weibull(2.0, size=500)*8.0
    k,A = fit_weibull(data)
    assert 1.0 < k < 3.0
    assert 5.0 < A < 15.0
    # plot should not raise or print
    plot_weibull(data, k, A, height=50, bins=10)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_wind_rose_smoke():
    # create DataFrame matching signature
    directions = np.linspace(0,360,36)
    speeds = np.abs(np.sin(np.deg2rad(directions)))
    df = pd.DataFrame({
        "wind_speed_at_50[m/s]": speeds,
        "direction_at_50[degrees]": directions
    })
    # should run without exception
    wind_rose(df, height=50)
