from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .product import ProductResponse


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    total_price: float
    product: ProductResponse

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_name: str
    customer_phone: str
    customer_whatsapp_id: Optional[str] = None
    shipping_address: str
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    shipping_address: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    order_number: str
    merchant_id: int
    status: str
    total_amount: float
    currency: str
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    size: int
    pages: int