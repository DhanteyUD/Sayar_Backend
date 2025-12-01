from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.MERCHANT
    agreed_to_terms: bool
    send_marketing_emails: bool = False


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    send_marketing_emails: Optional[bool] = None


class UserInDB(UserBase):
    id: UUID
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    agreed_to_terms: bool
    send_marketing_emails: bool

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    agreed_to_terms: bool
    send_marketing_emails: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+2348012345678",
                "role": "merchant",
                "is_active": True,
                "is_verified": True,
                "avatar_url": None,
                "agreed_to_terms": True,
                "send_marketing_emails": False,
                "created_at": "2024-01-01T00:00:00"
            }
        }

    class UserWithMerchantsResponse(BaseModel):
        id: UUID
        email: EmailStr
        first_name: str
        last_name: str
        phone: str
        role: UserRole
        is_active: bool
        is_verified: bool
        avatar_url: Optional[str] = None
        created_at: datetime
        agreed_to_terms: bool
        send_marketing_emails: bool

        merchants: List[dict] = []

        class Config:
            from_attributes = True
