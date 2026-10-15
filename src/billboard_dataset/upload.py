"""One-time upload of the Billboard CSV files to Neon.

The two files are large (about 46 MB and 10 MB), so they are not in Git and the
notebook does not upload them on every run. Instead, run this once from the
project root to download them (if they are not already in data/) and load them
into Neon:

    PYTHONPATH=src python -m billboard_dataset.upload

Re-running replaces the tables, so it never creates duplicate rows.
"""

from urllib.request import urlretrieve

import pandas as pd

from common.database import NeonDatabase

from .config import (
    AUDIO_CSV_PATH,
    AUDIO_SOURCE_URL,
    AUDIO_TABLE_NAME,
    CHART_CSV_PATH,
    CHART_SOURCE_URL,
    CHART_TABLE_NAME,
)
from .loading import read_billboard_csv, read_billboard_neon

FILES = [
    (CHART_CSV_PATH, CHART_SOURCE_URL, CHART_TABLE_NAME),
    (AUDIO_CSV_PATH, AUDIO_SOURCE_URL, AUDIO_TABLE_NAME),
]


def download_missing():
    """Download each source CSV into data/ unless it is already there."""
    for path, url, _ in FILES:
        if not path.exists():
            print(f"Downloading {url} -> {path}")
            path.parent.mkdir(exist_ok=True)
            urlretrieve(url, path)


def upload_billboard(db):
    """Upload both CSVs in their original row order, then check the Neon copies match."""
    for path, _, table in FILES:
        rows = db.upload_ordered(pd.read_csv(path), table)
        print(f"Uploaded {rows:,} rows to table '{table}'")

    for from_csv, from_db in zip(read_billboard_csv(), read_billboard_neon(db)):
        pd.testing.assert_frame_equal(from_db, from_csv)
    print("Verified: Neon tables match the CSV files exactly.")


def main():
    download_missing()
    db = NeonDatabase.from_env()
    try:
        upload_billboard(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
