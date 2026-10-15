# PROG8245 Lab 2 – Tidying, Cleaning, Imputation, and Outlier Detection

Group repository for PROG8245 (Machine Learning Programming) Lab 2. Each project takes a raw dataset, stores it in a shared Neon PostgreSQL database, loads it back into pandas, and works through data preparation, exploratory data analysis, and inferential statistics. Each notebook opens with a research question and ends with its answer.

**The submission notebook is [`week5Lab.ipynb`](week5Lab.ipynb)**: all four sections in one notebook, in the handout's order, with a Replicability Check at the top. It is built from the four section notebooks in `notebooks/` (see [Rebuilding `week5Lab.ipynb`](#rebuilding-week5labipynb)).

## Projects

| Section | Notebook | Dataset | Research question |
|---|---|---|---|
| **1 – Tidy data** | [`notebooks/pew.ipynb`](notebooks/pew.ipynb) | Neon tables `npors23_raw`–`npors25_raw` – Pew NPORS surveys 2023–2025, 16,381 respondents (licensed data, not stored in the repo) | Do adults who use the internet "almost constantly" differ in average age from internet users who go online less often? |
| **2 – Billboard** | [`notebooks/billboard_section.ipynb`](notebooks/billboard_section.ipynb) | Neon tables `billboard_hot100_raw` and `billboard_audio_features_raw` – Billboard Hot 100 weekly charts, 1958–2021 (327,895 rows), plus Spotify audio features for 29,386 songs | Which characteristics of a song, known when it first enters the chart, help explain how many weeks it stays on the Hot 100? |
| **3 – Data cleaning** | [`notebooks/car_section.ipynb`](notebooks/car_section.ipynb) | [`data/Car details v3.csv`](data/) – 8,128 CarDekho used-car listings | Do diesel cars achieve significantly better mileage than petrol cars, and how well can a car's listed characteristics predict its mileage? |
| **4 – Outlier detection** | [`notebooks/diabetes.ipynb`](notebooks/diabetes.ipynb) | [`data/diabetes_dataset.csv`](data/) – 5,288 patients | Do diabetic patients have significantly higher glucose, BMI, and systolic blood pressure, and does that hold once outliers are taken into account? |

### Section 1 – Pew NPORS

Validates and harmonizes three yearly Pew Research Center NPORS releases (distributed by ARDA): it checks every answer code against the codebook, keeps refusals (code 99) separate from real answers, and aligns income bands and internet-use categories across years. It then:

