from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ShippingBase(BaseModel):
    order_id: int
    carrier: str
    shipping_address: str
    estimated_delivery: Optional[datetime] = None


class ShippingCreate(ShippingBase):
    pass


class ShippingUpdate(BaseModel):
    status: Optional[str] = None
    tracking_number: Optional[str] = None
    actual_delivery: Optional[datetime] = None
    tracking_events: Optional[List[Dict[str, Any]]] = None


class TrackingEvent(BaseModel):
    timestamp: datetime
    location: str
    status: str
    description: str


class ShippingResponse(ShippingBase):
    id: int
    tracking_number: str
    status: str
    actual_delivery: Optional[datetime] = None
    tracking_events: List[TrackingEvent] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ShippingRateRequest(BaseModel):
    from_address: Dict[str, str]
    to_address: Dict[str, str]
    package_details: Dict[str, Any]


class ShippingRateResponse(BaseModel):
    carrier: str
    service: str
    rate: float
    days: int
    currency: str = "NGN"
