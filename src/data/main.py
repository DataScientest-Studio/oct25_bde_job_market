from .fetch_api_data import fetch_jobs
from .postgres_db import store_jobs_sql, get_latest_job_date_sql
from .mongo_db import store_jobs_nosql
from datetime import timedelta

def main(max_pages=5, start_page=1):
    # Determine the newest job date we already have
    latest_job_date = get_latest_job_date_sql()

    # Refetch last 2 days to catch any missed jobs
    if latest_job_date:
        fetch_from = latest_job_date - timedelta(days=2)
        print(f"Fetching jobs newer than {fetch_from}")
        pages = max_pages
    else:
        fetch_from = None
        pages = max_pages
        print(f"No jobs in DB yet – initial fetch (limited to {pages} pages)")

    # Fetch jobs incrementally from API
    print("Fetching job listings...")
    result = fetch_jobs(newest_seen=fetch_from, max_pages=pages, start_page=start_page)
    jobs = result.get("jobs", [])
    next_start_page = result.get("next_start_page")
    print(f"Fetched {len(jobs)} candidate job(s).\n")

    # Store in Postgres
    print("Storing in SQL database (Postgres)...")
    store_jobs_sql(jobs)

    # Store in MongoDB
    print("Storing in NoSQL database (MongoDB)...")
    store_jobs_nosql(jobs)

    return {
        "status": "success",
        "jobs_fetched": len(jobs),
        "next_start_page": next_start_page,
    }

if __name__ == "__main__":
    main(max_pages=5)