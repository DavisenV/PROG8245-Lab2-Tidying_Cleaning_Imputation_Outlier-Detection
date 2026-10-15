# PROG8245-Lab2-Tidying_Cleaning_Imputation_Outlier Detection
Repo for PROG8245 Lab 2 - Tidying, Cleaning, Imputation, and Outlier Detection

## Car details analysis (Section 3)

`notebooks/car_section.ipynb` uploads `data/Car details v3.csv` (CarDekho used-car listings) to a Neon PostgreSQL database, loads it back into pandas, then runs data cleaning and imputation, feature engineering, EDA, a two-sample hypothesis test (diesel vs petrol mileage), and a regression model that predicts mileage. Reusable helpers live in `src/car_dataset/`. The Neon connection class (`NeonDatabase`) lives in `src/common/database.py` and is shared with Section 4. Each section writes to its own table (`car_details_raw`, `diabetes_raw`) in the same database.

### How to run

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and set `NEON_DATABASE_URL` to your Neon connection string (`.env` is git-ignored).
3. Open `notebooks/car_section.ipynb` and choose **Restart & Run All**. Without a connection string, the notebook falls back to reading the local CSV.

## Diabetes analysis (Section 4)

`notebooks/diabetes.ipynb` uploads `data/diabetes_dataset.csv` to a Neon PostgreSQL database, loads it back into pandas, then runs data preparation, EDA, normality checks + t-tests, and outlier detection. Reusable classes live in `src/diabetes_dataset/`.

### How to run

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and set `NEON_DATABASE_URL` to your Neon connection string (`.env` is git-ignored).
3. Open `notebooks/diabetes.ipynb` and choose **Restart & Run All**. Without a connection string, the notebook falls back to reading the local CSV.
