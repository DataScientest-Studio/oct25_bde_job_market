from src.data.fetch_api_data import fetch_jobs
from src.data.postgres_db import store_jobs_sql, get_latest_job_date_sql
# from src.data.mongo_db import store_jobs_nosql
from datetime import timedelta

def main(max_pages=5):
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
    jobs = fetch_jobs(newest_seen=fetch_from, max_pages=pages)
    print(f"Fetched {len(jobs)} candidate job(s).\n")

    # Store in Postgres
    print("Storing in SQL database (Postgres)...")
    store_jobs_sql(jobs)

    # Store in MongoDB
    print("Storing in NoSQL database (MongoDB)...")
    store_jobs_nosql(jobs)

if __name__ == "__main__":
    main(max_pages=5)