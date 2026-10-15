"""Read the NPORS SPSS files and move them in and out of Neon.

Each year is stored as raw numeric answer codes (never labelled text), so the
notebook can tell a refusal coded 99 apart from a real answer. The SPSS value
labels travel with the data in one long table, so a Neon load does not need the
.sav files at all.
"""

import pandas as pd
import pyreadstat

from .config import EXPECTED_ROWS, sav_path


def read_npors_sav(year):
    """Read one year's SPSS file. Returns (codes DataFrame, {variable: {code: label}})."""
    frame, meta = pyreadstat.read_sav(str(sav_path(year)), apply_value_formats=False, user_missing=True)
    frame.columns = frame.columns.str.strip().str.upper()
    labels = {name.strip().upper(): codes for name, codes in meta.variable_value_labels.items()}
    return frame, labels


def validate_npors(frame, year):
    """Check a loaded year: unique columns, expected sample size, one row per respondent."""
    assert frame.columns.is_unique
    assert len(frame) == EXPECTED_ROWS[year], f"Unexpected sample size in {year}"
    assert frame["RESPID"].notna().all() and frame["RESPID"].is_unique


def labels_to_frame(labels_by_year):
    """Flatten {year: {variable: {code: label}}} into one long table for Neon."""
    rows = [
        {"survey_year": year, "variable": variable, "code": float(code), "label": label}
        for year, labels in labels_by_year.items()
        for variable, codes in labels.items()
        for code, label in codes.items()
    ]
    return pd.DataFrame(rows, columns=["survey_year", "variable", "code", "label"])


def labels_from_frame(df):
    """Rebuild {year: {variable: {code: label}}} from the long Neon table."""
    labels = {}
    for row in df.itertuples(index=False):
        labels.setdefault(int(row.survey_year), {}).setdefault(row.variable, {})[float(row.code)] = row.label
    return labels
