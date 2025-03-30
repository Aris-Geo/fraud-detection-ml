from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import transactions
from api.models.transaction import MLModel
from api.dependencies.database import engine, Base, SessionLocal
from api.core.config import settings
from api.services.ml_model import model_service

Base.metadata.create_all(bind=engine)

def init_ml_model():
    db = SessionLocal()
    model_exists = db.query(MLModel).first() is not None
    
    if not model_exists:
        model = MLModel(
            model_name="RandomForest",
            description="Initial fraud detection model",
            performance_metrics={
                "accuracy": 0.95,
                "precision": 0.92,
                "recall": 0.89,
                "f1": 0.90
            },
            active=True
        )
        db.add(model)
        db.commit()
    
    db.close()

app = FastAPI(
    title="Fraud Detection API",
    description="API for detecting fraudulent financial transactions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)

@app.on_event("startup")
async def startup_event():
    init_ml_model()

@app.on_event("shutdown")
async def shutdown_event():
    pass

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Fraud Detection API",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    init_ml_model()
    
    if model_service.model is None:
        print("WARNING: ML model could not be loaded! Predictions will fail!")
    else:
        print("ML model loaded successfully and ready for predictions")