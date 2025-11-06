from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .user import User


class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    type: str = Field(max_length=100)
    subject: str = Field(max_length=255)
    description: str
    priority: str = Field(default="medium", max_length=50)
    status: str = Field(default="open", max_length=50)
    meta_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    resolved_at: Optional[datetime] = Field(default=None)
    resolved_by: Optional[int] = Field(default=None, foreign_key="user.id")

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="feedback",
        sa_relationship_kwargs={"foreign_keys": "[Feedback.user_id]"}
    )

    resolver: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Feedback.resolved_by]"}
    )

    class Config:
        from_attributes = True

