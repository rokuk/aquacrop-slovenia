from __future__ import annotations

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
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
    station_lat: float | None = None,
    station_lon: float | None = None,
    station_label: str = "Meteo station",
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
    print(f"Nearest grid cell: lat={nearest_lat:.4f}, lon={nearest_lon:.4f}")

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

    # Meteo station
    if station_lat is not None and station_lon is not None:
        ax.scatter(
            [station_lon],
            [station_lat],
            s=90,
            color="green",
            marker="^",
            zorder=7,
            transform=_DATA_CRS,
            label=f"{station_label} ({station_lat:.3f}°N, {station_lon:.3f}°E)",
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
    "hist": "Historical",
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
    print(f"Loaded {len(dfs)} timeseries files for '{location_name}'")
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
    varname: str,
    location: str,
) -> plt.Figure:
    """Plot modelled vs observed yield over time on the same axes.

    Parameters
    ----------
    model:
        results["season"] DataFrame; must contain "Year1" and varname columns.
    truth:
        DataFrame from get_yield(); must contain "year" and "yield" columns.
    location:
        Used as the plot title, e.g. "jablje" or "rakican".
    """
    all_years = pd.RangeIndex(
        min(model["Year1"].min(), truth["year"].min()),
        max(model["Year1"].max(), truth["year"].max()) + 1,
    )
    model_s = model.set_index("Year1")[varname].reindex(all_years)
    truth_s = truth.set_index("year")["yield"].reindex(all_years)

    fig, ax = plt.subplots()
    ax.plot(all_years, model_s, marker="o", markersize=4, linewidth=1.2, label="Model")
    ax.plot(all_years, truth_s, marker="s", markersize=4, linewidth=1.2, label="Observed")
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Year")
    ax.set_ylabel(varname + (" [t/ha]" if (varname in ["Y(dry)", "BioMass"]) else ""))
    ax.set_title(location)
    ax.legend()
    fig.tight_layout()


def plot_yield_timeseries_residuals(
    model: pd.DataFrame,
    truth: pd.DataFrame,
    varname: str,
) -> plt.Figure:
    """Plot modelled vs observed yield over time on the same axes.

    Parameters
    ----------
    model:
        results["season"] DataFrame; must contain "Year1" and varname columns.
    truth:
        DataFrame from get_yield(); must contain "year" and "yield" columns.
    """
    fig, ax = plt.subplots()
    residuals = model[varname].values - truth["yield"].values
    ax.stem(model["Year1"], residuals)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Year")
    ax.set_title(f"Modelled minus observed maize {varname}")
    fig.tight_layout()


def plot_yield_residuals_histogram(
    model: pd.DataFrame,
    truth: pd.DataFrame,
    varname: str,
) -> plt.Figure:
    fig, ax = plt.subplots()
    residuals = model[varname].values - truth["yield"].values
    ax.hist(residuals, bins="auto", edgecolor="white")
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Residual (t ha⁻¹)")
    ax.set_ylabel("Count")
    ax.set_title(f"Residual histogram — maize {varname}")
    fig.tight_layout()


def plot_yield_residuals_qq(
    model: pd.DataFrame,
    truth: pd.DataFrame,
    varname: str,
) -> plt.Figure:
    fig, ax = plt.subplots()
    residuals = model[varname].values - truth["yield"].values
    (osm, osr), (slope, intercept, _) = stats.probplot(residuals, dist="norm")
    ax.scatter(osm, osr, s=30, zorder=3)
    x = np.array([osm[0], osm[-1]])
    ax.plot(x, slope * x + intercept, color="gray", linewidth=1, linestyle="--")
    ax.set_xlabel("Theoretical quantiles")
    ax.set_ylabel("Sample quantiles")
    ax.set_title(f"Q-Q plot of residuals — maize {varname}")
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

    hi = max(merged["modelled"].max(), merged["observed"].max())
    diag = [0, hi]
    ax.plot(diag, diag, color="gray", linewidth=1, linestyle="--")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid(True, which="both", axis="both", linewidth=0.5, color="gray", alpha=0.5)

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
        fig, axes = plt.subplots(1, len(fertilizations), figsize=(16, 4), sharey=True)
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
                ax.plot(
                    s["year"],
                    s["yield"],
                    color=colors[mgmt],
                    marker="o",
                    markersize=3,
                    linewidth=1.2,
                )
            ax.set_title(fert)
            if ax is axes[0]:
                ax.set_ylabel("Yield (t ha⁻¹)")
            ax.tick_params(axis="x", rotation=30)

        fig.legend(handles=color_handles, loc="upper right", fontsize=9)
        fig.suptitle(f"Maize {quantity} yield — {loc.capitalize()}", fontsize=13)
        fig.tight_layout()
        figs.append(fig)
    return figs


