import pandas as pd
import numpy as np
from scipy.stats import pearsonr

from aquacrop_slovenia import config


def calculate_growing_degree_days(temp_max, temp_min, Tbase, Tupp):
    temp_max = min(temp_max, Tupp)
    temp_max = max(temp_max, Tbase)

    temp_min = min(temp_min, Tupp)
    Tmean = (temp_max + temp_min) / 2
    Tmean = max(Tmean, Tbase)
    gdd = Tmean - Tbase
    return gdd


def compute_annual_gdd(station_id: int, base_temp: float, upper_temp: float) -> pd.Series:
    df = pd.read_pickle(config.PROCESSED_WEATHER_DIR / f"station_{station_id}.pkl")
    return (
        df.assign(
            gdd=df.apply(
                lambda r: calculate_growing_degree_days(
                    r["tmax"], r["tmin"], base_temp, upper_temp
                ),
                axis=1,
            )
        )
        .groupby(df["datum"].dt.year)["gdd"]
        .sum()
        .rename_axis("year")
        .rename("gdd")
    )


# Nash-Sutcliff efficiency
def nse(predictions, targets):
    return 1 - (np.sum((targets - predictions) ** 2) / np.sum((targets - np.mean(targets)) ** 2))

# Kling-Gupta efficiency
def kge(predictions, targets):
    r = pearsonr(predictions, targets)[0]
    alpha = np.std(predictions) / np.std(targets)
    beta = np.mean(predictions) / np.mean(targets)
    return 1 - np.sqrt((r-1)**2 + (alpha-1)**2 + (beta-1)**2)

# Modified Kling-Gupta efficiency (Kling et al., 2012)
def mkge(predictions, targets):
    r = pearsonr(predictions, targets)[0]
    beta = np.mean(predictions) / np.mean(targets)
    alpha = (np.std(predictions) / np.std(targets)) / beta
    return 1 - np.sqrt((r-1)**2 + (alpha-1)**2 + (beta-1)**2)