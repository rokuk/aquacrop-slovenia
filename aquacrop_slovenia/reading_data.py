import pandas as pd

from aquacrop_slovenia import config


def get_co2(scenario: str) -> pd.DataFrame:
    return pd.read_pickle(config.CO2_PROCESSED_DIR / f"{scenario}.pkl")


def get_co2_for_aquacrop(scenario: str) -> list[tuple[int, float]]:
    df = get_co2(scenario)
    return list(df.itertuples(index=False, name=None))


def get_climate(
    location: str, model: str, scenario: str
) -> tuple[list[tuple[float, float]], list[float], list[float]]:
    path = config.PROCESSED_CLIMATE_DIR / f"{location}_{model}_{scenario}.pkl"
    return pd.read_pickle(path)


def get_yield(location: str, management: str, fertilization: str) -> pd.DataFrame:
    df = pd.read_pickle(config.PROCESSED_DIR / "yield" / "maize.pkl")
    mask = (df["product"] == "grain") & (df["location"] == location) & (df["management"] == management) & (df["fertilization"] == fertilization)
    return df.loc[mask, ["year", "yield"]].reset_index(drop=True)


def get_yield_for_comparison(location: str, management: str, fertilization: str) -> pd.DataFrame:
    """Like get_yield, but excludes years that are not simulated by the model due to missing et or yield data."""
    df = get_yield(location, management, fertilization)
    exclude = {2017}
    if location == "rakican":
        exclude |= {1998, 2023}
    return df[~df["year"].isin(exclude)].reset_index(drop=True)
