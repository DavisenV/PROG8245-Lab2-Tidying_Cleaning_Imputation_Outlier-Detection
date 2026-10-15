"""Project-wide constants for the Pew NPORS analysis (Section 1)."""

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"  # CSV reports written by the notebook

# --------------------------------------------------------------------------- #
# Surveys
# --------------------------------------------------------------------------- #
# Respondents in each public release; every load is checked against these.
EXPECTED_ROWS = {2023: 5733, 2024: 5626, 2025: 5022}
SURVEY_YEARS = list(EXPECTED_ROWS)

# --------------------------------------------------------------------------- #
# Database (the connection string itself lives in .env, shared with all sections)
# --------------------------------------------------------------------------- #
LABELS_TABLE_NAME = "npors_value_labels"


def short_year(year):
    return str(year)[-2:]


def sav_path(year):
    """Where the ARDA SPSS download for ``year`` must be saved, e.g. data/NPORS23.sav."""
    return DATA_DIR / f"NPORS{short_year(year)}.sav"


def raw_table_name(year):
    """Neon table holding that year's raw response codes, e.g. npors23_raw."""
    return f"npors{short_year(year)}_raw"


def source_url(year):
    return f"https://www.thearda.com/data-archive?fid=NPORS{short_year(year)}"


def codebook_url(year):
    return f"{source_url(year)}&tab=2"
