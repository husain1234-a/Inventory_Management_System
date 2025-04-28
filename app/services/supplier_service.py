from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate

class SupplierService:
    def __init__(self, db: Session):
        self.db = db

    def create_supplier(self, supplier: SupplierCreate) -> Supplier:
        db_supplier = Supplier(
            name=supplier.name,
            contact_info=supplier.contact_info,
            address=supplier.address
        )
        self.db.add(db_supplier)
        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier

    def get_supplier(self, supplier_id: int) -> Optional[Supplier]:
        return self.db.query(Supplier).filter(Supplier.id == supplier_id).first()

    def get_suppliers(self, skip: int = 0, limit: int = 100) -> List[Supplier]:
        return self.db.query(Supplier).offset(skip).limit(limit).all()

    def update_supplier(self, supplier_id: int, supplier_update: SupplierUpdate) -> Optional[Supplier]:
        db_supplier = self.get_supplier(supplier_id)
        if not db_supplier:
            return None
            
        for field, value in supplier_update.dict(exclude_unset=True).items():
            setattr(db_supplier, field, value)
            
        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier

    def delete_supplier(self, supplier_id: int) -> bool:
        db_supplier = self.get_supplier(supplier_id)
        if not db_supplier:
            return False
            
        self.db.delete(db_supplier)
        self.db.commit()
        return True