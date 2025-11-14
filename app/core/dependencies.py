from fastapi import Depends
from .security import get_current_user
from app.models.user import User

# Re-export the get_current_user dependency
get_current_user = get_current_user


async def get_current_merchant_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user only if they are a merchant
    """
    if current_user.role != "merchant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Merchant account required."
        )
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user only if they are an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin privileges required."
        )
    return current_user
