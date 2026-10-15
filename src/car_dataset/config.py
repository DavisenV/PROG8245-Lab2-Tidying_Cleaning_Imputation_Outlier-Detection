"""Project-wide constants for the car details analysis (Section 3)."""

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_CSV_PATH = DATA_DIR / "Car details v3.csv"

# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #
# The connection string itself lives in .env (NEON_DATABASE_URL), shared with Section 4.
RAW_TABLE_NAME = "car_details_raw"
