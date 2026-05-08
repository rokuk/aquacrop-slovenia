"""AquaCrop-OSPy calibration for Slovenian maize fields."""

from __future__ import annotations

from typing import Any
import warnings

from aquacrop import CO2, AquaCropModel, Crop, InitialWaterContent, Soil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from aquacrop_slovenia import config

SOIL_TYPES: dict[str, str] = {
    "jablje": "SiltLoam",
    "rakican": "LoamySand",
}

CALIBRATION_PERIOD: tuple[int, int] = (1993, 2010)

PARAM_NAMES: tuple[str, ...] = ("HI0", "WP", "CGC", "CDC")

# [HI0, WP (g/m²), CGC (frac/GDD), CDC (frac/GDD)]
DEFAULT_BOUNDS: list[tuple[float, float]] = [
    (0.30, 0.55),
    (15.0, 40.0),
    (0.005, 0.025),
    (0.004, 0.020),
]

# Maturity GDD threshold representing a short-season Slovenian maize variety (FAO ~300).
# The seasonal GDD at Jablje ranges 1513–1913; setting 1400 ensures all calibration years
# can run without triggering AquaCrop's assertion that total GDD >= Maturity.
MAIZE_MATURITY_GDD: int = 1400

# MaizeGDD defaults — used as smoke-test reference
MAIZE_GDD_DEFAULTS: tuple[float, float, float, float] = (0.48, 33.7, 0.012494, 0.01)


def prepare_aquacrop_weather(df: pd.DataFrame) -> pd.DataFrame:
    """Convert raw climate CSV (K, kg m⁻² s⁻¹) to AquaCrop-OSPy format (°C, mm/day).

    Input DataFrame must have a DatetimeIndex named 'time' and columns:
    tasmin, tasmax, pr, evspsblpot.
    """
    out = pd.DataFrame(index=df.index)
    out["MinTemp"] = df["tasmin"] - 273.15
    out["MaxTemp"] = df["tasmax"] - 273.15
    out["Precipitation"] = df["pr"] * 86400.0
    # Clip ETo to ≥ 0.1 mm/day to avoid division-by-zero in the water balance
    out["ReferenceET"] = (df["evspsblpot"] * 86400.0).clip(lower=0.1)
    out = out.reset_index().rename(columns={"time": "Date"})
    return out[["MinTemp", "MaxTemp", "Precipitation", "ReferenceET", "Date"]]


def load_climate(location: str, model: str = "obs", scenario: str = "hist") -> pd.DataFrame:
    """Load interim climate CSV for *location* and return an AquaCrop-ready DataFrame."""
    path = config.INTERIM_CLIMATE_DIR / f"{location}_{model}_{scenario}.csv"
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return prepare_aquacrop_weather(df)


def load_co2(year: int) -> float:
    """Return annual mean CO2 concentration (ppm) for *year* from Scripps MLO/SPO data.

    Raises KeyError if no valid value exists for the requested year.
    """
    path = config.CO2_DIR / "mlo_spo_annual_mean.csv"
    raw = pd.read_csv(path, comment="%", header=None, names=["decimal_year", "ppm"])
    raw["year"] = raw["decimal_year"].apply(lambda x: int(float(x)))
    row = raw[raw["year"] == year]
    if row.empty or np.isnan(float(row["ppm"].iloc[0])):
        raise KeyError(f"No valid CO2 data for year {year}")
    return float(row["ppm"].iloc[0])


def run_single_season(
    year: int,
    params: tuple[float, float, float, float],
    location: str,
    weather: pd.DataFrame,
    planting_date: str = "05/01",
) -> float | None:
    """Run one maize growing season and return simulated grain yield (kg/ha).

    Returns None if the simulation cannot be constructed or fails to finish.

    Args:
        year: Calendar year for the season.
        params: (HI0, WP, CGC, CDC) parameter tuple.
        location: 'jablje' or 'rakican'.
        weather: AquaCrop-ready weather DataFrame (output of load_climate / prepare_aquacrop_weather).
        planting_date: Crop planting date as 'MM/DD'.
    """
    hi0, wp, cgc, cdc = params

    sim_start = f"{year}/04/01"
    sim_end = f"{year}/11/30"

    # Validate weather coverage before constructing the model
    w_dates = pd.to_datetime(weather["Date"])
    if w_dates.min() > pd.Timestamp(sim_start) or w_dates.max() < pd.Timestamp(sim_end):
        return None

    try:
        co2_ppm = load_co2(year)
    except KeyError:
        return None

    soil = Soil(SOIL_TYPES[location])
    crop = Crop(
        "MaizeGDD",
        planting_date=planting_date,
        HI0=hi0,
        WP=wp,
        CGC=cgc,
        CDC=cdc,
        Maturity=MAIZE_MATURITY_GDD,
    )
    init_wc = InitialWaterContent(value=["FC"])
    co2 = CO2(constant_conc=True, current_concentration=co2_ppm)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = AquaCropModel(
                sim_start_time=sim_start,
                sim_end_time=sim_end,
                weather_df=weather,
                soil=soil,
                crop=crop,
                initial_water_content=init_wc,
                co2_concentration=co2,
            )
            model.run_model(till_termination=True)
    except Exception:
        return None

    results = model.get_simulation_results()
    if results is False or not isinstance(results, pd.DataFrame) or results.empty:
        return None

    return float(results["Dry yield (tonne/ha)"].iloc[-1]) * 1000.0


