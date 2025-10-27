from pydantic import BaseModel, EmailStr, Field
from .user import UserResponse ,UserBase


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserSignIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class MessageResponse(BaseModel):
    message: str
