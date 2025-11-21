import os
from dotenv import load_dotenv
import requests

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

def fetch_jobs(category="it-jobs", country="de", results_per_page=50):
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "category": category,
        "results_per_page": results_per_page
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # raise error if unauthorized, etc.
    data = response.json()
    return data.get("results", [])

