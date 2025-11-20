# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from datetime import datetime
# from enum import Enum
#
#
# class UserRole(str, Enum):
#     MERCHANT = "merchant"
#     ADMIN = "admin"
#     CUSTOMER = "customer"
#
#
# class UserBase(BaseModel):
#     email: EmailStr
#     phone_number: str
#     full_name: str
#
#
# class UserCreate(UserBase):
#     password: str
#     business_name: str  # For merchant registration
#
#
# class UserLogin(BaseModel):
#     email_or_phone: str
#     password: str
#
#
# class UserUpdate(BaseModel):
#     email: Optional[EmailStr] = None
#     phone_number: Optional[str] = None
#     full_name: Optional[str] = None
#     password: Optional[str] = None
#
#
# class UserResponse(UserBase):
#     id: int
#     role: UserRole
#     is_active: bool
#     is_verified: bool
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#
#     class Config:
#         from_attributes = True
#
#
# class Token(BaseModel):
#     access_token: str
#     refresh_token: str
#     token_type: str
#
#
# class TokenData(BaseModel):
#     user_id: Optional[int] = None
