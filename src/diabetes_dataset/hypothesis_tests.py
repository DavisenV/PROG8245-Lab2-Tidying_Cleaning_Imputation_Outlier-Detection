"""Inferential statistics: normality checks and two-group comparisons."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from scipy import stats

from .config import ALPHA, GROUP_COLOURS, TARGET
from .eda import apply_plot_style, label_for


class NormalityChecker:
    """Check whether each group's values look normally distributed.

    The independent-samples t-test assumes that each group comes from a
    roughly normal distribution, so we check that FIRST with:

    * a **Q-Q plot** (visual check), and
    * the **Shapiro-Wilk test** (formal check).
    """

    def __init__(self, df: pd.DataFrame, group_col: str = TARGET,
                 groups: tuple[str, str] = ("No", "Yes"), alpha: float = ALPHA) -> None:
        self.df = df
        self.group_col = group_col
        self.groups = groups
        self.alpha = alpha
        apply_plot_style()

    def _values(self, feature: str, group: str) -> pd.Series:
        return self.df.loc[self.df[self.group_col] == group, feature].dropna()

    def shapiro_wilk(self, features: list[str]) -> pd.DataFrame:
        """Shapiro-Wilk test for every feature in every group.

        H0: the data come from a normal distribution.
        p < alpha  -> reject H0 -> the data are NOT normal.
        """
        rows = []
        for feature in features:
            for group in self.groups:
                values = self._values(feature, group)
                w_stat, p_value = stats.shapiro(values)
                rows.append(
                    {
                        "feature": feature,
                        "group": group,
                        "n": len(values),
                        "skewness": round(values.skew(), 3),
                        "W": round(w_stat, 4),
                        "p_value": p_value,
                        "is_normal": p_value >= self.alpha,
                    }
                )
        return pd.DataFrame(rows)

    def plot_qq(self, features: list[str]) -> Figure:
        """Q-Q plot for each feature (rows) and each group (columns).

        If the data are normal the dots fall on the grey straight line.
        Curves away from the line at the ends mean skew or heavy tails.
        """
        fig, axes = plt.subplots(len(features), len(self.groups),
                                 figsize=(5 * len(self.groups), 3.6 * len(features)),
                                 squeeze=False)
        for r, feature in enumerate(features):
            for c, group in enumerate(self.groups):
                ax = axes[r, c]
                (osm, osr), (slope, intercept, _) = stats.probplot(
                    self._values(feature, group), dist="norm"
                )
                ax.scatter(osm, osr, s=10, color=GROUP_COLOURS.get(group, "#2a78d6"),
                           alpha=0.6, edgecolor="none", label="Observed data")
                ax.plot(osm, slope * osm + intercept, color="#52514e", linewidth=2,
                        label="Perfectly normal")
                ax.set(title=f"{label_for(feature)} - Diabetic = {group}",
                       xlabel="Theoretical quantiles (normal)",
                       ylabel=f"Observed quantiles\n{label_for(feature)}")
                ax.legend(loc="upper left", fontsize=8, frameon=False)
        fig.suptitle("Q-Q plots: normality check before the t-tests",
                     fontweight="bold", y=1.0)
        fig.tight_layout()
        return fig


class GroupComparison:
    """Compare a numeric feature between two independent groups.

    For each feature it runs:

    1. **Levene's test** - are the two groups' variances equal?
    2. **Welch's t-test** - are the two group means different?
       (Welch's version does not assume equal variances or equal group sizes,
       which suits our data: ~4,900 non-diabetic vs ~340 diabetic patients.)
    3. **Mann-Whitney U** - a non-parametric back-up that compares the groups
       without assuming normality.
    4. **Cohen's d** - effect size: *how big* the difference is, not just
       whether it exists.
    """

    def __init__(self, df: pd.DataFrame, group_col: str = TARGET,
                 group_a: str = "Yes", group_b: str = "No", alpha: float = ALPHA) -> None:
        self.df = df
        self.group_col = group_col
        self.group_a = group_a
        self.group_b = group_b
        self.alpha = alpha

    def _split(self, feature: str) -> tuple[pd.Series, pd.Series]:
        a = self.df.loc[self.df[self.group_col] == self.group_a, feature].dropna()
        b = self.df.loc[self.df[self.group_col] == self.group_b, feature].dropna()
        return a, b

    @staticmethod
    def cohens_d(a: pd.Series, b: pd.Series) -> float:
        """Difference in means divided by the pooled standard deviation.

        Rough guide: 0.2 = small, 0.5 = medium, 0.8 = large.
        """
        n_a, n_b = len(a), len(b)
        pooled_sd = np.sqrt(((n_a - 1) * a.var() + (n_b - 1) * b.var()) / (n_a + n_b - 2))
        return (a.mean() - b.mean()) / pooled_sd

    @staticmethod
    def effect_label(d: float) -> str:
        d = abs(d)
        if d < 0.2:
            return "negligible"
        if d < 0.5:
            return "small"
        if d < 0.8:
            return "medium"
        return "large"

    def compare(self, feature: str) -> dict:
        a, b = self._split(feature)
        levene_p = stats.levene(a, b).pvalue
        welch = stats.ttest_ind(a, b, equal_var=False)
        mwu = stats.mannwhitneyu(a, b, alternative="two-sided")
        d = self.cohens_d(a, b)
        return {
            "feature": feature,
            f"mean_{self.group_a}": round(a.mean(), 2),
            f"mean_{self.group_b}": round(b.mean(), 2),
            "mean_diff": round(a.mean() - b.mean(), 2),
            "levene_p": levene_p,
            "welch_t": round(welch.statistic, 3),
            "welch_df": round(welch.df, 1),
            "welch_p": welch.pvalue,
            "mannwhitney_p": mwu.pvalue,
            "cohens_d": round(d, 3),
            "effect_size": self.effect_label(d),
            "significant": welch.pvalue < self.alpha,
        }

    def compare_all(self, features: list[str]) -> pd.DataFrame:
        return pd.DataFrame([self.compare(f) for f in features]).set_index("feature")


def format_p_values(table: pd.DataFrame) -> pd.DataFrame:
    """Copy of ``table`` with p-value columns shown in scientific notation.

    Very small p-values (e.g. 1e-29) otherwise display as 0.0, which wrongly
    suggests a probability of exactly zero.
    """
    formatted = table.copy()
    for col in formatted.columns:
        name = col.split(" ")[0]          # e.g. "welch_p (treated)" -> "welch_p"
        if "p_value" in name or name.endswith("_p"):
            formatted[col] = formatted[col].map(lambda p: f"{p:.2e}")
    return formatted
