from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from ..database.connection import get_session
from ..schemas.auth import (
    UserCreate,
    UserSignIn,
    TokenResponse,
    ForgotPasswordRequest,
    MessageResponse
)
from ..services.auth_service import AuthService, get_auth_service
from ..utils.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user account."""
    try:
        user = auth_service.create_user(user_data)
        return MessageResponse(
            message="User registered successfully"
        )
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/signin", response_model=TokenResponse)
async def sign_in(
    credentials: UserSignIn,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return JWT token."""
    try:
        return auth_service.sign_in(credentials)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Send password reset email."""
    try:
        # In a real application, you would send an email here
        # For now, we'll just create the token and return success
        token = auth_service.create_password_reset_token(request.email)
        
        # TODO: Send email with reset token
        # For development, you might want to log the token
        
        return MessageResponse(
            message="Password reset email sent"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user (invalidate session)."""
    # In a more sophisticated implementation, you might:
    # 1. Add the token to a blacklist
    # 2. Store session information in Redis
    # 3. Track active sessions
    
    # For now, we'll just return success
    # The client should discard the token
    return MessageResponse(
        message="Successfully logged out"
    )
