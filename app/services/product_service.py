from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product: ProductCreate) -> Product:
        # Check if product with same SKU already exists
        existing_product = (
            self.db.query(Product).filter(Product.sku == product.sku).first()
        )
        if existing_product:
            raise HTTPException(
                status_code=400, detail=f"Product with SKU {product.sku} already exists"
            )

        # Validate that supplier exists
        supplier = (
            self.db.query(Supplier).filter(Supplier.id == product.supplier_id).first()
        )
        if not supplier:
            raise HTTPException(
                status_code=400,
                detail=f"Supplier with id {product.supplier_id} not found",
            )

        db_product = Product(**product.model_dump(exclude_unset=True))
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.db.query(Product).offset(skip).limit(limit).all()

    def update_product(
        self, product_id: int, product: ProductUpdate
    ) -> Optional[Product]:
        db_product = self.get_product(product_id)
        if not db_product:
            return None

        update_data = product.dict(exclude_unset=True)

        # If supplier_id is being updated, validate it exists
        if "supplier_id" in update_data:
            supplier = (
                self.db.query(Supplier)
                .filter(Supplier.id == update_data["supplier_id"])
                .first()
            )
            if not supplier:
                raise HTTPException(
                    status_code=400,
                    detail=f"Supplier with id {update_data['supplier_id']} not found",
                )

        for field, value in update_data.items():
            setattr(db_product, field, value)

        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int) -> bool:
        db_product = self.get_product(product_id)
        if db_product:
            self.db.delete(db_product)
            self.db.commit()
            return True
        return False
