"""Read and write any section's data in the shared Neon (PostgreSQL) database."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from .config import ENV_PATH, ENV_VAR_NAME

PLACEHOLDER_MARKER = "<"  # the .env placeholder looks like "<your-connection-string>"
MAX_PARAMS_PER_INSERT = 30_000  # stays under both PostgreSQL's and SQLite's per-statement limits
ROW_ID = "row_id"  # helper column used by upload_ordered / read_ordered


class NeonDatabase:
    """A small wrapper around a SQLAlchemy engine connected to Neon.

    Neon is a hosted PostgreSQL service, so we talk to it with ordinary
    PostgreSQL tools: SQLAlchemy builds the connection and ``psycopg`` is the
    driver underneath.

    Example
    -------
    >>> db = NeonDatabase.from_env()
    >>> db.upload_dataframe(df, "diabetes_raw")
    >>> df = db.read_table("diabetes_raw")
    """

    def __init__(self, connection_url: str) -> None:
        self.connection_url = self._normalise_url(connection_url)
        self.engine: Engine = create_engine(self.connection_url, pool_pre_ping=True)

    # ------------------------------------------------------------------ #
    # Construction helpers
    # ------------------------------------------------------------------ #
    @classmethod
    def from_env(
        cls, env_path: Path = ENV_PATH, var_name: str = ENV_VAR_NAME
    ) -> "NeonDatabase":
        """Create a connection using the connection string stored in ``.env``."""
        url = cls.read_connection_string(env_path, var_name)
        if url is None:
            raise ValueError(
                f"{var_name} is missing or still a placeholder in {env_path}. "
                "Paste your Neon connection string into the .env file."
            )
        return cls(url)

    @staticmethod
    def read_connection_string(
        env_path: Path = ENV_PATH, var_name: str = ENV_VAR_NAME
    ) -> str | None:
        """Return the connection string, or ``None`` if it has not been set yet."""
        load_dotenv(env_path, override=True)
        url = os.getenv(var_name, "").strip()
        if not url or PLACEHOLDER_MARKER in url:
            return None
        return url

    @staticmethod
    def _normalise_url(url: str) -> str:
        """Tell SQLAlchemy to use the psycopg (v3) driver.

        Neon gives you ``postgresql://...`` (or ``postgres://...``). Without a
        driver name SQLAlchemy would look for the older ``psycopg2`` package,
        so we rewrite the prefix to ``postgresql+psycopg://``.
        """
        for prefix in ("postgresql://", "postgres://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url

    # ------------------------------------------------------------------ #
    # Operations
    # ------------------------------------------------------------------ #
    def test_connection(self) -> str:
        """Run a trivial query and return the server version string."""
        with self.engine.connect() as conn:
            if self.engine.dialect.name == "postgresql":
                return conn.execute(text("SELECT version()")).scalar_one()
            conn.execute(text("SELECT 1"))
            return self.engine.dialect.name

    def upload_dataframe(
        self, df: pd.DataFrame, table_name: str, if_exists: str = "replace"
    ) -> int:
        """Write a DataFrame to a table and return the number of rows stored.

        ``if_exists="replace"`` drops and recreates the table, so re-running the
        notebook never creates duplicate rows.
        """
        df.to_sql(
            table_name,
            self.engine,
            if_exists=if_exists,
            index=False,
            method="multi",   # send many rows per INSERT (much faster over the internet)
            # Each cell is one query parameter, and databases cap parameters per
            # statement (PostgreSQL 65,535; SQLite 32,766), so wide tables need
            # fewer rows per INSERT.
            chunksize=max(1, MAX_PARAMS_PER_INSERT // max(1, len(df.columns))),
        )
        return self.count_rows(table_name)

    def upload_ordered(self, df: pd.DataFrame, table_name: str) -> int:
        """Upload ``df`` with a ``row_id`` column so its row order can be restored.

        SQL tables have no guaranteed row order, so a plain ``SELECT *`` may come
        back shuffled. Use this with ``read_ordered`` whenever later steps
        (head/tail, duplicates, sampling, train/test splits) depend on row order.
        """
        return self.upload_dataframe(df.rename_axis(ROW_ID).reset_index(), table_name)

    def read_ordered(self, table_name: str) -> pd.DataFrame:
        """Read a table written by ``upload_ordered`` back in its original row order."""
        df = self.read_query(f'SELECT * FROM "{table_name}" ORDER BY "{ROW_ID}"')
        return df.drop(columns=ROW_ID)

    def upload_csv(self, csv_path: Path, table_name: str) -> int:
        """Read a CSV file and upload it to ``table_name``."""
        return self.upload_dataframe(pd.read_csv(csv_path), table_name)

    def read_table(self, table_name: str) -> pd.DataFrame:
        """Load an entire table into a DataFrame."""
        return self.read_query(f'SELECT * FROM "{table_name}"')

    def read_query(self, sql: str) -> pd.DataFrame:
        """Run any SELECT statement and return the result as a DataFrame."""
        with self.engine.connect() as conn:
            return pd.read_sql(text(sql), conn)

    def count_rows(self, table_name: str) -> int:
        with self.engine.connect() as conn:
            return conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar_one()

    def list_tables(self) -> list[str]:
        return inspect(self.engine).get_table_names()

    def close(self) -> None:
        self.engine.dispose()

