from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.dependencies.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    time = Column(Float)
    v1 = Column(Float)
    v2 = Column(Float)
    v3 = Column(Float)
    v4 = Column(Float)
    v5 = Column(Float)
    v6 = Column(Float)
    v7 = Column(Float)
    v8 = Column(Float)
    v9 = Column(Float)
    v10 = Column(Float)
    v11 = Column(Float)
    v12 = Column(Float)
    v13 = Column(Float)
    v14 = Column(Float)
    v15 = Column(Float)
    v16 = Column(Float)
    v17 = Column(Float)
    v18 = Column(Float)
    v19 = Column(Float)
    v20 = Column(Float)
    v21 = Column(Float)
    v22 = Column(Float)
    v23 = Column(Float)
    v24 = Column(Float)
    v25 = Column(Float)
    v26 = Column(Float)
    v27 = Column(Float)
    v28 = Column(Float)
    amount = Column(Float)
    is_fraud = Column(Boolean, nullable=True)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(50), default="api")
    
    predictions = relationship("FraudPrediction", back_populates="transaction")

class FraudPrediction(Base):
    __tablename__ = "fraud_predictions"
    
    prediction_id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.transaction_id"))
    model_id = Column(Integer, ForeignKey("ml_models.model_id"))
    fraud_probability = Column(Float, nullable=False)
    prediction_threshold = Column(Float, nullable=False)
    predicted_class = Column(Boolean, nullable=False)
    prediction_time = Column(DateTime(timezone=True), server_default=func.now())
    features_used = Column(JSON)
    explanation = Column(JSON)
    
    transaction = relationship("Transaction", back_populates="predictions")
    model = relationship("MLModel")

class MLModel(Base):
    __tablename__ = "ml_models"
    
    model_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    performance_metrics = Column(JSON)
    active = Column(Boolean, default=False)