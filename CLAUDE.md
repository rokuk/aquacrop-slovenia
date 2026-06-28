# CLAUDE.md

AquaCrop yield projections for Slovenian maize fields (Jablje + Rakičan). Extracts EURO-CORDEX RCM timeseries, prepares climate/CO2 inputs, and runs projections through 2100 for 6 GCM-RCM combinations × RCP 2.6/4.5/8.5 scenarios.

## Environment & Commands

```bash
make create_environment   # uv: create .venv (Python 3.14)
make requirements         # uv sync
make lint                 # ruff format --check && ruff check
make format               # ruff check --fix && ruff format
```

Activate: `source ./.venv/bin/activate` (Unix) or `.\.venv\Scripts\activate` (Windows).  
Ruff: line length 99, import sorting, first-party `aquacrop_slovenia`.

## Package: `aquacrop_slovenia/`

| Module | Purpose |
|--------|---------|
| `config.py` | Path constants (`ROOT_DIR`, `DATA_DIR`, `INTERIM_CLIMATE_DIR`, `RESULTS_DIR`, `RAMDISK_DIR`, …) |
| `climate_data.py` | Parse NetCDF files, find nearest grid cell, extract CSVs, convert to processed pickles |
| `yield_projections.py` | `run_all_projections()`, `run_model_projection()`, `compute_period_statistics()` |
| `reading_data.py` | Load station weather, climate pickles, CO2, and observed yield (incl. avg-management variants) |
| `diagnostics.py` | `compute_annual_gdd()`; NSE/KGE/mKGE metrics and `print_metrics()` |
| `plots.py` | Grid maps, multi-model timeseries, period statistics, yield comparison plots |
| `parameter_defaults_jablje.py` | Jablje `Crop`, `SoilLayer`, curve number, REW, `jablje_optimal_management`, `jablje_initial_cond` |
| `parameter_defaults_rakican.py` | Same for Rakičan |

## Data Layout

```
data/
  external/climate/{hist,rcp26,rcp45,rcp85}/  # NetCDF files (immutable)
  external/co2/mlo_spo_annual_mean.csv
  interim/climate/                             # {location}_{model}_{scenario}.csv + model_mapping.csv
  processed/climate/                           # Pickled (temperatures, eto, precip) tuples
  processed/co2/{hist,rcp26,rcp45,rcp85}.pkl
  processed/weather/station_{id}.pkl
  processed/yield/maize.pkl
results/projections_v1_{jablje,rakican}.pkl
```

**Pipeline:** `climate_data.extract_all_timeseries()` → `climate_data.prepare_climate_data()` → `yield_projections.run_all_projections()`

Raw units: temperatures in K, precip/ET in kg m⁻² s⁻¹ (× 86400 = mm/day). Historical: 1981–2010; projections: 2011–2100.

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

Short names sorted alphabetically by (GCM, RCM); saved to `model_mapping.csv` on extraction.

## Model Directories

`models/testing3/` (both locations, used by `yield_projections.py`) — has `DATA/`, `LIST/`, `OUTP/`, `SIMUL/` for `aquacrop.exe`.

## Known Quirks

- **model4 / rcp45**: Duplicate date `2099-12-26` (should be `2099-12-25`). Patched in `extract_all_timeseries()`.
- **model4 projections**: End year 2099, not 2100. Handled in `setup_model_for_projections()`.
- **HadGEM2-ES (model3)**: 365-day calendar → converted via `convert_calendar("standard")`; Feb 29 dropped.
- **CO2**: Historical from Scripps MLO/SPO; future from RCP database (CMIP5).
- **Yield exclusions**: 2017 excluded everywhere (missing ET); Rakičan also excludes 1998 and 2023. See `reading_data.get_yield_for_comparison()`.

## Notebooks

```
notebooks/
  data_preparation/   # Extract CSVs, prepare CO2, station weather, yield data
  exploration/        # Projections, optimization (CMA-ES, DE, grid search),
                      #   parameter sensitivity, GDD, daily simulations
  examples/           # Basic AquaCrop usage
reports/location-map.ipynb
```

All notebooks use `%autoreload 2`.
