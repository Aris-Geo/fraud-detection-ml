import pandas as pd
import pickle
import os
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from api.models.transaction import Transaction, FraudPrediction, MLModel
from api.schemas.transaction import TransactionCreate
from api.dependencies.storage import minio_client

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml_models", "fraud_model.pkl")

model = None
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

def get_active_model(db: Session):
    return db.query(MLModel).filter(MLModel.active == True).first()

def process_transaction(db: Session, transaction: TransactionCreate):
    # Process a transaction
    
    # 1. Convert transaction to the right format for the model
    # 2. Use the model to predict fraud
    # 3. Store prediction in database
    # 4. Return the prediction result
    if model is None:
        raise ValueError("ML model not loaded")
    
    df = pd.DataFrame([transaction.dict()])
    
    feature_cols = [
        'time', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10',
        'v11', 'v12', 'v13', 'v14', 'v15', 'v16', 'v17', 'v18', 'v19', 'v20',
        'v21', 'v22', 'v23', 'v24', 'v25', 'v26', 'v27', 'v28', 'amount'
    ]
    
    fraud_prob = model.predict_proba(df[feature_cols])[0, 1]
    threshold = 0.5
    is_fraud = fraud_prob > threshold
    
    # Calculate confidence (higher when closer to 0 or 1)
    confidence = 2 * abs(fraud_prob - 0.5)
    
    active_model = get_active_model(db)
    if active_model:
        prediction = FraudPrediction(
            transaction_id=db.query(Transaction).order_by(Transaction.transaction_id.desc()).first().transaction_id,
            model_id=active_model.model_id,
            fraud_probability=float(fraud_prob),
            prediction_threshold=threshold,
            predicted_class=bool(is_fraud),
            features_used=feature_cols,
            explanation={"importance": {}}  # Simplified explanation
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
    
    return {
        "transaction_id": prediction.transaction_id,
        "fraud_probability": fraud_prob,
        "is_fraud": is_fraud,
        "confidence": confidence,
        "prediction_time": datetime.now()
    }