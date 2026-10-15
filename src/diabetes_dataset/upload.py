"""One-time upload of the diabetes CSV to Neon.

The notebook only reads from Neon, so it works with a read-only login. Run this
from the project root whenever the CSV changes:

    PYTHONPATH=src python -m diabetes_dataset.upload

The table is stored with a ``row_id`` so the notebook can read the rows back in
their original order. Re-running replaces the table, so it never creates duplicate rows.
"""

import pandas as pd

from common.database import NeonDatabase

from .config import RAW_CSV_PATH, RAW_TABLE_NAME


def main():
    db = NeonDatabase.from_env()
    try:
        df = pd.read_csv(RAW_CSV_PATH)
        rows = db.upload_ordered(df, RAW_TABLE_NAME)
        print(f"Uploaded {rows:,} rows to table '{RAW_TABLE_NAME}'")
        pd.testing.assert_frame_equal(db.read_ordered(RAW_TABLE_NAME), df)
        print("Verified: the Neon table matches the CSV exactly.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
