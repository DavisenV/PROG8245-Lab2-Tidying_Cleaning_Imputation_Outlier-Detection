"""Store and fetch the raw car data in Neon, keeping the original row order.

The notebook's head()/tail(), duplicate handling and train/test split all depend
on row order, so these use ``NeonDatabase.upload_ordered`` / ``read_ordered``
(``src/common/database.py``), which store a ``row_id`` and sort by it.
"""

from .config import RAW_TABLE_NAME


def upload_cars(db, df, table_name=RAW_TABLE_NAME):
    """Upload df with a row_id column and return the number of rows stored."""
    return db.upload_ordered(df, table_name)


def read_cars(db, table_name=RAW_TABLE_NAME):
    """Read the table back in its original row order, without the helper row_id column."""
    return db.read_ordered(table_name)
