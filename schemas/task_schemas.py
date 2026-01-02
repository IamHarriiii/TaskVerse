from datetime import datetime,timezone
from typing import Literal,Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TaskBaseSchema(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    priority: Literal[1, 2, 3, 4, 5] = 3
    status: Literal["pending", "in_progress", "done"]
    due_date: datetime


class TaskCreateInput(TaskBaseSchema):
    user_id: UUID
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return name.strip()
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, description: Optional[str]) -> Optional[str]:
        if description is not None:
            stripped = description.strip()
            return stripped if stripped else None
        return description
    
    @field_validator("due_date")
    @classmethod
    def validate_due_date_is_future(cls, time: datetime) -> datetime:
        now = datetime.now(timezone.utc)

        if time.tzinfo is None:
            time = time.replace(tzinfo=timezone.utc)
        
        if time <= now:
            raise ValueError("due_date must be a future datetime")
        return time


class TaskUpdateInput(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    description: Optional[str] = None
    priority: Literal[1, 2, 3, 4, 5] | None = None
    status: Optional[Literal["pending", "in_progress", "done"]] = None
    due_date: Optional[datetime] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, name: Optional[str]) -> Optional[str]:
        if name is not None:
            if not name.strip():
                raise ValueError("Title cannot be empty or whitespace")
            return name.strip()
        return name
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, description: Optional[str]) -> Optional[str]:
        if description is not None:
            stripped = description.strip()
            return stripped if stripped else None
        return description
    
    @field_validator("due_date")
    @classmethod
    def validate_updated_due_date_is_future(cls, time: Optional[datetime]) -> Optional[datetime]:
        if time is not None:
            now = datetime.now(timezone.utc)
            if time.tzinfo is None:
                time = time.replace(tzinfo=timezone.utc)
            
            if time <= now:
                raise ValueError("due_date must be a future datetime")
        return time


class TaskResponse(TaskBaseSchema):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime