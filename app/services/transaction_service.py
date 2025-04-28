from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, transaction: TransactionCreate) -> Transaction:
        db_transaction = Transaction(
            type=transaction.type,
            product_id=transaction.product_id,
            quantity=transaction.quantity,
            unit_price=transaction.unit_price,
            total_amount=transaction.total_amount,
            payment_status="pending"  # Default status for new transactions
        )
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def get_transactions(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return self.db.query(Transaction).offset(skip).limit(limit).all()

    def update_transaction(self, transaction_id: int, transaction_update: TransactionUpdate) -> Optional[Transaction]:
        db_transaction = self.get_transaction(transaction_id)
        if not db_transaction:
            return None
            
        for field, value in transaction_update.dict(exclude_unset=True).items():
            setattr(db_transaction, field, value)
            
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    async def update_payment_status(self, transaction_id: int, status: str) -> Optional[Transaction]:
        db_transaction = self.get_transaction(transaction_id)
        if not db_transaction:
            return None
            
        db_transaction.payment_status = status
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction