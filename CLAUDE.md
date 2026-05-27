# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AquaCrop yield projections for Slovenian maize fields. The project:
1. **Extracts** point timeseries from EURO-CORDEX regional climate model (RCM) NetCDF files (ARSO historical + 6 GCM-RCM combinations × RCP 2.6/4.5/8.5 scenarios).
2. **Prepares** climate and CO2 inputs for AquaCrop simulations.
3. **Runs yield projections** through 2100 using `pyaquacrop` for each model/scenario combination at both locations.


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
make clean     # Remove compiled Python files and __pycache__
```

Run linting directly:
```bash
ruff check aquacrop_slovenia/
ruff format --check aquacrop_slovenia/
```

## Code Architecture

The package is `aquacrop_slovenia/`.

| Module | Purpose |
|--------|---------|
| `config.py` | Path constants (`ROOT_DIR`, `DATA_DIR`, `INTERIM_CLIMATE_DIR`, `RESULTS_DIR`, …) |
| `climate_data.py` | Discover/parse NetCDF files, find nearest grid cell, extract & save per-model CSV timeseries, convert to processed pickles |
| `yield_projections.py` | `run_all_projections()` / `run_model_projection()` using `pyaquacrop`; `compute_period_statistics()` for 30-year summary stats |
| `reading_data.py` | Load processed climate pickles, CO2 records, and observed yield data |
| `prepare_weather.py` | Load station weather pickles → `(temperatures, eto_values, rainfall_values)` |
| `diagnostics.py` | `compute_annual_gdd()` from station weather data |
| `plots.py` | Cartopy grid maps, multi-model timeseries, 30-year period statistics, observed/modelled yield comparison plots |
| `parameter_defaults_jablje.py` | Jablje maize `Crop` params, `SoilLayer`, curve number, readily evaporable water |
| `parameter_defaults_rakican.py` | Same for Rakičan |
| `management_defaults.py` | Shared `optimal_management` object |
| `intial_conditions_defaults.py` | Shared `InitialConditions` params (note: typo in filename is intentional) |

Code in the package is called from Jupyter notebooks in `notebooks/`.

## Data Layout and Flow

```
data/
  external/
    climate/{hist,rcp26,rcp45,rcp85}/   # Original NetCDF files (immutable)
    co2/mlo_spo_annual_mean.csv          # Scripps historical CO2
    mapdata/DMV0250/                     # DEM tiles from GURS
  interim/
    climate/                             # Per-location/model/scenario CSVs
                                         #   {location}_{model}_{scenario}.csv
                                         #   model_mapping.csv
    yield/maize-{location}.csv           # Processed observed yield data
  processed/
    climate/                             # Pickled (temperatures, eto, precip) tuples
    co2/{hist,rcp26,rcp45,rcp85}.pkl     # CO2 records for AquaCrop
    weather/station_{id}.pkl             # Processed ARSO station weather
    yield/maize.pkl                      # Combined yield DataFrame

results/
  projections_v1_jablje.pkl
  projections_v1_rakican.pkl
```

**Processing pipeline:**

1. **Extract timeseries** — `climate_data.extract_all_timeseries(lat, lon, location)` reads NetCDF → writes CSV + `model_mapping.csv` to `data/interim/climate/`
2. **Prepare climate** — `climate_data.prepare_climate_data(location)` converts CSVs (K, kg m⁻² s⁻¹) to pickled `(temperatures, eto, precip)` tuples (°C, mm/day)
3. **Run projections** — `yield_projections.run_all_projections(location)` → saves results to `results/`

## NetCDF File Naming

RCM files: `{variable}_{resolution}_{GCM}_{scenario}_{run}_{RCM}_{version}_day_{start}_{end}.nc`

ARSO observational files: `{variable}_12km_ARSO_{version}_day_{start}_{end}.nc`

Variables: `pr` (precipitation), `tas` (mean temperature), `tasmax`, `tasmin`, `evspsblpot` (potential ET).

Raw units: temperatures in **K**, precipitation and ET in **kg m⁻² s⁻¹** (multiply by 86400 for mm/day).

Historical data covers 1981–2010; future projections cover 2011–2100.

## GCM-RCM Combinations

| Short name | GCM | RCM | RCP2.6 | RCP4.5 | RCP8.5 |
|-----------|-----|-----|--------|--------|--------|
| obs | ARSO | — | hist only | — | — |
| model1 | CNRM-CM5-LR | CCLM4-8-17 | | x | x |
| model2 | EC-EARTH | HIRHAM5 | x | x | x |
| model3 | HadGEM2-ES | RACMO22E | x | x | x |
| model4 | IPSL-CM5A-MR | WRF331F | | x | x |
| model5 | MPI-ESM-LR | CCLM4-8-17 | | x | x |
| model6 | MPI-ESM-LR | RCA4 | | x | x |

Short names are stable: RCM models sorted alphabetically by (GCM, RCM). The mapping is saved to `data/interim/climate/model_mapping.csv` on each extraction run.

## Model Directories

AquaCrop `.exe`-based runs use prepared directories under `models/`:

| Directory | Contents |
|-----------|----------|
| `models/testing/` | Jablje-only setup |
| `models/testing2/` | Rakičan-only setup |
| `models/testing3/` | Both Jablje and Rakičan (used by `yield_projections.py`) |

Each directory has the `DATA/`, `LIST/`, `OUTP/`, and `SIMUL/` subdirectories expected by `aquacrop.exe`.

## Known Quirks

- **model4 / rcp45**: Contains a duplicate date `2099-12-26` (instead of `2099-12-25`). Patched in `climate_data.extract_all_timeseries()`.
- **model4 projections**: End year is 2099 instead of 2100. Handled in `yield_projections.setup_model()`.
- **HadGEM2-ES (model3)**: Uses a 365-day calendar. Converted to standard Gregorian via `xr.DataArray.convert_calendar("standard")` — Feb 29 is dropped.
- **CO2 data**: Historical (1981–2010) from Scripps MLO/SPO; future from the RCP database (CMIP5 recommended).
- **Observed yield exclusions**: Year 2017 is excluded from comparisons (missing ET data); Rakičan additionally excludes 1998 and 2023 (some missing yield data). See `reading_data.get_yield_for_comparison()`.

## Notebooks

```
notebooks/
  data_preparation/    # Extract climate CSVs, prepare CO2, station weather, yield data
  exploration/         # Run projections and explore results for Jablje and Rakičan
  examples/            # Basic AquaCrop usage examples
reports/
  location-map.ipynb   # Station/field location map
```

All notebooks use `%autoreload 2` for iterative development against the package.

## Documentation

MkDocs site in `docs/`. Source in `docs/docs/`:
- `index.md` — overview
- `data-sources.md` — data provenance (OPSI, ARSO, Scripps, GURS)
- `calibration.md` — notes on excluded years
- `parameters.md` — AquaCrop parameter descriptions

## Ruff Configuration

Line length: 99. Import sorting enabled (`extend-select = ["I"]`). First-party: `aquacrop_slovenia`.