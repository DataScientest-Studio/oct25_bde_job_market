Job Market Salary Predictor
==============================

## 📊 Overview

App that predicts IT job salaries in Germany. It pulls job data from the Adzuna API, trains a machine learning model to predict salaries, and lets you use it via a web app or REST API.

What you get:
- Daily job data pulled from Adzuna (~1,500 jobs so far)
- Salary predictions within ~€15k accuracy
- A Streamlit web UI to try predictions
- An API for programmatic access
- Docker setup that works on Mac, Windows, and Linux

---

## 🚀 Quick Start

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

## 🏗️ Architecture

The stack is fairly straightforward:

- **FastAPI** (port 8000): Handles the API and ML
- **Streamlit** (port 8501): The web UI for predictions
- **PostgreSQL**: Stores job data 
- **MongoDB**: Stores full job descriptions
- **pgAdmin & Mongo Express**: Web UIs to browse the databases
- **Airflow** (optional): Daily job fetching and model retraining

All in Docker, connected together on the same network.

## ⚙️ What's Running

| Service | Port | What it does |
|---------|------|------|
| FastAPI | 8000 | Predictions, data endpoints, model training |
| Streamlit | 8501 | Web UI for trying predictions |
| PostgreSQL | 5432 | Jobs database |
| MongoDB | 27017 | Full job descriptions |
| pgAdmin | 5050 | Browse PostgreSQL |
| Mongo Express | 8081 | Browse MongoDB |
| Airflow WebServer | 8080 | Schedule and watch jobs (optional) |

## 🤖 The Model

Uses RandomForest with 100 trees and max depth 10. Trained on ~332 jobs that have salary info.

**Accuracy:**
- Mean error: €14,676 (so within ±€15k most of the time)

**What affects salary:**
1. Location (city)
2. Job title
3. Permanent vs contract
4. Job title length
5. Years of experience required

## 🔄 Data Pipeline (Airflow)

Two main things Airflow does:

1. **Daily at 2 AM**: Fetches new jobs from Adzuna and saves them to PostgreSQL and MongoDB
2. **On-demand**: Retrains the model when you call `/ml/train`

Logs go to `airflow/logs/dag_id=adzuna_pipeline_v1/`

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:8000`

**Predict a salary:**
```bash
curl -X POST http://localhost:8000/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "job_description": "Build backend systems",
    "city": "Berlin",
    "country": "Deutschland",
    "contract_type": "permanent",
    "contract_time": "full_time"
  }'
```
Response: `{"predicted_salary": 65000.50}`

**Retrain the model:**
```bash
curl -X POST http://localhost:8000/ml/train
```

**Pull new jobs from Adzuna:**
```bash
curl -X PUT http://localhost:8000/data
```

**List jobs in the database:**
```bash
curl "http://localhost:8000/data/postings?limit=10"
```

**Check if the API is up:**
```bash
curl http://localhost:8000/health
```

For all endpoints and to test them interactively, visit http://localhost:8000/docs

---

## ⚡ Customizing

**Retrain the model manually:**
```bash
docker exec my-fastapi-app python src/models/train_model.py
```

Or just call the API endpoint above.

**Add new keywords or features:**

Edit `src/models/train_model.py`. Lines 45-77 have lists of keywords that the model looks for in job descriptions. Add or remove keywords here.

**Tweak the model hyperparameters:**

In the same file, find RandomForestRegressor and try different values:
```python
RandomForestRegressor(
    n_estimators=100,    # More trees = slower but potentially better
    max_depth=10,        # Deeper = more complex patterns
    random_state=42,
    n_jobs=-1           # Use all CPU cores
)
```

**Manage Airflow DAGs:**

Go to http://localhost:8080 (login: `airflow` / password: `airflow`) to see scheduled tasks.

DAG file: `airflow/dags/adzuna_dag.py`

Manually trigger the daily job fetch:
```bash
docker exec airflow-airflow-scheduler-1 airflow dags trigger adzuna_pipeline_v1
```

---

## 📈 How Good Is This Actually?

**The numbers:**
- MAE: €14,676 (within ±€15k usually)
- RMSE: €20,074 (sometimes bigger misses)
- R²: -0.03 (basically at baseline)

**Why it's not great:**
- Only ~22% of Adzuna jobs have salary info. Hard to learn from 332 data points.
- Job descriptions are messy
- Salary varies wildly even for same job/location

**How to improve it:**
- Get more data with salaries (more Adzuna pages, other job boards)
- Better keyword extraction from descriptions
- Try a different algorithm

**What we have now:**
- 1,529 total jobs
- 332 with salary data
- 265 for training, 67 for testing

---

## 🎯 Different Ways to Run It

**Everything (including Airflow):**
```bash
./setup.sh
```

This starts all services. Warning: Airflow uses a lot of memory.

**Just the essentials (lighter for development):**
```bash
./setup.sh --skip-airflow
```

Runs API, Streamlit, and databases. Faster to start.

**Manual with Docker Compose:**
```bash
docker-compose up -d
```

Add Airflow later if needed:
```bash
cd airflow && docker-compose up -d && cd ..
```

---

## 🔧 Troubleshooting

**Streamlit can't talk to the API:**
- Make sure `API_URL` is `http://api:8000` (in Docker)
- Check they're on the same Docker network

**Airflow is broken:**
- Check logs: `docker logs airflow-airflow-scheduler-1`
- Make sure `.env` exists in both root and `airflow/` directories
- Make sure PostgreSQL and MongoDB are running

**Model training failed:**
- Check PostgreSQL has job data with salaries: `SELECT COUNT(*) FROM job WHERE salary_min IS NOT NULL;`
- Look at the script output for details

**Ports already in use:**
- Edit `docker-compose.yml` to use different port numbers
- Check what's using a port: `lsof -i :8000` (Mac/Linux) or `netstat -ano | findstr :8000` (Windows)

---

## 🛠️ Tech Stack

- FastAPI, Streamlit (frontend)
- PostgreSQL, MongoDB (databases)
- scikit-learn, pandas, numpy (ML/data processing)
- Apache Airflow (scheduling)
- Docker & Docker Compose

---

## 👥 Who Made This

DataScienceTest Data Engineering Bootcamp (Oct 2025 - January 2026) project by Alexander Weiß, Yannis Wittig, Tom Krause and Birgit Hermsen.

---

## 📄 License

See LICENSE file for details.

---

## 💬 Contact & Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs: `docker-compose logs -f [service_name]`
3. Check API docs at http://localhost:8000/docs
4. Review Airflow logs at http://localhost:8080

