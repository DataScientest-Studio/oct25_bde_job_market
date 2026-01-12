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
    client = None
    try:
        # Create new client connection
        client = MongoClient(
            host='localhost',
            port=27017,
            username=os.getenv("MONGO_USER"),
            password=os.getenv("MONGO_PASS"),
            authSource="admin",
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        db = client.adzuna
        collection = db.jobs
        collection.create_index("id", unique=True)

        inserted_count = 0
        
        for job in jobs:
            job.pop('_id', None)
            result = collection.update_one(
                {"id": job["id"]},
                {"$setOnInsert": job},
                upsert=True
            )
            if result.upserted_id:
                inserted_count += 1

        if inserted_count:
            print(f"✅ Inserted {inserted_count} new jobs into MongoDB.")
        else:
            print("ℹ️  No new jobs to insert into MongoDB.")

        return inserted_count
        
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        raise
    finally:
        # Only close if client was created
        if client is not None:
            client.close()
