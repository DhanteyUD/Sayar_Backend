from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


class MerchantSignupRequest(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    business_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    referral_code: Optional[str] = Field(None, max_length=50)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')
        return value

    @model_validator(mode='after')
    def password_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        phone = re.sub(r'[\s\-()]', '', value)
        if not re.match(r'^\+?[1-9]\d{9,14}$', phone):
            raise ValueError('Invalid phone number format')
        return phone

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+2348012345678",
                "business_name": "Simi Enterprises",
                "password": "SecurePass123",
                "confirm_password": "SecurePass123",
                "referral_code": "SAYAR123"
            }
        }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123",
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 604800
            }
        }


class TokenPayload(BaseModel):
    sub: UUID
    exp: datetime
    type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')
        return value

    @model_validator(mode='after')
    def password_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
