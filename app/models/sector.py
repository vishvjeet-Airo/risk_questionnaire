from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, DateTime, func

class Sector(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow,sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow,sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None)

    class Config:
        from_attributes = True