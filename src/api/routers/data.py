from fastapi import APIRouter, HTTPException, Query, status, Body
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from sqlalchemy import create_engine
import logging
import os
from dotenv import load_dotenv
from src.data.main import main as ingestion_pipeline

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data", tags=["data"])

class IngestRequest(BaseModel):
    max_pages: Optional[int] = 5  # Default 5

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def trigger_ingestion(request: Optional[IngestRequest] = Body(None)):
    """Fetches fresh jobs from Adzuna API and upserts into Postgres/Mongo."""
    try:
        max_pages = request.max_pages if request else 5
        ingestion_pipeline(max_pages=max_pages)
        logger.info(f"Ingestion completed: {max_pages} pages")
        return {
            "status": "ingestion_accepted", 
            "pages_fetched": max_pages,
            "message": "Check logs/DB for inserted count"
        }
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/postings")
def get_jobs(columns: List[str] = Query(...)):
    """Returns stored job postings data."""
    sql_columns = ["title", "contract_type", "contract_time", "created_at", "ref_number", 
                   "redirect_url", "salary_is_predicted", "company_name", "city"]
    mongo_columns = ["description"]
    existing_columns = sql_columns + mongo_columns
    missing_columns = [col for col in columns if col not in existing_columns]
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Invalid columns requested: {missing_columns}")

    sql_df = None
    mongo_df = None

    if any(col in sql_columns for col in columns):
        try:
            engine = create_engine(os.getenv("PG_CONN"))
            df_main = pd.read_sql("""
                SELECT *
                FROM job
                LEFT JOIN company USING(company_id)
                LEFT JOIN location USING(location_id)
                LEFT JOIN category USING(category_id)
            """, engine)
            logger.info("SQL Database access successful")
            columns_to_extract = ["job_id"] + [col for col in columns if col in sql_columns]
            sql_df = df_main[columns_to_extract].fillna("NA")
        except Exception as e:
            logger.error(f"SQL Database access failed: {str(e)}")
            raise HTTPException(status_code=500, detail="SQL Database access failed")

    if any(col in mongo_columns for col in columns):
        try:
            from pymongo import MongoClient
            MONGO_URI = os.getenv("MONGO_URI")
            client = MongoClient(MONGO_URI)
            db = client["adzuna"]
            collection = db["jobs"]
            cursor = collection.find({}, {"_id": 0, "id": 1, "description": 1})
            mongo_df = pd.DataFrame(list(cursor))
            mongo_df = mongo_df.rename(columns={"id": "job_id"})
            logger.info("MongoDB Database access successful")
        except Exception as e:
            logger.error(f"MongoDB Database access failed: {str(e)}")
            raise HTTPException(status_code=500, detail="MongoDB Database access failed")

    if sql_df is not None and mongo_df is not None:
        merged_df = sql_df.merge(mongo_df, on="job_id", how="left")
        return merged_df.to_dict(orient="records")
    elif sql_df is not None:
        return sql_df.to_dict(orient="records")
    elif mongo_df is not None:
        return mongo_df.to_dict(orient="records")
    else:
        return []
