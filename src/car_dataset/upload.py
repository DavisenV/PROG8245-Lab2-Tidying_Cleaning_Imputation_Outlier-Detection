"""One-time upload of the car details CSV to Neon.

The notebook only reads from Neon, so it works with a read-only login. Run this
from the project root whenever the CSV changes:

    PYTHONPATH=src python -m car_dataset.upload

Re-running replaces the table, so it never creates duplicate rows.
"""

import pandas as pd

from common.database import NeonDatabase

from .config import RAW_TABLE_NAME
from .database import read_cars, upload_cars
from .preparation import load_car_data


def main():
    db = NeonDatabase.from_env()
    try:
        df = load_car_data()
        rows = upload_cars(db, df)
        print(f"Uploaded {rows:,} rows to table '{RAW_TABLE_NAME}'")
        pd.testing.assert_frame_equal(read_cars(db), df)
        print("Verified: the Neon table matches the CSV exactly.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
