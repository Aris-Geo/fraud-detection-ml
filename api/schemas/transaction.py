from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from api.schemas.prediction import PredictionResponse

class TransactionBase(BaseModel):
    time: float
    v1: float
    v2: float
    v3: float
    v4: float
    v5: float
    v6: float
    v7: float
    v8: float
    v9: float
    v10: float
    v11: float
    v12: float
    v13: float
    v14: float
    v15: float
    v16: float
    v17: float
    v18: float
    v19: float
    v20: float
    v21: float
    v22: float
    v23: float
    v24: float
    v25: float
    v26: float
    v27: float
    v28: float
    amount: float

class TransactionCreate(TransactionBase):
    pass

class TransactionInDB(TransactionBase):
    transaction_id: int
    is_fraud: Optional[bool] = None
    processed_at: datetime
    source: str

    class Config:
        from_attributes = True

class TransactionResponse(TransactionInDB):
    pass

class TransactionWithPrediction(TransactionResponse):
    prediction: Optional[PredictionResponse] = None

class TransactionAnalytics(BaseModel):
    total_transactions: int
    fraud_count: int
    fraud_rate: float
    average_transaction_amount: float
    total_amount: float
    fraud_amount: float