from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime, timezone
import uuid
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MERCHANT = "merchant"
    CUSTOMER = "customer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    hashed_password = Column(String(255), nullable=False)

    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.CUSTOMER)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc))
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    agreed_to_terms: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    send_marketing_emails: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships (to be defined in other models)
    # merchants = relationship("Merchant", back_populates="user")
    # customer = relationship("Customer", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
