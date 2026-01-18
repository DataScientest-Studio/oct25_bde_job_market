import os
import sys
import pendulum
from datetime import datetime
from airflow.sdk import dag, task
from airflow.operators.python import get_current_context



PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


from src.config.job_config import get_config
from src.data.fetch_api_data import fetch_jobs
from src.data.postgres_db import store_jobs_sql
from src.data.mongo_db import store_jobs_nosql
from src.models.train_model import train_salary_model


# def get_run_dates():
#     try:
#         context = get_current_context()
#         conf = context['dag_run'].conf or {}
#     except:
#         conf = {}
#     return get_config(start_str=conf.get('start_date'), end_str=conf.get('end_date'))

def get_run_dates():
    """Extracts dates from the current Airflow context."""
    context = get_current_context()
    conf = context['dag_run'].conf or {}
    return get_config(
        start_str=conf.get('start_date'), 
        end_str=conf.get('end_date')
  )

@dag(
    dag_id="adzuna_pipeline_v1",
    schedule="@daily",
    start_date=pendulum.datetime(2025, 11, 1, tz="UTC"),
    catchup=False,
    tags=["jobs", "initial-etl"],
)
def adzuna_workflow():

    @task
    def extract():
        return fetch_jobs()

    @task
    def load_postgres(jobs: list):
        start, end = get_run_dates()
        return store_jobs_sql(jobs, start, end)

    @task
    def load_mongo(jobs: list):
        start, end = get_run_dates()
        return store_jobs_nosql(jobs, start, end)

    # @task
    # def load_postgres(jobs: list):
    #     start = datetime(2025, 11, 1)
    #     end = datetime(2025, 12, 10)
    #     return store_jobs_sql(jobs, start, end)

    # @task
    # def load_mongo(jobs: list):
    #     start = datetime(2025, 11, 1)
    #     end = datetime(2025, 12, 10)
    #    return store_jobs_nosql(jobs, start, end)

    @task
    def train():
        model_path = os.path.join(PROJECT_ROOT, "models", "salary_model.pkl")
        print(f"Training model and saving to {model_path}...")
        train_salary_model() 
        return model_path

    # Flow
    raw_data = extract()
    #trained_model = [load_postgres(raw_data), load_mongo(raw_data)] >> train()
    #predictions = predict(raw_data, trained_model)
    [load_postgres(raw_data), load_mongo(raw_data)] >> train()

adzuna_workflow()



# if __name__ == "__main__":
#     adzuna_workflow().test()
