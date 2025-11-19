from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....models.merchant import Merchant
from ....models.order import Order, OrderItem
from ....models.product import Product
from ....schemas.order import OrderCreate, OrderResponse, OrderUpdate, OrderListResponse

router = APIRouter()


@router.post("/", response_model=OrderResponse)
async def create_order(
        order_data: OrderCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Get merchant for current user
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant account not found"
        )

    # Validate products and calculate total
    total_amount = 0
    order_items = []

    for item in order_data.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.merchant_id == merchant.id
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )

        if product.inventory_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient inventory for product: {product.name}"
            )

        item_total = item.quantity * item.unit_price
        total_amount += item_total

        order_items.append(OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item_total
        ))

    # Generate unique order number
    order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"

    # Create order
    db_order = Order(
        **order_data.dict(exclude={'items'}),
        order_number=order_number,
        merchant_id=merchant.id,
        total_amount=total_amount,
        status="pending",
        items=order_items
    )

    # Update product inventory
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.inventory_quantity -= item.quantity

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return db_order


@router.get("/", response_model=OrderListResponse)
async def get_orders(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        status: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Get merchant for current user
    merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant account not found"
        )

    # Base query
    query = db.query(Order).filter(Order.merchant_id == merchant.id)

    # Filter by status if provided
    if status:
        query = query.filter(Order.status == status)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    return OrderListResponse(
        items=orders,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
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
            detail="Not authorized to view this order"
        )

    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
        order_id: int,
        order_data: OrderUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
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
            detail="Not authorized to update this order"
        )

    # Update order fields
    for field, value in order_data.dict(exclude_unset=True).items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)

    return order


@router.post("/{order_id}/cancel")
async def cancel_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
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
            detail="Not authorized to cancel this order"
        )

    # Check if order can be cancelled
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled in its current status"
        )

    # Restore product inventory
    for item in order.items:
        product = item.product
        product.inventory_quantity += item.quantity

    order.status = "cancelled"
    db.commit()

    return {"message": "Order cancelled successfully"}
