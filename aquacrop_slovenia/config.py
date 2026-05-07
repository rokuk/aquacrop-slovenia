from pathlib import Path

ROOT_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = ROOT_DIR / "data"
CLIMATE_DIR: Path = DATA_DIR / "external" / "climate"
INTERIM_CLIMATE_DIR: Path = DATA_DIR / "interim" / "climate"
