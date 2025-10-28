from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Technology(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    deleted_at: Optional[datetime] = Field(default=None)
    
    class Config:
        from_attributes = True

