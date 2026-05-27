# Parameters

The file crop_maize_defaults contains the default values for the parameters. Most parameters are as given in Aquacrop's MaizeGDD.CRO file, adjusted parameters are listed in the table below.

## Set parameters

These parameters were changed from the default Aquacrop file Maize.GDD and are assumed to be valid.

| Type       | Parameter         | Value | Notes             |
|------------|-------------------|-------|-------------------|
| Crop-Maize | base_temp         | 10    | not 8 degrees!    |
| Crop-Maize | upper_temp        | 30    |                   |
| Crop-Maize | plant_density     | 80000 | Aleš: 75000-85000 |
| Crop-Maize | runoff_adjustment | 10    | Vir:              |

V diplomi Vučko K. UL BF agro 2009 so podatki o tleh:
FC do 135 cm 21.7 V%, PWP do 135 cm 9.3 V% za Rakičan
FC do 140 cm 36.3 V%, PWP do 140 cm 14.1 V% za Jablje

TODO! preveri GDD crop cyle length v literaturi za naš tip

For soil parameters we use the default values from Aquacrop's SlitLoam file. Na KIS pravijo, da je v Jabljah slit loam.

For field management we use the default Aquacrop values without mulches, no effect on runoff and perfect weed management.
TODO! in reality there is some weed management - check if suitably modeled

## Notes

Defaults value for max_canopy_cover is 0.96, na KIS pravijo cca 0.9 (0.8-0.95)!

Check what is the dry matter content of biomass, adjust parameter!

Is groundwater relevant for Rakican?