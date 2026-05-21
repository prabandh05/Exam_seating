"""Subject schemas — request/response models for subject management."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.core.enums import SemesterEnum


class SubjectBase(BaseModel):
    """Base subject fields."""
    subject_code: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Za-z0-9\-]+$")
    subject_name: str = Field(..., min_length=1, max_length=100)
    department: str = Field(..., min_length=1, max_length=50)
    semester: SemesterEnum


class SubjectCreate(SubjectBase):
    """Schema for creating a new subject."""
    pass


class SubjectUpdate(BaseModel):
    """Schema for updating a subject."""
    subject_name: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    semester: Optional[SemesterEnum] = None


class SubjectResponse(SubjectBase):
    """Schema for subject data in API responses."""
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SubjectListResponse(BaseModel):
    """List of subjects."""
    subjects: List[SubjectResponse]
    total: int
