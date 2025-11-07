from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session

from ..database.connection import get_session
from ..schemas.auth import (
    UserCreate,
    UserSignIn,
    TokenResponse,
    ForgotPasswordRequest,
    MessageResponse,
    UserResponse,
    UserProfileResponse,
    RefreshTokenRequest
)
from ..services.auth_service import AuthService, get_auth_service
from ..utils.dependencies import get_current_user
from ..models.user import User
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user account."""
    result = auth_service.create_user(user_data)

    # Router just returns whatever service provides
    return JSONResponse(
        status_code=result["status_code"],
        content={
            "message": result["message"],
            "data": result["data"]
        }
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


@router.get("/user-details", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current user profile via JWT."""
    response = auth_service.get_user_details(current_user)
    return response


@router.post("/refresh-token")
async def refresh_token(
    refresh_token: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Generate new access token using refresh token."""
    return auth_service.refresh_access_token(refresh_token)

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


@router.post("/logout")
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user=Depends(get_current_user)
):
    """
    Logout API — Blacklist the provided access token.
    """
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Missing or invalid authorization header", "data": None}
        )

    token = auth_header.split(" ")[1]
    return auth_service.logout_user(token, current_user)
