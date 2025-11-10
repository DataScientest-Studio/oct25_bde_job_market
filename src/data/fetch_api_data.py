import os
from dotenv import load_dotenv
import requests

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

url = "https://api.adzuna.com/v1/api/jobs/de/search/"
params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "category": "it-jobs",
    "results_per_page": 50
}

response = requests.get(url, params=params)
#print(response.json())

