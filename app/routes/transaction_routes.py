from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionInDB
from app.services.transaction_service import TransactionService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

@router.post("/", response_model=TransactionInDB)
async def create_transaction(
    transaction: TransactionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    transaction_service = TransactionService(db)
    payment_service = PaymentService()
    
    # Create transaction record
    new_transaction = transaction_service.create_transaction(transaction)
    
    # Process payment in background
    background_tasks.add_task(
        payment_service.process_payment,
        new_transaction.id,
        new_transaction.total_amount
    )
    
    return new_transaction

@router.get("/", response_model=List[TransactionInDB])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    return transaction_service.get_transactions(skip=skip, limit=limit)

@router.get("/{transaction_id}", response_model=TransactionInDB)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    transaction = transaction_service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/{transaction_id}", response_model=TransactionInDB)
def update_transaction(transaction_id: int, transaction: TransactionUpdate, db: Session = Depends(get_db)):
    transaction_service = TransactionService(db)
    updated_transaction = transaction_service.update_transaction(transaction_id, transaction)
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction

@router.post("/webhook")
async def payment_webhook(payload: dict, db: Session = Depends(get_db)):
    payment_service = PaymentService()
    transaction_service = TransactionService(db)
    
    # Verify and process the webhook
    event = payment_service.verify_webhook(payload)
    if event:
        await transaction_service.update_payment_status(
            event.get("transaction_id"),
            event.get("status")
        )
    return {"status": "success"}