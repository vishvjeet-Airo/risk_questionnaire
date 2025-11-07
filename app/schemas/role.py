from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoleCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class MessageResponse(BaseModel):
    message: str
    data: Optional[dict] = None
