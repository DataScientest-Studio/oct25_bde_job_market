Project Name
==============================

## Overview

This project predicts job market salaries using machine learning and provides a web interface for interactive predictions. It ingests job data from the Adzuna API, stores it in PostgreSQL and MongoDB, trains a RandomForest model, and exposes predictions via both a REST API and Streamlit web UI.

**Key Features:**
- 🔄 Automated daily job data ingestion (988+ jobs currently)
- 🤖 ML-powered salary predictions (MAE: €13,935)
- 🌐 REST API for programmatic access
- 💻 Interactive Streamlit dashboard
- 📊 Cross-platform Docker setup (Mac/Windows/Linux)

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Setup & Run

```bash
# Clone and navigate to project
cd oct25_bde_job_market

# Copy environment template
cp .env.example .env

# Start all services (PostgreSQL, MongoDB, FastAPI, Streamlit)
docker-compose up -d

# Services will be available at:
# - API: http://localhost:8000/docs (Swagger UI)
# - Streamlit: http://localhost:8501
# - pgAdmin: http://localhost:5050
# - Mongo Express: http://localhost:8081
```

### Using the Salary Predictor

**Via Streamlit UI:**
1. Open http://localhost:8501
2. Enter job details (title, description, city, etc.)
3. Click "Predict Salary" to get an instant prediction

**Via API (POST):**
```bash
curl -X POST "http://localhost:8000/ml/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "job_description": "Build scalable backend systems",
    "city": "Berlin",
    "country": "Deutschland",
    "contract_type": "permanent",
    "contract_time": "full_time"
  }'
```

---

## Project Organization


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

## Architecture & Components

### Current Services
- **FastAPI** (Port 8000): REST API for salary predictions and data endpoints
- **PostgreSQL**: Relational database for structured job data
- **MongoDB**: NoSQL database for job descriptions and metadata
- **Streamlit** (Port 8501): Interactive UI for salary predictions
- **ML Model**: RandomForest regressor trained on historical salary data

### Missing Component: Apache Airflow
**Status:** ⏳ To be implemented

Airflow will automate the daily workflows for:
- **Data Ingestion**: Fetch latest job postings from Adzuna API and sync to PostgreSQL/MongoDB
- **Model Retraining**: Retrain the salary prediction model with newly ingested data
- **Monitoring**: Track data quality and model performance metrics

**Proposed Setup:**
```yaml
airflow:
  image: apache/airflow:latest
  services:
    - scheduler: Orchestrates DAG execution
    - webserver: Monitoring & management UI (Port 8080)
    - executor: Celery or Local executor for task distribution
```

**DAGs to implement:**
1. `daily_ingestion_dag`: Run `/data` endpoint to fetch new jobs (triggers at 02:00 UTC)
2. `weekly_training_dag`: Retrain model if sufficient new salary data exists (triggers Sundays at 03:00 UTC)
3. `data_quality_dag`: Validate data integrity and alert on anomalies

--------

