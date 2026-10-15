"""Reusable classes for the diabetes analysis in ``notebooks/diabetes.ipynb``."""

from common.database import NeonDatabase  # shared with Section 3; re-exported so existing imports keep working
from .eda import EDAVisualizer, apply_plot_style, label_for
from .hypothesis_tests import GroupComparison, NormalityChecker, format_p_values
from .outliers import OutlierDetector
from .preprocessing import DiabetesDataPreparer

__all__ = [
    "NeonDatabase",
    "DiabetesDataPreparer",
    "EDAVisualizer",
    "NormalityChecker",
    "GroupComparison",
    "OutlierDetector",
    "format_p_values",
    "apply_plot_style",
    "label_for",
]
