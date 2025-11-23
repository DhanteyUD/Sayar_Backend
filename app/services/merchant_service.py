from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy import and_
from sqlalchemy.engine import Row
from datetime import datetime, timezone
from uuid import uuid4, UUID
from typing import Optional, List, Tuple, Any

from app.models.merchant import Merchant, MerchantUser, MerchantRole, MembershipStatus
from app.models.user import User
from app.schemas.merchant import MerchantCreate, MerchantUpdate


class MerchantService:
    @staticmethod
    def get_merchant_by_id(db: Session, merchant_id: UUID) -> Optional[Merchant]:
        return db.query(Merchant).filter(Merchant.id == merchant_id).first()

    @staticmethod
    def get_merchant_by_business_name(db: Session, business_name: str) -> Optional[Merchant]:
        return db.query(Merchant).filter(Merchant.business_name == business_name).first()

    @staticmethod
    def get_user_merchants(db: Session, user_id: UUID) -> List[Row[tuple[Merchant, MerchantUser]]]:
        results = db.query(Merchant, MerchantUser).join(
            MerchantUser, Merchant.id == MerchantUser.merchant_id
        ).filter(
            and_(
                MerchantUser.user_id == user_id,
                MerchantUser.status == MembershipStatus.ACTIVE
            )
        ).all()

        return results

    @staticmethod
    def get_merchant_user_role(
            db: Session,
        merchant_id: UUID | str | InstrumentedAttribute[UUID],
        user_id: UUID | str | InstrumentedAttribute[UUID]
    ) -> Optional[MerchantUser]:
        return db.query(MerchantUser).filter(
            and_(
                MerchantUser.merchant_id == merchant_id,
                MerchantUser.user_id == user_id,
                MerchantUser.status == MembershipStatus.ACTIVE
            )
        ).first()

    @staticmethod
    def create_merchant(
            db: Session,
            merchant_data: MerchantCreate,
            owner_user_id: UUID
    ) -> Tuple[Merchant, MerchantUser]:
        existing = MerchantService.get_merchant_by_business_name(
            db,
            merchant_data.business_name
        )
        if existing:
            raise ValueError("Business name already exists")

        merchant = Merchant(
            id=uuid4(),
            business_name=merchant_data.business_name,
            business_email=merchant_data.business_email,
            business_phone=merchant_data.business_phone,
            business_description=merchant_data.business_description,
            business_logo_url=merchant_data.business_logo_url,
            category=merchant_data.category,
            industry=merchant_data.industry,
            currency=merchant_data.currency or "NGN",
            timezone=merchant_data.timezone or "Africa/Lagos",
            locale=merchant_data.locale or "en-NG",
            is_active=True,
            is_verified=False,
            kyc_status="pending",
            subscription_plan="free",
            current_month_orders=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(merchant)
        db.flush()

        merchant_user = MerchantUser(
            id=uuid4(),
            merchant_id=merchant.id,
            user_id=owner_user_id,
            role=MerchantRole.OWNER,
            status=MembershipStatus.ACTIVE,
            joined_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(merchant_user)
        db.commit()
        db.refresh(merchant)
        db.refresh(merchant_user)

        return merchant, merchant_user

    @staticmethod
    def update_merchant(
            db: Session,
            merchant_id: UUID,
            merchant_data: MerchantUpdate,
            user_id: UUID
    ) -> Merchant:
        """
        Update merchant information
        User must have OWNER or ADMIN role
        """
        merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, user_id)
        if not merchant_user or merchant_user.role not in [MerchantRole.OWNER, MerchantRole.ADMIN]:
            raise PermissionError("Insufficient permissions to update merchant")

        merchant = MerchantService.get_merchant_by_id(db, merchant_id)
        if not merchant:
            raise ValueError("Merchant not found")

        update_data = merchant_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(merchant, field, value)

        merchant.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(merchant)

        return merchant

    @staticmethod
    def deactivate_merchant(
            db: Session,
            merchant_id: UUID,
            user_id: UUID
    ) -> Merchant:
        """
        Deactivate merchant (soft delete)
        Only OWNER can deactivate
        """
        merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, user_id)
        if not merchant_user or merchant_user.role != MerchantRole.OWNER:
            raise PermissionError("Only owner can deactivate merchant")

        merchant = MerchantService.get_merchant_by_id(db, merchant_id)
        if not merchant:
            raise ValueError("Merchant not found")

        merchant.is_active = False
        merchant.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(merchant)

        return merchant

    @staticmethod
    def verify_merchant(
            db: Session,
            merchant_id: UUID
    ) -> Merchant:
        merchant = MerchantService.get_merchant_by_id(db, merchant_id)
        if not merchant:
            raise ValueError("Merchant not found")

        merchant.is_verified = True
        merchant.verified_at = datetime.now(timezone.utc)
        merchant.kyc_status = "verified"
        merchant.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(merchant)

        return merchant

    @staticmethod
    def invite_user_to_merchant(
            db: Session,
            merchant_id: UUID,
            inviter_user_id: UUID,
            invitee_email: str,
            role: MerchantRole = MerchantRole.STAFF
    ) -> MerchantUser:
        """
        Inviter must be OWNER or ADMIN
        """
        inviter_merchant_user = MerchantService.get_merchant_user_role(
            db, merchant_id, inviter_user_id
        )
        if not inviter_merchant_user or inviter_merchant_user.role not in [
            MerchantRole.OWNER, MerchantRole.ADMIN
        ]:
            raise PermissionError("Insufficient permissions to invite users")

        invitee = db.query(User).filter(User.email == invitee_email).first()
        if not invitee:
            raise ValueError("User not found")

        existing = MerchantService.get_merchant_user_role(db, merchant_id, invitee.id)
        if existing:
            raise ValueError("User is already a member of this merchant")

        merchant_user = MerchantUser(
            id=uuid4(),
            merchant_id=merchant_id,
            user_id=invitee.id,
            role=role,
            status=MembershipStatus.PENDING_INVITE,
            invited_by=inviter_user_id,
            invitation_token=str(uuid4()),
            invitation_expires_at=datetime.now(timezone.utc).replace(hour=23, minute=59, second=59) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(merchant_user)
        db.commit()
        db.refresh(merchant_user)

        # TODO: Send invitation email

        return merchant_user

    @staticmethod
    def accept_merchant_invitation(
            db: Session,
            invitation_token: str,
            user_id: UUID
    ) -> MerchantUser:
        merchant_user: Any | None = db.query(MerchantUser).filter(
            and_(
                MerchantUser.invitation_token == invitation_token,
                MerchantUser.user_id == user_id,
                MerchantUser.status == MembershipStatus.PENDING_INVITE
            )
        ).first()

        if not merchant_user:
            raise ValueError("Invalid invitation")

        if merchant_user.invitation_expires_at < datetime.now(timezone.utc):
            raise ValueError("Invitation has expired")

        merchant_user.status = MembershipStatus.ACTIVE
        merchant_user.joined_at = datetime.now(timezone.utc)
        merchant_user.invitation_token = None
        merchant_user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(merchant_user)

        return merchant_user

    @staticmethod
    def remove_user_from_merchant(
            db: Session,
            merchant_id: UUID,
            remover_user_id: UUID,
            user_to_remove_id: UUID
    ) -> MerchantUser:
        """
        OWNER and ADMIN can remove STAFF
        Only OWNER can remove ADMIN
        """
        remover = MerchantService.get_merchant_user_role(db, merchant_id, remover_user_id)
        if not remover:
            raise PermissionError("User is not a member of this merchant")

        user_to_remove = MerchantService.get_merchant_user_role(db, merchant_id, user_to_remove_id)
        if not user_to_remove:
            raise ValueError("User to remove not found in merchant")

        if user_to_remove.role == MerchantRole.OWNER:
            raise PermissionError("Cannot remove owner")

        if user_to_remove.role == MerchantRole.ADMIN and remover.role != MerchantRole.OWNER:
            raise PermissionError("Only owner can remove admin")

        if remover.role == MerchantRole.STAFF:
            raise PermissionError("Staff cannot remove users")

        user_to_remove.status = MembershipStatus.REMOVED
        user_to_remove.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user_to_remove)

        return user_to_remove

    @staticmethod
    def update_user_role(
            db: Session,
            merchant_id: UUID,
            updater_user_id: UUID,
            user_to_update_id: UUID,
            new_role: MerchantRole
    ) -> MerchantUser:
        """
        Only OWNER can change roles
        """
        updater = MerchantService.get_merchant_user_role(db, merchant_id, updater_user_id)
        if not updater or updater.role != MerchantRole.OWNER:
            raise PermissionError("Only owner can update user roles")

        user_to_update = MerchantService.get_merchant_user_role(db, merchant_id, user_to_update_id)
        if not user_to_update:
            raise ValueError("User not found in merchant")

        if user_to_update.role == MerchantRole.OWNER:
            raise PermissionError("Cannot change owner role")

        user_to_update.role = new_role
        user_to_update.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user_to_update)

        return user_to_update

    @staticmethod
    def get_merchant_users(
            db: Session,
            merchant_id: UUID,
            include_inactive: bool = False
    ) -> List[Row[Tuple[User, MerchantUser]]]:
        query = db.query(User, MerchantUser).join(
            MerchantUser, User.id == MerchantUser.user_id
        ).filter(MerchantUser.merchant_id == merchant_id)

        if not include_inactive:
            query = query.filter(MerchantUser.status == MembershipStatus.ACTIVE)

        return query.all()

    @staticmethod
    def increment_order_count(db: Session, merchant_id: UUID) -> Merchant:
        merchant = MerchantService.get_merchant_by_id(db, merchant_id)
        if not merchant:
            raise ValueError("Merchant not found")

        merchant.current_month_orders += 1
        merchant.last_active_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(merchant)

        return merchant

    @staticmethod
    def reset_monthly_order_count(db: Session, merchant_id: UUID) -> Merchant:
        merchant = MerchantService.get_merchant_by_id(db, merchant_id)
        if not merchant:
            raise ValueError("Merchant not found")

        merchant.current_month_orders = 0
        merchant.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(merchant)

        return merchant


from datetime import timedelta
