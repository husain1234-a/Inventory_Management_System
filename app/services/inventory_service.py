from sqlalchemy.orm import Session
from app.models.inventory import InventoryItem
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from typing import List, Optional

class InventoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_inventory_item(self, inventory: InventoryCreate) -> InventoryItem:
        db_item = InventoryItem(**inventory.dict())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def get_inventory_item(self, item_id: int) -> Optional[InventoryItem]:
        return self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    
    def get_inventory_items(self, skip: int = 0, limit: int = 100) -> List[InventoryItem]:
        return self.db.query(InventoryItem).offset(skip).limit(limit).all()
    
    def update_inventory_item(self, item_id: int, inventory: InventoryUpdate) -> Optional[InventoryItem]:
        db_item = self.get_inventory_item(item_id)
        if db_item:
            update_data = inventory.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_item, field, value)
            self.db.commit()
            self.db.refresh(db_item)
        return db_item
    
    def delete_inventory_item(self, item_id: int) -> bool:
        db_item = self.get_inventory_item(item_id)
        if db_item:
            self.db.delete(db_item)
            self.db.commit()
            return True
        return False