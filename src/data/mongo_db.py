import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def store_jobs_nosql(jobs):
    client = MongoClient(MONGO_URI)
    db = client["adzuna"]
    collection = db["jobs"]
    collection.insert_many(jobs)
    client.close()