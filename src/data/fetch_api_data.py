import os
import requests
from math import ceil
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

def fetch_jobs(category="it-jobs", country="de", results_per_page=50, newest_seen=None, max_pages=None):
    """
    Fetch jobs from Adzuna API incrementally.
    Stops fetching older jobs than `newest_seen`.
    max_pages limits API calls to avoid hitting API limits.
    """
    base_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "category": category,
        "results_per_page": results_per_page,
        "sort_by": "date" # newest first
    }

    jobs = []
    page = 1

    while True:
        print(f"About to fetch page {page}, max_pages={max_pages}")
        if max_pages is not None and page > max_pages:
            print("Breaking due to max_pages")
            break

        url = f"{base_url}/{page}"
        print(f"Fetching page {page}...")
        response = requests.get(url, params=params)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"API results count: {len(data.get('results', []))}")

        page_jobs = data.get("results", [])
        if not page_jobs:
            break

        for job in page_jobs:
            created_dt = datetime.fromisoformat(job["created"].rstrip("Z"))

            if newest_seen and created_dt <= newest_seen:
                return jobs

            jobs.append(job)

        page += 1

    return jobs