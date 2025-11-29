from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional

from app.models.onboarding import MerchantOnboarding, OnboardingStatus
from app.models.merchant import Merchant
from app.schemas.onboarding import (
    BusinessDetailsRequest
)


class OnboardingService:
    """Service for merchant onboarding operations"""

    @staticmethod
    def get_or_create_onboarding(
            db: Session,
            merchant_id: UUID,
    ) -> Optional[MerchantOnboarding]:
        onboarding = db.query(MerchantOnboarding).filter(
            MerchantOnboarding.merchant_id == merchant_id,
        ).first()

        if not onboarding:
            onboarding = MerchantOnboarding(
                merchant_id=merchant_id,
                steps_completed=0,
                total_steps=4,
                is_completed=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(onboarding)
            db.commit()
            db.refresh(onboarding)

        return onboarding

    @staticmethod
    def complete_business_details(
            db: Session,
            merchant_id: UUID,
            data: BusinessDetailsRequest
    ) -> Optional[MerchantOnboarding]:
        merchant = db.query(Merchant).filter(
            Merchant.id == merchant_id).first()

        if not merchant:
            raise ValueError("Merchant not found")

        merchant.business_name = data.business_name
        merchant.business_email = str(data.business_email)
        merchant.business_logo_url = data.business_logo_url
        merchant.category = data.business_category
        merchant.currency = data.operating_currency
        merchant.business_description = data.business_description
        merchant.business_phone = data.business_phone
        merchant.address_line1 = data.address_line1
        merchant.address_line2 = data.address_line2
        merchant.country = data.country
        merchant.state = data.state
        merchant.city = data.city
        merchant.postal_code = data.postal_code
        merchant.updated_at = datetime.now(timezone.utc)

        onboarding = OnboardingService.get_or_create_onboarding(db, merchant_id)

        if onboarding.business_details_status != OnboardingStatus.COMPLETED:
            onboarding.business_details_status = OnboardingStatus.COMPLETED
            onboarding.business_details_completed_at = datetime.now(timezone.utc)
            onboarding.steps_completed += 1
            onboarding.updated_at = datetime.now(timezone.utc)

        OnboardingService._check_completion(onboarding)

        db.commit()
        db.refresh(onboarding)

        return onboarding

    @staticmethod
    def _check_completion(onboarding: MerchantOnboarding):
        """Check if all onboarding steps are completed"""
        if onboarding.steps_completed >= onboarding.total_steps:
            onboarding.is_completed = True
            if not onboarding.completed_at:
                onboarding.completed_at = datetime.now(timezone.utc)

    @staticmethod
    def get_onboarding_status(db: Session, merchant_id: UUID) -> Optional[MerchantOnboarding]:
        """Get onboarding status for merchant"""
        return db.query(MerchantOnboarding).filter(
            MerchantOnboarding.merchant_id == merchant_id
        ).first()

    @staticmethod
    def skip_step(
            db: Session,
            merchant_id: UUID,
            step: str
    ) -> MerchantOnboarding:
        """Skip an onboarding step"""
        onboarding = OnboardingService.get_or_create_onboarding(db, merchant_id)

        step_mapping = {
            "whatsapp_connection": "whatsapp_connection_status",
            "catalog_id": "catalog_id_status",
        }

        if step in step_mapping:
            attr = step_mapping[step]
            current_status = getattr(onboarding, attr)

            if current_status == OnboardingStatus.PENDING:
                setattr(onboarding, attr, OnboardingStatus.SKIPPED)
                onboarding.steps_completed += 1
                onboarding.updated_at = datetime.now(timezone.utc)

                OnboardingService._check_completion(onboarding)

                db.commit()
                db.refresh(onboarding)

        return onboarding
