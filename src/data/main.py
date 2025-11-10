from fetch_api_data import fetch_jobs
from postgres_db import store_jobs_sql
from mongo_db import store_jobs_nosql

def main():
    print("Fetching job listings...")
    jobs = fetch_jobs()

    print(f"Fetched {len(jobs)} jobs.")

    print("Storing in SQL database...")
    store_jobs_sql(jobs)

    print("Storing in NoSQL database...")
    store_jobs_nosql(jobs)

    print("Done!")

if __name__ == "__main__":
    main()