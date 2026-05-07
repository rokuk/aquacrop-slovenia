# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Calibration of AquaCrop for Slovenian locations. The project processes regional climate model (RCM) outputs from NetCDF files (historical, rcp26, rcp45, rcp85 scenarios from OPSI) and extracts/transforms timeseries for use in AquaCrop simulations.

## Environment Setup

Uses `uv` for dependency and environment management:

```bash
make create_environment   # Create .venv with Python 3.14
make requirements         # Install dependencies (uv sync)
```

Activate the environment:
- Windows: `.\.venv\Scripts\activate`
- Unix/macOS: `source ./.venv/bin/activate`

## Common Commands

```bash
make lint      # Check formatting and linting (ruff format --check && ruff check)
make format    # Auto-fix and format (ruff check --fix && ruff format)
make data      # Run dataset generation script
make clean     # Remove compiled Python files and __pycache__
```

Run linting directly:
```bash
ruff check aquacrop_slovenia/
ruff format --check aquacrop_slovenia/
```

## Code Architecture

The package is `aquacrop_slovenia/` (installed via `setup.py` with `find_packages()`). The planned module structure (from README) is:

- `config.py` — shared variables and configuration (paths, constants)
- `dataset.py` — data download/generation scripts
- `features.py` — feature engineering for modeling
- `modeling/train.py` — model training
- `modeling/predict.py` — inference with trained models
- `plots.py` — visualization utilities

**Note:** As of initial commit, only `__init__.py` exists; the other modules are planned but not yet implemented.

## Data Layout

```
data/
  external/                                  # External data sources (immutable)
  external/climate/{hist,rcp26,rcp45,rcp85}/ # Original NetCDF files (immutable)
  raw/                                       # Raw data
  interim/                                   # Intermediate transformed data
  processed/                                 # Final datasets for modeling
```

NetCDF files follow the naming pattern: `{variable}_{resolution}_{GCM}_{scenario}_{run}_{RCM}_{version}_day_{start}_{end}.nc`

Variables: `pr` (precipitation), `tas` (mean temperature), `tasmax`, `tasmin`, `evspsblpot` (potential evapotranspiration).

Historical data covers 1981-2010; future projections cover 2011-2100 in 30-year chunks.

## Ruff Configuration

Line length: 99. Import sorting is enabled (`extend-select = ["I"]`). First-party module: `aquacrop_slovenia`.

## Notebooks

Jupyter notebooks live in `notebooks/`. The `Extract Timeseries` notebook reads climate projections from the NetCDF files and extracts point timeseries for each model/scenario combination. Uses `%autoreload 2` for iterative development against the package.