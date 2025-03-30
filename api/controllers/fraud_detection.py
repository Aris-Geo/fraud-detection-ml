from sqlalchemy.orm import Session
from api.models.transaction import Transaction, FraudPrediction, MLModel
from api.schemas.transaction import TransactionCreate
from api.services.ml_model import model_service
from datetime import datetime

def get_active_model(db: Session):
    return db.query(MLModel).filter(MLModel.active == True).first()

def process_transaction(db: Session, transaction: TransactionCreate):
    # Process a transaction for fraud detection.
    
    # 1. Convert transaction to the right format for the model
    # 2. Use the model to predict fraud
    # 3. Store prediction in database
    # 4. Return the prediction result
    try:
        transaction_dict = transaction.dict()
        
        prediction_result = model_service.predict(transaction_dict)
        
        active_model = get_active_model(db)
        if active_model:
            latest_transaction = db.query(Transaction).order_by(Transaction.transaction_id.desc()).first()
            
            prediction = FraudPrediction(
                transaction_id=latest_transaction.transaction_id,
                model_id=active_model.model_id,
                fraud_probability=prediction_result["fraud_probability"],
                prediction_threshold=0.5,
                predicted_class=prediction_result["is_fraud"],
                features_used=["time", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10",
                              "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19", "v20",
                              "v21", "v22", "v23", "v24", "v25", "v26", "v27", "v28", "amount"],
                explanation={"importance": {}}
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
        
        prediction_result["transaction_id"] = latest_transaction.transaction_id
        prediction_result["prediction_time"] = datetime.now()
        
        return prediction_result
        
    except Exception as e:
        print(f"Error processing transaction: {e}")
        raise