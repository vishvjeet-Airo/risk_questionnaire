from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    deleted_at: Optional[datetime] = Field(default=None)
    
    questionnaire_files: List["QuestionnaireFile"] = Relationship(back_populates="client")

    class Config:
        from_attributes = True

