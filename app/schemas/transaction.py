from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionTypes

class TransactionBase(BaseModel):
    type: TransactionTypes
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    total_amount: float = Field(..., gt=0)

    @validator('type', pre=True)
    def lowercase_type(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

class TransactionCreate(TransactionBase):
    type: TransactionTypes
    product_id: int
    quantity: int
    unit_price: float
    total_amount: float
    payment_status: str
    payment_id: Optional[int] = None

class TransactionUpdate(BaseModel):
    payment_status: Optional[str] = None
    payment_id: Optional[str] = None

class TransactionInDB(TransactionBase):
    id: int
    payment_status: str
    payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
