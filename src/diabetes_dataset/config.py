"""Project-wide constants for the diabetes analysis.

Keeping column names, thresholds, and colours in one place means every module
(and the notebook) uses the same values, and a change only has to be made once.
"""

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_CSV_PATH = DATA_DIR / "diabetes_dataset.csv"
ENV_PATH = PROJECT_ROOT / ".env"

# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #
ENV_VAR_NAME = "NEON_DATABASE_URL"
RAW_TABLE_NAME = "diabetes_raw"

# --------------------------------------------------------------------------- #
# Columns
# --------------------------------------------------------------------------- #
TARGET = "diabetic"          # "Yes" / "No"
TARGET_FLAG = "diabetic_flag"  # 1 / 0 version created during feature engineering

NUMERIC_FEATURES = [
    "age",
    "pulse_rate",
    "systolic_bp",
    "diastolic_bp",
    "glucose",
    "height",
    "weight",
    "bmi",
]

BINARY_FEATURES = [
    "family_diabetes",
    "hypertensive",
    "family_hypertension",
    "cardiovascular_disease",
    "stroke",
]

CATEGORICAL_FEATURES = ["gender", TARGET]

# The three measurements our research question is about.
ANALYSIS_FEATURES = ["glucose", "bmi", "systolic_bp"]

# --------------------------------------------------------------------------- #
# Physiological plausibility limits
# --------------------------------------------------------------------------- #
# Values outside these ranges cannot belong to a living adult patient, so they
# are treated as data-entry/measurement ERRORS (not as statistical outliers).
# Units: age in years, pulse in beats/min, blood pressure in mmHg,
# glucose in mmol/L, height in metres, weight in kg, BMI in kg/m^2.
PLAUSIBLE_RANGES = {
    "age": (18, 110),
    "pulse_rate": (30, 220),
    "systolic_bp": (60, 260),
    "diastolic_bp": (30, 160),
    "glucose": (2.0, 40.0),
    "height": (1.0, 2.3),
    "weight": (25.0, 300.0),
    "bmi": (10.0, 80.0),
}

# --------------------------------------------------------------------------- #
# Statistics / outliers
# --------------------------------------------------------------------------- #
ALPHA = 0.05            # significance level for every hypothesis test
Z_THRESHOLD = 3.0       # |z| > 3  -> potential outlier
IQR_MULTIPLIER = 1.5    # Q1 - 1.5*IQR, Q3 + 1.5*IQR
RANDOM_STATE = 42

# --------------------------------------------------------------------------- #
# Plot colours (colour-blind-safe, validated categorical pair)
# --------------------------------------------------------------------------- #
GROUP_COLOURS = {"No": "#2a78d6", "Yes": "#eb6834"}
NEUTRAL_COLOUR = "#9a9993"
OUTLIER_COLOUR = "#d03b3b"
TEXT_SECONDARY = "#52514e"
