"""Cleaning, validation, and feature engineering for the diabetes dataset."""

from __future__ import annotations

import pandas as pd

from .config import (
    BINARY_FEATURES,
    NUMERIC_FEATURES,
    PLAUSIBLE_RANGES,
    TARGET,
    TARGET_FLAG,
)


class DiabetesDataPreparer:
    """Turn the raw diabetes table into an analysis-ready DataFrame.

    Each step is its own method so it can be run (and explained) one at a time
    in the notebook, or all together with :meth:`run`. Every step records what
    it did in ``self.log`` so the whole pipeline is auditable.

    The raw DataFrame passed in is never modified - we always work on a copy.
    """

    def __init__(self, raw_df: pd.DataFrame) -> None:
        self.raw_df = raw_df
        self.df = raw_df.copy()
        self.log: list[dict] = []

    # ------------------------------------------------------------------ #
    # Inspection
    # ------------------------------------------------------------------ #
    def quality_report(self) -> pd.DataFrame:
        """One row per column: type, missing values, unique values, zeros."""
        df = self.df
        return pd.DataFrame(
            {
                "dtype": df.dtypes.astype(str),
                "missing": df.isna().sum(),
                "missing_%": (df.isna().mean() * 100).round(2),
                "unique": df.nunique(),
                "zeros": (df == 0).sum(),
            }
        )

    # ------------------------------------------------------------------ #
    # Cleaning steps
    # ------------------------------------------------------------------ #
    def standardise_columns(self) -> "DiabetesDataPreparer":
        """Make column names lowercase snake_case with no stray spaces."""
        self.df.columns = (
            self.df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
        )
        self._record("standardise column names")
        return self

    def clean_categoricals(self) -> "DiabetesDataPreparer":
        """Tidy text values so 'female ', 'FEMALE' and 'Female' are one category."""
        self.df["gender"] = self.df["gender"].str.strip().str.title()
        self.df[TARGET] = self.df[TARGET].str.strip().str.title()
        self._record("clean text categories (gender, diabetic)")
        return self

    def enforce_dtypes(self) -> "DiabetesDataPreparer":
        """Make sure numeric columns are numbers and flags are small integers."""
        for col in NUMERIC_FEATURES:
            # errors="coerce" turns anything non-numeric into NaN instead of crashing
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
        for col in BINARY_FEATURES:
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce").astype("Int8")
        self.df["gender"] = self.df["gender"].astype("category")
        self._record("enforce data types")
        return self

    def remove_duplicates(self) -> "DiabetesDataPreparer":
        n_dupes = int(self.df.duplicated().sum())
        self.df = self.df.drop_duplicates().reset_index(drop=True)
        self._record(f"remove duplicate rows ({n_dupes} found)")
        return self

    def implausible_value_report(self) -> pd.DataFrame:
        """Count values outside the physiological limits in ``PLAUSIBLE_RANGES``."""
        rows = []
        for col, (low, high) in PLAUSIBLE_RANGES.items():
            series = self.df[col]
            rows.append(
                {
                    "feature": col,
                    "allowed_min": low,
                    "allowed_max": high,
                    "observed_min": series.min(),
                    "observed_max": series.max(),
                    "below_min": int((series < low).sum()),
                    "above_max": int((series > high).sum()),
                }
            )
        report = pd.DataFrame(rows).set_index("feature")
        report["total_invalid"] = report["below_min"] + report["above_max"]
        return report

    def invalid_row_mask(self) -> pd.Series:
        """``True`` for every row with at least one impossible measurement,
        or where systolic pressure is not greater than diastolic pressure."""
        mask = pd.Series(False, index=self.df.index)
        for col, (low, high) in PLAUSIBLE_RANGES.items():
            mask |= ~self.df[col].between(low, high)
        mask |= self.df["systolic_bp"] <= self.df["diastolic_bp"]
        return mask

    def remove_implausible_rows(self) -> "DiabetesDataPreparer":
        """Drop rows that contain physiologically impossible values."""
        mask = self.invalid_row_mask()
        self.df = self.df.loc[~mask].reset_index(drop=True)
        self._record(f"remove rows with impossible values ({int(mask.sum())} rows)")
        return self

    def drop_missing(self) -> "DiabetesDataPreparer":
        """Drop any rows that are still missing a value after cleaning."""
        n_missing_rows = int(self.df.isna().any(axis=1).sum())
        self.df = self.df.dropna().reset_index(drop=True)
        self._record(f"drop rows with missing values ({n_missing_rows} rows)")
        return self

    # ------------------------------------------------------------------ #
    # Feature engineering
    # ------------------------------------------------------------------ #
    def engineer_features(self) -> "DiabetesDataPreparer":
        """Add new, more interpretable columns derived from the raw ones."""
        df = self.df

        # 1/0 version of the target - handy for averages ("% diabetic") and ML.
        df[TARGET_FLAG] = (df[TARGET] == "Yes").astype("int8")

        # Recalculate BMI from height and weight so it is guaranteed consistent.
        df["bmi"] = (df["weight"] / df["height"] ** 2).round(2)

        # Pulse pressure = systolic - diastolic (a marker of arterial stiffness).
        df["pulse_pressure"] = df["systolic_bp"] - df["diastolic_bp"]

        # Age bands make trends easier to see than 60 separate ages.
        df["age_group"] = pd.cut(
            df["age"],
            bins=[17, 29, 39, 49, 59, 69, 120],
            labels=["18-29", "30-39", "40-49", "50-59", "60-69", "70+"],
        )

        # WHO adult BMI categories.
        df["bmi_category"] = pd.cut(
            df["bmi"],
            bins=[0, 18.5, 25, 30, float("inf")],
            labels=["Underweight", "Normal", "Overweight", "Obese"],
            right=False,
        )

        # Simplified ACC/AHA blood-pressure categories.
        df["bp_category"] = df.apply(self._bp_category, axis=1).astype(
            pd.CategoricalDtype(
                ["Normal", "Elevated", "Stage 1", "Stage 2"], ordered=True
            )
        )

        self._record("engineer features (diabetic_flag, bmi, pulse_pressure, age_group, bmi_category, bp_category)")
        return self

    @staticmethod
    def _bp_category(row: pd.Series) -> str:
        sys_bp, dia_bp = row["systolic_bp"], row["diastolic_bp"]
        if sys_bp >= 140 or dia_bp >= 90:
            return "Stage 2"
        if sys_bp >= 130 or dia_bp >= 80:
            return "Stage 1"
        if sys_bp >= 120:
            return "Elevated"
        return "Normal"

    # ------------------------------------------------------------------ #
    # Pipeline
    # ------------------------------------------------------------------ #
    def run(self) -> pd.DataFrame:
        """Run every step in order and return the cleaned DataFrame."""
        (
            self.standardise_columns()
            .clean_categoricals()
            .enforce_dtypes()
            .remove_duplicates()
            .remove_implausible_rows()
            .drop_missing()
            .engineer_features()
        )
        return self.df

    def summary(self) -> pd.DataFrame:
        """The pipeline log as a table: step, rows before, rows after."""
        return pd.DataFrame(self.log)

    def _record(self, step: str) -> None:
        rows_before = self.log[-1]["rows_after"] if self.log else len(self.raw_df)
        self.log.append(
            {
                "step": step,
                "rows_before": rows_before,
                "rows_after": len(self.df),
                "rows_removed": rows_before - len(self.df),
            }
        )
