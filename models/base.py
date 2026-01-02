from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class BaseDomainModal(BaseModel):
    """Base class for entities like Task and User.

    Provides common system-managed fields such as unique identifiers 
    and timestamps for auditing."""

    id : UUID = Field(default_factory = uuid4)
    created_at: datetime = Field(default_factory = lambda : datetime.now(timezone.utc))