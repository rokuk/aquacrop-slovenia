import pandas as pd

from aquacrop_slovenia import config


def load_station_weather(
    station_id: int,
) -> tuple[list[tuple[float, float]], list[float], list[float]]:
    """Load processed weather data for a station and return arrays for the Weather class.

    Returns:
        temperatures: list of (tmin, tmax) tuples in °C
        eto_values: list of reference evapotranspiration values in mm/day
        rainfall_values: list of precipitation values in mm
    """
    df: pd.DataFrame = pd.read_pickle(
        config.PROCESSED_WEATHER_DIR / f"station_{station_id}.pkl"
    )
    temperatures = list(zip(df["tmin"], df["tmax"]))
    eto_values = df["etp"].tolist()
    rainfall_values = df["pad"].tolist()
    return temperatures, eto_values, rainfall_values