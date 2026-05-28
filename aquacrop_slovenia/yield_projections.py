from datetime import date

import pandas as pd
from aquacrop import Weather, Crop, Soil, AquaCrop, InitialConditions

from aquacrop_slovenia import config
from aquacrop_slovenia.intial_conditions_defaults import intial_cond_params
from aquacrop_slovenia.parameter_defaults_jablje import (
    jablje_soil_layers,
    jablje_maize_params,
    jablje_curve_number,
    jablje_readily_evaporable_water,
    optimal_management,
)
from aquacrop_slovenia.reading_data import get_co2_for_aquacrop, get_climate
from aquacrop_slovenia.parameter_defaults_rakican import (
    rakican_soil_layers,
    rakican_curve_number,
    rakican_readily_evaporable_water,
    rakican_maize_params,
)


def setup_model(working_dir, location, model, scenario, crop, soil):
    if model == "model4":
        end_year = 2099
    else:
        end_year = 2100

    simulation_periods = [
        {
            "start_date": date(year, 1, 1),
            "end_date": date(year, 10, 10),  # TODO temporary
            "planting_date": date(year, 4, 20),  # TODO temporary
            "is_seeding_year": True,
        }
        for year in range(1981, end_year + 1)
    ]

    temperatures, eto, precip = get_climate(location, model, scenario)

    co2_concentrations = get_co2_for_aquacrop(scenario)

    weather = Weather(
        location=location,
        temperatures=temperatures,
        eto_values=eto,
        rainfall_values=precip,
        record_type=1,
        first_day=1,
        first_month=1,
        first_year=1981,
        co2_records=co2_concentrations,
    )

    default_initial_conditions = InitialConditions(
        name="DefaultInitialConditions",
        description="Default initial conditions with AquaCrop calculated defaults",
        params=intial_cond_params,
    )

    simulation = AquaCrop(
        simulation_periods=simulation_periods,
        crop=crop,
        soil=soil,
        management=optimal_management,
        initial_conditions=default_initial_conditions,
        climate=weather,
        working_dir=working_dir,
        need_daily_output=False,
        need_seasonal_output=True,
        need_harvest_output=False,
        need_evaluation_output=False,
    )

    return simulation


def run_model_projection(location, model, scenario):
    if location == "rakican":
        crop = Crop(
            name="Rakican Maize",
            description="Rakican maize uncalibrated",
            params=rakican_maize_params,
        )
        soil = Soil(
            name="Rakican Soil",
            description="Rakican silt loam soil uncalibrated",
            soil_layers=rakican_soil_layers,
            curve_number=rakican_curve_number,
            readily_evaporable_water=rakican_readily_evaporable_water,
        )
    elif location == "jablje":
        crop = Crop(
            name="Jablje Maize",
            description="Jablje maize uncalibrated",
            params=jablje_maize_params,
        )
        soil = Soil(
            name="Jablje Soil",
            description="Jablje silt loam soil uncalibrated",
            soil_layers=jablje_soil_layers,
            curve_number=jablje_curve_number,
            readily_evaporable_water=jablje_readily_evaporable_water,
        )
    else:
        print("incorrect location")
        raise Exception

    simulation = setup_model(config.MODELS_DIR / "testing3", location, model, scenario, crop, soil)
    results = simulation.run()
    return results["season"][["Year1", "Y(dry)"]]


def get_model_scenario_combinations(location: str) -> list[tuple[str, str]]:
    """Return (model, scenario) pairs for which a climate CSV exists for the given location."""
    pattern = f"{location}_model*_rcp*.csv"
    combinations = []
    for path in sorted(config.INTERIM_CLIMATE_DIR.glob(pattern)):
        parts = path.stem.split("_")  # filename: {location}_{model}_{scenario}
        model = parts[1]
        scenario = parts[2]
        combinations.append((model, scenario))
    return combinations


def run_all_projections(location):
    projections = {}
    for model, scenario in get_model_scenario_combinations(location):
        print(f"Running projection for {location} with {model} and {scenario}")
        projections[(model, scenario)] = run_model_projection(location, model, scenario)
    return projections


PERIODS: dict[str, tuple[int, int]] = {
    "1981-2010": (1981, 2010),
    "2011-2040": (2011, 2040),
    "2041-2070": (2041, 2070),
    "2071-2100": (2071, 2100),
}


def compute_period_statistics(result: pd.DataFrame) -> pd.DataFrame:
    """Compute summary statistics for each standard 30-year period.

    Parameters
    ----------
    result:
        DataFrame with columns "Year1" and "Y(dry)" as returned by run_model_projection.

    Returns
    -------
    DataFrame indexed by period label with columns Mean, Std, Min, Median, Max.
    """
    rows = []
    for label, (start, end) in PERIODS.items():
        s = result.loc[(result["Year1"] >= start) & (result["Year1"] <= end), "Y(dry)"]
        rows.append(
            {
                "Period": label,
                "Mean": s.mean(),
                "Std": s.std(),
                "Min": s.min(),
                "Median": s.median(),
                "Max": s.max(),
            }
        )
    return pd.DataFrame(rows).set_index("Period")
