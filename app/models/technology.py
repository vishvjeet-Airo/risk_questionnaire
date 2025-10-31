from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlmodel import SQLModel, Field

class Technology(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=255)
    created_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))
    deleted_at: datetime | None = None

