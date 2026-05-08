from pathlib import Path

ROOT_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = ROOT_DIR / "data"
RAW_CLIMATE_DIR: Path = DATA_DIR / "external" / "climate"
INTERIM_CLIMATE_DIR: Path = DATA_DIR / "interim" / "climate"
RAW_YIELD_DIR: Path = DATA_DIR / "raw" / "yield"
INTERIM_YIELD_DIR: Path = DATA_DIR / "interim" / "yield"
CO2_DIR: Path = DATA_DIR / "external" / "co2"