from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


class BusinessDetailsRequest(BaseModel):
    """Schema for Step 1: Business Details"""
    business_name: str = Field(..., min_length=2, max_length=255, description="Business name")
    business_email: EmailStr = Field(..., description="Business email")
    business_logo_url: Optional[str] = Field(None, description="URL to uploaded business logo")
    business_category: str = Field(..., description="Business category")
    operating_currency: str = Field(default="NGN", description="Operating currency (e.g., NGN)")
    business_description: str = Field(None, max_length=500, description="Business business description")
    business_phone: str = Field(..., description="Business phone number")

    address_line1: str = Field(..., min_length=5, max_length=255, description="Address line 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Address line 2")
    country: str = Field(..., description="Country")
    state: str = Field(..., description="State/Province")
    city: Optional[str] = Field(None, description="City")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP code")

    website: Optional[str] = Field(None, description="Business website URL")

    @field_validator("business_phone")
    @classmethod
    def validate_phone(cls, value):
        phone = re.sub(r'[\s\-()]', '', value)
        if not re.match(r'^\+?[1-9]\d{9,14}$', phone):
            raise ValueError('Invalid phone number format')
        return phone

    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "Sayar Retail Solutions",
                "business_email": "john@usesayar.com",
                "business_logo_url": "https://cloudinary.com/logo.png",
                "business_category": "retail",
                "operating_currency": "NGN",
                "business_description": "Provide a brief description of your business, products, or services...",
                "business_phone": "+234 801-234-5678",
                "address_line1": "123 Main Street",
                "address_line2": "Suite 100",
                "country": "Nigeria",
                "state": "Lagos",
                "city": "Ikeja",
                "postal_code": "100001",
                "website": "https://mysayarstore.com"
            }
        }


# class WhatsAppConnectionRequest(BaseModel):
#     """Schema for Step 2: WhatsApp Connection"""
#     whatsapp_number: str = Field(..., description="WhatsApp Business phone number")
#     whatsapp_business_id: Optional[str] = Field(None, description="WhatsApp Business Account ID")
#     verification_code: Optional[str] = Field(None, description="Verification code from WhatsApp")
#
#     @field_validator('whatsapp_number')
#     @classmethod
#     def validate_whatsapp_number(cls, v):
#         """Validate WhatsApp number format"""
#         phone = re.sub(r'[\s\-\(\)]', '', v)
#         if not re.match(r'^\+?[1-9]\d{9,14}$', phone):
#             raise ValueError('Invalid WhatsApp number format')
#         return phone
#
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "whatsapp_number": "+2348012345678",
#                 "whatsapp_business_id": "1234567890",
#                 "verification_code": "123456"
#             }
#         }


# class CatalogIDRequest(BaseModel):
#     """Schema for Step 3: Catalog ID"""
#     catalog_id: str = Field(..., min_length=1, max_length=255, description="Product catalog ID")
#     catalog_name: Optional[str] = Field(None, description="Catalog name/description")
#
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "catalog_id": "CAT-2024-001",
#                 "catalog_name": "Main Product Catalog"
#             }
#         }
#

# class PaymentDetailsRequest(BaseModel):
#     """Schema for Step 4: Payment Details"""
#     bank_name: str = Field(..., min_length=2, max_length=255, description="Bank name")
#     account_number: str = Field(..., min_length=10, max_length=20, description="Bank account number")
#     account_name: str = Field(..., min_length=2, max_length=255, description="Account holder name")
#     bank_code: Optional[str] = Field(None, description="Bank code")
#
#     # Tax information
#     tax_id: Optional[str] = Field(None, description="Business tax ID/VAT number")
#
#     @field_validator('account_number')
#     @classmethod
#     def validate_account_number(cls, v):
#         """Validate account number is numeric"""
#         if not v.isdigit():
#             raise ValueError('Account number must contain only digits')
#         if len(v) < 10:
#             raise ValueError('Account number must be at least 10 digits')
#         return v
#
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "bank_name": "First Bank of Nigeria",
#                 "account_number": "1234567890",
#                 "account_name": "Sayar Retail Solutions",
#                 "bank_code": "011",
#                 "tax_id": "12345678-0001"
#             }
#         }


class OnboardingStatusResponse(BaseModel):
    """Schema for onboarding status response"""
    merchant_id: UUID
    steps_completed: int
    total_steps: int
    completion_percentage: int
    is_completed: bool
    current_step: str

    # Step statuses
    business_details_status: str
    whatsapp_connection_status: str
    catalog_id_status: str
    payment_details_status: str

    # Completion timestamps
    business_details_completed_at: Optional[datetime] = None
    whatsapp_connection_completed_at: Optional[datetime] = None
    catalog_id_completed_at: Optional[datetime] = None
    payment_details_completed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OnboardingStepResponse(BaseModel):
    """Schema for individual step completion response"""
    step: str
    status: str
    message: str
    next_step: Optional[str] = None
    onboarding_progress: OnboardingStatusResponse

    class Config:
        from_attributes = True
