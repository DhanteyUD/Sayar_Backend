from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, Tuple

from app.models.onboarding import (
    MerchantOnboarding,
    WhatsAppConfig,
    CatalogConfig,
    PaymentConfig,
    OnboardingStatus,
    OnboardingStepStatus
)
from app.models.merchant import Merchant
from app.schemas.onboarding import (
    BusinessDetailsRequest,
    WhatsAppConnectionRequest,
    CatalogConnectionRequest,
    PaymentDetailsRequest
)
from app.utils.encryption import get_encryption_service


class OnboardingService:
    """Service for merchant onboarding operations"""

    @staticmethod
    def get_or_create_onboarding(
            db: Session,
            merchant_id: UUID,
            user_id: UUID
    ) -> MerchantOnboarding:
        onboarding = db.query(MerchantOnboarding).filter(
            MerchantOnboarding.merchant_id == merchant_id,
        ).first()

        if not onboarding:
            onboarding = MerchantOnboarding(
                merchant_id=merchant_id,
                user_id=user_id,
                status=OnboardingStatus.IN_PROGRESS.value,
                current_step=1,
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
    ) -> Tuple[Merchant, MerchantOnboarding]:
        """Complete Step 1: Business Details"""

        merchant: Optional[Merchant] = db.query(Merchant).filter(
            Merchant.id == merchant_id).first()

        if not merchant:
            raise ValueError("Merchant not found")

        merchant.business_name = data.business_name
        merchant.business_email = str(data.business_email)
        merchant.business_logo_url = data.business_logo_url
        merchant.category = data.business_category.value
        merchant.currency = data.operating_currency.value
        merchant.business_description = data.business_description
        merchant.business_phone = data.business_phone
        merchant.address_line1 = data.address_line1
        merchant.country = data.country
        merchant.state = data.state
        merchant.updated_at = datetime.now(timezone.utc)

        onboarding: Optional[MerchantOnboarding] = db.query(MerchantOnboarding).filter(
            MerchantOnboarding.merchant_id == merchant_id
        ).first()

        if not onboarding:
            raise ValueError("Onboarding record not found")

        onboarding.business_details_status = OnboardingStatus.COMPLETED.value
        onboarding.business_details_completed_at = datetime.now(timezone.utc)
        onboarding.steps_completed = OnboardingService._count_completed_steps(onboarding)
        onboarding.current_step = 2
        onboarding.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(merchant)
        db.refresh(onboarding)

        return merchant, onboarding

    @staticmethod
    def complete_whatsapp_connection(
            db: Session,
            merchant_id: UUID,
            data: WhatsAppConnectionRequest
    ) -> Tuple[WhatsAppConfig, MerchantOnboarding]:
        """Complete Step 2: WhatsApp Connection"""

        encryption_service = get_encryption_service()

        encrypted_app_secret = encryption_service.encrypt(data.app_secret)
        encrypted_access_token = encryption_service.encrypt(data.access_token)

        encryption_salt = encryption_service.get_salt()

        whatsapp_config = db.query(WhatsAppConfig).filter(
            WhatsAppConfig.merchant_id == merchant_id
        ).first()

        if whatsapp_config:
            whatsapp_config.app_id = data.app_id
            whatsapp_config.app_secret = encrypted_app_secret
            whatsapp_config.business_account_id = data.business_account_id
            whatsapp_config.phone_number_id = data.phone_number_id
            whatsapp_config.whatsapp_phone_number = data.whatsapp_phone_number
            whatsapp_config.access_token = encrypted_access_token
            whatsapp_config.encryption_salt = encryption_salt
            whatsapp_config.updated_at = datetime.now(timezone.utc)
        else:
            whatsapp_config = WhatsAppConfig(
                merchant_id=merchant_id,
                app_id=data.app_id,
                app_secret=encrypted_app_secret,
                business_account_id=data.business_account_id,
                phone_number_id=data.phone_number_id,
                whatsapp_phone_number=data.whatsapp_phone_number,
                access_token=encrypted_access_token,
                encryption_salt=encryption_salt,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(whatsapp_config)

        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if merchant:
            merchant.whatsapp_number = data.whatsapp_phone_number
            merchant.whatsapp_business_id = data.business_account_id

        onboarding: Optional[MerchantOnboarding] = db.query(MerchantOnboarding).filter(
            MerchantOnboarding.merchant_id == merchant_id
        ).first()

        if not onboarding:
            raise ValueError("Onboarding record not found")

        onboarding.whatsapp_connection_status = OnboardingStepStatus.COMPLETED.value
        onboarding.whatsapp_connection_completed_at = datetime.now(timezone.utc)
        onboarding.steps_completed = OnboardingService._count_completed_steps(onboarding)
        onboarding.current_step = 3
        onboarding.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(whatsapp_config)
        db.refresh(onboarding)

        return whatsapp_config, onboarding

    @staticmethod
    def test_whatsapp_connection(
            db: Session,
            merchant_id: UUID
    ) -> bool:
        whatsapp_config = db.query(WhatsAppConfig).filter(
            WhatsAppConfig.merchant_id == merchant_id
        ).first()

        if not whatsapp_config:
            raise ValueError("WhatsApp configuration not found")

        # TODO: Implement actual Meta Cloud API test
        # For now, just mark as tested
        whatsapp_config.last_test_at = datetime.now(timezone.utc)
        whatsapp_config.test_status = "success"
        whatsapp_config.is_verified = True
        whatsapp_config.verified_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(whatsapp_config)

        return True

    @staticmethod
    def complete_catalog_connection(
            db: Session,
            merchant_id: UUID,
            data: CatalogConnectionRequest
    ) -> Tuple[CatalogConfig, MerchantOnboarding]:
        """Complete Step 3: Meta Catalog ID"""

        catalog_config = db.query(CatalogConfig).filter(
            CatalogConfig.merchant_id == merchant_id
        ).first()

        if catalog_config:
            catalog_config.catalog_id = data.catalog_id
            catalog_config.product_feed_url = str(data.product_feed_url) if data.product_feed_url else None
            catalog_config.updated_at = datetime.now(timezone.utc)
        else:
            catalog_config = CatalogConfig(
                merchant_id=merchant_id,
                catalog_id=data.catalog_id,
                product_feed_url=str(data.product_feed_url) if data.product_feed_url else None,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(catalog_config)

        onboarding: Optional[MerchantOnboarding] = db.query(MerchantOnboarding).filter(
            MerchantOnboarding.merchant_id == merchant_id
        ).first()

        if not onboarding:
            raise ValueError("Onboarding record not found")

        onboarding.catalog_id_status = OnboardingStepStatus.COMPLETED.value
        onboarding.catalog_id_completed_at = datetime.now(timezone.utc)
        onboarding.steps_completed = OnboardingService._count_completed_steps(onboarding)
        onboarding.current_step = 4
        onboarding.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(catalog_config)
        db.refresh(onboarding)

        return catalog_config, onboarding

    @staticmethod
    def test_catalog_connection(
            db: Session,
            merchant_id: UUID
    ) -> bool:
        catalog_config = db.query(CatalogConfig).filter(
            CatalogConfig.merchant_id == merchant_id
        ).first()

        if not catalog_config:
            raise ValueError("Catalog configuration not found")

        # TODO: Implement actual Meta Catalog API test
        # For now, just mark as ready
        catalog_config.feed_status = "ready"
        catalog_config.is_verified = True
        catalog_config.verified_at = datetime.now(timezone.utc)
        catalog_config.last_sync_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(catalog_config)

        return True

    @staticmethod
    def complete_payment_details(
            db: Session,
            merchant_id: UUID,
            data: PaymentDetailsRequest
    ) -> Tuple[PaymentConfig, MerchantOnboarding]:
        """Complete Step 4: Payment Details"""

        # TODO: Verify account with Paystack
        account_name = "Account Name (To be verified)"

        payment_config = db.query(PaymentConfig).filter(
            PaymentConfig.merchant_id == merchant_id
        ).first()

        if payment_config:
            payment_config.bank_name = data.bank_name
            payment_config.account_number = data.account_number
            payment_config.account_name = account_name
            payment_config.verification_status = "pending"
            payment_config.updated_at = datetime.now(timezone.utc)
        else:
            payment_config = PaymentConfig(
                merchant_id=merchant_id,
                bank_name=data.bank_name,
                bank_code="044",  # TODO: Get actual bank code
                account_number=data.account_number,
                account_name=account_name,
                verification_status="pending",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(payment_config)

        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if merchant:
            merchant.settlement_bank = data.bank_name
            merchant.account_number = data.account_number

        onboarding: Optional[MerchantOnboarding] = db.query(MerchantOnboarding).filter(
            MerchantOnboarding.merchant_id == merchant_id
        ).first()

        if not onboarding:
            raise ValueError("Onboarding record not found")

        onboarding.payment_details_status = OnboardingStepStatus.COMPLETED.value
        onboarding.payment_details_completed_at = datetime.now(timezone.utc)
        onboarding.steps_completed = OnboardingService._count_completed_steps(onboarding)

        if onboarding.steps_completed == onboarding.total_steps:
            onboarding.status = OnboardingStatus.COMPLETED.value
            onboarding.is_completed = True
            onboarding.completed_at = datetime.now(timezone.utc)

        onboarding.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(payment_config)
        db.refresh(onboarding)

        return payment_config, onboarding

    @staticmethod
    def verify_payment_account(
            db: Session,
            merchant_id: UUID
    ) -> PaymentConfig:
        payment_config: Optional[Merchant] = db.query(PaymentConfig).filter(
            PaymentConfig.merchant_id == merchant_id
        ).first()

        if not payment_config:
            raise ValueError("Payment configuration not found")

        # TODO: Implement actual Paystack account verification
        # TODO: Create Paystack subaccount

        payment_config.is_verified = True
        payment_config.verification_status = "verified"
        payment_config.verified_at = datetime.now(timezone.utc)
        payment_config.account_name = "Verified Account Name"  # From Paystack

        db.commit()
        db.refresh(payment_config)

        return payment_config

    @staticmethod
    def get_decrypted_whatsapp_config(db: Session, merchant_id: UUID) -> Optional[dict]:
        """
        Retrieve and decrypt WhatsApp config for a merchant

        Returns:
            Dictionary with decrypted app_secret and access_token, or None if not found
        """
        whatsapp_config = db.query(WhatsAppConfig).filter(
            WhatsAppConfig.merchant_id == merchant_id
        ).first()

        if not whatsapp_config:
            return None

        try:
            from app.utils.encryption import get_encryption_service_with_salt

            encryption_service = get_encryption_service_with_salt(whatsapp_config.encryption_salt)

            decrypted_app_secret = encryption_service.decrypt(whatsapp_config.app_secret)
            decrypted_access_token = encryption_service.decrypt(whatsapp_config.access_token)

            if decrypted_app_secret is None or decrypted_access_token is None:
                raise ValueError("Failed to decrypt sensitive data")

            return {
                'id': whatsapp_config.id,
                'merchant_id': whatsapp_config.merchant_id,
                'app_id': whatsapp_config.app_id,
                'app_secret': decrypted_app_secret,
                'business_account_id': whatsapp_config.business_account_id,
                'phone_number_id': whatsapp_config.phone_number_id,
                'whatsapp_phone_number': whatsapp_config.whatsapp_phone_number,
                'access_token': decrypted_access_token,
                'webhook_url': whatsapp_config.webhook_url,
                'webhook_verify_token': whatsapp_config.webhook_verify_token,
                'is_verified': whatsapp_config.is_verified,
                'is_active': whatsapp_config.is_active,
                'created_at': whatsapp_config.created_at,
                'updated_at': whatsapp_config.updated_at
            }
        except Exception as e:
            raise ValueError(f"Failed to decrypt WhatsApp config: {str(e)}")

    @staticmethod
    def update_whatsapp_credentials(
            db: Session,
            merchant_id: UUID,
            app_secret: Optional[str] = None,
            access_token: Optional[str] = None
    ) -> Optional[WhatsAppConfig]:
        """
        Update WhatsApp credentials with encryption
        """
        whatsapp_config: Optional[WhatsAppConfig] = db.query(WhatsAppConfig).filter(
            WhatsAppConfig.merchant_id == merchant_id
        ).first()

        if not whatsapp_config:
            return None

        from app.utils.encryption import EncryptionService
        import base64
        import os

        salt_bytes = base64.urlsafe_b64decode(whatsapp_config.encryption_salt.encode())
        encryption_password = os.getenv('ENCRYPTION_PASSWORD')
        encryption_service = EncryptionService(encryption_password, salt_bytes)

        if app_secret is not None:
            whatsapp_config.app_secret = encryption_service.encrypt(app_secret)

        if access_token is not None:
            whatsapp_config.access_token = encryption_service.encrypt(access_token)

        whatsapp_config.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(whatsapp_config)

        return whatsapp_config

    @staticmethod
    def _count_completed_steps(onboarding: MerchantOnboarding) -> int:
        count = 0
        if onboarding.business_details_status == OnboardingStepStatus.COMPLETED.value:
            count += 1
        if onboarding.whatsapp_connection_status == OnboardingStepStatus.COMPLETED.value:
            count += 1
        if onboarding.catalog_id_status == OnboardingStepStatus.COMPLETED.value:
            count += 1
        if onboarding.payment_details_status == OnboardingStepStatus.COMPLETED.value:
            count += 1
        return count

    @staticmethod
    def skip_step(
            db: Session,
            merchant_id: UUID,
            step_name: str
    ) -> MerchantOnboarding:
        onboarding: Optional[Merchant] = db.query(MerchantOnboarding).filter(
            MerchantOnboarding.merchant_id == merchant_id
        ).first()

        if not onboarding:
            raise ValueError("Onboarding record not found")

        if step_name == "catalog_id":
            onboarding.catalog_id_status = OnboardingStepStatus.SKIPPED.value
            onboarding.current_step = 4

        onboarding.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(onboarding)

        return onboarding
