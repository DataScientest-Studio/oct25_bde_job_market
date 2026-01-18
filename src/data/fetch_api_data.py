import os
import requests
import time

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

def fetch_jobs(category="it-jobs", country="de", results_per_page=50, newest_seen=None, max_pages=None):
    """
    Fetch jobs for a category with pagination up to max_pages.
    Uses an Airflow Variable to remember the next page to start from.
    After fetching, updates the Variable to last_page + 1.
    Respects limit of 25 page hits per minute.
    """
    base_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "category": category,
        "results_per_page": results_per_page,
        "sort_by": "date" # newest first
    }

    # Read starting page from Airflow Variable (default to 1 if not set)
    #start_page_str = Variable.get(page_var_name, default_var="1")
    #start_page = int(start_page_str)

    jobs = []
    page = 1
    # 25 hits per minute -> at least 60/25 ≈ 2.4 seconds between calls
    delay_seconds = 2.5

    for page in range(start_page, start_page + max_pages):
        url = f"{base_url}/{page}"
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        page_results = data.get("results", [])
        if not page_results:
            print(f"No results on page {page}, stopping.")
            last_page_fetched = page
            break

        # Add newest_seen check from secondary code
        if newest_seen:
            for job in page_results:
                created_dt = datetime.fromisoformat(job["created"])
                if created_dt <= newest_seen:
                    print(f"Reached jobs older than newest_seen on page {page}, stopping early.")
                    last_page_fetched = page  # Still update last_fetched
                    break  # Break the for-job loop
            else:
                # Continue to extend only if no early stop
                jobs.extend(page_results)
        else:
            # Original behavior without newest_seen
            jobs.extend(page_results)

        last_page_fetched = page
        print(f"Fetched page {page}, total jobs so far: {len(jobs)}")

        # Delay before next request
        time.sleep(delay_seconds)

    # If nothing was fetched, still move the pointer one page ahead of where tried
    if last_page_fetched is None:
        last_page_fetched = start_page - 1

    next_page = last_page_fetched + 1
    Variable.set(page_var_name, str(next_page))
    print(f"Updated Airflow Variable '{page_var_name}' to: {next_page}")

    return jobs
