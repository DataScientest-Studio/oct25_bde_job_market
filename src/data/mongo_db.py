import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB connection string from .env
MONGO_URI = os.getenv("MONGO_URI")

def store_jobs_nosql(jobs):
    """
    Inserts jobs into MongoDB, avoiding duplicates.
    Uses the job 'id' field as unique identifier.
    Returns the number of NEW jobs inserted.
    """
    client = MongoClient(MONGO_URI)
    db = client.adzuna
    collection = db.jobs
    collection.create_index("id", unique=True)

    inserted_count = 0
    
    for job in jobs:
        # Remove MongoDB _id if present
        job.pop('_id', None)
        result = collection.update_one(
            {"id": job["id"]},        # find job by unique Adzuna ID
            {"$setOnInsert": job},    # insert only if not exists
            upsert=True
        )
        if result.upserted_id:        # increment if a new job was actually inserted
            inserted_count += 1

    if inserted_count:
        print(f"Inserted {inserted_count} new jobs into MongoDB.")
    else:
        print("No new jobs to insert into MongoDB.")

    client.close()
    return inserted_count
