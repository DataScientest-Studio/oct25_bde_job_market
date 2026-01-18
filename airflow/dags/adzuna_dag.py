import requests
import pendulum
from airflow.sdk import Variable, dag, task



@dag(
    dag_id="adzuna_pipeline_v1",
    schedule="@daily",
    start_date=pendulum.datetime(2025, 11, 1, tz="UTC"),
    catchup=False,
    tags=["jobs", "initial-etl"],
)
def adzuna_workflow():

    @task
    def ingest():
        start_page = Variable.get("adzuna_start_page", 1)
        max_pages = Variable.get("max_pages", default=5)
        fastapi_url = "http://my-fastapi-app:8000/data/ingest"
        response = requests.post(fastapi_url, json={
            "start_page": start_page, 
            "max_pages": max_pages
        })
        result = response.json()

        Variable.set("adzuna_start_page", result["next_start_page"])

        response.raise_for_status()
        return result  # Returns pages fetched, etc.

    @task
    def train():
        fastapi_url = "http://my-fastapi-app:8000/ml/train"
        response = requests.post(fastapi_url)
        response.raise_for_status()
        return response.json()  # Returns {"status": "trained"}

    # Flow
    ingest() >> train()

adzuna_workflow()



# if __name__ == "__main__":
#     adzuna_workflow().test()
