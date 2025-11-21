import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB connection string from .env
MONGO_URI = os.getenv("MONGO_URI")

def store_jobs_nosql(jobs, start_date, end_date):
    """
    Filter jobs by creation date and insert into MongoDB.
    Used for batch imports with date filtering.
    """
    client = MongoClient(MONGO_URI)
    db = client.adzuna
    collection = db.jobs

    filtered_jobs = []
    for job in jobs:
        created_str = job.get("created")
        if created_str:
            # Remove 'Z' and parse ISO datetime
            created_date = datetime.fromisoformat(created_str.rstrip("Z"))
            if start_date <= created_date <= end_date:
                job.pop('_id', None)
                filtered_jobs.append(job)

    if filtered_jobs:
        collection.insert_many(filtered_jobs)
        print(f"Inserted {len(filtered_jobs)} jobs from API into MongoDB.")
    else:
        print("No jobs to insert for the specified date range.")

    client.close()

    return len(filtered_jobs)
