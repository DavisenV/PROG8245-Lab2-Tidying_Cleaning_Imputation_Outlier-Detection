"""Load the Billboard chart and audio data, from Neon or from the local CSV files."""

import numpy as np
import pandas as pd

from .config import AUDIO_CSV_PATH, AUDIO_TABLE_NAME, CHART_CSV_PATH, CHART_TABLE_NAME


def restore_explicit(series):
    """Return spotify_track_explicit as True/False/NaN, exactly as pandas reads it from the CSV.

    Databases store this column as a number (SQLite: 1/0) or a boolean with NULLs
    (PostgreSQL), so it needs converting back after a round trip.
    """
    return series.map(lambda value: np.nan if pd.isna(value) else bool(value)).astype(object)


def read_billboard_csv():
    """Read (chart, audio) from the local CSV files in data/."""
    return pd.read_csv(CHART_CSV_PATH), pd.read_csv(AUDIO_CSV_PATH)


def read_billboard_neon(db):
    """Read (chart, audio) from Neon in their original row order."""
    chart = db.read_ordered(CHART_TABLE_NAME)
    audio = db.read_ordered(AUDIO_TABLE_NAME)
    audio["spotify_track_explicit"] = restore_explicit(audio["spotify_track_explicit"])
    return chart, audio
