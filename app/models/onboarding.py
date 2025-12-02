from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
import uuid
import enum
from app.core.database import Base


class OnboardingStatus(str, enum.Enum):
    """Onboarding status enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class OnboardingStepStatus(str, enum.Enum):
    """Individual step status"""
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class BusinessCategory(str, enum.Enum):
    EDUCATION = "education"
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    FOOD_BEVERAGE = "food_beverage"
    HEALTH_BEAUTY = "health_beauty"
    HOME_GARDEN = "home_garden"
    RETAIL = "retail"
    SERVICES = "services"
    SPORTS_FITNESS = "sports_fitness"
    WHOLESALE = "wholesale"
    OTHER = "other"


class Currency(str, enum.Enum):
    NGN = "NGN"
    USD = "USD"
    GBP = "GBP"
    EUR = "EUR"


class MerchantOnboarding(Base):
    __tablename__ = "merchant_onboarding"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    merchant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False,
                                              index=True)

    # Overall Status
    status = Column(
        SQLEnum(
            OnboardingStatus,
            name="onboardingstatus",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=OnboardingStatus.NOT_STARTED,
        nullable=False
    )
    current_step = Column(Integer, default=1, nullable=False)  # 1-4

    # Step 1: Business Details
    business_details_status = Column(
        SQLEnum(
            OnboardingStepStatus,
            name="onboardingstepstatus",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=OnboardingStepStatus.PENDING,
        nullable=False
    )
    business_details_completed_at = Column(DateTime, nullable=True)

    # Step 2: WhatsApp Connection
    whatsapp_connection_status = Column(
        SQLEnum(
            OnboardingStepStatus,
            name="onboardingstepstatus",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=OnboardingStepStatus.PENDING,
        nullable=False
    )
    whatsapp_connection_completed_at = Column(DateTime, nullable=True)

    # Step 3: Meta Catalog ID
    catalog_id_status = Column(
        SQLEnum(
            OnboardingStepStatus,
            name="onboardingstepstatus",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=OnboardingStepStatus.PENDING,
        nullable=False
    )
    catalog_id_completed_at = Column(DateTime, nullable=True)

    # Step 4: Payment Details
    payment_details_status = Column(
        SQLEnum(
            OnboardingStepStatus,
            name="onboardingstepstatus",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=OnboardingStepStatus.PENDING,
        nullable=False
    )
    payment_details_completed_at = Column(DateTime, nullable=True)

    steps_completed = Column(Integer, default=0, nullable=False)
    total_steps = Column(Integer, default=4, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    # Completion
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    merchant = relationship("Merchant", backref="onboarding_progress")
    user = relationship("User")

    def __repr__(self):
        return f"<MerchantOnboarding {self.merchant_id} - {self.steps_completed}/{self.total_steps}>"

    @property
    def completion_percentage(self):
        return int((self.steps_completed / self.total_steps) * 100)

    def get_current_step(self):
        if self.business_details_status == OnboardingStepStatus.PENDING:
            return "business_details"
        elif self.whatsapp_connection_status == OnboardingStepStatus.PENDING:
            return "whatsapp_connection"
        elif self.catalog_id_status == OnboardingStepStatus.PENDING:
            return "catalog_id"
        elif self.payment_details_status == OnboardingStepStatus.PENDING:
            return "payment_details"
        else:
            return "completed"


class WhatsAppConfig(Base):
    """
    WhatsApp Business API configuration for merchants
    Stores Meta Cloud API credentials and settings
    """
    __tablename__ = "whatsapp_configs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    merchant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False,
                                              index=True)

    app_id = Column(String(255), nullable=False)
    app_secret = Column(Text, nullable=False)
    business_account_id = Column(String(255), nullable=False)
    phone_number_id = Column(String(255), nullable=False)
    whatsapp_phone_number = Column(String(20), nullable=False)

    access_token = Column(Text, nullable=False)

    encryption_salt = Column(Text, nullable=False)

    webhook_url = Column(Text, nullable=True)
    webhook_verify_token = Column(String(255), nullable=True)

    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    last_test_at = Column(DateTime, nullable=True)
    test_status = Column(String(50), nullable=True)  # success, failed, pending

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)
    verified_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", backref="whatsapp_config")

    def __repr__(self):
        return f"<WhatsAppConfig {self.merchant_id} - {self.whatsapp_phone_number}>"


class CatalogConfig(Base):
    """
    Meta Catalog configuration for product management
    Links merchant's product catalog with Meta's catalog system
    """
    __tablename__ = "catalog_configs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    merchant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False,
                                              index=True)

    catalog_id = Column(String(255), nullable=False)
    product_feed_url = Column(Text, nullable=True)

    feed_status = Column(String(50), default="pending", nullable=True)  # ready, pending, error
    last_sync_at = Column(DateTime, nullable=True)

    is_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)
    verified_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", backref="catalog_config")

    def __repr__(self):
        return f"<CatalogConfig {self.merchant_id} - {self.catalog_id}>"


class PaymentConfig(Base):
    """
    Payment configuration for merchants
    Stores bank account details for Paystack subaccount creation
    """
    __tablename__ = "payment_configs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    merchant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False,
                                              index=True)

    bank_name = Column(String(255), nullable=False)
    bank_code = Column(String(10), nullable=False)
    account_number = Column(String(20), nullable=False)
    account_name = Column(String(255), nullable=False)

    paystack_subaccount_code = Column(String(255), nullable=True, unique=True)
    paystack_subaccount_id = Column(String(255), nullable=True)

    settlement_percentage = Column(Integer, default=100, nullable=False)

    is_verified = Column(Boolean, default=False, nullable=False)
    verification_status = Column(String(50), default="pending", nullable=True)  # pending, verified, failed

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)
    verified_at = Column(DateTime, nullable=True)

    merchant = relationship("Merchant", backref="payment_config")

    def __repr__(self):
        return f"<PaymentConfig {self.merchant_id} - {self.bank_name}>"
