# PROG8245 Lab 2 – Tidying, Cleaning, Imputation, and Outlier Detection

Group repository for PROG8245 (Machine Learning Programming) Lab 2. Each project takes a raw dataset, loads it into pandas, and works through data preparation, exploratory data analysis, and inferential statistics. Sections 3 and 4 store their data in a shared Neon PostgreSQL database first (with a local CSV fallback); Section 2 reads local CSV files directly. Each notebook opens with a research question and ends with its answer.

## Projects

| Section | Notebook | Dataset | Research question |
|---|---|---|---|
| **2 – Billboard** | [`notebooks/billboard_section.ipynb`](notebooks/billboard_section.ipynb) | Billboard Hot 100 weekly charts, 1958–2021 (327,895 rows) plus Spotify audio features for 29,386 songs – [download first](#4-download-the-billboard-data-section-2-only) | Which characteristics of a song, known when it first enters the chart, help explain how many weeks it stays on the Hot 100? |
| **3 – Data cleaning** | [`notebooks/car_section.ipynb`](notebooks/car_section.ipynb) | [`data/Car details v3.csv`](data/) – 8,128 CarDekho used-car listings | Do diesel cars achieve significantly better mileage than petrol cars, and how well can a car's listed characteristics predict its mileage? |
| **4 – Outlier detection** | [`notebooks/diabetes.ipynb`](notebooks/diabetes.ipynb) | [`data/diabetes_dataset.csv`](data/) – 5,288 patients | Do diabetic patients have significantly higher glucose, BMI, and systolic blood pressure, and does that hold once outliers are taken into account? |

### Section 2 – Billboard

Reshapes chart data with `melt()` (a wide table of weekly rank columns is built first), cleans the week labels with pandas string methods, rebuilds chart dates with `Timedelta`, and handles missing ranks (dropped, not imputed). Duplicate rows and impossible Spotify values are removed, and a before/after validation table checks the result. It then:

- engineers song-level features known at debut (debut rank and era, genre family, duration, explicit flag, audio features) and keeps leaking variables out;
- compares outliers with the box plot, IQR rule, and Z-score, and checks that the conclusions survive removing them;
- chooses regression features with correlation tests, Welch's t-tests with Mann–Whitney U, and ANOVA (Holm correction, effect sizes, VIF);
- fits a linear regression of log(weeks on chart) in statsmodels and in a scikit-learn `Pipeline` with a mean baseline and 5-fold cross-validation (test R² 0.19).

### Section 3 – Car details

Cleans the car listings (strips units from text columns, separates CNG/LPG cars whose mileage is in km/kg, recodes impossible values, removes 1,201 duplicate listings), then compares drop, mean, median, and mode strategies before imputing with `SimpleImputer`. It then:

- engineers a power-per-litre feature;
- explores mileage by fuel type, transmission, and engine size;
- tests diesel vs petrol mileage (Q-Q plots, Shapiro–Wilk, Levene, Welch's t-test, Mann–Whitney U);
- trains a linear regression that predicts mileage, compared against a mean baseline on held-out data (R² 0.72, MAPE 8.8%).

### Section 4 – Diabetes

Removes physiologically impossible values, engineers clinical features (BMI and blood-pressure categories, age groups), and compares diabetic and non-diabetic patients with normality checks, Welch's t-tests, and Mann–Whitney U. It then applies the four outlier methods (box plot, scatter plot, Z-score, IQR) and checks whether the conclusions survive outlier treatment.

## Project structure

```text
.
├── data/
│   ├── billboard_hot100.csv             # Section 2 chart data (download, not in Git)
│   ├── billboard_audio_features.csv     # Section 2 Spotify features (download, not in Git)
│   ├── Car details v3.csv        # Section 3 raw data
│   └── diabetes_dataset.csv      # Section 4 raw data
├── notebooks/
│   ├── billboard_section.ipynb   # Section 2 (self-contained, reads ./data directly)
│   ├── car_section.ipynb         # Section 3
│   └── diabetes.ipynb            # Section 4
├── src/
│   ├── common/                   # shared by all sections
│   │   ├── config.py             #   .env location and variable name
│   │   └── database.py           #   NeonDatabase: connect, upload, read
│   ├── car_dataset/              # Section 3 helpers (loading, cleaning, Neon upload/read)
│   └── diabetes_dataset/         # Section 4 classes (preparation, EDA, tests, outliers)
├── week5Lab_Students.ipynb       # original assignment handout
├── requirements.txt
└── README.md
```

The Section 3 and 4 notebooks add `src/` to Python's search path themselves, so the packages need no installation step. The Section 2 notebook does not use `src/`.

## Setup

### 1. Prerequisites

- **Python 3.13** or newer
- **Git**
- **VS Code** with the *Python* and *Jupyter* extensions, or JupyterLab

### 2. Clone the repository

```bash
git clone https://github.com/DavisenV/PROG8245-Lab2-Tidying_Cleaning_Imputation_Outlier-Detection.git
cd PROG8245-Lab2-Tidying_Cleaning_Imputation_Outlier-Detection
```

### 3. Create a virtual environment and install the requirements

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you use [uv](https://docs.astral.sh/uv/), the equivalent is `uv venv` followed by `uv pip install -r requirements.txt`.

To use JupyterLab instead of VS Code, also run `pip install jupyterlab`.

### 4. Download the Billboard data (Section 2 only)

The two Billboard files are large (about 46 MB and 10 MB), so they are listed in `.gitignore` and are **not** in the repository. Download them once from the project root (they come from the TidyTuesday 2021-09-14 release):

```bash
BASE=https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2021/2021-09-14
curl -L $BASE/billboard.csv       -o data/billboard_hot100.csv
curl -L $BASE/audio_features.csv  -o data/billboard_audio_features.csv
```

The file names must match exactly. The notebook does not download anything itself.

### 5. Connect to the Neon database (optional, Sections 3 and 4)

The Section 3 and 4 notebooks upload their data to a [Neon](https://neon.tech) PostgreSQL database and read it back from there. Create a file named **`.env`** in the project root containing your connection string:

```text
NEON_DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
```

- You can find the connection string in the Neon dashboard under **Connect**. Ask the team for the shared database's string, or create a free Neon project of your own.
- `.env` is listed in `.gitignore`, so the password is never committed. **Never paste the connection string into a notebook or commit it.**
- **Without a `.env`, the notebooks still run.** They print a warning and read the local CSV in `data/` instead. The analysis results are identical either way.

Each section writes only its own table (`car_details_raw`, `diabetes_raw`) and replaces it on every run, so sections never overwrite each other and re-running never duplicates rows.

## Running the notebooks

1. Open the project folder in VS Code (or start `jupyter lab` from the project root).
2. Open a notebook from `notebooks/`.
3. Select the **`.venv`** interpreter as the kernel. In VS Code, use the kernel picker in the top-right corner of the notebook.
4. Choose **Restart** and then **Run All**. Each notebook should run from top to bottom without errors. The Section 2 notebook takes about a minute because of the large chart file.

The first code cell of each notebook reports where the data came from, for example `Loaded 8,128 rows x 13 columns from Neon table 'car_details_raw'`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'pandas'` (or `sqlalchemy`, `psycopg`…) | The notebook kernel isn't using `.venv`. Select the `.venv` kernel, or re-run `pip install -r requirements.txt` with the environment activated. |
| `ModuleNotFoundError: No module named 'car_dataset'` / `'common'` | Open the notebook from the `notebooks/` folder, or start Jupyter from the project root, so the notebook can find `src/`. |
| `WARNING: NEON_DATABASE_URL is not set in .env` | Expected if you haven't created `.env`: the notebook falls back to the local CSV. Add the connection string (step 5) to use Neon. |
| `FileNotFoundError` for `billboard_hot100.csv` | The Billboard files are not in the repository. Run the download commands in step 4. |
| Connection or SSL error | Check that the connection string ends with `?sslmode=require` and that your Neon project is not suspended. |
