

# 🌬️ Wind Resource Assessment – *final-project-brunchyy*

This Python package performs a full **wind resource assessment** using reanalysis data, power curves from reference wind turbines, and spatial interpolation to estimate energy yield at a given site. The package processes NetCDF data, interpolates wind values at a target location, computes Weibull distributions, and estimates Annual Energy Production (AEP) using reference turbine curves.

It is designed to help users assess the viability of wind energy projects and visualize key metrics such as wind roses and power curves.

---

##  File Structure

```
WIND RESOURCE ASSESSMENT/
├── inputs/                      # All input data (NetCDF, turbine CSVs, diagrams)
│   ├── 1997-1999.nc
│   ├── 2000-2002.nc
│   ├── 2003-2005.nc
│   ├── 2006-2008.nc
│   ├── NREL_Reference_15MW_240.csv
│   ├── NREL_Reference_5MW_126.csv
│   └── Wind_resource_assessment_procedure.jpeg
├── outputs/                     # To be populated by results
├── src/                         # Source functions and classes
│   └── __init__.py
│   └── <wra_brunchyy>/          # Main package directory 
├── examples/                    # Run-ready scripts
│   └── main.py
├── tests/                       # Unit tests
│   ├── test_core.py
│   └── test_turbine.py
├── Diagram.drawio              # Architecture diagram
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
└── environment.yml
```

---

## 1 - Overview of the Package

This package offers a **modular and reusable workflow** for evaluating the wind energy potential at any given location based on meteorological data and turbine characteristics. Core functionalities include:

* Parsing and organizing NetCDF files
* Sorting and interpolating wind data
* Applying turbine power curves
* Estimating Weibull parameters
* Visualizing results (histograms, wind roses, power curves)
* Computing AEP

---

## 2 - Installation Instructions

Open Anaconda Prompt, then navigate to the folder where you want to place the project, and follow the next steps.

### Step 1: Clone the Repository

```bash
git clone https://github.com/DTUWindEducation/final-project-brunchyy.git
cd final-project-brunchyy
```

### Step 2: Create and Activate the Conda Environment

```bash
conda env create -f environment.yml
conda activate wra_brunchyy
```

### Step 3: Install the Package (Editable Mode)

```bash
pip install -e .
```

### Step 4: Run the Main Script

```bash
python examples/main.py
```

This will output:

* Wind turbine power curve plots
* Interpolated wind data
* Weibull fit and histogram
* Wind rose diagram
* AEP estimate

### Step 5: Run Tests

```bash
pytest tests/
```

---

## 3 - Architecture and Class Description

This package follows a clean, modular design. Key components include:

* **Data Loading & Sorting**
  Functions that load NetCDF data and organize it by grid cells.

* **Interpolation**
  Interpolates wind data (speed and direction) to a target location based on surrounding grid cells.

* **WindTurbine Class**
  Encapsulates turbine parameters and interpolates power output using the given power curve.

* **Plotting Functions**
  Used to create wind roses, histograms, and power curve plots.

### Architecture Diagram

A visual representation of function interactions and data flow:

![figure](diagram.jpeg)

---

## 4 - Description of Classes

**WindTurbine (in `src/__init__.py`)**
A class that takes hub height, rotor diameter, rated power, and power curve data. Core method:

* `get_power(wind_speeds)` → returns estimated power output.

**Interpolation Function**
Interpolates wind speed and direction using bilinear interpolation from surrounding grid data.

**Utility Functions**
Load turbine CSVs, calculate Weibull distributions, visualize wind data.

---

## 5 - Git Workflow & Collaboration Description

Our team followed a **branch-based Git workflow**, collaborating via GitHub:

* Each member created their own feature/test branches.
* We used pull requests (PRs) to propose changes, ensuring that every PR included:

  * A brief description
  * Associated tests
  * Code reviews before merging to `main`

Tests were written using `pytest`, and code was organized in a testable, modular structure from the beginning. We used `environment.yml` to keep dependencies unified.

---


## Collaboration Workflow

We **equally divided the work** and collaborated on each core task using dedicated **feature branches**. Each member was responsible for implementing and reviewing different parts of the workflow, but all decisions were made collectively.

* For each task, we **created a separate branch** (e.g., `feature/interpolation`, `test/weibull`, etc.).
* Once a task was complete, we **opened a pull request** and **requested feedback** from all team members.
* **Nothing was pushed to `main`** without **consensus and approval** from the full team.
* We followed a **test-driven** approach, writing tests for each function to ensure correctness before merging.
* Code was reviewed collaboratively, and **every contribution required passing tests and lint checks**.

This approach helped ensure high code quality and a shared understanding of the full project.

---

##  License

This project is licensed under the MIT License – see the `LICENSE` file for details.

