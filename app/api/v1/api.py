from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter()

api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["Authentication"]
)

# Additional routers will be added here
# api_router.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
# api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])