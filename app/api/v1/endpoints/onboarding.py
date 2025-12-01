from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_merchant_user
from app.models.user import User
from app.schemas.onboarding import (
    BusinessDetailsRequest,
    WhatsAppConnectionRequest,
    CatalogConnectionRequest,
    PaymentDetailsRequest,
    OnboardingProgressResponse,
    OnboardingStatusUpdate,
    OnboardingStepResponse
)
from app.services.onboarding_service import OnboardingService
from app.services.merchant_service import MerchantService

router = APIRouter()


def build_onboarding_response(onboarding) -> OnboardingProgressResponse:
    return OnboardingProgressResponse(
        id=onboarding.id,
        merchant_id=onboarding.merchant_id,
        status=onboarding.status,
        current_step=onboarding.current_step,
        steps_completed=onboarding.steps_completed,
        total_steps=onboarding.total_steps,
        completion_percentage=onboarding.completion_percentage,
        is_completed=onboarding.is_completed,
        business_details=OnboardingStepResponse(
            step_number=1,
            step_name="Business Details",
            status=onboarding.business_details_status,
            completed_at=onboarding.business_details_completed_at
        ),
        whatsapp_connection=OnboardingStepResponse(
            step_number=2,
            step_name="WhatsApp Connection",
            status=onboarding.whatsapp_connection_status,
            completed_at=onboarding.whatsapp_connection_completed_at
        ),
        catalog_id=OnboardingStepResponse(
            step_number=3,
            step_name="Meta Catalog ID",
            status=onboarding.catalog_id_status,
            completed_at=onboarding.catalog_id_completed_at
        ),
        payment_details=OnboardingStepResponse(
            step_number=4,
            step_name="Payment Details",
            status=onboarding.payment_details_status,
            completed_at=onboarding.payment_details_completed_at
        ),
        completed_at=onboarding.completed_at,
        created_at=onboarding.created_at,
        updated_at=onboarding.updated_at
    )


@router.get("/progress", response_model=OnboardingProgressResponse)
def get_onboarding_progress(
        merchant_id: UUID,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Get onboarding progress for a merchant
    """
    user_id = UUID(str(current_user.id))

    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    onboarding = OnboardingService.get_or_create_onboarding(
        db, merchant_id, user_id
    )

    return build_onboarding_response(onboarding)


# ============================================================================
# Step 1: Business Details
# ============================================================================

@router.post("/step1/business-details", response_model=OnboardingStatusUpdate)
def complete_business_details(
        merchant_id: UUID,
        data: BusinessDetailsRequest,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Complete Step 1: Business Details

    Provide essential business information to get started with Sayar
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    try:
        merchant, onboarding = OnboardingService.complete_business_details(
            db, merchant_id, data
        )

        return OnboardingStatusUpdate(
            message="Business details saved successfully!",
            onboarding=build_onboarding_response(onboarding)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# ============================================================================
# Step 2: WhatsApp Connection
# ============================================================================

@router.post("/step2/whatsapp-connection", response_model=OnboardingStatusUpdate)
def complete_whatsapp_connection(
        merchant_id: UUID,
        data: WhatsAppConnectionRequest,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Complete Step 2: WhatsApp Connection

    Link your WhatsApp Business account for seamless customer interaction
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    try:
        whatsapp_config, onboarding = OnboardingService.complete_whatsapp_connection(
            db, merchant_id, data
        )

        return OnboardingStatusUpdate(
            message="WhatsApp connection configured successfully!",
            onboarding=build_onboarding_response(onboarding)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/step2/test-connection", response_model=dict)
def test_whatsapp_connection(
        merchant_id: UUID,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Test WhatsApp Business API connection
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    try:
        success = OnboardingService.test_whatsapp_connection(db, merchant_id)

        if success:
            return {
                "success": True,
                "message": "WhatsApp connection test successful!"
            }
        else:
            return {
                "success": False,
                "message": "WhatsApp connection test failed"
            }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# ============================================================================
# Step 3: Meta Catalog
# ============================================================================

@router.post("/step3/catalog-connection", response_model=OnboardingStatusUpdate)
def complete_catalog_connection(
        merchant_id: UUID,
        data: CatalogConnectionRequest,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Complete Step 3: Meta Catalog ID

    Input and verify your Meta catalog ID to showcase your products
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    try:
        catalog_config, onboarding = OnboardingService.complete_catalog_connection(
            db, merchant_id, data
        )

        return OnboardingStatusUpdate(
            message="Catalog connection configured successfully!",
            onboarding=build_onboarding_response(onboarding)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/step3/test-connection", response_model=dict)
def test_catalog_connection(
        merchant_id: UUID,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Test Meta Catalog connection
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    try:
        success = OnboardingService.test_catalog_connection(db, merchant_id)

        if success:
            return {
                "success": True,
                "message": "Catalog connection test successful!",
                "feed_status": "ready"
            }
        else:
            return {
                "success": False,
                "message": "Catalog connection test failed"
            }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/step3/skip", response_model=OnboardingStatusUpdate)
def skip_catalog_step(
        merchant_id: UUID,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Skip catalog configuration step (optional)
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    try:
        onboarding = OnboardingService.skip_step(db, merchant_id, "catalog_id")

        return OnboardingStatusUpdate(
            message="Catalog step skipped. You can configure it later.",
            onboarding=build_onboarding_response(onboarding)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# Step 4: Payment Details
# ============================================================================

@router.post("/step4/payment-details", response_model=OnboardingStatusUpdate)
def complete_payment_details(
        merchant_id: UUID,
        data: PaymentDetailsRequest,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Complete Step 4: Payment Details

    Set up your bank information for fast and secure payouts
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    try:
        payment_config, onboarding = OnboardingService.complete_payment_details(
            db, merchant_id, data
        )

        message = "Payment details saved successfully!"
        if onboarding.is_completed:
            message = "🎉 Congratulations! Onboarding completed successfully!"

        return OnboardingStatusUpdate(
            message=message,
            onboarding=build_onboarding_response(onboarding)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/step4/verify-account", response_model=dict)
def verify_payment_account(
        merchant_id: UUID,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Verify bank account with Paystack
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    try:
        payment_config = OnboardingService.verify_payment_account(db, merchant_id)

        return {
            "success": True,
            "message": "Account verified successfully!",
            "account_name": payment_config.account_name
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
