from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_merchant_user
from app.models.user import User
# from app.models.merchant import Merchant
from app.services.onboarding_service import OnboardingService
from app.services.merchant_service import MerchantService
from app.schemas.onboarding import (
    BusinessDetailsRequest,
    # WhatsAppConnectionRequest,
    # CatalogIDRequest,
    # PaymentDetailsRequest,
    OnboardingStatusResponse,
    OnboardingStepResponse
)

router = APIRouter()


@router.get("/status", response_model=OnboardingStatusResponse)
def get_onboarding_status(
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Get merchant onboarding status

    Returns the current progress of merchant onboarding
    """

    # Get user's first merchant (or active merchant)
    merchants = MerchantService.get_user_merchants(db, UUID(str(current_user.id)))

    if not merchants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No merchant found for this user"
        )

    merchant, _ = merchants[0]

    onboarding = OnboardingService.get_or_create_onboarding(db, merchant.id)

    return OnboardingStatusResponse(
        merchant_id=UUID(str(onboarding.merchant_id)),
        steps_completed=onboarding.steps_completed,
        total_steps=onboarding.total_steps,
        completion_percentage=onboarding.completion_percentage,
        is_completed=onboarding.is_completed,
        current_step=onboarding.get_current_step(),
        business_details_status=onboarding.business_details_status.value,
        whatsapp_connection_status=onboarding.whatsapp_connection_status.value,
        catalog_id_status=onboarding.catalog_id_status.value,
        payment_details_status=onboarding.payment_details_status.value,
        business_details_completed_at=onboarding.business_details_completed_at,
        whatsapp_connection_completed_at=onboarding.whatsapp_connection_completed_at,
        catalog_id_completed_at=onboarding.catalog_id_completed_at,
        payment_details_completed_at=onboarding.payment_details_completed_at,
        completed_at=onboarding.completed_at
    )


@router.post("/business-details", response_model=OnboardingStepResponse)
def complete_business_details(
        data: BusinessDetailsRequest,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Complete Step 1: Business Details

    Provide essential business information to get started
    """
    try:
        # Get user's merchant
        merchants = MerchantService.get_user_merchants(db, UUID(str(current_user.id)))

        if not merchants:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No merchant found for this user"
            )

        merchant, _ = merchants[0]

        # Complete business details step
        onboarding = OnboardingService.complete_business_details(
            db, merchant.id, data
        )

        return OnboardingStepResponse(
            step="business_details",
            status="completed",
            message="Business details saved successfully",
            next_step=onboarding.get_current_step(),
            onboarding_progress=OnboardingStatusResponse(
                merchant_id=UUID(str(onboarding.merchant_id)),
                steps_completed=onboarding.steps_completed,
                total_steps=onboarding.total_steps,
                completion_percentage=onboarding.completion_percentage,
                is_completed=onboarding.is_completed,
                current_step=onboarding.get_current_step(),
                business_details_status=onboarding.business_details_status.value,
                whatsapp_connection_status=onboarding.whatsapp_connection_status.value,
                catalog_id_status=onboarding.catalog_id_status.value,
                payment_details_status=onboarding.payment_details_status.value,
                business_details_completed_at=onboarding.business_details_completed_at,
                whatsapp_connection_completed_at=onboarding.whatsapp_connection_completed_at,
                catalog_id_completed_at=onboarding.catalog_id_completed_at,
                payment_details_completed_at=onboarding.payment_details_completed_at,
                completed_at=onboarding.completed_at
            )
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


@router.post("/skip/{step}", response_model=OnboardingStepResponse)
def skip_onboarding_step(
        step: str,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Skip an optional onboarding step

    Only WhatsApp Connection and Catalog ID can be skipped
    """
    if step not in ["whatsapp_connection", "catalog_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only whatsapp_connection and catalog_id steps can be skipped"
        )

    try:
        merchants = MerchantService.get_user_merchants(db, UUID(str(current_user.id)))

        if not merchants:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No merchant found"
            )

        merchant, _ = merchants[0]

        onboarding = OnboardingService.skip_step(db, merchant.id, step)

        return OnboardingStepResponse(
            step=step,
            status="skipped",
            message=f"{step.replace('_', ' ').title()} step skipped",
            next_step=onboarding.get_current_step(),
            onboarding_progress=OnboardingStatusResponse(
                merchant_id=UUID(str(onboarding.merchant_id)),
                steps_completed=onboarding.steps_completed,
                total_steps=onboarding.total_steps,
                completion_percentage=onboarding.completion_percentage,
                is_completed=onboarding.is_completed,
                current_step=onboarding.get_current_step(),
                business_details_status=onboarding.business_details_status.value,
                whatsapp_connection_status=onboarding.whatsapp_connection_status.value,
                catalog_id_status=onboarding.catalog_id_status.value,
                payment_details_status=onboarding.payment_details_status.value,
                business_details_completed_at=onboarding.business_details_completed_at,
                whatsapp_connection_completed_at=onboarding.whatsapp_connection_completed_at,
                catalog_id_completed_at=onboarding.catalog_id_completed_at,
                payment_details_completed_at=onboarding.payment_details_completed_at,
                completed_at=onboarding.completed_at
            )
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