def add_reference_boxplots(
    ax: plt.Axes,
    center: float,
    hist_results: pd.DataFrame | None,
    obs_yields: pd.DataFrame | None,
    box_width: float = 0.20,
    box_gap: float = 0.04,
    vert: bool = True,
) -> None:
    """Draw measured/historical-modelled reference boxplots centred on `center`.

    Used to add a "ground truth" reference group to a projections plot: the
    station-based historical model run and/or the observed yields. Also adds
    proxy legend entries (via zero-length `ax.plot` calls) for each box drawn;
    call `ax.legend()` afterwards to show them.

    `center`/`box_width`/`box_gap` are along the position axis (x if `vert`, else
    y); set `vert=False` to draw the boxes horizontally, e.g. as a strip above a
    yield-on-x-axis histogram.
    """
    ref_items = []
    if obs_yields is not None:
        ref_items.append((obs_yields["yield"].values, "gold", None, "izmerjeno"))
    if hist_results is not None:
        ref_items.append((hist_results["Y(dry)"].values, "#555555", "///", "AquaCrop"))
    n_ref = len(ref_items)

    for k, (data, color, hatch, label) in enumerate(ref_items):
        x = center + (k - (n_ref - 1) / 2) * (box_width + box_gap)
        bp = ax.boxplot([data], positions=[x], widths=box_width * 0.85, vert=vert,
                        patch_artist=True, manage_ticks=False)
        bp["boxes"][0].set_facecolor(color)
        bp["boxes"][0].set_alpha(0.75)
        if hatch:
            bp["boxes"][0].set_hatch(hatch)
        ec = "goldenrod" if color == "gold" else color
        for key in ("whiskers", "caps", "fliers"):
            for line in bp[key]:
                line.set_color(ec)
        for line in bp["medians"]:
            line.set_color("black" if color == "gold" else "white")
        ax.plot([], [], color=color, linewidth=3, alpha=0.75, label=label)


def add_reference_violins(
    ax: plt.Axes,
    center: float,
    hist_results: pd.DataFrame | None,
    obs_yields: pd.DataFrame | None,
    violin_width: float = 0.20,
    box_gap: float = 0.04,
) -> None:
    """Draw measured/historical-modelled reference violins centred on `center`.

    Same reference data and color scheme as `add_reference_boxplots`, but drawn
    as violins so they match a violin-plot main panel. Also adds proxy legend
    entries; call `ax.legend()` afterwards to show them.
    """
    ref_items = []
    if obs_yields is not None:
        ref_items.append((obs_yields["yield"].values, "gold", None, "measured"))
    if hist_results is not None:
        ref_items.append((hist_results["Y(dry)"].values, "#555555", "///", "historical (modelled)"))
    n_ref = len(ref_items)

    for k, (data, color, hatch, label) in enumerate(ref_items):
        x = center + (k - (n_ref - 1) / 2) * (violin_width + box_gap)
        parts = ax.violinplot(
            [data], positions=[x], widths=violin_width * 0.9, showmedians=True, showextrema=True
        )
        for body in parts["bodies"]:
            body.set_facecolor(color)
            body.set_alpha(0.6)
            if hatch:
                body.set_hatch(hatch)
        ec = "goldenrod" if color == "gold" else color
        for key in ("cmins", "cmaxes", "cbars"):
            parts[key].set_color(ec)
        parts["cmedians"].set_color("black")
        parts["cmedians"].set_linewidth(1.5)
        ax.plot([], [], color=color, linewidth=3, alpha=0.75, label=label)


