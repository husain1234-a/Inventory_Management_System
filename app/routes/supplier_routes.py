from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.services.supplier_service import SupplierService

router = APIRouter(
    prefix="/suppliers",
    tags=["suppliers"]
)

@router.post("/", response_model=SupplierResponse)
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    supplier_service = SupplierService(db)
    return supplier_service.create_supplier(supplier)

@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier_service = SupplierService(db)
    supplier = supplier_service.get_supplier(supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.get("/", response_model=List[SupplierResponse])
def get_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    supplier_service = SupplierService(db)
    return supplier_service.get_suppliers(skip=skip, limit=limit)

@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, supplier: SupplierUpdate, db: Session = Depends(get_db)):
    supplier_service = SupplierService(db)
    updated_supplier = supplier_service.update_supplier(supplier_id, supplier)
    if updated_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return updated_supplier

@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier_service = SupplierService(db)
    if not supplier_service.delete_supplier(supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted successfully"}