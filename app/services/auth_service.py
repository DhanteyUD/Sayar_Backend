from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional, Tuple

from app.models.user import User, UserRole
from app.models.merchant import Merchant, MerchantUser, MerchantRole, MembershipStatus
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.schemas.auth import MerchantSignupRequest, LoginRequest


class AuthService:
    @staticmethod
    def create_merchant_account(
            db: Session,
            signup_data: MerchantSignupRequest
    ) -> Tuple[User, Merchant, MerchantUser]:
        existing_user = db.query(User).filter(User.email == signup_data.email).first()

        if existing_user:
            raise ValueError("Email already registered")

        existing_merchant = db.query(Merchant).filter(
            Merchant.business_name == signup_data.business_name
        ).first()
        if existing_merchant:
            raise ValueError("Business name already taken")

        user = User(
            id=uuid4(),
            email=signup_data.email,
            first_name=signup_data.first_name,
            last_name=signup_data.last_name,
            phone=signup_data.phone,
            hashed_password=get_password_hash(signup_data.password),
            role=UserRole.MERCHANT,
            is_active=True,
            is_verified=False,
            verification_token=str(uuid4()),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(user)
        db.flush()

        merchant = Merchant(
            id=uuid4(),
            business_name=signup_data.business_name,
            is_active=True,
            is_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(merchant)
        db.flush()

        merchant_user = MerchantUser(
            id=uuid4(),
            merchant_id=merchant.id,
            user_id=user.id,
            role=MerchantRole.OWNER,
            status=MembershipStatus.ACTIVE,
            joined_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(merchant_user)
        db.commit()
        db.refresh(user)
        db.refresh(merchant)
        db.refresh(merchant_user)

        # TODO: Send verification email

        return user, merchant, merchant_user

    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> Optional[User]:
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user:
            return None

        if not verify_password(login_data.password, user.hashed_password):
            return None

        user.last_login_at = datetime.now(timezone.utc)
        db.commit()

        return user

    @staticmethod
    def generate_tokens(user_id: str) -> dict:
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    @staticmethod
    def verify_email(db: Session, token: str) -> bool:
        user = db.query(User).filter(User.verification_token == token).first()

        if not user:
            return False

        user.is_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        user.verification_token = None
        db.commit()

        return True

    @staticmethod
    def request_password_reset(db: Session, email: str) -> Optional[str]:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        reset_token = str(uuid4())
        user.reset_token = reset_token
        user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db.commit()

        # TODO: Send password reset email

        return reset_token

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        user = db.query(User).filter(User.reset_token == token).first()

        if not user:
            return False

        if user.reset_token_expires_at < datetime.now(timezone.utc):
            return False

        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires_at = None
        db.commit()

        return True
