"""One-time upload of the ARDA NPORS SPSS files to Neon.

The notebook reads the survey data only from Neon, so the licensed .sav files never
need to be in the repository. Whoever holds the ARDA downloads saves them as
data/NPORS23.sav, data/NPORS24.sav and data/NPORS25.sav (git-ignored), then runs,
from the project root:

    PYTHONPATH=src python -m pew_dataset.upload

Re-running replaces the tables, so it never creates duplicate rows.
"""

from common.database import NeonDatabase

from .config import LABELS_TABLE_NAME, SURVEY_YEARS, raw_table_name, sav_path
from .loading import labels_from_frame, labels_to_frame, read_npors_sav, validate_npors


def upload_npors(db):
    """Upload each year's raw codes plus the value labels, then check the copy matches."""
    raw, labels = {}, {}
    for year in SURVEY_YEARS:
        raw[year], labels[year] = read_npors_sav(year)
        validate_npors(raw[year], year)
        rows = db.upload_ordered(raw[year], raw_table_name(year))
        print(f"Uploaded {rows:,} rows to table '{raw_table_name(year)}'")
    rows = db.upload_dataframe(labels_to_frame(labels), LABELS_TABLE_NAME)
    print(f"Uploaded {rows:,} value labels to table '{LABELS_TABLE_NAME}'")

    for year in SURVEY_YEARS:
        assert db.read_ordered(raw_table_name(year)).equals(raw[year]), f"Neon copy of {year} differs"
    assert labels_from_frame(db.read_table(LABELS_TABLE_NAME)) == labels, "Neon value labels differ"
    print("Verified: Neon tables match the SPSS files exactly.")


def main():
    missing = [str(sav_path(year)) for year in SURVEY_YEARS if not sav_path(year).exists()]
    if missing:
        raise SystemExit("Save the ARDA downloads first. Missing: " + ", ".join(missing))
    db = NeonDatabase.from_env()
    try:
        upload_npors(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
