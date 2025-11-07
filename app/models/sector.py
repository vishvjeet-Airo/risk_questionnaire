from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from app.models.questionnaire_file import QuestionnaireSectorLink


class Sector(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow,sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow,sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = Field(default=None)
    
    questionnaire_files: List["QuestionnaireFile"] = Relationship(
        back_populates="sectors",
        link_model=QuestionnaireSectorLink
    )
    
    class Config:
        from_attributes = True