from pydantic import BaseModel, EmailStr, Field
from .user import UserResponse ,UserBase
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str
    role_id: int | None = None
    
class UserLoginResponse(BaseModel):
    """Schema for simplified user info returned after login"""
    id: int
    email: EmailStr
    name: str

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_id: int

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    message: str
    user: UserOut


class UserSignIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserLoginResponse


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class MessageResponse(BaseModel):
    message: str
    
    
class UserProfileResponse(BaseModel):
    id: int
    first_name: str
    email: EmailStr
    role_id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserProfileDetailResponse(BaseModel):
    message: str
    user: UserProfileResponse
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str
