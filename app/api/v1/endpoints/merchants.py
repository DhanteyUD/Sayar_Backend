from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_merchant_user, get_current_admin_user
from app.models.user import User
from app.models.merchant import Merchant, MerchantRole
from app.schemas.merchant import MerchantResponse, MerchantDetailResponse
from app.schemas.user import UserResponse
from app.services.merchant_service import MerchantService

router = APIRouter()


@router.get("/stats", response_model=dict)
def get_merchant_stats(
        merchant_id: UUID = Query(..., description="Merchant ID"),
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Get statistics for a merchant

    Returns user count, roles distribution, etc.
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    merchant_users = MerchantService.get_merchant_users(db, merchant_id)

    roles_count = {
        "owner": 0,
        "admin": 0,
        "staff": 0
    }

    for _, mu in merchant_users:
        if mu.role == MerchantRole.OWNER:
            roles_count["owner"] += 1
        elif mu.role == MerchantRole.ADMIN:
            roles_count["admin"] += 1
        elif mu.role == MerchantRole.STAFF:
            roles_count["staff"] += 1

    return {
        "merchant_id": str(merchant_id),
        "total_users": len(merchant_users),
        "roles": roles_count,
        "active_users": sum(1 for _, mu in merchant_users if mu.status.value == "active")
    }


@router.get("/merchant-users", response_model=List[dict])
def list_merchant_users(
        merchant_id: UUID = Query(..., description="Merchant ID"),
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Get all users associated with a merchant

    Returns list of users with their roles in the merchant context.
    Only accessible by merchant owners and admins.
    """
    requester_role = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)

    if not requester_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    if requester_role.role not in [MerchantRole.OWNER, MerchantRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can view merchant users"
        )

    merchant_users = MerchantService.get_merchant_users(db, merchant_id)

    result = []
    for user, merchant_user in merchant_users:
        result.append({
            "user_id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "role": merchant_user.role.value,
            "status": merchant_user.status.value,
            "joined_at": merchant_user.joined_at,
            "created_at": merchant_user.created_at
        })

    return result


@router.get("/merchant-users/{user_id}", response_model=dict)
def get_merchant_user(
        merchant_id: UUID = Query(..., description="Merchant ID"),
        user_id: UUID = Path(..., description="User ID"),
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Get specific user details in merchant context
    """
    requester_role = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not requester_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, user_id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with this merchant"
        )

    return {
        "user_id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "role": merchant_user.role.value,
        "status": merchant_user.status.value,
        "joined_at": merchant_user.joined_at,
        "created_at": user.created_at,
        "is_active": user.is_active,
        "is_verified": user.is_verified
    }


@router.get("/list", response_model=List[dict])
def list_user_merchants(
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Get all merchants associated with the current user

    Returns list of merchants with user's role in each merchant.
    """

    user_id = UUID(str(current_user.id))

    merchants_with_roles = MerchantService.get_user_merchants(db, user_id)

    result = []
    for merchant, merchant_user in merchants_with_roles:
        result.append({
            "merchant_id": str(merchant.id),
            "business_name": merchant.business_name,
            "business_email": merchant.business_email,
            "business_logo_url": merchant.business_logo_url,
            "category": merchant.category,
            "currency": merchant.currency,
            "is_active": merchant.is_active,
            "is_verified": merchant.is_verified,
            "user_role": merchant_user.role.value,
            "user_status": merchant_user.status.value,
            "created_at": merchant.created_at
        })

    return result


@router.get("/{merchant_id}", response_model=MerchantDetailResponse)
def get_merchant_details(
        merchant_id: UUID,
        current_user: User = Depends(get_current_merchant_user),
        db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific merchant

    Only accessible by users associated with the merchant.
    """
    merchant_user = MerchantService.get_merchant_user_role(db, merchant_id, current_user.id)
    if not merchant_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this merchant"
        )

    merchant = MerchantService.get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )

    return MerchantDetailResponse.model_validate(merchant)


@router.get("/all/merchants", response_model=List[MerchantResponse])
def list_all_merchants(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        _current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    Get all merchants in the system (Admin only)

    Returns paginated list of all merchants.
    Only accessible by admin users.
    """
    merchants = db.query(Merchant).offset(skip).limit(limit).all()
    return [MerchantResponse.model_validate(m) for m in merchants]


@router.get("/all/users", response_model=List[UserResponse])
def list_all_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        role: str = Query(None, description="Filter by role (admin, merchant, customer)"),
        _current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """
    Get all users in the system (Admin only)

    Returns paginated list of all users. Can filter by role.
    Only accessible by admin users.
    """
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()
    return [UserResponse.model_validate(u) for u in users]
