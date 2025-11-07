from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from ..database.connection import get_session
from ..models.user import User, BlacklistedToken
from ..schemas.auth import UserCreate, UserSignIn, TokenResponse, ForgotPasswordRequest
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_password_reset_token,
    verify_token, 
    create_refresh_token
    
)
from ..schemas.auth import (
    UserCreate,
    UserSignIn,
    TokenResponse,
    ForgotPasswordRequest,
    MessageResponse,
    UserResponse,
    UserOut,
    RefreshTokenRequest
)
from app.core.logger import api_logger
from fastapi.responses import JSONResponse
from ..core.config import settings
import re

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

PASSWORD_REGEX = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data):
        """Handles user creation, validation, and DB operations."""
        try:
            # Email format validation
            if not re.match(EMAIL_REGEX, user_data.email):
                return {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid email format.",
                    "data": None,
                }

            # Password match validation
            if user_data.password != user_data.confirm_password:
                return {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Passwords do not match.",
                    "data": None,
                }
                
            if not re.match(PASSWORD_REGEX, user_data.password):
                return {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": (
                        "Password must be at least 8 characters long, "
                        "contain one uppercase letter, one lowercase letter, "
                        "one digit, and one special character."
                    ),
                    "data": None,
                }

            # Duplicate email check
            existing_user = self.db.exec(
                select(User).where(User.email == user_data.email)
            ).first()
            if existing_user:
                return {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Email already registered.",
                    "data": None,
                }

            # Hash password and create user
            hashed_password = get_password_hash(user_data.password)
            user = User(
                first_name=user_data.name,
                email=user_data.email,
                hashed_password=hashed_password,
                role_id=user_data.role_id or 2,  # Default role
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            return {
                "status_code": status.HTTP_201_CREATED,
                "message": "User registered successfully.",
                "data": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "email": user.email,
                    "role_id": user.role_id,
                },
            }

        except Exception as e:
            api_logger.excpetion(f"Error while creating user: {str(e)}")
            return {
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error while creating user.",
                "data": None,
            }
            
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = self.db.exec(
            select(User).where(User.email == email)
        ).first()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user

    def sign_in(self, credentials: UserSignIn) -> TokenResponse:
        """Sign in a user and return access token."""
        try:
            user = self.authenticate_user(credentials.email, credentials.password)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )
            
            user.last_login = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)

            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=access_token_expires
            )
            
            refresh_token = create_refresh_token(
                            data={"sub": str(user.id), "email": user.email},
                            expires_delta=refresh_token_expires
                        )

            # Build the new response schema
            user_data = {
                        "id": user.id,
                        "email": user.email,
                        "name": user.first_name,
                    }

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token, 
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes,
                user=user_data
            )
        except Exception as e:
            api_logger.excpetion(f"Error while sign-in user: {str(e)}")

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.exec(
            select(User).where(User.email == email)
        ).first()

    def create_password_reset_token(self, email: str) -> str:
        """Create password reset token for user."""
        user = self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        return create_password_reset_token(email)

    def get_current_user(self, token: str) -> User:
        """Get current user from JWT token."""
        
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        user = self.db.get(User, int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    def get_user_details(self, current_user: User):
        """Fetch user details with structured response."""
        try:
            if not current_user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "message": "User not authenticated.",
                        "data": None
                    }
                )

            # Success response
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "User fetched successfully.",
                    "data": {
                        "id": current_user.id,
                        "first_name": current_user.first_name,
                        "email": current_user.email,
                        "role": current_user.role_id,
                        "is_active": current_user.is_active,
                        "created_at": str(current_user.created_at),
                        "last_login": str(current_user.last_login) if current_user.last_login else None,
                    },
                },
            )

        except Exception as e:
            api_logger.exception(f"Error while fetching user details: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "Internal server error while fetching user details.",
                    "data": None
                },
            )
            
    def refresh_access_token(self, payload: RefreshTokenRequest) -> JSONResponse:
        """Validate refresh token and return new access token."""
        try:
            token = payload.refresh_token  
            decoded = verify_token(token)

            if decoded.get("type") != "refresh":
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"message": "Invalid token type.", "data": None}
                )

            user_id = decoded.get("sub")
            email = decoded.get("email")

            if not user_id or not email:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"message": "Invalid token payload.", "data": None}
                )

            user = self.db.get(User, int(user_id))
            if not user or not user.is_active:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"message": "User inactive or not found.", "data": None}
                )

            # Create new access token
            new_access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Access token refreshed successfully.",
                    "data": {
                        "access_token": new_access_token,
                        "token_type": "bearer",
                        "expires_in": settings.access_token_expire_minutes * 60
                    }
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            api_logger.exception(f"Error while refreshing token: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Invalid or expired refresh token.", "data": None}
            )

    def logout_user(self, token: str, user):
        """
        Blacklist the user's token so it can't be reused.
        """
        try:
            payload = verify_token(token)
            exp_timestamp = payload.get("exp")

            expires_at = None
            if exp_timestamp:
                expires_at = datetime.utcfromtimestamp(exp_timestamp)

            # Check if already blacklisted
            existing = self.db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
            if existing:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": "Token already blacklisted.", "data": None}
                )

            blacklisted = BlacklistedToken(
                token=token,
                user_id=user.id,
                blacklisted_at=datetime.utcnow(),
                expires_at=expires_at,
            )
            self.db.add(blacklisted)
            self.db.commit()

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Logged out successfully.", "data": None}
            )

        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": f"Logout failed: {str(e)}", "data": None}
            )


def get_auth_service(db: Session = Depends(get_session)) -> AuthService:
    """Get authentication service instance."""
    return AuthService(db)
