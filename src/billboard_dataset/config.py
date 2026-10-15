"""Project-wide constants for the Billboard analysis (Section 2)."""

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths (local copies are optional and git-ignored; the data lives in Neon)
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CHART_CSV_PATH = DATA_DIR / "billboard_hot100.csv"
AUDIO_CSV_PATH = DATA_DIR / "billboard_audio_features.csv"

# --------------------------------------------------------------------------- #
# Source: TidyTuesday 2021-09-14 release
# --------------------------------------------------------------------------- #
SOURCE_BASE_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2021/2021-09-14"
CHART_SOURCE_URL = f"{SOURCE_BASE_URL}/billboard.csv"
AUDIO_SOURCE_URL = f"{SOURCE_BASE_URL}/audio_features.csv"

# --------------------------------------------------------------------------- #
# Database (the connection string itself lives in .env, shared with all sections)
# --------------------------------------------------------------------------- #
CHART_TABLE_NAME = "billboard_hot100_raw"
AUDIO_TABLE_NAME = "billboard_audio_features_raw"
