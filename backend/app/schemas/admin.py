"""Admin schemas — request/response models for admin management."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class AdminResponse(BaseModel):
    """Schema for admin data in API responses."""
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminUpdate(BaseModel):
    """Schema for updating admin profile."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
