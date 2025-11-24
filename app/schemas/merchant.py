from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.models.merchant import MerchantRole, MembershipStatus
import json


class MerchantBase(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=255)
    business_email: Optional[str] = None
    business_phone: Optional[str] = None
    business_description: Optional[str] = None
    business_logo_url: Optional[str] = None
    category: Optional[str] = None
    industry: Optional[str] = None


class MerchantCreate(MerchantBase):
    currency: Optional[str] = "NGN"
    merchant_timezone: Optional[str] = "Africa/Lagos"
    locale: Optional[str] = "en-NG"


class MerchantUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=2, max_length=255)
    business_email: Optional[str] = None
    business_phone: Optional[str] = None
    business_description: Optional[str] = None
    business_logo_url: Optional[str] = None
    category: Optional[str] = None
    industry: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    tax_id: Optional[str] = None

    whatsapp_number: Optional[str] = None

    settlement_bank: Optional[str] = None
    account_number: Optional[str] = None

    business_hours: Optional[str] = None
    merchant_timezone: Optional[str] = None

    currency: Optional[str] = None
    locale: Optional[str] = None

    @field_validator('business_hours')
    @classmethod
    def validate_business_hours(cls, v):
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('business_hours must be valid JSON')
        return v


class MerchantResponse(BaseModel):
    id: UUID
    business_name: str
    business_email: Optional[str] = None
    business_phone: Optional[str] = None
    business_description: Optional[str] = None
    business_logo_url: Optional[str] = None

    category: Optional[str] = None
    industry: Optional[str] = None

    paystack_integration_status: bool
    paystack_subaccount_code: Optional[str] = None

    whatsapp_number: Optional[str] = None
    whatsapp_verified: bool

    is_active: bool
    is_verified: bool
    kyc_status: Optional[str] = None

    subscription_plan: Optional[str] = None
    monthly_order_limit: Optional[int] = None
    current_month_orders: int

    currency: str
    merchant_timezone: Optional[str] = None
    locale: Optional[str] = None

    created_at: datetime
    verified_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MerchantDetailResponse(MerchantResponse):
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    tax_id: Optional[str] = None

    settlement_bank: Optional[str] = None
    account_number: Optional[str] = None

    business_hours: Optional[str] = None

    whatsapp_business_id: Optional[str] = None
    whatsapp_webhook_url: Optional[str] = None

    updated_at: datetime

    class Config:
        from_attributes = True


class MerchantUserResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    user_id: UUID
    role: MerchantRole
    status: MembershipStatus
    created_at: datetime
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MerchantWithUserRole(MerchantResponse):
    user_role: MerchantRole
    user_status: MembershipStatus

    class Config:
        from_attributes = True