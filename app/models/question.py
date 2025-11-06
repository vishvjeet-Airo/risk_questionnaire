from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .questionnaire_file import QuestionnaireFile
    from .user import User


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    questionnaire_file_id: int = Field(foreign_key="questionnairefile.id", index=True)
    question_text: str
    original_answer: str
    suggested_answer: Optional[str] = Field(default=None)
    is_incorrect: bool = Field(default=False)
    comment: Optional[str] = Field(default=None)
    k_value: Optional[int] = Field(default=None)
    meta_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    reviewed_at: Optional[datetime] = Field(default=None)
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id")
    
    # Relationships
    questionnaire_file: "QuestionnaireFile" = Relationship(back_populates="questions")
    reviewed_by_user: Optional["User"] = Relationship(back_populates="questions")
    
    class Config:
        from_attributes = True

