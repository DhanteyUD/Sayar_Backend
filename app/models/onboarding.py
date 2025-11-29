from sqlalchemy import Column, Boolean, DateTime, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
import uuid
import enum
from app.core.database import Base


class OnboardingStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class MerchantOnboarding(Base):
    __tablename__ = "merchant_onboarding"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    merchant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False,
                                              index=True)

    business_details_status = Column(SQLEnum(OnboardingStatus), default=OnboardingStatus.PENDING, nullable=False)
    whatsapp_connection_status = Column(SQLEnum(OnboardingStatus), default=OnboardingStatus.PENDING, nullable=False)
    catalog_id_status = Column(SQLEnum(OnboardingStatus), default=OnboardingStatus.PENDING, nullable=False)
    payment_details_status = Column(SQLEnum(OnboardingStatus), default=OnboardingStatus.PENDING, nullable=False)

    steps_completed = Column(Integer, default=0, nullable=False)
    total_steps = Column(Integer, default=4, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    business_details_completed_at = Column(DateTime, nullable=True)
    whatsapp_connection_completed_at = Column(DateTime, nullable=True)
    catalog_id_completed_at = Column(DateTime, nullable=True)
    payment_details_completed_at = Column(DateTime, nullable=True)

    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                        nullable=False)

    merchant = relationship("Merchant", backref="onboarding")

    def __repr__(self):
        return f"<MerchantOnboarding {self.merchant_id} - {self.steps_completed}/{self.total_steps}>"

    @property
    def completion_percentage(self):
        return int((self.steps_completed / self.total_steps) * 100)

    def get_current_step(self):
        if self.business_details_status == OnboardingStatus.PENDING:
            return "business_details"
        elif self.whatsapp_connection_status == OnboardingStatus.PENDING:
            return "whatsapp_connection"
        elif self.catalog_id_status == OnboardingStatus.PENDING:
            return "catalog_id"
        elif self.payment_details_status == OnboardingStatus.PENDING:
            return "payment_details"
        else:
            return "completed"


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
