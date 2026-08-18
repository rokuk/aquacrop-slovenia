import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import pandas as pd
from aquacrop import Weather, Crop, Soil, AquaCrop

from aquacrop_slovenia import config
from aquacrop_slovenia.parameters_projections_jablje import (
    jablje_soil_layers,
    jablje_maize_params,
    jablje_curve_number,
    jablje_readily_evaporable_water,
    jablje_optimal_management,
    jablje_initial_cond,
    jablje_groundwater
)
from aquacrop_slovenia.reading_data import get_co2_for_aquacrop, get_climate
from aquacrop_slovenia.parameters_projections_rakican import (
    rakican_soil_layers,
    rakican_curve_number,
    rakican_readily_evaporable_water,
    rakican_maize_params,
    rakican_initial_cond,
    rakican_optimal_management,
    rakican_groundwater
)


def setup_model_for_projections(working_dir, location, model, scenario, crop, soil):
    if model == "model4":
        end_year = 2099
    else:
        end_year = 2100

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

    if location == "jablje":
        initial_conditions = jablje_initial_cond
        management = jablje_optimal_management
        simulation_periods = [
            {
                "start_date": date(year, 1, 1),
                "end_date": date(year, 12, 31),
                "planting_date": date(year, 5, 3),
                "is_seeding_year": True,
            }
            for year in range(1981, end_year + 1)
        ]
    elif location == "rakican":
        initial_conditions = rakican_initial_cond
        management = rakican_optimal_management
        simulation_periods = [
            {
                "start_date": date(year, 1, 1),
                "end_date": date(year, 12, 31),
                "planting_date": date(year, 4, 20),
                "is_seeding_year": True,
            }
            for year in range(1981, end_year + 1)
        ]
    else:
        print("incorrect location")
        raise Exception


    simulation = AquaCrop(
        simulation_periods=simulation_periods,
        crop=crop,
        soil=soil,
        management=management,
        initial_conditions=initial_conditions,
        #ground_water=jablje_groundwater
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
            description="Rakican maize projections",
            params=rakican_maize_params,
        )
        soil = Soil(
            name="Rakican Soil",
            description="Rakican silt loam soil projections",
            soil_layers=rakican_soil_layers,
            curve_number=rakican_curve_number,
            readily_evaporable_water=rakican_readily_evaporable_water,
        )
    elif location == "jablje":
        crop = Crop(
            name="Jablje Maize",
            description="Jablje maize projections",
            params=jablje_maize_params,
        )
        soil = Soil(
            name="Jablje Soil",
            description="Jablje silt loam soil projections",
            soil_layers=jablje_soil_layers,
            curve_number=jablje_curve_number,
            readily_evaporable_water=jablje_readily_evaporable_water,
        )
    else:
        print("incorrect location")
        raise Exception

    working_dir = config.MODEL_RUNNING_DIR / f"proj_{location}_{model}_{scenario}"
    try:
        simulation = setup_model_for_projections(working_dir, location, model, scenario, crop, soil)
        results = simulation.run()
    finally:
        shutil.rmtree(working_dir, ignore_errors=True)
    return results["season"][["Year1", "Y(dry)"]]


def run_historical_simulation(location: str) -> pd.DataFrame:
    """Run AquaCrop for the calibration period using station weather data.

    Returns the season DataFrame with columns Year1, Y(dry), and the yearly stress
    indicators TempStr, ExpStr and StoStr (% of the season, 0 = no stress).
    """
    if location == "jablje":
        from aquacrop_slovenia.reading_data import get_station_weather
        temperatures, eto, precip = get_station_weather(8)
        first_year = 1993
        exclude = {2017}
        crop = Crop(name="Jablje Maize", description="", params=jablje_maize_params)
        soil = Soil(
            name="Jablje Soil",
            description="",
            soil_layers=jablje_soil_layers,
            curve_number=jablje_curve_number,
            readily_evaporable_water=jablje_readily_evaporable_water,
        )
        simulation_periods = [
            {
                "start_date": date(year, 1, 1),
                "end_date": date(year, 12, 31),
                "planting_date": date(year, 5, 3),
                "is_seeding_year": True,
            }
            for year in range(1993, 2024)
            if year not in exclude
        ]
        management = jablje_optimal_management
        initial_conditions = jablje_initial_cond
    elif location == "rakican":
        from aquacrop_slovenia.reading_data import get_station_weather
        temperatures, eto, precip = get_station_weather(355)
        first_year = 1993
        exclude = {1998, 2023, 2017}
        crop = Crop(name="Rakican Maize", description="", params=rakican_maize_params)
        soil = Soil(
            name="Rakican Soil",
            description="",
            soil_layers=rakican_soil_layers,
            curve_number=rakican_curve_number,
            readily_evaporable_water=rakican_readily_evaporable_water,
        )
        simulation_periods = [
            {
                "start_date": date(year, 1, 1),
                "end_date": date(year, 12, 31),
                "planting_date": date(year, 4, 20),
                "is_seeding_year": True,
            }
            for year in range(1993, 2024)
            if year not in exclude
        ]
        management = rakican_optimal_management
        initial_conditions = rakican_initial_cond
    else:
        raise ValueError(f"Unknown location: {location}")

    co2 = get_co2_for_aquacrop("historical")
    weather = Weather(
        location=location,
        temperatures=temperatures,
        eto_values=eto,
        rainfall_values=precip,
        record_type=1,
        first_day=1,
        first_month=1,
        first_year=first_year,
        co2_records=co2,
    )
    working_dir = config.MODEL_RUNNING_DIR / f"hist_{location}"
    try:
        sim = AquaCrop(
            simulation_periods=simulation_periods,
            crop=crop,
            soil=soil,
            management=management,
            initial_conditions=initial_conditions,
            climate=weather,
            working_dir=working_dir,
            need_daily_output=False,
            need_seasonal_output=True,
            need_harvest_output=False,
            need_evaluation_output=False,
        )
        results = sim.run()
    finally:
        shutil.rmtree(working_dir, ignore_errors=True)
    return results["season"][["Year1", "Y(dry)", "TempStr", "ExpStr", "StoStr"]]


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


def run_all_projections(location, max_workers=None):
    combinations = get_model_scenario_combinations(location)
    projections = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_model_projection, location, model, scenario): (model, scenario)
            for model, scenario in combinations
        }
        for future in as_completed(futures):
            model, scenario = futures[future]
            print(f"Completed {location} {model} {scenario}")
            projections[(model, scenario)] = future.result()

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
