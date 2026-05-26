from __future__ import annotations

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from loguru import logger
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from aquacrop_slovenia import config
from aquacrop_slovenia.climate_data import _lat_lon_arrays

# Lambert Conformal Conic centred on Slovenia — preserves shape well at this scale
_PROJECTION = ccrs.LambertConformal(
    central_longitude=15.0,
    central_latitude=46.0,
    standard_parallels=(44.0, 48.0),
)
_DATA_CRS = ccrs.PlateCarree()

_NE1_RASTER = config.DATA_DIR / "external" / "natural_earth" / "NE1_HR_LC_SR_W_DR.tif"


def get_grid_coords(climate_dir: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Open one NetCDF file and return (lat2d, lon2d, valid_mask).

    valid_mask is True where the first variable's first time step has finite data.
    """
    hist_dir = climate_dir / "hist"
    nc_files = sorted(hist_dir.glob("*.nc"))
    if not nc_files:
        raise FileNotFoundError(f"No .nc files found in {hist_dir}")
    ds = xr.open_dataset(nc_files[0], engine="netcdf4")
    lat2d, lon2d = _lat_lon_arrays(ds)
    data_var = next(iter(ds.data_vars))
    valid_mask = np.isfinite(ds[data_var].isel(time=0).values)
    ds.close()
    return lat2d, lon2d, valid_mask


def plot_grid_points(
    target_lat: float,
    target_lon: float,
    climate_dir: Path | None = None,
    figsize: tuple[float, float] = (10, 8),
) -> plt.Figure:
    """Plot all NetCDF grid points on a projected map, highlighting the nearest cell.

    Parameters
    ----------
    target_lat, target_lon:
        Geographic coordinates of the target point.
    climate_dir:
        Root of the climate NetCDF files. Defaults to config.CLIMATE_DIR.
    figsize:
        Figure size in inches.

    Returns
    -------
    plt.Figure
    """
    climate_dir = climate_dir or config.EXTERNAL_CLIMATE_DIR
    lat2d, lon2d, valid_mask = get_grid_coords(climate_dir)

    # Nearest valid cell only
    dist2 = (lat2d - target_lat) ** 2 + (lon2d - target_lon) ** 2
    dist2[~valid_mask] = np.inf
    ri, rj = np.unravel_index(int(np.argmin(dist2)), lat2d.shape)
    nearest_lat = float(lat2d[ri, rj])
    nearest_lon = float(lon2d[ri, rj])
    logger.info(f"Nearest grid cell: lat={nearest_lat:.4f}, lon={nearest_lon:.4f}")

    fig, ax = plt.subplots(figsize=figsize, subplot_kw={"projection": _PROJECTION})

    # Vector overlays
    ax.add_feature(cfeature.LAKES.with_scale("10m"), facecolor="#d0e8f5", linewidth=0.3, zorder=1)
    ax.add_feature(cfeature.COASTLINE.with_scale("10m"), linewidth=0.6, edgecolor="#444", zorder=2)
    ax.add_feature(
        cfeature.BORDERS.with_scale("10m"),
        linewidth=0.8,
        edgecolor="#555",
        linestyle="-",
        zorder=2,
    )

    # Valid grid points only
    mask_flat = valid_mask.ravel()
    ax.scatter(
        lon2d.ravel()[mask_flat],
        lat2d.ravel()[mask_flat],
        s=4,
        color="steelblue",
        alpha=0.55,
        transform=_DATA_CRS,
        label="Grid points",
        zorder=3,
    )

    # Nearest grid cell
    ax.scatter(
        [nearest_lon],
        [nearest_lat],
        s=90,
        color="crimson",
        zorder=5,
        transform=_DATA_CRS,
        label=f"Nearest cell ({nearest_lat:.3f}°N, {nearest_lon:.3f}°E)",
    )

    # Target point
    ax.scatter(
        [target_lon],
        [target_lat],
        s=70,
        color="orange",
        marker="x",
        linewidths=2,
        zorder=6,
        transform=_DATA_CRS,
        label=f"Target ({target_lat:.3f}°N, {target_lon:.3f}°E)",
    )

    # Extent: pad the valid-data bounding box by 0.3 degree
    pad = 0.3
    valid_lats = lat2d.ravel()[mask_flat]
    valid_lons = lon2d.ravel()[mask_flat]
    ax.set_extent(
        [
            valid_lons.min() - pad,
            valid_lons.max() + pad,
            valid_lats.min() - pad,
            valid_lats.max() + pad,
        ],
        crs=_DATA_CRS,
    )

    gl = ax.gridlines(draw_labels=True, linewidth=0.4, color="gray", alpha=0.6, linestyle="--")
    gl.top_labels = False
    gl.right_labels = False

    ax.set_title("EURO-CORDEX 12 km grid — selected point", fontsize=12)
    ax.legend(loc="lower left", fontsize=9)

    return fig


_SCENARIO_ORDER = ["hist", "rcp26", "rcp45", "rcp85"]
_SCENARIO_LABELS = {
    "hist": "Historical (obs)",
    "rcp26": "RCP 2.6",
    "rcp45": "RCP 4.5",
    "rcp85": "RCP 8.5",
}
_VARIABLE_LABELS = {
    "pr": "Precipitation (kg m⁻² day⁻¹)",
    "tas": "Mean temperature (K)",
    "tasmax": "Max temperature (K)",
    "tasmin": "Min temperature (K)",
    "evspsblpot": "Potential ET (kg m⁻² day⁻¹)",
}
_PERIOD_VARIABLE_LABELS = {
    "pr": "Precipitation (kg m⁻² day⁻¹)",
    "tas": "Mean temperature (°C)",
    "tasmax": "Max temperature (°C)",
    "tasmin": "Min temperature (°C)",
    "evspsblpot": "Potential ET (kg m⁻² day⁻¹)",
}


def load_all_timeseries(
    location_name: str,
    interim_dir: Path | None = None,
) -> pd.DataFrame:
    """Load all CSV timeseries for a location into one combined DataFrame.

    Returns a DataFrame with MultiIndex columns (model, scenario, variable)
    and a DatetimeIndex.
    """
    interim_dir = interim_dir or config.INTERIM_CLIMATE_DIR
    prefix = f"{location_name}_"
    dfs = []

    for csv_path in sorted(interim_dir.glob(f"{prefix}*.csv")):
        stem = csv_path.stem[len(prefix) :]  # "obs_hist" or "model1_rcp45"
        model, scenario = stem.rsplit("_", 1)
        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        df.columns = pd.MultiIndex.from_tuples(
            [(model, scenario, col) for col in df.columns],
            names=["model", "scenario", "variable"],
        )
        dfs.append(df)

    combined = pd.concat(dfs, axis=1)
    combined.index.name = "date"
    logger.info(f"Loaded {len(dfs)} timeseries files for '{location_name}'")
    return combined


def plot_variable_timeseries(
    df: pd.DataFrame,
    variable: str,
    figsize: tuple[float, float] = (16, 4),
) -> plt.Figure:
    """Plot one variable: one subplot per scenario (all in a row), all models as lines."""
    present = set(df.columns.get_level_values("scenario"))
    scenarios = [s for s in _SCENARIO_ORDER if s in present]

    fig, axes = plt.subplots(1, len(scenarios), figsize=figsize, sharey=True)
    if len(scenarios) == 1:
        axes = [axes]

    for ax, scenario in zip(axes, scenarios):
        mask = (df.columns.get_level_values("scenario") == scenario) & (
            df.columns.get_level_values("variable") == variable
        )
        sub = df.loc[:, mask].copy()
        sub.columns = df.columns[mask].get_level_values("model")

        for model in sub.columns:
            ax.plot(sub.index, sub[model], linewidth=0.6, alpha=0.7, label=model)

        ax.set_title(_SCENARIO_LABELS.get(scenario, scenario))
        ax.tick_params(axis="x", rotation=30)

    axes[0].set_ylabel(_VARIABLE_LABELS.get(variable, variable))
    fig.suptitle(_VARIABLE_LABELS.get(variable, variable), fontsize=11)

    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", fontsize=8)
    fig.tight_layout()
    return fig


def plot_all_timeseries(
    df: pd.DataFrame,
    figsize: tuple[float, float] = (16, 4),
) -> list[plt.Figure]:
    """Create one figure per variable showing all models and scenarios."""
    variables = df.columns.get_level_values("variable").unique()
    return [plot_variable_timeseries(df, var, figsize) for var in variables]


def plot_period_statistics(
    yearly_summary: pd.DataFrame,
    variable: str,
    figsize: tuple[float, float] = (14, 4),
) -> plt.Figure:
    """Plot mean with min/max band per 30-year period for one variable.

    One subplot per scenario; one coloured line+shaded band per model.
    Expects yearly_summary with MultiIndex (period, scenario, model) and
    MultiIndex columns (variable, stat) where stat ∈ {mean, min, max}.
    """
    present_scenarios = yearly_summary.index.get_level_values("scenario").unique()
    scenarios = [s for s in _SCENARIO_ORDER if s in present_scenarios and s != "hist"]
    periods = list(yearly_summary.index.get_level_values("period").unique())
    x_pos = list(range(len(periods)))

    fig, axes = plt.subplots(1, len(scenarios), figsize=figsize, sharey=True)
    if len(scenarios) == 1:
        axes = [axes]

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for ax, scenario in zip(axes, scenarios):
        try:
            sub = yearly_summary[variable].xs(scenario, level="scenario")
        except KeyError:
            ax.set_visible(False)
            continue
        models = sub.index.get_level_values("model").unique()
        for i, model in enumerate(models):
            color = colors[i % len(colors)]
            mdata = sub.xs(model, level="model").reindex(periods)
            mean = mdata["mean"].values
            mn = mdata["min"].values
            mx = mdata["max"].values
            ax.plot(x_pos, mean, marker="o", markersize=4, linewidth=1.2, color=color, label=model)
            ax.fill_between(x_pos, mn, mx, color=color, alpha=0.15)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(periods, rotation=30, ha="right")
        ax.set_title(_SCENARIO_LABELS.get(scenario, scenario))

    axes[0].set_ylabel(_PERIOD_VARIABLE_LABELS.get(variable, variable))
    fig.suptitle(_PERIOD_VARIABLE_LABELS.get(variable, variable), fontsize=11)
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", fontsize=8)
    fig.tight_layout()
    return fig


def plot_all_period_statistics(
    yearly_summary: pd.DataFrame,
    figsize: tuple[float, float] = (14, 4),
) -> list[plt.Figure]:
    """Create one figure per variable showing mean/min/max across 30-year periods."""
    variables = yearly_summary.columns.get_level_values(0).unique()
    return [plot_period_statistics(yearly_summary, var, figsize) for var in variables]


def plot_yield_timeseries_comparison(
    model: pd.DataFrame,
    truth: pd.DataFrame,
) -> plt.Figure:
    """Plot modelled vs observed yield over time on the same axes.

    Parameters
    ----------
    model:
        results["season"] DataFrame; must contain "Year1" and "Y(dry)" columns.
    truth:
        DataFrame from get_yield(); must contain "year" and "yield" columns.
    """
    fig, ax = plt.subplots()
    ax.plot(model["Year1"], model["Y(dry)"], marker="o", markersize=4, linewidth=1.2, label="Model Y(dry)")
    ax.plot(truth["year"], truth["yield"], marker="s", markersize=4, linewidth=1.2, label="Observed yield")
    ax.set_xlabel("Year")
    ax.set_ylabel("Dry yield (t ha⁻¹)")
    ax.set_title("Modelled vs observed maize dry yield")
    ax.legend()
    fig.tight_layout()


def plot_yield_scatter(
    model: pd.DataFrame,
    truth: pd.DataFrame,
) -> plt.Figure:
    """Scatter plot of observed yield (x) vs modelled yield (y) with 1:1 diagonal.

    Parameters
    ----------w
    model:
        results["season"] DataFrame; must contain "Year1" and "Y(dry)" columns.
    truth:
        DataFrame from get_yield(); must contain "year" and "yield" columns.
    """
    merged = pd.merge(
        model[["Year1", "Y(dry)"]].rename(columns={"Year1": "year", "Y(dry)": "modelled"}),
        truth.rename(columns={"yield": "observed"}),
        on="year",
    )
    fig, ax = plt.subplots()
    ax.scatter(merged["observed"], merged["modelled"], s=40, zorder=3)

    lo = min(merged["modelled"].min(), merged["observed"].min())
    hi = max(merged["modelled"].max(), merged["observed"].max())
    pad = (hi - lo) * 0.05
    diag = [lo - pad, hi + pad]
    ax.plot(diag, diag, color="gray", linewidth=1, linestyle="--")

    ax.set_xlabel("Observed yield (t ha⁻¹)")
    ax.set_ylabel("Model Y(dry) (t ha⁻¹)")
    ax.set_title("Modelled vs observed yield")
    fig.tight_layout()


def plot_observed_yield(
    yield_df: pd.DataFrame,
    quantity: str,
) -> list[plt.Figure]:
    """One figure per location: grain yield over time, one subplot per fertilization, coloured by management.

    Parameters
    ----------
    yield_df:
        Long-form DataFrame with columns: location, year, management, fertilization, product, yield.
        Typically the processed maize.pkl loaded into a DataFrame.
    quantity:
        grain, straw, biomass or hi
    """
    import matplotlib.lines as mlines

    managements = sorted(yield_df["management"].unique())
    fertilizations = sorted(yield_df["fertilization"].unique())
    locations_list = sorted(yield_df["location"].unique())

    colors = dict(zip(managements, ["tab:blue", "tab:orange", "tab:green"]))
    color_handles = [
        mlines.Line2D([], [], color=colors[m], linewidth=1.5, label=f"Management {m}")
        for m in managements
    ]

    figs = []
    for loc in locations_list:
        fig, axes = plt.subplots(1, len(fertilizations), figsize=(16,4), sharey=True)
        for ax, fert in zip(axes, fertilizations):
            sub = yield_df[
                (yield_df["location"] == loc)
                & (yield_df["fertilization"] == fert)
                & (yield_df["product"] == quantity)
            ]
            for mgmt in managements:
                s = sub[sub["management"] == mgmt]
                if s.empty:
                    continue
                ax.plot(s["year"], s["yield"], color=colors[mgmt], marker="o", markersize=3, linewidth=1.2)
            ax.set_title(fert)
            if ax is axes[0]:
                ax.set_ylabel("Yield (t ha⁻¹)")
            ax.tick_params(axis="x", rotation=30)

        fig.legend(handles=color_handles, loc="upper right", fontsize=9)
        fig.suptitle(f"Maize {quantity} yield — {loc.capitalize()}", fontsize=13)
        fig.tight_layout()
        figs.append(fig)
    return figs


def plot_gdd_and_yield(gdd_by_year: pd.Series, season_df: pd.DataFrame, title: str = "Annual GDD and Maize Dry Yield"):
    """Dual-axis bar/line plot: GDD bars (left) and dry yield line (right)."""
    season = season_df.set_index("Year1") if "Year1" in season_df.columns else season_df

    fig, ax1 = plt.subplots(figsize=(12, 5))

    ax1.bar(gdd_by_year.index, gdd_by_year.values, color="tab:orange", alpha=0.6, label="GDD")
    ax1.set_ylabel("GDD (°C·day)", color="tab:orange")
    ax1.tick_params(axis="y", labelcolor="tab:orange")

    ax2 = ax1.twinx()
    ax2.plot(season.index, season["Y(dry)"], marker="o", color="tab:blue", label="Yield (dry)")
    ax2.set_ylabel("Dry yield (t/ha)", color="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:blue")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax1.set_xlabel("Year")
    plt.title(title)
    plt.tight_layout()