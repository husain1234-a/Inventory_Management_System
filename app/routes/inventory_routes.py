from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryInDB
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])

@router.post("/", response_model=InventoryInDB)
def create_inventory_item(inventory: InventoryCreate, db: Session = Depends(get_db)):
    inventory_service = InventoryService(db)
    return inventory_service.create_inventory_item(inventory)

@router.get("/", response_model=List[InventoryInDB])
def get_inventory_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    inventory_service = InventoryService(db)
    return inventory_service.get_inventory_items(skip=skip, limit=limit)

@router.get("/{item_id}", response_model=InventoryInDB)
def get_inventory_item(item_id: int, db: Session = Depends(get_db)):
    inventory_service = InventoryService(db)
    item = inventory_service.get_inventory_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@router.put("/{item_id}", response_model=InventoryInDB)
def update_inventory_item(item_id: int, inventory: InventoryUpdate, db: Session = Depends(get_db)):
    inventory_service = InventoryService(db)
    updated_item = inventory_service.update_inventory_item(item_id, inventory)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return updated_item

@router.delete("/{item_id}")
def delete_inventory_item(item_id: int, db: Session = Depends(get_db)):
    inventory_service = InventoryService(db)
    if not inventory_service.delete_inventory_item(item_id):
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"message": "Inventory item deleted successfully"}