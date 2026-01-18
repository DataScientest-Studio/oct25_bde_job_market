from fastapi import FastAPI
from .routers.data import router as data_router
from .routers.ml import router as ml_router

app = FastAPI(title="Job Market API", version="1.0.0")

app.include_router(data_router)
app.include_router(ml_router)

@app.get("/health")
def check_health():
    return {"status": "API is functional"}
