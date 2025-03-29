from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from api.schemas.transaction import TransactionCreate, TransactionResponse, TransactionWithPrediction
from api.controllers.transaction import create_transaction, get_transaction, get_transactions
from api.dependencies.database import get_db
from api.core.security import get_api_key

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_api_key)]
)

@router.post("/", response_model=TransactionWithPrediction)
def create_new_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    db_transaction, prediction = create_transaction(db, transaction)
    
    result = TransactionResponse.from_orm(db_transaction)
    response = TransactionWithPrediction(
        **result.dict(),
        prediction=prediction
    )
    
    return response

@router.get("/{transaction_id}", response_model=TransactionResponse)
def read_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.get("/", response_model=List[TransactionResponse])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):

    transactions = get_transactions(db, skip=skip, limit=limit)
    return transactions