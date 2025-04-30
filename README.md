```markdown
[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zjSXGKeR)

# Wind Resource Assessment Package

**Team:** Alicia Masero, August …  , Sofia …

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Quick-start Guide](#quick-start-guide)  
4. [Architecture & Modules](#architecture--modules)  
5. [Installation](#installation)  
6. [Usage Examples](#usage-examples)  
7. [Testing](#testing)  
8. [Peer Review Notes](#peer-review-notes)  
9. [License](#license)  

---

## Overview

This Python package automates a full wind-resource assessment (WRA) workflow using ERA5 reanalysis data. It supports:

- Loading & parsing multi-year NetCDF4 files (ERA5 u/v at 10 m & 100 m).  
- Computing wind speed & direction at measurement heights.  
- Bilinear interpolation to an arbitrary site within the grid.  
- Vertical extrapolation to turbine hub height via the power-law profile.  
- Statistical analysis: Weibull distribution fitting & histogram overlay.  
- Wind-rose visualization of directional frequency and speed classes.  
- AEP estimation using generic or data-driven turbine power curves.  

This package implements Questions 1–8 of the DTU “Scientific Programming for Wind Energy” final project.

---

## Features

- **Data ingestion:** `nc_reader`  
- **Wind metrics:** `wind_speed`, `wind_direction`  
- **Spatial interpolation:** `nc_sorter`, `interpolation`  
- **Vertical extrapolation:** `compute_power_law`  
- **Weibull analysis:** `fit_weibull`, `plot_weibull`  
- **Wind rose:** `wind_rose`  
- **Turbine modeling:** `GeneralWindTurbine`, `WindTurbine`, `TurbineParameters`  
- **AEP calculation** (coming in Q8)  

---

## Quick-start Guide

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-org/your-repo.git
   cd your-repo
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the analysis script**  
   ```bash
   python src/analysis.py
   ```
   This will produce:
   - Time-series plots of wind speed  
   - Weibull‐fit histogram  
   - Wind-rose polar plots  

4. **Run tests**  
   ```bash
   pytest tests/
   ```

---

## Architecture & Modules

```
wind_resource_assessment/
├── inputs/                 # ERA5 NetCDF4 files
├── src/
│   ├── __init__.py         # core functions
│   ├── analysis.py         # end-to-end driver script
│   ├── stats.py            # Weibull fitting & plotting
│   ├── wind_rose.py        # wind-rose visualization
│   ├── data_loader.py      # nc_reader, wind_speed, nc_sorter
│   └── shear.py            # compute_power_law
├── turbine_data/           # CSV power-curve files
├── tests/                  # pytest suites
├── requirements.txt
└── README.md
```

- **`data_loader.py`**: Q1–Q3  
- **`shear.py`**: Q4  
- **`stats.py`**: Q5–Q6  
- **`wind_rose.py`**: Q7  
- **`analysis.py`**: orchestrates Q1–Q7 and prepares for Q8  

---

## Installation

```bash
# create & activate virtual env (optional)
python -m venv venv && source venv/bin/activate

# install requirements
pip install -r requirements.txt
```

---

## Usage Examples

### 1. Load & preprocess data  
```python
from data_loader import nc_reader, wind_speed, nc_sorter, interpolation

df2 = nc_reader("inputs/1997-1999.nc")
df  = wind_speed(df2)
c1, c2, c3, c4 = nc_sorter(df)
site_df = interpolation(55.527, 7.906, c1,c2,c3,c4)
```

### 2. Shear to hub height  
```python
from shear import compute_power_law
hub_df = compute_power_law(site_df, z1=10, z2=100, height=90)
```

### 3. Weibull analysis  
```python
from stats import fit_weibull, plot_weibull
speed_array = hub_df["wind_speed_90m"].to_numpy()
k, A = fit_weibull(speed_array)
plot_weibull(speed_array, k, A)
```

### 4. Wind rose  
```python
from wind_rose import plot_wind_rose
dirs  = hub_df["wind_direction_90m"].to_numpy()
speeds= hub_df["wind_speed_90m"].to_numpy()
plot_wind_rose(dirs, speeds, dir_bins=16, speed_bins=[0,4,8,12,16])
```

---

## Testing

We use **pytest**. To run all tests:

```bash
pytest tests/
```

Coverage reports ensure each function is exercised.

---

## Peer Review Notes

- **Interpolation**: check lat/lon fraction ordering.  
- **Shear**: validated against analytical power-law.  
- **Weibull fit**: cross-checked with SciPy reference.  
- **Wind rose**: verified directional bin counts.  
- **Turbine models**: edge cases (cut-in/out) tested.  

Please leave comments on module clarity, edge-case handling, and documentation completeness.

---

## License

This project is released under the MIT License.  
```
