from pathlib import Path

ROOT_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = ROOT_DIR / "data"
EXTERNAL_DIR: Path = DATA_DIR / "external"
INTERIM_DIR: Path = DATA_DIR / "interim"
EXTERNAL_CLIMATE_DIR: Path = EXTERNAL_DIR / "climate"
INTERIM_CLIMATE_DIR: Path = INTERIM_DIR / "climate"
EXTERNAL_MAPDATA_DIR: Path = EXTERNAL_DIR / "mapdata"
INTERIM_MAPDATA_DIR: Path = INTERIM_DIR / "mapdata"