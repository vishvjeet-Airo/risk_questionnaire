from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.enums import UserRole

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
