"""Build week5Lab.ipynb: the four section notebooks combined into one, in the handout's order.

The section notebooks in notebooks/ are the source of truth. This script copies
their cells into a single notebook in the project root, after an introduction
and a replicability check (INTRO_CELLS below), and ends with the handout's
submission checklist (CHECKLIST_CELL below).

Run from the project root, then open week5Lab.ipynb and choose Restart & Run All:

    python scripts/build_week5lab.py

Only the standard library is used, so it adds nothing to requirements.txt.
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "week5Lab.ipynb"
SECTIONS = [
    "notebooks/pew.ipynb",
    "notebooks/billboard_section.ipynb",
    "notebooks/car_section.ipynb",
    "notebooks/diabetes.ipynb",
]

# --------------------------------------------------------------------------- #
# Notebook text that is not part of any section
# --------------------------------------------------------------------------- #
INTRO_CELLS = [
    """\
# **Lab 2 – Tidying, Cleaning, Imputation, and Outlier Detection**

## Machine Learning Programming

This notebook contains **all four completed sections** of the lab, in the handout's order. Each section starts with its own setup cell, so a section can be read and run independently.

The purpose of this lab is to practice the data-preprocessing work that normally takes place before machine learning: reshaping data, cleaning inconsistent values, handling missing data, detecting outliers, visualizing results, and explaining the decisions you make.
""",
    """\
## **Replicability Check**

### How to reproduce this notebook

1. Create a virtual environment with **Python 3.13** and run `pip install -r requirements.txt` (exact versions from `pip freeze`).
2. Create a `.env` file in the project root containing `NEON_DATABASE_URL=<connection string>` (see the README). **Section 1 needs it**: its licensed Pew survey data is stored only in the team's Neon database and cannot be published in the repository. Sections 2–4 also read from Neon, but fall back to the CSV files committed in `data/` when `.env` is missing. The notebook **only reads** from the database, so a read-only login is enough.
3. Open this notebook, select the `.venv` kernel, and choose **Restart** then **Run All**.

> **Without the Neon connection string, Run All stops at Section 1.** Ask the team for the connection string. Sections 2–4 can still be run on their own from `notebooks/`.

### Test in a clean environment

| Item | Detail |
|---|---|
| Date | 2026-10-15 |
| Machine | macOS, Python 3.13.13 |
| Method | Fresh `git clone` of the GitHub repository into an empty folder, new virtual environment created only from `requirements.txt`, then **Run All** |
| Result with `.env` | All four sections ran without errors (data loaded from Neon) |
| Result without `.env` | Sections 2–4 ran without errors using the committed CSV files; Section 1 stopped with its "`NEON_DATABASE_URL` is not set" message, as designed |

### Issues found and how they were fixed

| Issue | Fix |
|---|---|
| Section 2 failed without `.env`: the Billboard CSV files were not in the repository | Committed both files to `data/` (public TidyTuesday data, 46 MB and 10 MB) |
| `requirements.txt` was not an exact freeze: six dependencies installed without pinned versions | Regenerated it with `pip freeze` from a clean environment, and checked that a fresh install freezes back to the identical file |
| Section 1 could not be loaded by teammates: `pyreadstat` was missing from `requirements.txt` | Added `pyreadstat` |
| Uploading the wide Pew tables to Neon failed: too many query parameters in one `INSERT` | Batch size is now set from the number of columns (`src/common/database.py`) |
| SQL tables have no guaranteed row order, which changed duplicate handling and train/test splits | Tables are uploaded with a `row_id` and read back with `ORDER BY row_id` |
| A True/False column (`spotify_track_explicit`) changed type after the database round trip | Converted back to True/False on loading (`src/billboard_dataset/loading.py`) |
| Sections 3 and 4 uploaded their CSV to Neon on every run, so they would fail with a read-only login | Uploading moved to one-time scripts (`python -m car_dataset.upload`, `python -m diabetes_dataset.upload`); every section now only reads from Neon |

### Test on a second machine

| Item | Detail |
|---|---|
| Date | |
| Tester and machine | |
| Operating system and Python version | |
| Result | |
| Issues and fixes | |
""",
    """\
## **Assignment Overview**

### Purpose
By the end of this lab, you should be able to take several imperfect datasets and make them more suitable for analysis and later machine-learning work.

### Learning Outcomes
You will practice how to:

