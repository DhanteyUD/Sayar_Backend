from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from typing import Optional
import uuid
import enum
from app.core.database import Base


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING_INVITE = "pending_invite"
    REMOVED = "removed"


class MerchantRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    STAFF = "staff"


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    business_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    business_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    business_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    business_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    business_logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    address_line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    tax_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    paystack_subaccount_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    paystack_integration_status: Mapped[bool] = mapped_column(Boolean, default=False)
    settlement_bank: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    whatsapp_business_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    whatsapp_webhook_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    whatsapp_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    business_hours: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    currency: Mapped[str] = mapped_column(String(3), default="NGN", nullable=False)
    locale: Mapped[Optional[str]] = mapped_column(String(10), default="en-NG", nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    kyc_status: Mapped[Optional[str]] = mapped_column(String(50), default="pending", nullable=True)

    subscription_plan: Mapped[Optional[str]] = mapped_column(String(50), default="free", nullable=True)
    monthly_order_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_month_orders: Mapped[int] = mapped_column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)
    verified_at = Column(DateTime, nullable=True)
    last_active_at = Column(DateTime, nullable=True)

    merchant_users = relationship("MerchantUser", back_populates="merchant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Merchant {self.business_name}>"


class MerchantUser(Base):
    __tablename__ = "merchant_users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    merchant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False,
                                              index=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    role: Mapped[MerchantRole] = mapped_column(SQLEnum(MerchantRole), nullable=False, default=MerchantRole.STAFF)

    status: Mapped[MembershipStatus] = mapped_column(SQLEnum(MembershipStatus), nullable=False,
                                                     default=MembershipStatus.ACTIVE)

    invited_by: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    invitation_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invitation_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)
    joined_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="merchant_users")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    def __repr__(self):
        return f"<MerchantUser {self.user_id} - {self.merchant_id} ({self.role})>"
