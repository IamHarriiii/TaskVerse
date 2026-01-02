from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional


class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class UserCreateInput(UserBase):
    @field_validator('name')
    @classmethod
    def validate_name(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return name.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, email: str) -> str:
        return email.lower().strip()


class UserUpdateInput(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, name: Optional[str]) -> Optional[str]:
        if name is not None:
            if not name.strip():
                raise ValueError("Name cannot be empty or whitespace")
            return name.strip()
        return name
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, email: Optional[str]) -> Optional[str]:
        if email is not None:
            return email.lower().strip()
        return email


class UserResponse(UserBase):
    id: UUID
    created_at: datetime