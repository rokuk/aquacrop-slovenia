# Parameters

The file crop_maize_defaults contains the default values for the parameters. Most parameters are as given in Aquacrop's MaizeGDD.CRO file, adjusted parameters are listed in the table below.

## Set parameters

These parameters were set and are assumed to be valid.

| Type       | Parameter     | Value | Notes             |
|------------|---------------|-------|-------------------|
| Crop-Maize | base_temp     | 10    |                   |
| Crop-Maize | upper_temp    | 30    |                   |
| Crop-Maize | plant_density | 80000 | Aleš: 75000-85000 |

TODO!!!!!!!!!!! preveri GDD crop cyle length v literaturi za naš tip

For soil parameters we use the default values from Aquacrop's SlitLoam file. Na KIS pravijo, da je v Jabljah slit loam.

For field management we use the default Aquacrop values without mulches, no effect on runoff and perfect weed management.
TODO!!!!!!!!!!! in reality there is some weed management - check if suitabliy modeled

## Notes

Defaults value for max_canopy_cover is 0.96, na KIS pravijo cca 0.9 (0.8-0.95)!!!