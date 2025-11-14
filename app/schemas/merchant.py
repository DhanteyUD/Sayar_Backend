from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MerchantBase(BaseModel):
    business_name: str
    business_registration_number: str
    business_address: str
    industry_type: str
    business_category: str


class MerchantCreate(MerchantBase):
    paystack_account_number: str
    paystack_bank_code: str


class MerchantUpdate(BaseModel):
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    industry_type: Optional[str] = None
    business_category: Optional[str] = None
    whatsapp_business_account_id: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None
    whatsapp_access_token: Optional[str] = None
    meta_business_manager_id: Optional[str] = None
    meta_catalog_id: Optional[str] = None
    paystack_bank_code: Optional[str] = None
    paystack_account_number: Optional[str] = None


class MerchantResponse(MerchantBase):
    id: int
    owner_id: int
    whatsapp_business_account_id: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None
    whatsapp_access_token: Optional[str] = None
    whatsapp_verified: bool
    meta_business_manager_id: Optional[str] = None
    meta_catalog_id: Optional[str] = None
    paystack_subaccount_id: Optional[str] = None
    paystack_bank_code: Optional[str] = None
    paystack_account_number: Optional[str] = None
    onboarding_completed: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True