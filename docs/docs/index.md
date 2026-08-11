# aquacrop-slovenia documentation

## Running notebooks

Install **Python** 3.x.

This project uses [`uv`](https://docs.astral.sh/uv/) to manage package dependencies. Install `uv` and then install required packages by syncing the environment with the lockfile:  
```bash
uv sync
```

## Reproducing results
1. Run Prepare CO2 Concentrations notebook.
2. Run Prepare Weather Letalisce Ljubljana notebook.
3. Run Prepare Weather Murska Sobota notebook.
4. Run Prepare Yield Data notebook.
5. Run Prepare Soil Properties Estimation to obtain Ksat and theta_sat values and copy them to their respective parameter_defaults files.
6. Run CMA-ES KFold Biomass for first round of calibration and copy the best parameters to the parameter_defaults files.
7. Run CMA-ES KFold Grain for second round of calibration and copy the best parameters to the parameter_defaults files.
8. Copy the resulting parameter values to respective projections_parameters files.
9. Run the Projections notebooks.

## Final results

Final calibration parameters can be found in the `models` folder.