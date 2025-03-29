from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PredictionBase(BaseModel):
    fraud_probability: float
    prediction_threshold: float
    predicted_class: bool
    features_used: List[str] = []
    
class PredictionCreate(PredictionBase):
    transaction_id: int
    model_id: int

class PredictionInDB(PredictionBase):
    prediction_id: int
    transaction_id: int
    model_id: int
    prediction_time: datetime
    explanation: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    transaction_id: int
    fraud_probability: float
    is_fraud: bool
    confidence: float
    prediction_time: datetime
    
    class Config:
        from_attributes = True