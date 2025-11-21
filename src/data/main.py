from fetch_api_data import fetch_jobs
from postgres_db import store_jobs_sql
from mongo_db import store_jobs_nosql
from datetime import datetime

def main():
    start_date = datetime.fromisoformat("2025-11-01")
    end_date = datetime.fromisoformat("2025-11-20")

    print("Fetching job listings...")
    jobs = fetch_jobs()
    print(f"Fetched {len(jobs)} job(s).\n")

    print("Storing in SQL database...")
    stored_count_sql = store_jobs_sql(jobs, start_date, end_date)
    #print(f"Stored {stored_count_sql} job(s).")
    
    print("Storing in NoSQL database...")
    stored_count_nosql = store_jobs_nosql(jobs, start_date, end_date)
    #print(f"Stored {stored_count_nosql} job(s).")
    
if __name__ == "__main__":
    main()