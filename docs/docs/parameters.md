# Parameters

The file crop_maize_defaults contains the default values for the parameters. Most parameters are as given in Aquacrop's MaizeGDD.CRO file, adjusted parameters are listed in the table below.

## Set parameters

These parameters were changed from the default Aquacrop file Maize.GDD and are assumed to be valid.

| Type               | Parameter          | Value | Notes                                                                               |
|--------------------|--------------------|-------|-------------------------------------------------------------------------------------|
| Crop-Maize         | base_temp          | 10    |                                                                                     |
| Crop-Maize         | upper_temp         | 30    |                                                                                     |
| Crop-Maize         | plant_density      | 85900 | Aleš: 85900 (75000-85000)                                                           |
| Crop-Maize         | runoff_adjustment  | 10    |                                                                                     |
| Crop-Maize         | max_canopy_cover   | 90    | Aleš: 90 (80-95) %                                                                  |
| Crop-Maize-Rakican | dry_matter_content | 83    | Calculated as average based on KIS measurements (tables for FAO 300 Rakičan 2024)   |
| Crop-Maize-Rakican | harvest_index      | 0.51  | Calculated average over median of biomass and yield over years for Rakican A,B,C-N3 |
| Crop-Maize-Jablje  | dry_matter_content | 76    | Calculated as average based on KIS measurements (tables for FAO 300 Jablje 2024)    |
| Crop-Maize-Jablje  | harvest_index      | 0.51  | Calculated average over median of biomass and yield over years for Jablje A,B,C-N3  |

Growing degree days (GDD) are calculated using the default calendar days at each location. GDDs between phenological phases are averaged over the years. Those averages are used as Aquacrop parameters.

## Soil parameters
Source: Deset let trajnih poskusov IOSDV v Sloveniji, Jablje in Rakičan 1993-2003: zbornik posveta, Žalec 12. december 2003, ISBN 961-90884-2-5

We use clay, silt, sand and bulk density to estimate Ksat and theta_s using Rosetta model 3 https://doi.org/10.1016/j.jhydrol.2017.01.004.

#### Jablje

|               | Size Range (µm) |            | 
|---------------|-----------------|------------|
| Clay          | < 2.0           | 16.77 %    |
| Silt (fine)   | 6.3–2.0         | 13.43 %    |
| Silt (medium) | 20–6.3          | 17.47 %    |
| Silt (coarse) | 63–20           | 24.63 %    |
| Sand (fine)   | 200–63          | 23.22 %    |
| Sand (medium) | 630–200         | 3.98 %     |
| Sand (coarse) | 2000–630        | 0.51 %     |
| Bulk density  | —               | 1.55 g/cm³ |

### Rakičan

|               | Size Range (µm) |            | 
|---------------|-----------------|------------|
| Clay          | < 2.0           | 14.67 %    |
| Silt (fine)   | 6.3–2.0         | 5.68 %     |
| Silt (medium) | 20–6.3          | 7.80 %     |
| Silt (coarse) | 63–20           | 17.72 %    |
| Sand (fine)   | 200–63          | 38.11 %    |
| Sand (medium) | 630–200         | 15.31 %    |
| Sand (coarse) | 2000–630        | 0.62 %     |
| Bulk density  | —               | 1.61 g/cm³ |



### Other sources

V diplomi Vučko K. UL BF agro 2009 so podatki o tleh:
FC do 135 cm 21.7 V%, PWP do 135 cm 9.3 V% za Rakičan
FC do 140 cm 36.3 V%, PWP do 140 cm 14.1 V% za Jablje

JABLJE (Vir: Urša, izmerjeno 2007, lastnosti tal na lokaciji poskusa v Jablah, njiva krompirja)
| Horizont   | Globina (cm)      | Glina (%) | Grobi melj (%)    | Fini melj (%) | Pesek (%) | Poroznost (%) | PK (%) | TV (%) |
|------------|-------------------|-----------|-------------------|---------------|-----------|---------------|--------|--------|
| Ap         | 0 - 30            | 22.0      | 16.4              | 25            | 36.6      | 29.18         | 36.5   | 25.2   |
| A2         | 30 - 65           | 24.4      | 15.4              | 24.6          | 35.6      | 25.57         |        |        |
| AB         | 65 - 91           | 23.2      | 16.0              | 21.0          | 39.8      | 24.29         |        |        |
| Gr         | 91 -              | 22.7      | 13.1              | 17.1          | 47.1      | 25.39         |        |        |

JABLJE (Vir: Deset let trajnih poskusov IOSDV v Sloveniji, Jablje in Rakičan 1993-2003: zbornik posveta, Žalec 12. december 2003, ISBN 961-90884-2-5)
Poljska kapaciteta za vodo (FK) do 140 cm 36.3 V%
Točka permenentnega venenja (PWP) do 140 cm 14.1 V%

RAKIČAN (Vir: Deset let trajnih poskusov IOSDV v Sloveniji, Jablje in Rakičan 1993-2003: zbornik posveta, Žalec 12. december 2003, ISBN 961-90884-2-5)
Poljska kapaciteta za vodo (FK) do 135 cm 21.7 V%
Točka permenentnega venenja (PWP) do 135 cm 9.3 V%
Opis pedološke jame do globine 135 cm
Ap, 0-22 cm, temnorjav ilovnat pesek, FK 33.8 %V (70 mm)
Al, 22-37 cm, svetlo rjavi meljasti pesek pod ornico, FK 30.3 %V (45 mm)
Bt, 37-62 cm, intenzivno rjave do rdečerjave barve, meljasta ilovica, FK 30.5 %V (76 mm)
Bv, 62-89 cm, intenzivno rjav ilovnat melj, FK 32.7 %V (88 mm)
Cv, 89-135 cm+, pretežno prodnat skelet, FK 4 %V (20 mm)

## Groundwater
(Vir: Deset let trajnih poskusov IOSDV v Sloveniji, Jablje in Rakičan 1993-2003: zbornik posveta, Žalec 12. december 2003, ISBN 961-90884-2-5)
JABLJE
Gladina podtalnice je na globini 2.5 - 3 m. Ob dolgotrajnejšem deževju se glaina podtalnice zaradi premajhne odtočne sposobnosti vodnih kanalov in slabe pronicnosti tal za krajši čas (1-2 dneva) dvigne do površja tal.

RAKIČAN
Odvisno od letnega časa leži raven podtalnice 2 - 3 m pod površino tal.


## Other parameters

TODO! preveri GDD crop cyle length v literaturi za naš tip

For soil parameters we use the default values from Aquacrop's SlitLoam file. Na KIS pravijo, da je v Jabljah slit loam.

For field management we use the default Aquacrop values without mulches, no effect on runoff and perfect weed management.

## Initial conditions

The soil water content initial conditions are set to field capacity.

## Notes

Default value for max_canopy_cover is 0.96, na KIS pravijo cca 0.9 (0.8-0.95)!

Check what is the dry matter content of biomass, adjust parameter!

Is groundwater relevant for Rakican?