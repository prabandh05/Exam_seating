"""Student schemas — request/response models for student management."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator
from app.core.enums import SemesterEnum, GenderEnum


class StudentBase(BaseModel):
    """Base student fields shared across create/update."""
    register_number: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Za-z0-9]+$")
    name: str = Field(..., min_length=1, max_length=100)
    department: str = Field(..., min_length=1, max_length=50)
    semester: SemesterEnum
    section: str = Field(..., min_length=1, max_length=10)
    year: int = Field(..., ge=1, le=4)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15, pattern=r"^[0-9+\-\s]+$")
    gender: GenderEnum


class StudentCreate(StudentBase):
    """Schema for creating a new student."""
    password: str = Field(..., min_length=6, max_length=128)


class StudentUpdate(BaseModel):
    """Schema for updating a student (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    semester: Optional[SemesterEnum] = None
    section: Optional[str] = Field(None, min_length=1, max_length=10)
    year: Optional[int] = Field(None, ge=1, le=4)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15, pattern=r"^[0-9+\-\s]+$")
    gender: Optional[GenderEnum] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    """Schema for student data in API responses."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    """Paginated list of students."""
    students: List[StudentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BulkUploadResponse(BaseModel):
    """Response after bulk student upload."""
    total_processed: int
    successful: int
    failed: int
    errors: List[dict]
