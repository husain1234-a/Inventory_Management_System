import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routes.product_routes import router as product_routes
from app.routes.inventory_routes import router as inventory_routes
from app.routes.supplier_routes import router as supplier_routes
from app.routes.auth import router as auth
from app.routes.transaction_routes import router as transaction_routes
from app.core.database import Base, engine

# Import all models to ensure they are registered with SQLAlchemy
# from app.models.inventory import InventoryItem
# from app.models.product import Product
# from app.models.supplier import Supplier
# from app.models.transaction import Transaction


def create_app():

    app = FastAPI(
        title="Inventory Management System API",
        description="API for the Inventory Management System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include all route modules
    app.include_router(product_routes)
    app.include_router(inventory_routes)
    app.include_router(supplier_routes)
    app.include_router(auth)
    app.include_router(transaction_routes)

    @app.on_event("startup")
    def startup_event():
        Base.metadata.create_all(bind=engine)

    return app
