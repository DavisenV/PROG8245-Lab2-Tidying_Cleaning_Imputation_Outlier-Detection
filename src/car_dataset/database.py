"""Store and fetch the raw car data in Neon, keeping the original row order.

SQL tables have no guaranteed row order, so a plain ``SELECT *`` may return rows
shuffled. The notebook's head()/tail(), duplicate handling and train/test split
all depend on row order, so we upload a ``row_id`` column and sort by it on the
way back.

``db`` is a ``NeonDatabase`` from ``src/common/database.py``.
"""

from .config import RAW_TABLE_NAME

ROW_ID = "row_id"


def upload_cars(db, df, table_name=RAW_TABLE_NAME):
    """Upload df with a row_id column and return the number of rows stored."""
    return db.upload_dataframe(df.rename_axis(ROW_ID).reset_index(), table_name)


def read_cars(db, table_name=RAW_TABLE_NAME):
    """Read the table back in its original row order, without the helper row_id column."""
    df = db.read_query(f'SELECT * FROM "{table_name}" ORDER BY "{ROW_ID}"')
    return df.drop(columns=ROW_ID)
