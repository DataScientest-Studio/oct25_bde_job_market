import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# MongoDB connection string from .env
MONGO_URI = os.getenv("MONGO_URI")

logger = logging.getLogger(__name__)

def store_jobs_nosql(jobs):
    """
    Inserts jobs into MongoDB, avoiding duplicates.
    Uses the job 'id' field as unique identifier.
    Returns the number of NEW jobs inserted.
    """
    logger.info(f"[MONGO] Starting store_jobs_nosql with {len(jobs)} jobs")
    print(f"[MONGO] Starting store_jobs_nosql with {len(jobs)} jobs")
    client = None
    try:
        # Create new client connection
        client = MongoClient(MONGO_URI)
        
        # Test connection
        client.admin.command('ping')
        logger.info("✅ Connected to MongoDB")
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
            logger.info(f"✅ Inserted {inserted_count} new jobs into MongoDB.")
            print(f"✅ Inserted {inserted_count} new jobs into MongoDB.")
        else:
            logger.info("ℹ️  No new jobs to insert into MongoDB.")
            print("ℹ️  No new jobs to insert into MongoDB.")

        return inserted_count
        
    except Exception as e:
        import traceback
        logger.error(f"❌ MongoDB error: {e}")
        print(f"❌ MongoDB error: {e}")
        traceback.print_exc()
        raise
    finally:
        # Only close if client was created
        if client is not None:
            client.close()