def objective_function(
    params: np.ndarray,
    obs_yield: pd.Series,
    location: str,
    weather: pd.DataFrame,
    planting_date: str,
) -> float:
    """RMSE (kg/ha) between observed and simulated grain yield.

    Returns a large penalty (1e6) when fewer than 2 seasons produce valid output,
    so that differential_evolution steers away from degenerate parameter regions.
    """
    obs_vals, sim_vals = [], []
    for year, obs in obs_yield.items():
        sim = run_single_season(year, params, location, weather, planting_date)
        if sim is not None:
            obs_vals.append(obs)
            sim_vals.append(sim)

    if len(obs_vals) < 2:
        return 1e6

    return float(np.sqrt(np.mean((np.array(obs_vals) - np.array(sim_vals)) ** 2)))


def calibrate(
    location: str,
    treatment: str = "N3",
    planting_date: str = "05/01",
    bounds: list[tuple[float, float]] = DEFAULT_BOUNDS,
    **de_kwargs: Any,
) -> dict[str, Any]:
    """Calibrate MaizeGDD parameters (HI0, WP, CGC, CDC) against observed grain yield.

    Uses scipy.optimize.differential_evolution (global optimizer) with RMSE as the
    objective. Calibration period: 1993–2010 (N3 fertilization, averaged over A/B/C mgmt).

    Args:
        location: 'jablje' or 'rakican'.
        treatment: Fertilization level to calibrate against ('N3' recommended).
        planting_date: Maize planting date as 'MM/DD'.
        bounds: Parameter bounds [(HI0_lo, HI0_hi), (WP_lo, WP_hi), (CGC_lo, CGC_hi), (CDC_lo, CDC_hi)].
        **de_kwargs: Extra keyword arguments forwarded to differential_evolution (override defaults).

    Returns:
        dict with keys: location, treatment, planting_date, params, rmse,
        obs_yield, sim_yield, de_result, n_years, n_valid.
    """
    # Load and filter observed yield
    yield_path = config.INTERIM_YIELD_DIR / f"maize-{location}.csv"
    yield_df = pd.read_csv(yield_path)
    obs = (
        yield_df[(yield_df["fertilization"] == treatment) & (yield_df["product"] == "Zrnje")]
        .groupby("year")["yield_kg_ha"]
        .mean()
    )
    obs = obs[(obs.index >= CALIBRATION_PERIOD[0]) & (obs.index <= CALIBRATION_PERIOD[1])]
    obs.index = obs.index.astype(int)

    weather = load_climate(location)

    de_defaults: dict[str, Any] = {
        "seed": 42,
        "maxiter": 500,
        "popsize": 15,
        "tol": 1e-4,
        "polish": True,
    }
    de_defaults.update(de_kwargs)

    result = differential_evolution(
        objective_function,
        bounds,
        args=(obs, location, weather, planting_date),
        **de_defaults,
    )

    # Collect simulated yields at the best parameters
    sim_dict: dict[int, float] = {}
    for year in obs.index:
        sim = run_single_season(year, result.x, location, weather, planting_date)
        if sim is not None:
            sim_dict[year] = sim

    sim_series = pd.Series(sim_dict, name="sim_yield_kg_ha")

    return {
        "location": location,
        "treatment": treatment,
        "planting_date": planting_date,
        "params": dict(zip(PARAM_NAMES, result.x)),
        "rmse": result.fun,
        "obs_yield": obs,
        "sim_yield": sim_series,
        "de_result": result,
        "n_years": len(obs),
        "n_valid": len(sim_dict),
    }


def plot_calibration_results(calibration_result: dict[str, Any]) -> plt.Figure:
    """Two-panel figure: obs vs simulated scatter (left) and time series (right).

    Consistent with plots.py conventions: returns the Figure, no plt.show().
    """
    obs = calibration_result["obs_yield"]
    sim = calibration_result["sim_yield"]
    rmse = calibration_result["rmse"]
    location = calibration_result["location"]
    params = calibration_result["params"]

    common = obs.index.intersection(sim.index)
    obs_c = obs[common]
    sim_c = sim[common]

    fig, (ax_scatter, ax_ts) = plt.subplots(1, 2, figsize=(12, 5))

    # --- Scatter ---
    ax_scatter.scatter(obs_c, sim_c, color="steelblue", edgecolors="white", zorder=3)
    lim_min = min(obs_c.min(), sim_c.min()) * 0.9
    lim_max = max(obs_c.max(), sim_c.max()) * 1.1
    ax_scatter.plot([lim_min, lim_max], [lim_min, lim_max], "k--", lw=1, label="1:1")
    ax_scatter.set_xlim(lim_min, lim_max)
    ax_scatter.set_ylim(lim_min, lim_max)
    ax_scatter.set_xlabel("Observed yield (kg/ha)")
    ax_scatter.set_ylabel("Simulated yield (kg/ha)")
    ax_scatter.set_title("Observed vs Simulated")
    ax_scatter.legend()
    ax_scatter.text(
        0.05,
        0.95,
        f"RMSE = {rmse:.0f} kg/ha\nn = {len(common)}",
        transform=ax_scatter.transAxes,
        va="top",
        fontsize=9,
    )

    # --- Time series ---
    ax_ts.plot(obs.index, obs.values, "o-", label="Observed (N3 avg)", color="steelblue")
    ax_ts.plot(sim.index, sim.values, "s--", label="Simulated", color="coral")
    ax_ts.set_xlabel("Year")
    ax_ts.set_ylabel("Yield (kg/ha)")
    ax_ts.set_title("Yield time series")
    ax_ts.legend()

    param_str = "  ".join(f"{k}={v:.4f}" for k, v in params.items())
    fig.suptitle(f"{location.capitalize()} calibration — {param_str}", fontsize=10)
    fig.tight_layout()
    return fig
