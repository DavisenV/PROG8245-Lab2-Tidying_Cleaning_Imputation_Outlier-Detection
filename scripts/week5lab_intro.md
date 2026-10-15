# **Lab 2 – Tidying, Cleaning, Imputation, and Outlier Detection**

## Machine Learning Programming

This notebook contains **all four completed sections** of the lab, in the handout's order. Each section starts with its own setup cell, so a section can be read and run independently.

The purpose of this lab is to practice the data-preprocessing work that normally takes place before machine learning: reshaping data, cleaning inconsistent values, handling missing data, detecting outliers, visualizing results, and explaining the decisions you make.

<!-- new cell -->

## **Replicability Check**

### How to reproduce this notebook

1. Create a virtual environment with **Python 3.13** and run `pip install -r requirements.txt` (exact versions from `pip freeze`).
2. Create a `.env` file in the project root containing `NEON_DATABASE_URL=<connection string>` (see the README). **Section 1 needs it**: its licensed Pew survey data is stored only in the team's Neon database and cannot be published in the repository. Sections 2–4 also read from Neon, but fall back to the CSV files committed in `data/` when `.env` is missing.
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

### Test on a second machine

| Item | Detail |
|---|---|
| Date | |
| Tester and machine | |
| Operating system and Python version | |
| Result | |
| Issues and fixes | |

<!-- new cell -->

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

<!-- new cell -->

## **How this notebook is organized**

| Section | Dataset | Research question |
|---|---|---|
| **1 – PEW Research Dataset** | Pew NPORS surveys 2023–2025 (16,381 respondents) | Do adults who use the internet "almost constantly" differ in average age from internet users who go online less often? |
| **2 – Billboard Dataset** | Billboard Hot 100 weekly charts 1958–2021, with Spotify audio features | Which characteristics of a song, known when it first enters the chart, help explain how many weeks it stays on the Hot 100? |
| **3 – Data Cleaning (Car Details Dataset)** | 8,128 CarDekho used-car listings | Do diesel cars achieve significantly better mileage than petrol cars, and how well can a car's listed characteristics predict its mileage? |
| **4 – Outlier Detection (Diabetes Dataset)** | 5,288 patients | Do diabetic patients have significantly higher glucose, BMI, and systolic blood pressure, and does that hold once outliers are taken into account? |

As a team, each section uses its own dataset rather than the handout's examples; each section explains its choice. Reusable code lives in `src/`, and the raw data is stored in a shared **Neon** (cloud PostgreSQL) database.

This notebook is built from the four section notebooks in `notebooks/` with `python scripts/build_week5lab.py`, so edits should be made there and the notebook rebuilt.
