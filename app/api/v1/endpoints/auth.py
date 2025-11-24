from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    MerchantSignupRequest,
    LoginRequest,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm
)
from app.schemas.user import UserResponse
from app.schemas.merchant import MerchantResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/signup/merchant", response_model=dict, status_code=status.HTTP_201_CREATED)
def merchant_signup(
        signup_data: MerchantSignupRequest,
        db: Session = Depends(get_db)
):
    """
    Register a new merchant account

    Creates:
    - User account
    - Merchant business profile
    - Merchant-user relationship with OWNER role
    """
    try:
        user, merchant, merchant_user = AuthService.create_merchant_account(db, signup_data)

        tokens = AuthService.generate_tokens(str(user.id))

        return {
            "message": "Merchant account created successfully",
            "user": UserResponse.model_validate(user),
            "merchant": MerchantResponse.model_validate(merchant),
            "tokens": tokens,
            "verification_required": True
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    Login with email and password

    Returns JWT access and refresh tokens
    """
    user = AuthService.authenticate_user(db, login_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    tokens = AuthService.generate_tokens(str(user.id))

    return TokenResponse(**tokens)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return UserResponse.model_validate(current_user)


@router.post("/verify-email/{token}", response_model=dict)
def verify_email(
        token: str,
        db: Session = Depends(get_db)
):
    """
    Verify user email with verification token
    """
    success = AuthService.verify_email(db, token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    return {
        "message": "Email verified successfully"
    }


@router.post("/password-reset/request", response_model=dict)
def request_password_reset(
        reset_request: PasswordResetRequest,
        db: Session = Depends(get_db)
):
    """
    Request password reset

    Sends password reset email with token
    """
    AuthService.request_password_reset(db, str(reset_request.email))

    return {
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/password-reset/confirm", response_model=dict)
def confirm_password_reset(
        reset_data: PasswordResetConfirm,
        db: Session = Depends(get_db)
):

    """
    Confirm password reset with token and new password
    """
    success = AuthService.reset_password(
        db,
        reset_data.token,
        reset_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    return {
        "message": "Password reset successfully"
    }


@router.post("/logout", response_model=dict)
def logout(
        _current_user: User = Depends(get_current_user)
):
    """
    Logout (client should delete tokens)

    Note: JWT tokens are stateless, so actual logout happens client-side
    For additional security, implement token blacklisting
    """
    return {
        "message": "Logged out successfully"
    }