def add_raincloud(
    ax: plt.Axes,
    data: np.ndarray,
    x: float,
    width: float,
    color: str,
    hatch: str | None = None,
    alpha: float = 0.6,
    rng: np.random.Generator | None = None,
) -> None:
    """Draw one raincloud — a half-violin "cloud", a thin boxplot, and jittered "rain" points.

    The cloud sits to the right of `x` with its flat edge at `x`; the box sits just left
    of the cloud; the jittered raw points sit further left still. `width` is the group's
    full footprint along the position axis, i.e. the same `width` you'd pass to a grouped
    `ax.boxplot`/`ax.violinplot` at the same position.
    """
    data = np.asarray(data)
    if data.size == 0:
        return
    if rng is None:
        rng = np.random.default_rng(0)

    # Cloud: half-violin, right half only (flat edge at x). Degenerate (near-constant)
    # data has no density to show, so skip straight to the box + rain in that case.
    if data.size >= 2 and np.ptp(data) > 0:
        parts = ax.violinplot(
            [data], positions=[x], widths=width, showmedians=False, showextrema=False
        )
        body = parts["bodies"][0]
        verts = body.get_paths()[0].vertices
        verts[:, 0] = np.clip(verts[:, 0], x, None)
        body.set_facecolor(color)
        body.set_edgecolor(color)
        body.set_alpha(alpha)
        if hatch:
            body.set_hatch(hatch)

    # Box: thin, centred just left of the cloud's flat edge
    box_x = x - width * 0.22
    bp = ax.boxplot(
        [data], positions=[box_x], widths=width * 0.18, patch_artist=True,
        manage_ticks=False, showfliers=False, zorder=3,
    )
    bp["boxes"][0].set_facecolor("white")
    bp["boxes"][0].set_edgecolor(color)
    bp["boxes"][0].set_linewidth(1.2)
    for key in ("whiskers", "caps"):
        for line in bp[key]:
            line.set_color(color)
    for line in bp["medians"]:
        line.set_color(color)
        line.set_linewidth(1.5)

    # Rain: jittered raw points, further left again
    jitter = rng.uniform(-width * 0.18, width * 0.02, size=data.size)
    ax.scatter(
        x - width * 0.42 + jitter, data, color=color, alpha=min(alpha + 0.15, 0.9),
        s=5, edgecolors="none", zorder=2,
    )


def add_reference_rainclouds(
    ax: plt.Axes,
    center: float,
    hist_results: pd.DataFrame | None,
    obs_yields: pd.DataFrame | None,
    cloud_width: float = 0.35,
    box_gap: float = 0.06,
    rng: np.random.Generator | None = None,
) -> None:
    """Draw measured/historical-modelled reference rainclouds centred on `center`.

    Same reference data and color scheme as `add_reference_boxplots`, but drawn via
    `add_raincloud` so they match a raincloud-plot main panel. Also adds proxy legend
    entries; call `ax.legend()` afterwards to show them.
    """
    ref_items = []
    if obs_yields is not None:
        ref_items.append((obs_yields["yield"].values, "gold", None, "izmerjeno"))
    if hist_results is not None:
        ref_items.append((hist_results["Y(dry)"].values, "#555555", "///", "AquaCrop"))
    n_ref = len(ref_items)
    if rng is None:
        rng = np.random.default_rng(0)

    for k, (data, color, hatch, label) in enumerate(ref_items):
        x = center + (k - (n_ref - 1) / 2) * (cloud_width + box_gap)
        add_raincloud(ax, data, x, cloud_width, color, hatch=hatch, rng=rng)
        ax.plot([], [], color=color, linewidth=3, alpha=0.75, label=label)


