from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductInDB
from app.services.product_service import ProductService
from app.services.websocket_service import WebSocketService

router = APIRouter(prefix="/api/v1/products", tags=["products"])
ws_service = WebSocketService()

@router.post("/", response_model=ProductInDB)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    new_product = product_service.create_product(product)
    product_dict = {
        column.name: getattr(new_product, column.name)
        for column in new_product.__table__.columns
    }
    await ws_service.broadcast_message({"event": "product_created", "data": product_dict})  
    return new_product

@router.get("/", response_model=List[ProductInDB])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.get_products(skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductInDB)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductInDB)
async def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    updated_product = product_service.update_product(product_id, product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    await ws_service.broadcast_message({"event": "product_updated", "data": updated_product.dict()})
    return updated_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    if not product_service.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_service.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_service.broadcast_message({"message": data})
    except:
        await ws_service.disconnect(websocket)
