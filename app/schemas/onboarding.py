from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.onboarding import (
    OnboardingStatus,
    OnboardingStepStatus,
    BusinessCategory,
    Currency
)
import re


# ============================================================================
# Step 1: Business Details Schemas
# ============================================================================

class BusinessDetailsRequest(BaseModel):
    """Schema for Step 1: Business Details"""
    business_name: str = Field(..., min_length=2, max_length=255, description="Business name")
    business_email: EmailStr = Field(..., description="Business email")
    business_logo_url: Optional[str] = Field(None, description="URL to uploaded business logo")
    business_category: BusinessCategory
    operating_currency: Currency = Currency.NGN
    business_description: Optional[str] = Field(None, max_length=500, description="Business business description")
    business_phone: str = Field(..., min_length=10, max_length=20, description="Business phone number")

    address_line1: Optional[str] = Field(None, min_length=5, max_length=255, description="Address line 1")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")

    website: Optional[str] = Field(None, description="Business website URL")

    @field_validator("business_phone")
    @classmethod
    def validate_phone(cls, value):
        if not value:
            raise ValueError('Business phone number is required')

        phone = re.sub(r'[\s\-()]', '', value)

        if not re.match(r'^\+?[1-9]\d{9,14}$', phone):
            raise ValueError('Invalid phone number format. Use international format (e.g., +234XXXXXXXXXX)')

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
                "website": "https://mysayarstore.com"
            }
        }


# ============================================================================
# Step 2: WhatsApp Connection Schemas
# ============================================================================

class WhatsAppConnectionRequest(BaseModel):
    """Schema for Step 2: WhatsApp Connection"""
    app_id: str = Field(..., min_length=1, max_length=255, description="WhatsApp Business App ID from Meta")
    app_secret: str = Field(..., min_length=1, description="App Token (Secret) - Keep this secure")
    business_account_id: str = Field(..., min_length=1, max_length=255, description="WhatsApp Business Account ID")
    phone_number_id: str = Field(..., min_length=1, max_length=255,
                                 description="Phone Number ID associated with WhatsApp Business")
    whatsapp_phone_number: str = Field(..., description="WhatsApp Business phone number")
    access_token: str = Field(..., description="Long-lived access token from Meta")

    @field_validator('whatsapp_phone_number')
    @classmethod
    def validate_whatsapp_number(cls, value):
        """
        Validate WhatsApp phone number format (E.164)
        E.164 format: +[country code][number] (max 15 digits including country code)
        """
        if not value:
            raise ValueError('WhatsApp phone number is required')

        phone = re.sub(r'[\s\-()]', '', value)

        if not re.match(r'^\+[1-9]\d{10,14}$', phone):
            raise ValueError('WhatsApp number must be in E.164 format (e.g., +2348012345678)')
        return phone

    class Config:
        json_schema_extra = {
            "example": {
                "app_id": "sayar-merchant-12345",
                "app_secret": "...",
                "business_account_id": "123456789012345",
                "phone_number_id": "987654321098765",
                "whatsapp_phone_number": "+2348012345678",
                "access_token": "EAAwG...YourAccessToken...xYz"
            }
        }


class TestWhatsAppConnectionRequest(BaseModel):
    test_message: Optional[str] = "Testing Sayar WhatsApp connection"


class WhatsAppConnectionResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    whatsapp_phone_number: str
    is_verified: bool
    is_active: bool
    last_test_at: Optional[datetime] = None
    test_status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Step 3: Meta Catalog Schemas
# ============================================================================

class CatalogConnectionRequest(BaseModel):
    catalog_id: str = Field(..., description="Meta Catalog ID", min_length=1)
    product_feed_url: Optional[HttpUrl] = Field(None, description="Product feed URL")

    class Config:
        json_schema_extra = {
            "example": {
                "catalog_id": "1234567890",
                "product_feed_url": "https://example.com/sayar/"
            }
        }


class TestCatalogConnectionRequest(BaseModel):
    pass  # No additional data needed for testing


class CatalogConnectionResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    catalog_id: str
    product_feed_url: Optional[str] = None
    feed_status: Optional[str] = None
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Step 4: Payment Details Schemas
# ============================================================================

class PaymentDetailsRequest(BaseModel):
    bank_name: str = Field(..., description="Bank name")
    account_number: str = Field(..., min_length=10, max_length=10, description="10-digit account number")

    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v):
        """Validate Nigerian account number (10 digits)"""
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Account number must be exactly 10 digits')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "bank_name": "Access Bank",
                "account_number": "0123456789"
            }
        }


class PaymentDetailsResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    bank_name: str
    account_number: str
    account_name: str
    is_verified: bool
    verification_status: Optional[str] = None
    paystack_subaccount_code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Onboarding Progress Schemas
# ============================================================================

class OnboardingStepResponse(BaseModel):
    step_number: int
    step_name: str
    status: OnboardingStepStatus
    completed_at: Optional[datetime] = None


class OnboardingProgressResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    status: OnboardingStatus
    current_step: int
    steps_completed: int
    total_steps: int
    completion_percentage: int
    is_completed: bool

    business_details: OnboardingStepResponse
    whatsapp_connection: OnboardingStepResponse
    catalog_id: OnboardingStepResponse
    payment_details: OnboardingStepResponse

    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OnboardingStatusUpdate(BaseModel):
    message: str
    onboarding: OnboardingProgressResponse