def plot_yield_projections_boxplot_with_hist(
    projections: dict,
    location: str,
    hist_results: pd.DataFrame | None = None,
    obs_yields: pd.DataFrame | None = None,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure:
    """Boxplot of projected yield by period, with historical run and observations in their own subplot.

    The observed/historical-modelled reference gets a dedicated (narrower) subplot on
    the left, titled like the scenario subplots via `_SCENARIO_LABELS["hist"]`. One
    further subplot per scenario shows the four 30-year projection periods, one box per
    climate model. Y-axis (dry yield) is shared across all subplots.

    Parameters
    ----------
    hist_results:
        Season DataFrame from run_historical_simulation() with columns Year1, Y(dry).
    obs_yields:
        Observed yield DataFrame from get_yield_for_comparison() with columns year, yield.
    """
    from aquacrop_slovenia.yield_projections import PERIODS

    scenarios = sorted({sc for _, sc in projections})
    model_names = sorted({model for model, _ in projections})
    period_labels = list(PERIODS.keys())
    n_models = len(model_names)
    n_scenarios = len(scenarios)

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    group_width = 0.65
    box_width = group_width / n_models
    ref_box_width = 0.6

    has_ref = hist_results is not None or obs_yields is not None
    n_panels = n_scenarios + (1 if has_ref else 0)

    if figsize is None:
        figsize = (0.15 * (1 if has_ref else 0) * 7 + 5 * n_scenarios, 5)

    width_ratios = ([0.15] if has_ref else []) + [1] * n_scenarios
    fig, axes = plt.subplots(
        1, n_panels, figsize=figsize, sharey=True,
        gridspec_kw={"width_ratios": width_ratios, "wspace": 0.08},
    )
    if n_panels == 1:
        axes = [axes]

    if has_ref:
        ref_ax = axes[0]
        add_reference_boxplots(ref_ax, 0, hist_results, obs_yields, box_width=ref_box_width)
        ref_ax.set_xticks([0])
        ref_ax.set_xticklabels(["Obs. period\n(1993–2023)"])
        ref_ax.set_title(_SCENARIO_LABELS.get("hist"))
        ref_ax.set_ylabel("Dry yield (t/ha)")
        ref_ax.legend(fontsize=8, frameon=False)
        scenario_axes = axes[1:]
    else:
        scenario_axes = axes
        scenario_axes[0].set_ylabel("Dry yield (t/ha)")

    for ax, scenario in zip(scenario_axes, scenarios):
        # One box per climate model within each 30-year period
        for i, model in enumerate(model_names):
            if (model, scenario) not in projections:
                continue
            result = projections[(model, scenario)]
            color = colors[i % len(colors)]
            positions, data = [], []
            for j, (plabel, (start, end)) in enumerate(PERIODS.items()):
                s = result.loc[
                    (result["Year1"] >= start) & (result["Year1"] <= end), "Y(dry)"
                ].values
                positions.append(j + (i - (n_models - 1) / 2) * box_width)
                data.append(s)
            bp = ax.boxplot(data, positions=positions, widths=box_width * 0.85,
                            patch_artist=True, manage_ticks=False)
            for patch in bp["boxes"]:
                patch.set_facecolor(color)
                patch.set_alpha(0.6)
            for key in ("whiskers", "caps", "fliers"):
                for line in bp[key]:
                    line.set_color(color)
            for line in bp["medians"]:
                line.set_color("black")
            ax.plot([], [], color=color, linewidth=3, label=model)

        ax.set_xticks(range(len(period_labels)))
        ax.set_xticklabels(period_labels)
        ax.set_title(_SCENARIO_LABELS.get(scenario, scenario))
        ax.legend(fontsize=8, frameon=False)

    fig.suptitle(
        f"AquaCrop yield projections — {location.capitalize()} — 30-year period distributions",
        fontsize=13,
    )
    fig.tight_layout()
    # tight_layout() recomputes spacing to fit the tick labels, undoing the gridspec
    # wspace above — reapply it afterwards so the panels stay tight.
    fig.subplots_adjust(wspace=0.08)
    return fig


def plot_yield_projections_raincloud_with_hist(
    projections: dict,
    location: str,
    hist_results: pd.DataFrame | None = None,
    obs_yields: pd.DataFrame | None = None,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure:
    """Raincloud plot of projected yield by period with historical run and observations as a separate period.

    Same layout as `plot_yield_projections_boxplot_with_hist` — periods on the x-axis,
    a dedicated "Observed period" group (index 0) for the station-based model run and
    observed yields, then one group per climate model within each of the four 30-year
    projection periods — but each group is drawn as a raincloud (half-violin density +
    thin boxplot + jittered raw points, via `add_raincloud`) instead of a plain box.

    Parameters
    ----------
    hist_results:
        Season DataFrame from run_historical_simulation() with columns Year1, Y(dry).
    obs_yields:
        Observed yield DataFrame from get_yield_for_comparison() with columns year, yield.
    """
    from aquacrop_slovenia.yield_projections import PERIODS

    scenarios = sorted({sc for _, sc in projections})
    model_names = sorted({model for model, _ in projections})
    period_labels = list(PERIODS.keys())
    n_models = len(model_names)

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    group_width = 0.6
    cloud_width = group_width / n_models
    ref_cloud_width = cloud_width  # measured/historical clouds match a single model's width
    ref_box_gap = 0.06
    period_spacing = 0.8  # < 1.0 pulls period groups closer together (group_width unchanged)

    # x positions: 0 = observed period, 1..4 = projection periods. The observed-period
    # group only has up to 2 clouds (vs. n_models), so its footprint — and hence the
    # offset to the first projection period — is sized from its own item count rather
    # than reusing group_width, keeping the gap to the first period visually consistent.
    has_ref = hist_results is not None or obs_yields is not None
    n_ref = int(obs_yields is not None) + int(hist_results is not None)
    ref_group_width = n_ref * ref_cloud_width + max(n_ref - 1, 0) * ref_box_gap
    period_gap = period_spacing - group_width  # empty gap between adjacent period groups
    proj_offset = ref_group_width / 2 + period_gap + group_width / 2 if has_ref else 0
    all_xtick_positions = []
    all_xtick_labels = []

    if has_ref:
        all_xtick_positions.append(0)
        all_xtick_labels.append("Obs. period\n(1993–2023)")

    for j, label in enumerate(period_labels):
        all_xtick_positions.append(j * period_spacing + proj_offset)
        all_xtick_labels.append(label)

    if figsize is None:
        figsize = (12, 3.5 * len(scenarios))

    fig, axes = plt.subplots(len(scenarios), 1, figsize=figsize, sharex=True)
    if len(scenarios) == 1:
        axes = [axes]

    rng = np.random.default_rng(0)

    for ax, scenario in zip(axes, scenarios):
        # Observed-period group: hist run and obs side by side
        if has_ref:
            add_reference_rainclouds(
                ax, 0, hist_results, obs_yields,
                cloud_width=ref_cloud_width, box_gap=ref_box_gap, rng=rng,
            )

        # Projection period groups: one raincloud per climate model
        for i, model in enumerate(model_names):
            if (model, scenario) not in projections:
                continue
            result = projections[(model, scenario)]
            color = colors[i % len(colors)]
            for j, (plabel, (start, end)) in enumerate(PERIODS.items()):
                s = result.loc[
                    (result["Year1"] >= start) & (result["Year1"] <= end), "Y(dry)"
                ].values
                if len(s) == 0:
                    continue
                x = j * period_spacing + proj_offset + (i - (n_models - 1) / 2) * cloud_width
                add_raincloud(ax, s, x, cloud_width, color, rng=rng)
            ax.plot([], [], color=color, linewidth=3, label=model)

        # Divider between observed period and projection periods
        if has_ref:
            divider_x = ref_group_width / 2 + period_gap / 2
            ax.axvline(divider_x, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)

        ax.set_xticks(all_xtick_positions)
        ax.set_ylabel("Dry yield (t ha⁻¹)")
        ax.set_title(_SCENARIO_LABELS.get(scenario, scenario))
        # Hang the legend just outside the axes, bottom-left, so it doesn't eat into
        # (or sit on top of) the obs./first-period raincloud. tight_layout() then
        # grows the left margin by exactly as much as the legend needs.
        ax.legend(fontsize=8, loc="lower left", frameon=False)

    # Only the bottom subplot needs x-tick labels; the rest share the same x-axis.
    for ax in axes[:-1]:
        ax.tick_params(labelbottom=False)
    axes[-1].set_xticklabels(all_xtick_labels)
    fig.suptitle(
        f"AquaCrop yield projections — {location.capitalize()} — 30-year period distributions",
        fontsize=13,
    )
    fig.tight_layout()
    return fig


def plot_yield_projections_by_period(
    projections: dict,
    location: str,
    hist_results: pd.DataFrame | None = None,
    obs_yields: pd.DataFrame | None = None,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure:
    """Histogram/density of projected yield by 30-year period, one subplot per scenario.

    Periods are on the x-axis; yield is on the y-axis. The distribution shape
    (violin = KDE density) is shown for each period, with all models pooled. If
    `hist_results` and/or `obs_yields` are given, a dedicated "Observed period"
    reference group (boxplots) is added before the projection periods.

    Parameters
    ----------
    hist_results:
        Season DataFrame from run_historical_simulation() with columns Year1, Y(dry).
    obs_yields:
        Observed yield DataFrame from get_yield_for_comparison() with columns year, yield.
    """
    from aquacrop_slovenia.yield_projections import PERIODS

    scenarios = sorted({sc for _, sc in projections})
    model_names = sorted({model for model, _ in projections})
    period_labels = list(PERIODS.keys())
    n_scenarios = len(scenarios)

    has_ref = hist_results is not None or obs_yields is not None
    proj_offset = 1 if has_ref else 0

    if figsize is None:
        figsize = (5 * n_scenarios, 5)

    fig, axes = plt.subplots(1, n_scenarios, figsize=figsize, sharey=True)
    if n_scenarios == 1:
        axes = [axes]

    period_colors = {
        "1981-2010": "steelblue",
        "2011-2040": "darkorange",
        "2041-2070": "seagreen",
        "2071-2100": "firebrick",
    }

    for ax, scenario in zip(axes, scenarios):
        if has_ref:
            add_reference_violins(ax, 0, hist_results, obs_yields, violin_width=0.5)

        data_by_period = []
        for label, (start, end) in PERIODS.items():
            all_yields = []
            for model in model_names:
                if (model, scenario) not in projections:
                    continue
                result = projections[(model, scenario)]
                s = result.loc[
                    (result["Year1"] >= start) & (result["Year1"] <= end), "Y(dry)"
                ].values
                all_yields.extend(s)
            data_by_period.append(all_yields)

        positions = [j + proj_offset for j in range(len(period_labels))]
        parts = ax.violinplot(
            data_by_period, positions=positions, showmedians=True, showextrema=True
        )
        for i, (body, label) in enumerate(zip(parts["bodies"], period_labels)):
            body.set_facecolor(period_colors[label])
            body.set_alpha(0.6)
        parts["cmedians"].set_color("black")
        parts["cmedians"].set_linewidth(1.5)

        if has_ref:
            ax.axvline(0.5, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)

        xtick_positions = ([0] if has_ref else []) + positions
        xtick_labels = (["Obs. period\n(1993–2023)"] if has_ref else []) + period_labels
        ax.set_xticks(xtick_positions)
        ax.set_xticklabels(xtick_labels, rotation=15, ha="right")
        ax.set_title(_SCENARIO_LABELS.get(scenario, scenario))
        if has_ref:
            ax.legend(fontsize=8)

    axes[0].set_ylabel("Dry yield (t ha⁻¹)")
    fig.suptitle(
        f"AquaCrop yield projections — {location.capitalize()} — 30-year period distributions",
        fontsize=13,
    )
    fig.tight_layout()
    return fig


def plot_yield_projections_by_model(
    projections: dict,
    location: str,
    hist_results: pd.DataFrame | None = None,
    obs_yields: pd.DataFrame | None = None,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure:
    """Histogram/density of projected yield by climate model, one subplot per scenario.

    Models are on the x-axis; yield is on the y-axis. Within each model group, one
    violin per 30-year period shows how that model's own distribution shifts over
    time (as opposed to `plot_yield_projections_by_period`, which pools all models
    together within each period). If `hist_results` and/or `obs_yields` are given,
    a dedicated "Observed" reference group (boxplots) is added before the models.

    Parameters
    ----------
    hist_results:
        Season DataFrame from run_historical_simulation() with columns Year1, Y(dry).
    obs_yields:
        Observed yield DataFrame from get_yield_for_comparison() with columns year, yield.
    """
    from aquacrop_slovenia.yield_projections import PERIODS

    scenarios = sorted({sc for _, sc in projections})
    model_names = sorted({model for model, _ in projections})
    period_labels = list(PERIODS.keys())
    n_periods = len(period_labels)
    n_scenarios = len(scenarios)

    has_ref = hist_results is not None or obs_yields is not None
    proj_offset = 1 if has_ref else 0

    if figsize is None:
        figsize = (5 * n_scenarios, 5)

    fig, axes = plt.subplots(1, n_scenarios, figsize=figsize, sharey=True)
    if n_scenarios == 1:
        axes = [axes]

    period_colors = {
        "1981-2010": "steelblue",
        "2011-2040": "darkorange",
        "2041-2070": "seagreen",
        "2071-2100": "firebrick",
    }

    group_width = 0.8
    violin_width = group_width / n_periods

    for ax, scenario in zip(axes, scenarios):
        if has_ref:
            add_reference_violins(ax, 0, hist_results, obs_yields, violin_width=group_width)

        for i, model in enumerate(model_names):
            if (model, scenario) not in projections:
                continue
            result = projections[(model, scenario)]
            for j, (plabel, (start, end)) in enumerate(PERIODS.items()):
                s = result.loc[
                    (result["Year1"] >= start) & (result["Year1"] <= end), "Y(dry)"
                ].values
                if len(s) == 0:
                    continue
                position = i + proj_offset + (j - (n_periods - 1) / 2) * violin_width
                parts = ax.violinplot(
                    [s], positions=[position], widths=violin_width * 0.9,
                    showmedians=True, showextrema=True,
                )
                for body in parts["bodies"]:
                    body.set_facecolor(period_colors[plabel])
                    body.set_alpha(0.6)
                parts["cmedians"].set_color("black")
                parts["cmedians"].set_linewidth(1.2)

        if has_ref:
            ax.axvline(0.5, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)

        xtick_positions = ([0] if has_ref else []) + [
            i + proj_offset for i in range(len(model_names))
        ]
        xtick_labels = (["Observed"] if has_ref else []) + model_names
        ax.set_xticks(xtick_positions)
        ax.set_xticklabels(xtick_labels, rotation=15, ha="right")
        ax.set_title(_SCENARIO_LABELS.get(scenario, scenario))

        for label in period_labels:
            ax.plot([], [], color=period_colors[label], linewidth=6, alpha=0.6, label=label)
        ax.legend(fontsize=8)

    axes[0].set_ylabel("Dry yield (t ha⁻¹)")
    fig.suptitle(
        f"AquaCrop yield projections — {location.capitalize()} — 30-year period distributions by model",
        fontsize=13,
    )
    fig.tight_layout()
    return fig


def plot_yield_projections_by_model_boxplot(
    projections: dict,
    location: str,
    hist_results: pd.DataFrame | None = None,
    obs_yields: pd.DataFrame | None = None,
    figsize: tuple[float, float] | None = None,
) -> plt.Figure:
    """Boxplot of projected yield by climate model, one subplot per scenario.

    Same layout as `plot_yield_projections_by_model` (models on the x-axis, one box
    per 30-year period within each model group), but drawn as boxplots instead of
    violins. If `hist_results` and/or `obs_yields` are given, a dedicated "Observed"
    reference group (boxplots) is added before the models.

    Parameters
    ----------
    hist_results:
        Season DataFrame from run_historical_simulation() with columns Year1, Y(dry).
    obs_yields:
        Observed yield DataFrame from get_yield_for_comparison() with columns year, yield.
    """
    from aquacrop_slovenia.yield_projections import PERIODS

    scenarios = sorted({sc for _, sc in projections})
    model_names = sorted({model for model, _ in projections})
    period_labels = list(PERIODS.keys())
    n_periods = len(period_labels)
    n_scenarios = len(scenarios)

    has_ref = hist_results is not None or obs_yields is not None
    proj_offset = 1 if has_ref else 0

    if figsize is None:
        figsize = (5 * n_scenarios, 5)

    fig, axes = plt.subplots(1, n_scenarios, figsize=figsize, sharey=True)
    if n_scenarios == 1:
        axes = [axes]

    period_colors = {
        "1981-2010": "steelblue",
        "2011-2040": "darkorange",
        "2041-2070": "seagreen",
        "2071-2100": "firebrick",
    }

    group_width = 0.8
    box_width = group_width / n_periods

    for ax, scenario in zip(axes, scenarios):
        if has_ref:
            add_reference_boxplots(ax, 0, hist_results, obs_yields, box_width=group_width)

        for i, model in enumerate(model_names):
            if (model, scenario) not in projections:
                continue
            result = projections[(model, scenario)]
            for j, (plabel, (start, end)) in enumerate(PERIODS.items()):
                s = result.loc[
                    (result["Year1"] >= start) & (result["Year1"] <= end), "Y(dry)"
                ].values
                if len(s) == 0:
                    continue
                position = i + proj_offset + (j - (n_periods - 1) / 2) * box_width
                bp = ax.boxplot(
                    [s], positions=[position], widths=box_width * 0.85,
                    patch_artist=True, manage_ticks=False,
                )
                for patch in bp["boxes"]:
                    patch.set_facecolor(period_colors[plabel])
                    patch.set_alpha(0.6)
                for key in ("whiskers", "caps", "fliers"):
                    for line in bp[key]:
                        line.set_color(period_colors[plabel])
                for line in bp["medians"]:
                    line.set_color("black")

        if has_ref:
            ax.axvline(0.5, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)

        xtick_positions = ([0] if has_ref else []) + [
            i + proj_offset for i in range(len(model_names))
        ]
        xtick_labels = (["Observed"] if has_ref else []) + model_names
        ax.set_xticks(xtick_positions)
        ax.set_xticklabels(xtick_labels, rotation=15, ha="right")
        ax.set_title(_SCENARIO_LABELS.get(scenario, scenario))

        for label in period_labels:
            ax.plot([], [], color=period_colors[label], linewidth=6, alpha=0.6, label=label)
        ax.legend(fontsize=8)

    axes[0].set_ylabel("Dry yield (t ha⁻¹)")
    fig.suptitle(
        f"AquaCrop yield projections — {location.capitalize()} — 30-year period distributions by model",
        fontsize=13,
    )
    fig.tight_layout()
    return fig


def plot_gdd_and_yield(
    gdd_by_year: pd.Series, season_df: pd.DataFrame, title: str = "Annual GDD and Maize Dry Yield"
):
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
