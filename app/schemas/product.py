from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    sku: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    supplier_id: int = Field(..., gt=0, description="ID of an existing supplier")


class ProductCreate(ProductBase):
    name: str
    description: Optional[str]
    sku: str
    price: float
    supplier_id: int


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    supplier_id: Optional[int] = None


class ProductInDB(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
