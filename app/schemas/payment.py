from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class PaymentBase(BaseModel):
    order_id: int
    amount: float
    currency: str = "NGN"


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    paystack_reference: str
    paystack_transaction_id: Optional[str] = None
    status: str
    payment_method: Optional[str] = None
    paystack_response: Optional[Dict[str, Any]] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentInitializeResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str


class PaymentVerificationResponse(BaseModel):
    status: str
    message: str
    data: Optional[PaymentResponse] = None