from __future__ import annotations

import collections
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from tqdm import tqdm
import xarray as xr

from aquacrop_slovenia import config
from aquacrop_slovenia.yield_projections import get_model_scenario_combinations

VARIABLES: list[str] = ["pr", "tas", "tasmax", "tasmin", "evspsblpot"]

GroupKey = tuple[str, str, str]  # (gcm, rcm, scenario)


@dataclass(frozen=True)
class FileInfo:
    path: Path
    variable: str
    gcm: str
    rcm: str
    scenario: str
    start: str
    end: str


def parse_filename(path: Path) -> FileInfo:
    """Parse a NetCDF filename into a FileInfo.

    Handles two naming patterns split on '_day_':
    - ARSO:  {var}_12km_ARSO_{version}  (4 tokens)
    - RCM:   {var}_12km_{GCM}_{scenario}_{run}_{RCM}_{version}  (7 tokens)
    """
    left, right = path.stem.split("_day_", 1)
    date_parts = right.split("_")
    start, end = date_parts[0], date_parts[1]
    tokens = left.split("_")

    if tokens[2] == "ARSO":
        return FileInfo(
            path=path,
            variable=tokens[0],
            gcm="ARSO",
            rcm="",
            scenario="hist",
            start=start,
            end=end,
        )
    # RCM: [var, 12km, GCM, scenario, run, RCM, version]
    return FileInfo(
        path=path,
        variable=tokens[0],
        gcm=tokens[2],
        rcm=tokens[5],
        scenario=tokens[3],
        start=start,
        end=end,
    )


def discover_files(climate_dir: Path) -> list[FileInfo]:
    """Return a FileInfo for every .nc file under climate_dir/{hist,rcp26,rcp45,rcp85}/."""
    files: list[FileInfo] = []
    for scenario in ("hist", "rcp26", "rcp45", "rcp85"):
        subdir = climate_dir / scenario
        if not subdir.exists():
            continue
        for nc_path in sorted(subdir.glob("*.nc")):
            files.append(parse_filename(nc_path))
    return files


def group_files(files: list[FileInfo]) -> dict[GroupKey, list[FileInfo]]:
    """Group FileInfo objects by (gcm, rcm, scenario)."""
    groups: dict[GroupKey, list[FileInfo]] = collections.defaultdict(list)
    for fi in files:
        groups[(fi.gcm, fi.rcm, fi.scenario)].append(fi)
    return dict(groups)


def _lat_lon_arrays(ds: xr.Dataset) -> tuple[np.ndarray, np.ndarray]:
    """Return (lat2d, lon2d) from a dataset regardless of coordinate naming.

    RCM files have 2D 'lat'/'lon' non-index coords with rlat/rlon dimensions.
    ARSO files have 1D 'Y'/'X' dimension coordinates (Y=latitude, X=longitude).
    """
    if "lat" in ds.coords and "lon" in ds.coords:
        lat, lon = ds["lat"].values, ds["lon"].values
    elif "Y" in ds.coords and "X" in ds.coords:
        lat, lon = ds["Y"].values, ds["X"].values
    else:
        raise ValueError(f"No lat/lon coordinates found. Available: {sorted(ds.coords)}")
    if lat.ndim == 1:
        lon, lat = np.meshgrid(lon, lat)
    return lat, lon


def find_nearest_cell(
    lat2d: np.ndarray,
    lon2d: np.ndarray,
    target_lat: float,
    target_lon: float,
) -> tuple[int, int]:
    """Return (rlat_idx, rlon_idx) of the grid cell nearest to (target_lat, target_lon)."""
    dist2 = (lat2d - target_lat) ** 2 + (lon2d - target_lon) ** 2
    flat_idx = int(np.argmin(dist2))
    rlat_idx, rlon_idx = np.unravel_index(flat_idx, lat2d.shape)
    return int(rlat_idx), int(rlon_idx)


def extract_variable_timeseries(
    files: list[FileInfo],
    variable: str,
    rlat_idx: int,
    rlon_idx: int,
) -> pd.Series:
    """Load all temporal chunks for one variable, concat, and extract the point."""
    var_files = sorted(
        (fi for fi in files if fi.variable == variable),
        key=lambda fi: fi.start,
    )
    arrays: list[xr.DataArray] = []
    lat_dim: str | None = None
    lon_dim: str | None = None
    for fi in var_files:
        ds = xr.open_dataset(fi.path, engine="netcdf4")
        if lat_dim is None:
            spatial = [d for d in ds[variable].dims if d != "time"]
            lat_dim, lon_dim = spatial[0], spatial[1]
        da = ds[variable].isel({lat_dim: rlat_idx, lon_dim: rlon_idx})
        arrays.append(da.load())
        ds.close()

    combined = xr.concat(arrays, dim="time")
    # Convert non-standard calendars (e.g. 365day in HadGEM2-ES) using xarray's
    # convert_calendar to standard gregorian calendar, 29th of February is dropped.
    combined = combined.convert_calendar("standard", use_cftime=False)  # TODO check
    series = combined.to_series()
    series.index = pd.DatetimeIndex(series.index).normalize()  # TODO check normalize
    series.name = variable
    return series


