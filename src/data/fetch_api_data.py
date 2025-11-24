import os
from math import ceil
from dotenv import load_dotenv
import requests

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

def fetch_jobs(category="it-jobs", country="de", results_per_page=50, max_pages=None):
    """
    Fetch all jobs for a category with pagination.
    If max_pages is given, it will stop after that many pages (for testing).
    """
    base_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "category": category,
        "results_per_page": results_per_page
    }

    # First call: page 1, get total count
    page = 1
    url = f"{base_url}/{page}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    total_count = data.get("count", 0)
    jobs = data.get("results", [])

    # How many pages total?
    total_pages = ceil(total_count / results_per_page) if total_count else 1
    if max_pages is not None:
        total_pages = min(total_pages, max_pages)
    
    # Remaining pages
    for page in range(2, total_pages + 1):
        url = f"{base_url}/{page}"
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        page_data = resp.json()
        jobs.extend(page_data.get("results", []))

    return jobs


