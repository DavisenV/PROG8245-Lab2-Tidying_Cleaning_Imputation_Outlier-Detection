"""Exploratory data analysis (EDA) plots for the diabetes dataset."""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure

from .config import GROUP_COLOURS, TARGET, TARGET_FLAG, TEXT_SECONDARY

# Diverging map for correlations: orange (negative) -> light grey (0) -> blue (positive)
CORRELATION_CMAP = LinearSegmentedColormap.from_list(
    "orange_grey_blue", ["#eb6834", "#f0efec", "#2a78d6"]
)

LABELS = {
    "age": "Age (years)",
    "pulse_rate": "Pulse rate (beats/min)",
    "systolic_bp": "Systolic BP (mmHg)",
    "diastolic_bp": "Diastolic BP (mmHg)",
    "glucose": "Glucose (mmol/L)",
    "height": "Height (m)",
    "weight": "Weight (kg)",
    "bmi": "BMI (kg/m²)",
    "pulse_pressure": "Pulse pressure (mmHg)",
}


def label_for(column: str) -> str:
    """Human-friendly axis label for a column (falls back to the column name)."""
    return LABELS.get(column, column.replace("_", " ").title())


def apply_plot_style() -> None:
    """A light, uncluttered style used by every chart in the project."""
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "axes.edgecolor": "#d6d5cf",
            "grid.color": "#ecebe7",
            "axes.titleweight": "bold",
            "axes.labelcolor": TEXT_SECONDARY,
            "xtick.color": TEXT_SECONDARY,
            "ytick.color": TEXT_SECONDARY,
            "figure.dpi": 100,
        }
    )


class EDAVisualizer:
    """General-purpose EDA plots, each returning its matplotlib ``Figure``."""

    def __init__(self, df: pd.DataFrame, target: str = TARGET) -> None:
        self.df = df
        self.target = target
        self.palette = GROUP_COLOURS
        apply_plot_style()

    # ------------------------------------------------------------------ #
    def plot_target_balance(self) -> Figure:
        """Bar chart of how many patients are diabetic vs. not."""
        counts = self.df[self.target].value_counts().reindex(["No", "Yes"])
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(counts.index, counts.values,
                      color=[self.palette[k] for k in counts.index], width=0.55)
        for bar, n in zip(bars, counts.values):
            pct = n / counts.sum() * 100
            ax.annotate(f"{n:,} ({pct:.1f}%)", (bar.get_x() + bar.get_width() / 2, n),
                        ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")
        ax.set(title="How many patients are diabetic?", xlabel="Diabetic",
               ylabel="Number of patients")
        ax.margins(y=0.12)
        fig.tight_layout()
        return fig

    def plot_distributions(self, features: list[str], ncols: int = 3) -> Figure:
        """Histogram + smooth density curve for each numeric feature."""
        fig, axes = self._grid(len(features), ncols, height=3)
        for ax, col in zip(axes, features):
            sns.histplot(self.df[col], kde=True, ax=ax, color="#2a78d6",
                         edgecolor="white", linewidth=0.5)
            skew = self.df[col].skew()
            ax.set(title=f"{label_for(col)}  (skew = {skew:.2f})",
                   xlabel=label_for(col), ylabel="Count")
        fig.suptitle("Distribution of each numeric feature", fontweight="bold", y=1.0)
        fig.tight_layout()
        return fig

    def plot_by_target(self, features: list[str], ncols: int = 3) -> Figure:
        """Box plot of each feature split by diabetic status."""
        fig, axes = self._grid(len(features), ncols, height=3.4)
        for ax, col in zip(axes, features):
            sns.boxplot(data=self.df, x=self.target, y=col, hue=self.target,
                        order=["No", "Yes"], palette=self.palette, legend=False,
                        width=0.5, fliersize=2, ax=ax)
            ax.set(title=label_for(col), xlabel="Diabetic", ylabel=label_for(col))
        fig.suptitle("Do diabetic and non-diabetic patients differ?",
                     fontweight="bold", y=1.0)
        fig.tight_layout()
        return fig

    def plot_correlation_heatmap(self, features: list[str]) -> Figure:
        """Pearson correlation between every pair of numeric features."""
        corr = self.df[features].corr()
        fig, ax = plt.subplots(figsize=(9, 7))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap=CORRELATION_CMAP, vmin=-1, vmax=1,
                    square=True, linewidths=2, linecolor="white",
                    cbar_kws={"label": "Pearson correlation (r)"}, ax=ax)
        ax.set(title="Correlation between numeric features", xlabel="Feature", ylabel="Feature")
        fig.tight_layout()
        return fig

    def plot_rate_by_category(self, category: str) -> Figure:
        """Percentage of patients who are diabetic within each category."""
        rate = (
            self.df.groupby(category, observed=True)[TARGET_FLAG]
            .agg(["mean", "size"])
            .rename(columns={"mean": "rate", "size": "n"})
        )
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(rate.index.astype(str), rate["rate"] * 100, color="#eb6834", width=0.6)
        for bar, (pct, n) in zip(bars, zip(rate["rate"] * 100, rate["n"])):
            ax.annotate(f"{pct:.1f}%\n(n={n:,})", (bar.get_x() + bar.get_width() / 2, pct),
                        ha="center", va="bottom", xytext=(0, 3), textcoords="offset points",
                        fontsize=9)
        ax.set(title=f"Share of patients who are diabetic, by {label_for(category).lower()}",
               xlabel=label_for(category), ylabel="Diabetic (%)")
        ax.margins(y=0.2)
        fig.tight_layout()
        return fig

    def group_summary(self, features: list[str]) -> pd.DataFrame:
        """Mean, median and standard deviation of each feature per group."""
        return (
            self.df.groupby(self.target)[features]
            .agg(["mean", "median", "std"])
            .round(2)
            .T
        )

    # ------------------------------------------------------------------ #
    @staticmethod
    def _grid(n_plots: int, ncols: int, height: float):
        nrows = math.ceil(n_plots / ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(4.6 * ncols, height * nrows),
                                 squeeze=False)
        axes = list(axes.flat)
        for ax in axes[n_plots:]:
            ax.set_visible(False)   # hide unused panels in the grid
        return fig, axes[:n_plots]
