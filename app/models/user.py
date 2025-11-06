from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, ForeignKey

if TYPE_CHECKING:
    from .questionnaire_file import QuestionnaireFile
    from .question import Question
    from .feedback import Feedback


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    role_id: int = Field(foreign_key="role.id", index=True)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    role: Optional["Role"] = Relationship(back_populates="users")
    blacklisted_tokens: List["BlacklistedToken"] = Relationship(back_populates="user")
    password_reset_tokens: List["PasswordResetToken"] = Relationship(back_populates="user")
    questionnaire_files: List["QuestionnaireFile"] = Relationship(back_populates="user")
    questions: List["Question"] = Relationship(back_populates="reviewed_by_user")

    # Clarify that this uses Feedback.user_id
    feedback: List["Feedback"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[Feedback.user_id]"}
    )

    class Config:
        from_attributes = True


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    deleted_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    users: List["User"] = Relationship(back_populates="role")
    
    class Config:
        from_attributes = True


class BlacklistedToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True, max_length=500)
    user_id: int = Field(foreign_key="user.id", index=True)
    blacklisted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    user: User = Relationship(back_populates="blacklisted_tokens")
    
    class Config:
        from_attributes = True


class PasswordResetToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True, max_length=500)
    user_id: int = Field(foreign_key="user.id", index=True)
    expires_at: datetime
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    user: User = Relationship(back_populates="password_reset_tokens")
    
    class Config:
        from_attributes = True
