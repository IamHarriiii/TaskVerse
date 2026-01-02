from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional


class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class UserCreateInput(UserBase):
    """Schema for creating a new user."""

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower().strip()


class UserUpdateInput(BaseModel):
    """Schema for updating an existing user."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Name cannot be empty or whitespace")
            return v.strip()
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.lower().strip()
        return v


class UserResponse(UserBase):
    """Schema for user responses."""
    id: UUID
    created_at: datetime