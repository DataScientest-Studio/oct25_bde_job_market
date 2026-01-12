import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Query
import json
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from src.data.main import main as ingestion_pipeline
from src.models.predict_model import predict_salary


load_dotenv()

api = FastAPI()

# System
@api.get("/health")
def check_health():
    return "API is functional"

# Ingestion
@api.put("/data")
def trigger_ingestion(max_pages:int):
    """
    Fetches data from Adzuna and stores it in SQL and NoSQL Database.
    """
    ingestion_pipeline(max_pages = max_pages)
    return {"Status": "ingestion complete"}
#?
# @api.put("/data/predictions")
# def trigger_training():

# db = client[DATABASE_NAME]
# GET/Dashboard
@api.get("/data/postings")
def get_jobs(columns:List[str] = Query(...)):
    """
    Returnes stored data.
    """
    try:
        engine = create_engine(os.getenv("PG_CONN"))
        df_main = pd.read_sql("""
                            SELECT * 
                            FROM job 
                            LEFT JOIN company USING(company_id)
                            LEFT JOIN location USING(location_id)
                            LEFT JOIN category USING(category_id)
                            """, engine)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Database access failed"
        )
    print("Database access sucessfull")
    # Check requested columns
    existing_columns = df_main.columns
    missing_columns = [col for col in columns if col not in existing_columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid column requested:{missing_columns}")
    # Prepare Output 
    job_postings = df_main[columns]
    job_postings = job_postings.fillna("NA")
    # Close engine
    engine.dispose()
    return json.loads(job_postings.to_json())


@api.get("/data/predictions")
def get_predictions(job_title:str, job_description:str):
    """
    Gives salary predictions for job titles and job desciptions
    """
    salary = predict_salary(job_title=job_title,job_description=job_description)
    return {"Predicted Salary": salary}







