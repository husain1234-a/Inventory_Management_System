from pydantic import BaseModel

class SupplierBase(BaseModel):
    name: str
    contact_info: str
    address: str

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: str | None = None
    contact_info: str | None = None
    address: str | None = None

class SupplierResponse(SupplierBase):
    id: int

    class Config:
        orm_mode = True