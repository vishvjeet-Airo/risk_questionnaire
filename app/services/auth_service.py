from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from ..database.connection import get_session
from ..models.user import User
from ..schemas.auth import UserCreate, UserSignIn, TokenResponse, ForgotPasswordRequest
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_password_reset_token
)
from ..core.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = self.db.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

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
        user = self.authenticate_user(credentials.email, credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=user
        )

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
        from ..core.security import verify_token
        
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


def get_auth_service(db: Session = Depends(get_session)) -> AuthService:
    """Get authentication service instance."""
    return AuthService(db)
