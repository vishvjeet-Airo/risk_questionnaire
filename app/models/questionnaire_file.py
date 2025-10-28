from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .question import Question


class QuestionnaireFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=500)
    original_filename: str = Field(max_length=500)
    s3_bucket_name: str = Field(max_length=255)
    s3_object_key: str = Field(unique=True, max_length=1000)
    s3_etag: Optional[str] = Field(default=None, max_length=255)
    s3_version_id: Optional[str] = Field(default=None, max_length=255)
    file_hash: str = Field(unique=True, max_length=255)
    file_size: int
    file_type: str = Field(max_length=100)
    is_draft: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id", index=True)
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    processing_errors: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    upload_status: str = Field(default="pending", max_length=50)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    user: "User" = Relationship(back_populates="questionnaire_files")
    questions: List["Question"] = Relationship(back_populates="questionnaire_file")
    
    class Config:
        from_attributes = True

