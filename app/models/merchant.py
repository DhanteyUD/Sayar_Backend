from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    business_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    business_email = Column(String(255), nullable=True)
    business_phone = Column(String(20), nullable=True)
    business_description = Column(Text, nullable=True)
    business_logo_url = Column(Text, nullable=True)

    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)

    category = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)

    tax_id = Column(String(100), nullable=True)

    paystack_subaccount_code = Column(String(255), nullable=True, Unique=True)
    paystack_integration_status = Column(Boolean, default=False)
    settlement_bank = Column(String(255), nullable=True)
    account_number = Column(String(255), nullable=True)

    whatsapp_number = Column(String(20), nullable=True)
    whatsapp_business_id = Column(String(255), nullable=True)
    whatsapp_webhook_url = Column(Text, nullable=True)
    whatsapp_verified = Column(Boolean, default=False)

    business_hours = Column(Text, nullable=True)
    timezone = Column(String(50), nullable=True)

    currency = Column(String(3), default="NGN", nullable=False)
    locale = Column(String(10), default="en-NG", nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    kyc_status = Column(String(50), default="pending", nullable=True)

    subscription_plan = Column(String(50), default="free", nullable=True)
    monthly_order_limit = Column(Integer, nullable=True)
    current_month_orders = Column(Integer, default=0)

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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    role = Column(SQLEnum(MerchantRole), nullable=False, default=MerchantRole.STAFF)

    status = Column(SQLEnum(MembershipStatus), nullable=False, default=MembershipStatus.ACTIVE)

    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    invitation_token = Column(String(255), nullable=True)
    invitation_expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)
    joined_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", back_populates="merchant_users")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    def __repr__(self):
        return f"<MerchantUser {self.user_id} - {self.merchant_id} ({self.role})>"
