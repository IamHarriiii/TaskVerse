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
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return v
    
    @field_validator("due_date")
    @classmethod
    def validate_due_date_is_future(cls, value: datetime) -> datetime:
        now = datetime.now(timezone.utc)

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        
        if value <= now:
            raise ValueError("due_date must be a future datetime")
        return value


class TaskUpdateInput(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    description: Optional[str] = None
    priority: Literal[1, 2, 3, 4, 5] | None = None
    status: Optional[Literal["pending", "in_progress", "done"]] = None
    due_date: Optional[datetime] = None
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty or whitespace")
            return v.strip()
        return v
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return v
    
    @field_validator("due_date")
    @classmethod
    def validate_updated_due_date_is_future(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is not None:
            now = datetime.now(timezone.utc)
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            
            if value <= now:
                raise ValueError("due_date must be a future datetime")
        return value


class TaskResponse(TaskBaseSchema):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime