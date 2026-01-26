import requests
import pendulum
import logging
from airflow.sdk import Variable, dag, task
from airflow import AirflowException

logger = logging.getLogger(__name__)

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
        start_page = Variable.get("start_page", 1)
        max_pages = Variable.get("max_pages", default=5)
        fastapi_url = "http://api:8000/data/ingest"

        payload = {
            "start_page": int(start_page), 
            "max_pages": int(max_pages)
        }

        logger.info(f"Sending ingest payload: {payload}")

        try:
            response = requests.post(fastapi_url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Ingest successful: {result}")

            next_start = result.get("next_start_page")
 
            Variable.set("start_page", result["next_start_page"], serialize_json=True)
            return result  # Returns pages fetched, etc.

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP {e.response.status_code} from ingest FastAPI: {e.response.text}")
            raise AirflowException(f"Ingest failed: {e.response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed in ingest: {str(e)}")
            raise AirflowException(f"Ingest request error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in ingest: {str(e)}")
            raise AirflowException(f"Ingest error: {str(e)}")

    @task
    def train():
        fastapi_url = "http://api:8000/ml/train"

        logger.info("Starting ML train request")

        try:
            response = requests.post(fastapi_url, timeout=600)  # Longer timeout for training
            response.raise_for_status()
            result = response.json()
            logger.info(f"Train successful: {result}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP {e.response.status_code} from train FastAPI: {e.response.text}")
            raise AirflowException(f"Train failed: {e.response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed in train: {str(e)}")
            raise AirflowException(f"Train request error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in train: {str(e)}")
            raise AirflowException(f"Train error: {str(e)}")

    # Flow
    ingest() >> train()

adzuna_workflow()