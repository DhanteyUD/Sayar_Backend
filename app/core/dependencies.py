from fastapi import Depends, HTTPException, status
from .security import get_current_user
from app.models.user import User

get_current_user = get_current_user


async def get_current_merchant_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "merchant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Merchant account required."
        )
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin privileges required."
        )
    return current_user
