import os
from src.data_loader import load_dataset

def test_load_dataset():
    # Get NetCDF file paths
    files = [f"inputs/{f}" for f in os.listdir("inputs") if f.endswith(".nc")]

    # Load dataset
    dataset = load_dataset(files)

    # Basic checks
    assert dataset is not None
    assert "u10" in dataset.variables
    assert "v10" in dataset.variables
    assert "u100" in dataset.variables
    assert "v100" in dataset.variables
    assert dataset.sizes["time"] > 0
