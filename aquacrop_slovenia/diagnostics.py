import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import root_mean_squared_error, r2_score

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
    r = kge_r(predictions, targets)
    alpha = kge_alpha(predictions, targets)
    beta = kge_beta(predictions, targets)
    return 1 - np.sqrt((r-1)**2 + (alpha-1)**2 + (beta-1)**2)

# Modified Kling-Gupta efficiency (Kling et al., 2012)
def mkge(predictions, targets):
    r = kge_r(predictions, targets)
    beta = kge_beta(predictions, targets)
    alpha = mkge_alpha(predictions, targets)
    return 1 - np.sqrt((r-1)**2 + (alpha-1)**2 + (beta-1)**2)


def kge_r(predictions, targets):
    return pearsonr(predictions, targets)[0]


def kge_beta(predictions, targets):
    return np.mean(predictions) / np.mean(targets)


def kge_alpha(predictions, targets):
    return np.std(predictions) / np.std(targets)


def mkge_alpha(predictions, targets):
    return (np.std(predictions) / np.std(targets)) / kge_beta(predictions, targets)


def willmott_d(predictions, targets):
    obs_mean = np.mean(targets)
    numerator = np.sum((targets - predictions) ** 2)
    denominator = np.sum((np.abs(predictions - obs_mean) + np.abs(targets - obs_mean)) ** 2)
    return 1 - numerator / denominator


# Willmott's refined index of agreement (Willmott et al., 2012)
def willmott_dr(predictions, targets):
    obs_mean = np.mean(targets)
    abs_errors = np.sum(np.abs(predictions - targets))
    potential = 2 * np.sum(np.abs(targets - obs_mean))
    if abs_errors <= potential:
        return 1 - abs_errors / potential
    else:
        return potential / abs_errors - 1


def print_metrics(seasonal, observed_df, modeled_col, label):
    merged = observed_df.merge(
        seasonal[["Year1", modeled_col]].rename(columns={"Year1": "year", modeled_col: "modeled"}),
        on="year",
    )
    y_obs = merged["yield"].values
    y_mod = merged["modeled"].values
    print(f"=== {label} ===")
    print(f"  RMSE:       {root_mean_squared_error(y_obs, y_mod):.4f}")
    print(f"  R2:         {r2_score(y_obs, y_mod):.4f}")
    print(f"  NSE:        {nse(y_mod, y_obs):.4f}")
    print(f"  KGE:        {kge(y_mod, y_obs):.4f}")
    print(f"  mKGE:       {mkge(y_mod, y_obs):.4f}")
    print(f"  KGE_r:      {kge_r(y_mod, y_obs):.4f}")
    print(f"  KGE_beta:   {kge_beta(y_mod, y_obs):.4f}")
    print(f"  KGE_alpha:  {kge_alpha(y_mod, y_obs):.4f}")
    print(f"  mKGE_alpha: {mkge_alpha(y_mod, y_obs):.4f}")
    print(f"  Willmott d: {willmott_d(y_mod, y_obs):.4f}")
    print(f"  Willmott dr:{willmott_dr(y_mod, y_obs):.4f}")