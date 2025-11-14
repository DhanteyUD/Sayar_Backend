from fastapi import APIRouter
from .endpoints import (
    auth,
    merchants,
    products,
    orders,
    payments,
    admin
)

# Create the main API router for v1
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