- compares missing-value strategies for age and demonstrates `SimpleImputer` on copies only;
- flags age outliers with Z-score and IQR rules and records each decision in a log;
- reshapes six shared survey questions with `melt()` (98,286 respondent–question rows) and visualizes them;
- tests whether mean age differs by internet-use intensity in 2024 (Q-Q plots, Shapiro–Wilk, Welch's t-test).

**The data lives only in Neon.** The ARDA downloads are licensed (downloading requires accepting ARDA's agreement), so they are not committed. Each year is stored as raw numeric codes (`npors23_raw`, `npors24_raw`, `npors25_raw`), with the SPSS value labels in `npors_value_labels`, and the notebook reads those tables. This section therefore **needs the Neon connection string** in `.env`. Acknowledge both ARDA and Pew Research Center when using the data.

To load or refresh the data in Neon, whoever holds the ARDA downloads saves them as `data/NPORS23.sav`, `data/NPORS24.sav` and `data/NPORS25.sav` (git-ignored), then runs this from the project root:

```bash
PYTHONPATH=src python -m pew_dataset.upload
```

The script reads the SPSS files with `pyreadstat`, replaces the four tables, and verifies that the Neon copy matches the files exactly.

### Section 2 – Billboard

Reshapes chart data with `melt()` (a wide table of weekly rank columns is built first), cleans the week labels with pandas string methods, rebuilds chart dates with `Timedelta`, and handles missing ranks (dropped, not imputed). Duplicate rows and impossible Spotify values are removed, and a before/after validation table checks the result. It then:

- engineers song-level features known at debut (debut rank and era, genre family, duration, explicit flag, audio features) and keeps leaking variables out;
- compares outliers with the box plot, IQR rule, and Z-score, and checks that the conclusions survive removing them;
- chooses regression features with correlation tests, Welch's t-tests with Mann–Whitney U, and ANOVA (Holm correction, effect sizes, VIF);
- fits a linear regression of log(weeks on chart) in statsmodels and in a scikit-learn `Pipeline` with a mean baseline and 5-fold cross-validation (test R² 0.19).

The data comes from the TidyTuesday 2021-09-14 release. Both files (about 46 MB and 10 MB) are committed in `data/`. They are also stored in Neon, and the notebook reads them from there; without a `.env`, it reads the committed CSVs instead. To load or refresh the Neon tables, run this once from the project root. It uploads the files in their original row order and verifies the Neon copy matches:

```bash
PYTHONPATH=src python -m billboard_dataset.upload
```

### Section 3 – Car details

Cleans the car listings (strips units from text columns, separates CNG/LPG cars whose mileage is in km/kg, recodes impossible values, removes 1,201 duplicate listings), then compares drop, mean, median, and mode strategies before imputing with `SimpleImputer`. It then:

- engineers a power-per-litre feature;
- explores mileage by fuel type, transmission, and engine size;
- tests diesel vs petrol mileage (Q-Q plots, Shapiro–Wilk, Levene, Welch's t-test, Mann–Whitney U);
- trains a linear regression that predicts mileage, compared against a mean baseline on held-out data (R² 0.72, MAPE 8.8%).

The notebook reads `car_details_raw` from Neon (or `data/Car details v3.csv` without a `.env`). To load or refresh the Neon table, run `PYTHONPATH=src python -m car_dataset.upload` from the project root.

### Section 4 – Diabetes

Removes physiologically impossible values, engineers clinical features (BMI and blood-pressure categories, age groups), and compares diabetic and non-diabetic patients with normality checks, Welch's t-tests, and Mann–Whitney U. It then applies the four outlier methods (box plot, scatter plot, Z-score, IQR) and checks whether the conclusions survive outlier treatment.

The notebook reads `diabetes_raw` from Neon (or `data/diabetes_dataset.csv` without a `.env`). To load or refresh the Neon table, run `PYTHONPATH=src python -m diabetes_dataset.upload` from the project root.

## Project structure

```text
.
├── data/
│   ├── billboard_hot100.csv      # Section 2 raw data (TidyTuesday)
│   ├── billboard_audio_features.csv
│   ├── Car details v3.csv        # Section 3 raw data
│   └── diabetes_dataset.csv      # Section 4 raw data
├── notebooks/
│   ├── pew.ipynb                 # Section 1
│   ├── billboard_section.ipynb   # Section 2
│   ├── car_section.ipynb         # Section 3
│   └── diabetes.ipynb            # Section 4
├── src/
│   ├── common/                   # shared by all sections
│   │   ├── config.py             #   .env location and variable name
│   │   └── database.py           #   NeonDatabase: connect, upload, read (incl. row-order-preserving upload/read)
│   ├── pew_dataset/              # Section 1 helpers (value labels, validation, one-time Neon upload)
│   ├── billboard_dataset/        # Section 2 helpers (Neon/CSV loading, one-time download and Neon upload)
│   ├── car_dataset/              # Section 3 helpers (loading, cleaning, Neon read, one-time Neon upload)
│   └── diabetes_dataset/         # Section 4 classes (preparation, EDA, tests, outliers)
├── results/                      # CSV reports written by the Section 1 notebook (git-ignored)
├── scripts/
│   └── build_week5lab.py         # combines the section notebooks into week5Lab.ipynb
├── week5Lab.ipynb                # submission notebook: all four sections
├── requirements.txt
└── README.md
```

The notebooks add `src/` to Python's search path themselves, so the packages need no installation step.

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

### 4. Connect to the Neon database

The notebooks read their data from a shared [Neon](https://neon.tech) PostgreSQL database. **They never write to it**, so a read-only login is enough to run them; each section's data is loaded into Neon once with its upload script (`PYTHONPATH=src python -m <section>_dataset.upload`). Create a file named **`.env`** in the project root containing your connection string:

```text
NEON_DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
```

- You can find the connection string in the Neon dashboard under **Connect**. Ask the team for the shared database's string, or create a free Neon project of your own.
- `.env` is listed in `.gitignore`, so the password is never committed. **Never paste the connection string into a notebook or commit it.**
- **Section 1 (Pew) requires `.env`**, because its licensed survey data is stored only in Neon.
- **Sections 2, 3 and 4 still run without a `.env`.** They print a warning and read local CSVs in `data/` instead, and the analysis results are identical either way.

Each section writes only its own tables (`npors23_raw`–`npors25_raw` and `npors_value_labels`, `billboard_hot100_raw` and `billboard_audio_features_raw`, `car_details_raw`, `diabetes_raw`) and its upload script replaces them on every run, so sections never overwrite each other and re-uploading never duplicates rows.

## Running the notebooks

1. Open the project folder in VS Code (or start `jupyter lab` from the project root).
2. Open **`week5Lab.ipynb`** (all four sections), or a single section from `notebooks/`.
3. Select the **`.venv`** interpreter as the kernel. In VS Code, use the kernel picker in the top-right corner of the notebook.
4. Choose **Restart** and then **Run All**. Each notebook should run from top to bottom without errors. `week5Lab.ipynb` takes about a minute and a half; Section 2 is the slowest part because of its large chart table.

Each section's data-loading cell reports where the data came from, for example `Loaded 8,128 rows x 13 columns from Neon table 'car_details_raw'`.

> **Without a `.env`, Run All of `week5Lab.ipynb` stops at Section 1**, whose licensed data is only in Neon. Sections 2–4 can still be run individually from `notebooks/`.

### Rebuilding `week5Lab.ipynb`

The section notebooks in `notebooks/` are the source of truth. After editing one, rebuild the combined notebook from the project root, then open it and choose **Restart** and **Run All** so its outputs are refreshed:

```bash
python scripts/build_week5lab.py
```

The introduction and the Replicability Check come from `scripts/week5lab_intro.md`, and the closing checklist from `scripts/week5lab_checklist.md`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'pandas'` (or `sqlalchemy`, `psycopg`, `pyreadstat`, `statsmodels`…) | The notebook kernel isn't using `.venv`. Select the `.venv` kernel, or re-run `pip install -r requirements.txt` with the environment activated. |
| `ModuleNotFoundError: No module named 'car_dataset'` / `'pew_dataset'` / `'billboard_dataset'` / `'common'` | Open the notebook from the `notebooks/` folder, or start Jupyter from the project root, so the notebook can find `src/`. |
| `WARNING: NEON_DATABASE_URL is not set in .env` | Expected if you haven't created `.env`: the notebook falls back to the local CSV. Add the connection string (step 4) to use Neon. |
| Connection or SSL error | Check that the connection string ends with `?sslmode=require` and that your Neon project is not suspended. |