- inspect the shape, columns, data types, and quality of a dataset;
- distinguish **wide** and **long/tidy** data;
- reshape data with `pd.melt()` or `DataFrame.melt()`;
- clean strings using Pandas string methods;
- identify, quantify, drop, and impute missing values;
- compare mean, median, mode, and `SimpleImputer` approaches;
- identify outliers visually with box plots and scatter plots;
- identify outliers statistically using **Z-Scores** and **IQR**;
- justify preprocessing decisions using evidence from the data;
- document a reproducible Python data-processing workflow.
""",
    """\
## **How this notebook is organized**

| Section | Dataset | Research question |
|---|---|---|
| **1 – PEW Research Dataset** | Pew NPORS surveys 2023–2025 (16,381 respondents) | Do adults who use the internet "almost constantly" differ in average age from internet users who go online less often? |
| **2 – Billboard Dataset** | Billboard Hot 100 weekly charts 1958–2021, with Spotify audio features | Which characteristics of a song, known when it first enters the chart, help explain how many weeks it stays on the Hot 100? |
| **3 – Data Cleaning (Car Details Dataset)** | 8,128 CarDekho used-car listings | Do diesel cars achieve significantly better mileage than petrol cars, and how well can a car's listed characteristics predict its mileage? |
| **4 – Outlier Detection (Diabetes Dataset)** | 5,288 patients | Do diabetic patients have significantly higher glucose, BMI, and systolic blood pressure, and does that hold once outliers are taken into account? |

As a team, each section uses its own dataset rather than the handout's examples; each section explains its choice. Reusable code lives in `src/`, and the raw data is stored in a shared **Neon** (cloud PostgreSQL) database.

This notebook is built from the four section notebooks in `notebooks/` with `python scripts/build_week5lab.py`, so edits should be made there and the notebook rebuilt.
""",
]

CHECKLIST_CELL = """\
---
# **Final Validation and Submission Checklist**

- [x] All four required sections are in this single notebook.
- [x] PEW uses `pd.melt()` or `DataFrame.melt()`.
- [x] Billboard uses `melt()` and Pandas string manipulation.
- [x] Cars demonstrates missing-value analysis, dropping, imputation, duplicates, and validation.
- [x] Diabetes includes box plot, scatter plot, Z-Score, and IQR.
- [x] Every required visualization has a meaningful title and axis labels.
- [x] Reflection questions are answered in Markdown.
- [x] Data is loaded using relative paths from a clearly named data folder (or from the team's Neon database).
- [x] `README.md`, `requirements.txt`, and `.gitignore` are included.
- [x] There are no unnecessary `!pip install` cells.
- [x] The kernel was restarted and **Run All** completed from top to bottom (see the Replicability Check).
"""


def markdown_cell(text, cell_id):
    return {"cell_type": "markdown", "id": cell_id, "metadata": {}, "source": text.strip("\n")}


def demote_headings(text):
    """Add one '#' to every Markdown heading outside fenced code blocks."""
    lines, in_fence = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and re.match(r"#{1,5} ", line):
            line = "#" + line
        lines.append(line)
    return "\n".join(lines)


def section_cells(path):
    """Copy a section notebook's cells: keep its title as H1, nest everything else one level down."""
    cells = json.loads((PROJECT_ROOT / path).read_text())["cells"]
    copied = []
    for index, cell in enumerate(cells):
        source = "".join(cell["source"])
        # Some notebooks store no cell ids; derive a stable one so rebuilds do not churn in Git
        cell_id = cell.get("id") or f"{Path(path).stem}-{index}"
        if cell["cell_type"] == "markdown":
            if index == 0:
                title, _, rest = source.partition("\n")
                source = title + ("\n" + demote_headings(rest) if rest else "")
            else:
                source = demote_headings(source)
            source = source.replace("](../", "](")  # links are now relative to the project root
            copied.append({"cell_type": "markdown", "id": cell_id, "metadata": {}, "source": source})
        else:
            copied.append({"cell_type": "code", "id": cell_id, "metadata": {},
                           "execution_count": None, "outputs": [], "source": source})
    return copied


def build():
    # Fixed ids for the cells written here, so rebuilding does not create noise in Git
    cells = [markdown_cell(text, f"week5lab-intro-{n}") for n, text in enumerate(INTRO_CELLS, start=1)]
    for path in SECTIONS:
        cells += section_cells(path)
    cells.append(markdown_cell(CHECKLIST_CELL, "week5lab-checklist"))

    seen = set()
    for cell in cells:  # cell ids must be unique within one notebook
        base, n = cell["id"], 1
        while cell["id"] in seen:
            n += 1
            cell["id"] = f"{base}-{n}"
        seen.add(cell["id"])

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {OUTPUT.relative_to(PROJECT_ROOT)} ({len(cells)} cells from {len(SECTIONS)} sections)")


if __name__ == "__main__":
    build()
