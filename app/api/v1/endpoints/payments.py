from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....models.merchant import Merchant
from ....models.order import Order
from ....models.payment import Payment
from ....schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentInitializeResponse,
    PaymentVerificationResponse
)
from ....services.payment_service import paystack_service
from ....services.whatsapp_service import whatsapp_service

router = APIRouter()


@router.post("/initialize", response_model=PaymentInitializeResponse)
async def initialize_payment(
        payment_data: PaymentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Get order
    order = db.query(Order).filter(Order.id == payment_data.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Check authorization
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not current_user.is_superuser and order.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to process payment for this order"
        )

    # Check if payment already exists
    existing_payment = db.query(Payment).filter(Payment.order_id == payment_data.order_id).first()
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this order"
        )

    # Generate unique reference
    reference = f"SAYAR_{order.id}_{int(datetime.now().timestamp())}"

    # Initialize payment with Paystack
    paystack_result = paystack_service.initialize_transaction(
        email=order.customer_phone + "@sayar.com",  # Using phone as email placeholder
        amount=payment_data.amount,
        reference=reference,
        metadata={
            "order_id": order.id,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone
        }
    )

    if not paystack_result.get("status"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment initialization failed: {paystack_result.get('message')}"
        )

    # Create payment record
    db_payment = Payment(
        order_id=payment_data.order_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        paystack_reference=reference,
        status="pending",
        paystack_response=paystack_result
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return PaymentInitializeResponse(
        authorization_url=paystack_result["data"]["authorization_url"],
        access_code=paystack_result["data"]["access_code"],
        reference=reference
    )


@router.get("/verify/{reference}", response_model=PaymentVerificationResponse)
async def verify_payment(
        reference: str,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Get payment record
    payment = db.query(Payment).filter(Payment.paystack_reference == reference).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Check authorization
    order = payment.order
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not current_user.is_superuser and order.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this payment"
        )

    # Verify payment with Paystack
    verification_result = paystack_service.verify_transaction(reference)

    if not verification_result.get("status"):
        return PaymentVerificationResponse(
            status="error",
            message=f"Verification failed: {verification_result.get('message')}"
        )

    transaction_data = verification_result["data"]

    # Update payment record
    payment.status = "success" if transaction_data["status"] == "success" else "failed"
    payment.paystack_transaction_id = transaction_data["id"]
    payment.payment_method = transaction_data["channel"]
    payment.paid_at = transaction_data.get("paid_at")
    payment.paystack_response = verification_result

    # Update order status
    if payment.status == "success":
        order.status = "paid"

        # Send WhatsApp notification in background
        background_tasks.add_task(
            whatsapp_service.send_order_confirmation,
            order.customer_whatsapp_id,
            order
        )
    else:
        order.status = "payment_failed"

    db.commit()

    return PaymentVerificationResponse(
        status="success",
        message="Payment verified successfully",
        data=payment
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
        payment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Check authorization
    order = payment.order
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not current_user.is_superuser and order.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )

    return payment
