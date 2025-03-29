import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from api.models.transaction import Transaction
from api.schemas.transaction import TransactionCreate
from api.services.message_queue import rabbitmq_client
from api.dependencies.storage import minio_client
from api.controllers.fraud_detection import process_transaction

def create_transaction(db: Session, transaction: TransactionCreate):
    db_transaction = Transaction(
        time=transaction.time,
        v1=transaction.v1, v2=transaction.v2, v3=transaction.v3,
        v4=transaction.v4, v5=transaction.v5, v6=transaction.v6,
        v7=transaction.v7, v8=transaction.v8, v9=transaction.v9,
        v10=transaction.v10, v11=transaction.v11, v12=transaction.v12,
        v13=transaction.v13, v14=transaction.v14, v15=transaction.v15,
        v16=transaction.v16, v17=transaction.v17, v18=transaction.v18,
        v19=transaction.v19, v20=transaction.v20, v21=transaction.v21,
        v22=transaction.v22, v23=transaction.v23, v24=transaction.v24,
        v25=transaction.v25, v26=transaction.v26, v27=transaction.v27,
        v28=transaction.v28,
        amount=transaction.amount,
        source="api"
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    transaction_data = transaction.dict()
    transaction_data["transaction_id"] = db_transaction.transaction_id
    transaction_data["timestamp"] = datetime.now().isoformat()
    
    minio_key = minio_client.store_transaction(transaction_data)
    
    rabbitmq_client.publish_transaction(transaction_data)
    
    prediction = process_transaction(db, transaction)
    
    return db_transaction, prediction

def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transaction).offset(skip).limit(limit).all()