def extract_group(
    group_files: list[FileInfo],
    target_lat: float,
    target_lon: float,
) -> pd.DataFrame:
    """Extract all 5 variables for one model/scenario group into a DataFrame."""
    sample_ds = xr.open_dataset(group_files[0].path, engine="netcdf4")
    lat2d, lon2d = _lat_lon_arrays(sample_ds)
    sample_ds.close()

    rlat_idx, rlon_idx = find_nearest_cell(lat2d, lon2d, target_lat, target_lon)
    actual_lat = float(lat2d[rlat_idx, rlon_idx])
    actual_lon = float(lon2d[rlat_idx, rlon_idx])
    print(
        f"Nearest cell: lat={actual_lat:.4f}, lon={actual_lon:.4f} "
        f"(target: {target_lat:.4f}, {target_lon:.4f})"
    )

    series_list: list[pd.Series] = []
    for var in VARIABLES:
        if any(fi.variable == var for fi in group_files):
            series_list.append(extract_variable_timeseries(group_files, var, rlat_idx, rlon_idx))

    return pd.concat(series_list, axis=1)


def build_model_mapping(groups: dict[GroupKey, list[FileInfo]]) -> dict[str, tuple[str, str]]:
    """Map short model names to (gcm, rcm) pairs.

    ARSO observations → "obs". RCM models → "model1", "model2", … sorted
    alphabetically by (gcm, rcm) so the numbering is stable across runs.

    Returns {"obs": ("ARSO", ""), "model1": ("CNRM-...", "CLMcom-..."), ...}
    """
    unique_models = sorted(set((gcm, rcm) for gcm, rcm, _ in groups if gcm != "ARSO"))
    mapping: dict[str, tuple[str, str]] = {"obs": ("ARSO", "")}
    for i, (gcm, rcm) in enumerate(unique_models):
        mapping[f"model{i + 1}"] = (gcm, rcm)
    return mapping


def make_output_filename(location: str, model_name: str, scenario: str) -> str:
    """Build the CSV output filename for a location/model/scenario combination."""
    if model_name == "obs":
        return f"{location}_obs_hist.csv"
    return f"{location}_{model_name}_{scenario}.csv"


def extract_all_timeseries(target_lat: float, target_lon: float, location_name: str) -> None:
    """Extract point timeseries for every model/scenario and save to CSV.

    Parameters
    ----------
    target_lat, target_lon:
        Geographic coordinates of the target point.
    location_name:
        Short label used as the filename prefix (e.g. "ljubljana").
    """
    files = discover_files(config.EXTERNAL_CLIMATE_DIR)
    groups = group_files(files)
    model_mapping = build_model_mapping(groups)

    # Save the name → GCM/RCM lookup table
    mapping_df = pd.DataFrame(
        [
            {"short_name": name, "gcm": gcm, "rcm": rcm}
            for name, (gcm, rcm) in model_mapping.items()
        ]
    )
    mapping_df.to_csv(config.INTERIM_CLIMATE_DIR / "model_mapping.csv", index=False)

    reverse: dict[tuple[str, str], str] = {
        (gcm, rcm): name for name, (gcm, rcm) in model_mapping.items()
    }

    for (gcm, rcm, scenario), gfiles in tqdm(
        groups.items(), desc="Extracting timeseries", file=sys.stdout
    ):
        model_name = reverse[(gcm, rcm)]
        print(f"Processing {model_name} ({gcm} / {rcm or 'obs'}) / {scenario}")
        df = extract_group(gfiles, target_lat, target_lon)
        if (
            model_name == "model4" and scenario == "rcp45"
        ):  # in this case, the date for 2099-12-25 is not calculated correctly, so we set it manually
            positions = [i for i, d in enumerate(df.index) if d == pd.Timestamp("2099-12-26")]
            if len(positions) == 2:
                new_index = df.index.tolist()
                new_index[positions[0]] = pd.Timestamp("2099-12-25")
                df.index = pd.DatetimeIndex(new_index, name=df.index.name)
        out_path = config.INTERIM_CLIMATE_DIR / make_output_filename(
            location_name, model_name, scenario
        )
        df.to_csv(out_path)


def prepare_climate_data(location: str) -> None:
    combinations = get_model_scenario_combinations(location)

    for model, scenario in combinations:
        print(f"Preparing climate data for {location} with {model} and {scenario}")

        path = config.INTERIM_CLIMATE_DIR / f"{location}_{model}_{scenario}.csv"
        df = pd.read_csv(path, index_col="time", parse_dates=True)
        # Fill missing calendar days (e.g. Feb 29 absent in 365-day calendar models)
        full_range = pd.date_range(df.index.min(), df.index.max(), freq="D")
        df = df.reindex(full_range).ffill()
        temperatures = list(zip(df["tasmin"] - 273.15, df["tasmax"] - 273.15))
        eto_values = (df["evspsblpot"] * 86400).tolist()
        rainfall_values = (df["pr"] * 86400).tolist()
        pickle_tuple = (temperatures, eto_values, rainfall_values)

        out_path = config.PROCESSED_CLIMATE_DIR / f"{location}_{model}_{scenario}.pkl"
        pd.to_pickle(pickle_tuple, out_path)
        print(f"Saved {out_path.name}")
