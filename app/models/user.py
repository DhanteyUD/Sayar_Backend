from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False, index=True)

    hashed_password = Column(String(255), nullable=False)

    avatar_url = Column(Text, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CUSTOMER)

    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onUpdate=datetime.now(timezone.utc))
    last_update_at = Column(DateTime, nullable=False)

    email_verified_at = Column(DateTime, nullable=True)
    verification_token = Column(String(255), nullable=True)

    reset_token = Column(String(255), nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)

    # Relationships (to be defined in other models)
    # merchants = relationship("Merchant", back_populates="user")
    # customer = relationship("Customer", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
