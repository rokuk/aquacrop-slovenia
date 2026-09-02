# aquacrop-slovenia

## THIS REPOSITORY IS A WORK IN PROGRESS UNTIL 31.8.2026 !!!

Data, figures, and code for a study of maize yield changes in Slovenia under different climate scenarios.  We calibrate Aquacrop for two field experiment sites in Slovenia based on 30 years of measurements of maize yield and biomass. We use the calibrated model to make projections of yield for future climate.

This repository was produced by a team from University of Ljubljana, Biotechnical Faculty, Department of Agronomy, and the Agricultural Institute of Slovenia. For the list of authors, see the [Zenodo repository](https://doi.org/10.5281/zenodo.21829886).

## License

Data and figures created by the code in this repository are licensed under [CC BY 4.0 International](https://creativecommons.org/licenses/by/4.0/). For licensing of the input data used, see below.

Code in this repository is licensed under the [MIT license](https://opensource.org/license/mit).

For a citation see the [Zenodo repository](https://doi.org/10.5281/zenodo.21829886).

## Reproducing results

Install `Python 3.14` or newer.

This project uses [uv](https://docs.astral.sh/uv/) to manage package dependencies. Install `uv` and then install required packages by syncing the environment with the lockfile:  
```bash
uv sync
```

To run the Aquacrop executable, we use the `py-aquacrop` python package. It should be installed through pypi by the command above. 
If not, we also include a copy of the `py-aquacrop` repository in the Zenodo copy of this repository (available under the MIT license).
`py-aquacrop` should automatically download the required Aquacrop executable when run. We use Aquacrop version 7.1.

To reproduce the figures and data:
1. Run Prepare CO2 Concentrations notebook.
2. Run Prepare Weather Letalisce Ljubljana notebook.
3. Run Prepare Weather Murska Sobota notebook.
4. Run Prepare Yield Data notebook.
5. Run Prepare Soil Properties Estimation to obtain Ksat and theta_sat values and copy them to their respective parameter_defaults files.
6. Run CMA-ES KFold Biomass for first round of calibration and copy the best parameters to the parameter_defaults files.
7. Run CMA-ES KFold Grain for second round of calibration and copy the best parameters to the parameter_defaults files.
8. Copy the resulting parameter values to respective parameters_projections_ files. 
9. Run Projections Jablje notebook.
10. Run Projections Rakican notebook.

## Final results

Final calibrated parameters used for making projections can be found in the `aquacrop_slovenia` folder, in files `parameter_projections_jablje.py` and `parameter_projections_rakican.py`.
Parameter files suitable for use in the Aquacrop GUI can be found in the `results` folder.

Yield projection figures can be found in the Projections Jablje notebook and Projections Rakican notebook. Yield projections timeseries from running Aquacrop with climate projections and summary statistics can be found in the `results` folder.

## Project Organization

```
├── data
│   ├── external       <- Data from third party sources.
│   │   ├── aquacrop-defaults <- Default AquaCrop crop/soil/management files (Maize.CRO, SiltLoam.SOL, ...).
│   │   ├── climate           <- Gridded ARSO climate model output (not included, see Data sources).
│   │   ├── co2               <- Historical and RCP CO2 concentration series.
│   │   ├── mapdata           <- DEM, national border, and hydrography source data.
│   │   ├── soil              <- Measured soil characteristics.
│   │   ├── weather           <- Raw ARSO station weather workbooks.
│   │   └── yield             <- Raw yield measurements.
│   ├── interim        <- Intermediate data that has been transformed (climate point data extracted from netcdf files).
│   ├── processed      <- The final pickled data sets (climate, co2, weather, yield).
│   └── raw            <- CSVs exported from weather and yield files in the external folder.
│
├── notebooks          <- Jupyter notebooks, grouped by stage:
│   ├── data_preparation      <- Extract climate/weather CSVs, prepare CO2 and yield data.
│   ├── parameter_estimations <- Soil property and GDD estimation.
│   ├── calibration            <- CMA-ES K-fold calibration (biomass and grain).
│   ├── exploration            <- Optimization experiments, sensitivity analysis, daily simulations.
│   └── climate_projections    <- Run and analyze yield projections to 2100.
│
├── pyproject.toml     <- Project configuration file with package metadata for
│                         project_name and configuration for tools like ruff
│
├── reports            <- Generated analysis (maps, notebooks).
│   └── figures        <- Generated graphics and figures
│
├── results            <- Calibration, optimization, and projection outputs (pickled).
│   └── figures        <- Diagnostic plots generated from results
│
├── uv.lock            <- Package lock file for reproducing the analysis environment,
│                         generated with `uv lock`
│
└── aquacrop_slovenia  <- Source code for use in this project.
    ├── config.py                          <- Path constants (ROOT_DIR, DATA_DIR, RESULTS_DIR, ...)
    ├── climate_data.py                    <- Parse NetCDF files, extract CSVs, convert to processed pickles
    ├── yield_projections.py               <- Run yield projections and compute period statistics
    ├── reading_data.py                    <- Load station weather, climate, CO2, and observed yield data
    ├── diagnostics.py                     <- GDD computation and NSE/KGE/mKGE metrics
    ├── plots.py                           <- Code to create visualizations
    ├── parameters_running_jablje.py       <- Parameters for Jablje used when running the model and as defaults in calibration
    ├── parameters_running_rakican.py      <- Parameters for Rakičan used when running the model and as defaults in calibration
    ├── parameters_projections_jablje.py   <- Parameters used for Jablje climate projections
    └── parameters_projections_rakican.py  <- Parameters used for Rakičan climate projections
```

## Data sources

### CO2 data

Historical CO2 data was downloaded from the Scripps Institution of Oceanography (SIO) [CO2 data](https://scrippsco2.ucsd.edu/data/atmospheric-co2-data/averaged-products/). We used the MLO and SPO yearly averages. Data is licensed under [CC BY 4.0 International](http://creativecommons.org/licenses/by/4.0/).

RCP CO2 concentrations were downloaded from the [RCP database](https://tntcat.iiasa.ac.at/RcpDb/dsd?Action=htmlpage&page=download). We used the CMIP5 recommended data.

### Meteorological data

Meteorological data for the historical period was provided by the Slovenian Environmental Agency (ARSO). It can be reused, but must be acknowledged with `Source: Slovenian Environment Agency or Source: ARSO`. We used measurements from the following stations:

| Field name | Field latitude | Field longitude | Field altitude [m] | Meteorological station             | ARSO station ID | Latitude | Longitude | Altitude [m] |
|------------|----------------|-----------------|--------------------|------------------------------------|-----------------|----------|-----------|--------------|
| Jablje     | 46.144         | 14.557          | 303                | Letališče Jožeta Pučnika Ljubljana | 8               | 46.2114  | 14.4784   | 362          |
| Rakičan    | 46.654         | 16.190          | 183                | Murska Sobota                      | 355             | 46.6521  | 16.1913   | 189          |

Measured data for Tmin, Tmax, and precipitation are homogenized, while ET0 is not homogenized.
The weather data files are named according to the ARSO station ID.

![map_stations_fields.png](/reports/figures/map_stations_fields.png)

### Climate data 

Gridded climate data was downloaded from the Slovenian open data portal [OPSI](https://podatki.gov.si/) (search for "Podnebne spremembe"). Climate analysis and projections were prepared by the Slovenian Environmental Agency (ARSO) and are available .
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

We use all combinations.

## Yield data

#TODO

## Soil properties

Soil properties in the `data/soil` folder were measured by the authors the Soil Physics Lab of University of Ljubljana, Biotechnical Faculty, Department of Agronomy. The data is available under [CC BY 4.0 International](http://creativecommons.org/licenses/by/4.0/) license.



## Map data

To produce the maps we used data from the Surveying and Mapping Authority of the Republic of Slovenia [GURS](https://ipi.eprostor.gov.si/jgp/data). We used the following datasets:
- National border record
- Digital elevation model (DEM25)
which are licensed under [CC BY 4.0 International](http://creativecommons.org/licenses/by/4.0/).

[Hydrography data](https://podatki.gov.si/dataset/hidrografija1) was downloaded from the Slovenian open data portal and is provided by the MNVP DRSV (Slovenian Water Agency) under [CC BY 4.0 International](http://creativecommons.org/licenses/by/4.0/).

## Additional information

For Jablje, year 2017 is excluded, because data for ET is missing for most of the vegetation period.

For Rakičan, years 1998 and 2023 are excluded because of missing yield data.