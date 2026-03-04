from pydantic import Field
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID
from models.base import BaseDomainModel


class SubTask(BaseDomainModel):
    """A lightweight sub-task nested inside a parent Task."""

    title: str = Field(min_length=1, max_length=200)
    is_completed: bool = False


class Task(BaseDomainModel):
    """
    Internal Task domain model.
    Represents how tasks are stored in the system.
    """

    user_id: UUID
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    priority: Literal[1, 2, 3, 4, 5] = 3
    status: Literal["pending", "done", "in_progress"] = "pending"
    due_date: datetime
    tags: list[str] = Field(default_factory=list)
    subtasks: list[SubTask] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))