Data sources
===============

## CO2 data

Historical CO2 data was downloaded from the Scripps Institution of Oceanography (SIO) [CO2 data](https://scrippsco2.ucsd.edu/data/atmospheric-co2-data/averaged-products/). We used the MLO and SPO yearly averages.

RCP CO2 concentrations were downloaded from the [RCP database](https://tntcat.iiasa.ac.at/RcpDb/dsd?Action=htmlpage&page=download). We used the CMIP5 recommended data.

## Meteorological data

Meteorological data for the historical period was provided by the Slovenian Environmental Agency (ARSO). It was measured at the following stations:

| Field name | Field latitude | Field longitude | Field altitude [m] | Meteorological station             | ARSO station ID | Latitude | Longitude | Altitude [m] |
|------------|----------------|----------------|--------------------|------------------------------------|-----------------|----------|-----------|--------------|
| Jablje     | 46.144         | 14.557         | 303                | Letališče Jožeta Pučnika Ljubljana | 8               | 46.2114  | 14.4784   | 362          |
| Rakičan    | 46.654         | 16.190         | 183                | Murska Sobota                      | 355             | 46.6521  | 16.1913   | 189          |

Measured data for Tmin, Tmax, and precipitation are homogenized, while ET0 is not homogenized.
The weather data files are named according to the ARSO station ID.

![map_stations_fields.png](../../reports/figures/map_stations_fields.png)

## Climate data 

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

Hydrography data was downloaded from the Slovenian open data portal and is provided by the Slovenian Water Agency. [Hydrography dataset](https://podatki.gov.si/dataset/hidrografija1)
