from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta, UTC

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....models.merchant import Merchant
from ....models.order import Order
from ....models.product import Product
from ....models.payment import Payment

router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    total_merchants = db.query(func.count(Merchant.id)).scalar()
    total_products = db.query(func.count(Product.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()

    total_revenue = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter_by(status="success")
        .scalar()
    )

    # Recent orders
    recent_orders = db.query(Order).order_by(desc(Order.created_at)).limit(10).all()

    # Merchant growth (last 30 days)
    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
    new_merchants = db.query(func.count(Merchant.id)).filter(
        Merchant.created_at >= thirty_days_ago
    ).scalar()

    return {
        "total_merchants": total_merchants,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "new_merchants_30d": new_merchants,
        "recent_orders": recent_orders
    }


@router.get("/merchants")
async def get_all_merchants(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    merchants = db.query(Merchant).offset(skip).limit(limit).all()
    return merchants


@router.get("/orders")
async def get_all_orders(
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = db.query(Order)
    if status:
        query = query.filter_by(status=status)

    orders = query.offset(skip).limit(limit).all()
    return orders
