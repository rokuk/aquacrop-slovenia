import pandas as pd

from aquacrop_slovenia import config

def get_yield(location: str, management: str, fertilization: str) -> pd.DataFrame:
    df = pd.read_pickle(config.PROCESSED_DIR / "yield" / "maize.pkl")
    mask = (df["product"] == "grain") & (df["location"] == location) & (df["management"] == management) & (df["fertilization"] == fertilization)
    return df.loc[mask, ["year", "yield"]].reset_index(drop=True)


def get_yield_for_comparison(location: str, management: str, fertilization: str) -> pd.DataFrame:
    """Like get_yield, but excludes years that fall outside the model simulation period."""
    df = get_yield(location, management, fertilization)
    exclude = {2017}
    if location == "rakican":
        exclude |= {1998, 2023}
    return df[~df["year"].isin(exclude)].reset_index(drop=True)
