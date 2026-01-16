import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Query
import json
# from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from src.data.main import main as ingestion_pipeline
from src.models.predict_model import predict_salary
from src.models.train_model import train_salary_model


load_dotenv()

api = FastAPI()

# System
@api.get("/health")
def check_health():
    return "API is functional"

# Ingestion
@api.put("/data")
def trigger_ingestion(max_pages:int = 5):
    """
    Fetches data from Adzuna and stores it in SQL and NoSQL Database.
    """
    ingestion_pipeline(max_pages = max_pages)
    return {"Status": "Ingestion complete"}

@api.put("/training")
def trigger_model_training():
    train_salary_model()
    return {"Status": "Training complete"}

@api.get("/data/postings")
def get_jobs(columns:List[str] = Query(...)):
    """
    Returnes stored data.
    """
    # Check requested columns
    sql_columns = ["title", "contract_type", "contract_time", "created_at", "ref_number", "redirect_url", "salary_is_predicted", "company_name", "city"]
    mongo_columns = ["description"]
    existing_columns = sql_columns + mongo_columns
    missing_columns = [col for col in columns if col not in existing_columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid column requested:{missing_columns}")
    
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
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="SQL Database access failed"
            )
        print("SQL Database access sucessfull")
        # Prepare Output 
        columns_to_extract = ["job_id"] + [col for col in columns if col in sql_columns]
        sql_df = df_main[columns_to_extract]
        sql_df = sql_df.fillna("NA")

    if any(col in mongo_columns for col in columns):
        try:
            MONGO_URI = os.getenv("MONGO_URI")
            client = MongoClient(MONGO_URI)
            db = client["adzuna"]
            collection = db["jobs"]

            cursor = collection.find( 
                    {},
                    {"_id": 0, "id": 1, "description": 1}
                )
            mongo_df = pd.DataFrame(list(cursor))
            mongo_df = mongo_df.rename(columns={"id": "job_id"})
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="MongoDB Database access failed"
            )
        print("MongoDB Database access sucessfull")

    if sql_df is not None and mongo_df is not None:
        merged_df = sql_df.merge(mongo_df, on="job_id", how="left")
        return merged_df.to_dict(orient="records")

    elif sql_df is not None:
        return sql_df.to_dict(orient="records")

    elif mongo_df is not None:
        return mongo_df.to_dict(orient="records")
    
    else:
        return []

@api.get("/data/predictions")
def get_predictions(job_title:str, job_description:str, city:str, contract_time:str, contract_type:str):
    """
    Gives salary predictions for job titles and job desciptions
    """
    salary = predict_salary(job_title=job_title,job_description=job_description,city=city,contract_time=contract_time,contract_type=contract_type)
    return {"Predicted Salary": salary}







