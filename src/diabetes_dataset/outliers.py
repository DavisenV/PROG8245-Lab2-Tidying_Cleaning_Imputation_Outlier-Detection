"""Outlier detection with box plots, scatter plots, Z-scores and the IQR rule."""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cbook
from matplotlib.figure import Figure

from .config import (
    GROUP_COLOURS,
    IQR_MULTIPLIER,
    NEUTRAL_COLOUR,
    OUTLIER_COLOUR,
    TARGET,
    Z_THRESHOLD,
)
from .eda import apply_plot_style, label_for


class OutlierDetector:
    """Find potential outliers in a set of numeric features.

    The detector never changes the DataFrame it is given. Methods return
    boolean "masks" (``True`` = potential outlier) that you can count, plot,
    or use to build a cleaned *copy* of the data.
    """

    def __init__(self, df: pd.DataFrame, features: list[str],
                 z_threshold: float = Z_THRESHOLD,
                 iqr_multiplier: float = IQR_MULTIPLIER) -> None:
        self.df = df
        self.features = features
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier
        apply_plot_style()

    # ------------------------------------------------------------------ #
    # Z-score method
    # ------------------------------------------------------------------ #
    def z_scores(self) -> pd.DataFrame:
        """z = (x - mean) / standard deviation, for every feature."""
        data = self.df[self.features]
        return (data - data.mean()) / data.std(ddof=0)

    def z_score_outliers(self) -> pd.DataFrame:
        """``True`` where |z| > threshold (default 3)."""
        return self.z_scores().abs() > self.z_threshold

    # ------------------------------------------------------------------ #
    # IQR method
    # ------------------------------------------------------------------ #
    def iqr_bounds(self) -> pd.DataFrame:
        """Q1, Q3, IQR and the lower/upper fences for every feature."""
        data = self.df[self.features]
        q1, q3 = data.quantile(0.25), data.quantile(0.75)
        iqr = q3 - q1
        return pd.DataFrame(
            {
                "Q1": q1,
                "Q3": q3,
                "IQR": iqr,
                "lower_bound": q1 - self.iqr_multiplier * iqr,
                "upper_bound": q3 + self.iqr_multiplier * iqr,
                "min": data.min(),
                "max": data.max(),
            }
        )

    def iqr_outliers(self) -> pd.DataFrame:
        """``True`` where a value is below the lower or above the upper fence."""
        bounds = self.iqr_bounds()
        data = self.df[self.features]
        return (data < bounds["lower_bound"]) | (data > bounds["upper_bound"])

    # ------------------------------------------------------------------ #
    # Box-plot method
    # ------------------------------------------------------------------ #
    def boxplot_flier_counts(self) -> pd.Series:
        """Number of points matplotlib draws beyond the whiskers ("fliers")."""
        counts = {
            f: len(cbook.boxplot_stats(self.df[f].dropna(), whis=self.iqr_multiplier)[0]["fliers"])
            for f in self.features
        }
        return pd.Series(counts, name="box_plot")

    # ------------------------------------------------------------------ #
    # Summaries
    # ------------------------------------------------------------------ #
    def summary(self) -> pd.DataFrame:
        """Outlier counts per feature for every method, side by side."""
        z_mask, iqr_mask = self.z_score_outliers(), self.iqr_outliers()
        table = pd.DataFrame(
            {
                "box_plot": self.boxplot_flier_counts(),
                "z_score": z_mask.sum(),
                "iqr_rule": iqr_mask.sum(),
                "flagged_by_both": (z_mask & iqr_mask).sum(),
                "skewness": self.df[self.features].skew().round(2),
            }
        )
        table["iqr_%"] = (table["iqr_rule"] / len(self.df) * 100).round(2)
        return table

    def outliers_by_group(self, mask: pd.DataFrame, group_col: str = TARGET) -> pd.DataFrame:
        """How many of the flagged values belong to each group (e.g. diabetic)."""
        return mask.groupby(self.df[group_col]).sum().T

    # ------------------------------------------------------------------ #
    # Treatment
    # ------------------------------------------------------------------ #
    def remove(self, method: str = "z_score",
               features: list[str] | None = None) -> pd.DataFrame:
        """Return a COPY of the data without rows flagged in ``features``."""
        masks = {"z_score": self.z_score_outliers, "iqr": self.iqr_outliers}
        if method not in masks:
            raise ValueError(f"method must be one of {list(masks)}")
        features = features or self.features
        row_is_outlier = masks[method]()[features].any(axis=1)
        return self.df.loc[~row_is_outlier].copy()

    @staticmethod
    def compare_statistics(before: pd.DataFrame, after: pd.DataFrame,
                           features: list[str]) -> pd.DataFrame:
        """Rows, mean, median and standard deviation before vs. after treatment."""
        stats = {}
        for label, data in (("before", before), ("after", after)):
            stats[label] = data[features].agg(["count", "mean", "median", "std"]).T
        table = pd.concat(stats, axis=1).swaplevel(axis=1).sort_index(axis=1, level=0)
        for stat in ("mean", "std"):
            table[(stat, "change_%")] = (
                (table[(stat, "after")] - table[(stat, "before")])
                / table[(stat, "before")] * 100
            )
        return table.round(2).sort_index(axis=1, level=0)

    # ------------------------------------------------------------------ #
    # Plots
    # ------------------------------------------------------------------ #
    def plot_boxplots(self, features: list[str] | None = None, ncols: int = 4,
                      title: str = "Box plots: points beyond the whiskers are potential outliers"
                      ) -> Figure:
        features = features or self.features
        nrows = math.ceil(len(features) / ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3.6 * nrows), squeeze=False)
        axes = list(axes.flat)
        flier_style = {"marker": "o", "markersize": 4, "markerfacecolor": OUTLIER_COLOUR,
                       "markeredgecolor": "white", "markeredgewidth": 0.5, "alpha": 0.7}
        for ax, col in zip(axes, features):
            ax.boxplot(self.df[col].dropna(), whis=self.iqr_multiplier, widths=0.5,
                       patch_artist=True, flierprops=flier_style,
                       boxprops={"facecolor": "#cde2fb", "edgecolor": "#2a78d6"},
                       medianprops={"color": "#0d366b", "linewidth": 2},
                       whiskerprops={"color": "#2a78d6"}, capprops={"color": "#2a78d6"})
            ax.set(title=label_for(col), ylabel=label_for(col), xticks=[])
        for ax in axes[len(features):]:
            ax.set_visible(False)
        fig.suptitle(title, fontweight="bold", y=1.0)
        fig.tight_layout()
        return fig

    def plot_scatter(self, x: str, y: str, mask: pd.DataFrame | None = None,
                     title: str | None = None) -> Figure:
        """Scatter plot coloured by diabetic status; flagged points ringed in red.

        ``mask`` is an outlier mask (e.g. from :meth:`iqr_outliers`). A point is
        highlighted when it is flagged on ``x`` OR ``y``.
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        for group, colour in GROUP_COLOURS.items():
            subset = self.df[self.df[TARGET] == group]
            ax.scatter(subset[x], subset[y], s=12, alpha=0.45, color=colour,
                       edgecolor="none", label=f"Diabetic = {group}")
        if mask is not None:
            flagged = mask[[c for c in (x, y) if c in mask.columns]].any(axis=1)
            ax.scatter(self.df.loc[flagged, x], self.df.loc[flagged, y], s=40,
                       facecolor="none", edgecolor=OUTLIER_COLOUR, linewidth=1.2,
                       label=f"Flagged outlier (n={int(flagged.sum())})")
        ax.set(title=title or f"{label_for(y)} vs {label_for(x)}",
               xlabel=label_for(x), ylabel=label_for(y))
        ax.legend(frameon=False)
        fig.tight_layout()
        return fig

    def plot_before_after(self, cleaned: pd.DataFrame, feature: str) -> Figure:
        """Histogram of one feature before and after outlier treatment."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharex=True)
        for ax, data, label, colour in (
            (axes[0], self.df, "Before", NEUTRAL_COLOUR),
            (axes[1], cleaned, "After", "#2a78d6"),
        ):
            ax.hist(data[feature], bins=40, color=colour, edgecolor="white")
            ax.axvline(data[feature].mean(), color=OUTLIER_COLOUR, linewidth=2,
                       label=f"Mean = {data[feature].mean():.2f}")
            ax.axvline(data[feature].median(), color="#0d366b", linewidth=2, linestyle="--",
                       label=f"Median = {data[feature].median():.2f}")
            ax.set(title=f"{label} treatment (n={len(data):,})",
                   xlabel=label_for(feature), ylabel="Count")
            ax.legend(frameon=False)
        fig.suptitle(f"{label_for(feature)}: before vs. after outlier treatment",
                     fontweight="bold", y=1.02)
        fig.tight_layout()
        return fig
