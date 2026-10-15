"""Reusable helpers for loading and preparing the CarDekho 'Car details v3' dataset."""

import pandas as pd

from .config import RAW_CSV_PATH


def load_car_data(path=RAW_CSV_PATH, na_values=None):
    """Read the raw car CSV. Extra strings in `na_values` are treated as missing."""
    return pd.read_csv(path, na_values=na_values)


def extract_number(series):
    """Pull the leading number out of text like '23.4 kmpl' or '1248 CC' as a float."""
    number_text = series.str.extract(r"(\d+\.?\d*)")[0]
    return pd.to_numeric(number_text, errors="coerce")


def missing_report(df):
    """Count and percentage of missing values per column, worst first."""
    counts = df.isna().sum()
    report = pd.DataFrame(
        {
            "missing": counts,
            "percent": (counts / len(df) * 100).round(2),
        }
    )
    return report.sort_values("missing", ascending=False)


def add_power_per_litre(df):
    """Return a copy of df with power_per_litre = max_power_bhp / engine size in litres."""
    df = df.copy()
    df["power_per_litre"] = df["max_power_bhp"] / (df["engine_cc"] / 1000)
    return df
