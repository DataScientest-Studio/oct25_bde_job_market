Project Name
==============================

This project is a starting Pack for MLOps projects based on the subject "movie_recommandation". It's not perfect so feel free to make some modifications on it.

Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── logs               <- Logs from training and predicting
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   ├── visualization  <- Scripts to create exploratory and results oriented visualizations
    │   │   └── visualize.py
    │   └── config         <- Describe the parameters used in train_model.py and predict_model.py

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
## ETL Pipeline (Adzuna Integration)

This branch (`feature/first_repo_integration`) contains a complete ETL pipeline that fetches job offers from the Adzuna API, transforms them and stores them in a PostgreSQL database.

### 1. Python environment

Create and activate a virtual environment:

    cd oct25_bde_job_market
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

### 2. Environment variables

Copy the example env file and fill in your values:

    cp .env.example .env

In `.env` set at least:

    ADZUNA_APP_ID=your_adzuna_app_id_here
    ADZUNA_APP_KEY=your_adzuna_app_key_here

    DB_HOST=localhost        # or a shared VM/database host, or a docker service name e.g. "postgres"
    DB_PORT=5432
    DB_NAME=jobs_db
    DB_USER=job_user         # or postgres / whatever your DB user is
    DB_PASSWORD=your_password

`src/db/db_config.py` reads these variables and builds the SQLAlchemy `DATABASE_URL` automatically.

### 3. Database setup

The ETL pipeline will automatically create the required tables on first run (see `src/db/models.py`, table `jobs`).

You can also initialize the database explicitly:

    source .venv/bin/activate
    python -c "from src.db.db_config import init_db; init_db()"

### 4. Running the ETL pipeline

From the project root:

    source .venv/bin/activate
    python -m src.main_first_repo

This will:

- call the Adzuna API,
- save the raw JSON under `data/raw/...`,
- transform the data,
- insert new jobs into the `jobs` table (skipping duplicates by `adzuna_id`),
- and log the total number of jobs in the database.

### 5. Optional: PostgreSQL with Docker Compose (local development)

If you do **not** have a local PostgreSQL installed, you can use the provided `docker-compose.yml`:

    docker compose up -d postgres

The service uses the same environment variables as the application:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

The data is stored in `./data/postgres` (ignored by git).

> On the DataScientest VM there may already be a shared PostgreSQL instance running.  
> In that case you can keep `DB_HOST=localhost` or set `DB_HOST` to the shared host as agreed in the team, without using the docker-compose Postgres.
