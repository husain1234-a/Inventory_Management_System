from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class InventoryBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=0)
    location: str = Field(..., min_length=1, max_length=100)

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, min_length=1, max_length=100)

class InventoryInDB(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True