# PROG8245-Lab2-Tidying_Cleaning_Imputation_Outlier Detection
Repo for PROG8245 Lab 2 - Tidying, Cleaning, Imputation, and Outlier Detection

## Diabetes analysis (Section 4)

`notebooks/diabetes.ipynb` uploads `data/diabetes_dataset.csv` to a Neon PostgreSQL database, loads it back into pandas, then runs data preparation, EDA, normality checks + t-tests, and outlier detection. Reusable classes live in `src/diabetes_dataset/`.

### How to run

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and set `NEON_DATABASE_URL` to your Neon connection string (`.env` is git-ignored).
3. Open `notebooks/diabetes.ipynb` and choose **Restart & Run All**. Without a connection string, the notebook falls back to reading the local CSV.
