from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import pickle
import os
import pandas as pd
from src.models.train_model import train_salary_model
from src.models.predict_model import predict_salary

router = APIRouter(prefix="/ml", tags=["ml"])

class PredictInput(BaseModel):
    title: str
    company: str | None = None
    jobdescription: str = "General position requiring relevant skills."
    contracttype: str = "permanent"
    contracttime: str = "fulltime"
    city: str = "Berlin"
    country: str = "Deutschland"

@router.post("/train")
async def train_model_endpoint() -> Dict[str, Any]:
    """Train/retrain ML model via train_model.py (saves internally)."""
    train_salary_model()
    return {"status": "trained", "model_saved": "salarymodel.pkl (by train_model.py)"}

@router.post("/predict")
async def predict_endpoint(data: PredictInput) -> Dict[str, float]:
    """Predict salary via predict_model.py."""
    prediction = predict_salary(
        jobtitle=data.title,
        jobdescription=data.jobdescription,
        contracttype=data.contracttype,
        contracttime=data.contracttime,
        city=data.city,
        country=data.country
    )
    return {"predicted_salary": float(prediction)}
