from pydantic import Field
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID
from models.base import BaseDomainModal

class TaskModel(BaseDomainModal):
    """
    Internal Task domain model.
    Represents how tasks are stored in the system.
    """
    user_id: UUID
    title: str = Field(min_length=3, max_length=50)
    description: str | None = None
    priority: int = Field(ge=1, le=5)
    status: Literal['pending', 'done', 'in_progress']
    due_date: datetime
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))