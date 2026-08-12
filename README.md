# aquacrop-slovenia

Data, figures and code for a study of maize yield changes in Slovenia under different climate scenarios.  We calibrate Aquacrop for two field experiment sites in Slovenia based on 30 years of measurements of maize yield and biomass. We use the calibrated model to make projections of yield for future climate.

Final calibrated parameters can be found in the [models](/models) folder.

## License

Data and figures are licensed under [CC BY 4.0 International](https://creativecommons.org/licenses/by/4.0/).

Code is licensed under the [MIT license](https://opensource.org/license/mit).

## Reproducing results

Install `Python 3.14` or newer.

This project uses [uv](https://docs.astral.sh/uv/) to manage package dependencies. Install `uv` and then install required packages by syncing the environment with the lockfile:  
```bash
uv sync
```

To reproduce the figures and data:
1. Run Prepare CO2 Concentrations notebook.
2. Run Prepare Weather Letalisce Ljubljana notebook.
3. Run Prepare Weather Murska Sobota notebook.
4. Run Prepare Yield Data notebook.
5. Run Prepare Soil Properties Estimation to obtain Ksat and theta_sat values and copy them to their respective parameter_defaults files.
6. Run CMA-ES KFold Biomass for first round of calibration and copy the best parameters to the parameter_defaults files.
7. Run CMA-ES KFold Grain for second round of calibration and copy the best parameters to the parameter_defaults files.
8. Copy the resulting parameter values to respective projections_parameters files.
9. Run Projections Jablje notebook.
10. Run Projections Rakican notebook.

## Final results

Final calibration parameters can be found in the `models` folder.

## Project Organization

```
├── data
│   ├── external       <- Data from third party sources (climate, co2, weather, yield, soil, mapdata).
│   ├── interim        <- Intermediate data that has been transformed (climate point data extracted from netcdf files).
│   ├── processed      <- The final pickled data sets (climate, co2, weather, yield).
│   └── raw            <- CSVs exported from weather and yield files in the external folder.
│
├── models             <- Calibrated AquaCrop model parameters.
│
├── notebooks          <- Jupyter notebooks, grouped by stage:
│   ├── data_preparation      <- Extract climate/weather CSVs, prepare CO2 and yield data.
│   ├── parameter_estimations <- Soil property and GDD estimation.
│   ├── calibration            <- CMA-ES K-fold calibration (biomass and grain).
│   ├── exploration            <- Optimization experiments, sensitivity analysis, daily simulations.
│   ├── climate_projections    <- Run and analyze yield projections to 2100.
│   └── examples                <- Basic AquaCrop usage examples.
│
├── pyproject.toml     <- Project configuration file with package metadata for
│                         project_name and configuration for tools like ruff
││
├── reports            <- Generated analysis (maps, notebooks).
│   └── figures        <- Generated graphics and figures
│
├── results            <- Calibration, optimization, and projection outputs (pickled).
│
├── uv.lock            <- Package lock file for reproducing the analysis environment,
│                         generated with `uv lock`
│
└── aquacrop_slovenia  <- Source code for use in this project.    │
    ├── config.py                       <- Path constants (ROOT_DIR, DATA_DIR, RESULTS_DIR, ...)
    ├── climate_data.py                 <- Parse NetCDF files, extract CSVs, convert to processed pickles
    ├── yield_projections.py            <- Run yield projections and compute period statistics
    ├── reading_data.py                 <- Load station weather, climate, CO2, and observed yield data
    ├── diagnostics.py                  <- GDD computation and NSE/KGE/mKGE metrics
    ├── plots.py                        <- Code to create visualizations
    ├── parameter_defaults_jablje.py    <- Parameters for Jablje used when running the model and as defaults in calibration
    ├── parameter_defaults_rakican.py   <- Parameters for Rakičan used when running the model and as defaults in calibration
    ├── projection_parameters_jablje.py <- Parameters used for Jablje climate projections
    └── projection_parameters_rakican.py<- Parameters used for Rakičan climate projections
```

## Data sources

### CO2 data

Historical CO2 data was downloaded from the Scripps Institution of Oceanography (SIO) [CO2 data](https://scrippsco2.ucsd.edu/data/atmospheric-co2-data/averaged-products/). We used the MLO and SPO yearly averages.

RCP CO2 concentrations were downloaded from the [RCP database](https://tntcat.iiasa.ac.at/RcpDb/dsd?Action=htmlpage&page=download). We used the CMIP5 recommended data.

### Meteorological data

Meteorological data for the historical period was provided by the Slovenian Environmental Agency (ARSO). It was measured at the following stations:

| Field name | Field latitude | Field longitude | Field altitude [m] | Meteorological station             | ARSO station ID | Latitude | Longitude | Altitude [m] |
|------------|----------------|-----------------|--------------------|------------------------------------|-----------------|----------|-----------|--------------|
| Jablje     | 46.144         | 14.557          | 303                | Letališče Jožeta Pučnika Ljubljana | 8               | 46.2114  | 14.4784   | 362          |
| Rakičan    | 46.654         | 16.190          | 183                | Murska Sobota                      | 355             | 46.6521  | 16.1913   | 189          |

Measured data for Tmin, Tmax, and precipitation are homogenized, while ET0 is not homogenized.
The weather data files are named according to the ARSO station ID.

![map_stations_fields.png](/reports/figures/map_stations_fields.png)

### Climate data 

Gridded climate data was downloaded from the Slovenian open data portal [OPSI](https://podatki.gov.si/) (search for "Podnebne spremembe: Projekcije"). Climate analysis and projections were prepared by the Slovenian Environmental Agency (ARSO).
There is one file for each variable, GCM-RCM combination, scenario, and time period. The files are not included in the repository. When downloaded from OPSI, the files should be placed in the `data/external/climate` directory. Model simulations for the historical period should be placed in the `data/external/climate/hist` directory and files for future periods should be placed in their respective scenario folders (e.g., `data/external/climate/rcp45`).

ARSO provides projections for the following combinations:

| GCM-RCM combination                     | RCP2.6 | RCP4.5 | RCP8.5 |
|-----------------------------------------|--------|--------|--------|
| CNRM_CERFACS-CNRM-CM5/CLMcom-CCLM4-8-17 |        | x      | x      |
| MPI-M-MPI-ESM-LR/CLMcom-CCLM4-8-17      |        | x      | x      |
| ICHEC-EC-EARTH/DMI-HIRHAM5              | x      | x      | x      |
| IPSL-IPSL-CM5A-MR/IPSL-INERIS-WRF331F   |        | x      | x      |
| MOHC-HadGEM2-ES/KNMI-RACMO22E           | x      | x      | x      |
| MPI-M-MPI-ESM-LR/SMHI-RCA4              |        | x      | x      |

## Map data

To produce the maps we used data from the Surveying and Mapping Authority of the Republic of Slovenia [GURS](https://ipi.eprostor.gov.si/jgp/data). We used the following datasets:
- National border record
- Digital elevation model (DEM25)

Hydrography data was downloaded from the Slovenian open data portal and is provided by the MNVP DRSV (Slovenian Water Agency). [Hydrography dataset](https://podatki.gov.si/dataset/hidrografija1)

## Additional information

For Jablje, year 2017 is excluded, because data for ET is missing for most of the vegetation period.

For Rakičan, years 1998 and 2023 are excluded because of missing yield data.

--------