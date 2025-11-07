from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from app.models.questionnaire_file import QuestionnaireTechnologyLink



class Technology(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=255)
    created_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))
    deleted_at: Optional[datetime] = None

    
    questionnaire_files: List["QuestionnaireFile"] = Relationship(
        back_populates="technologies",
        link_model=QuestionnaireTechnologyLink
    )
    
    class Config:
        from_attributes = True

