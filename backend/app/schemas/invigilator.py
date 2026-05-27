"""Invigilator schemas — request/response models for invigilator management."""

from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from app.core.enums import UserRoleEnum


class InvigilatorBase(BaseModel):
    """Base invigilator fields."""
    invigilator_id: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    department: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=15, pattern=r"^[0-9+\-\s]+$")
    email: EmailStr


class InvigilatorCreate(InvigilatorBase):
    """Schema for creating a new invigilator."""
    password: str = Field(..., min_length=6, max_length=128)


class InvigilatorUpdate(BaseModel):
    """Schema for updating an invigilator (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=10, max_length=15, pattern=r"^[0-9+\-\s]+$")
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class InvigilatorResponse(InvigilatorBase):
    """Schema for invigilator data in API responses."""
    id: int
    is_active: bool
    total_duties: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvigilatorListResponse(BaseModel):
    """Paginated list of invigilators."""
    invigilators: List[InvigilatorResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DutyAssignRequest(BaseModel):
    """Manual duty assignment request."""
    invigilator_id: int
    hall_id: int
    exam_date: date
    start_time: time
    end_time: time


class DutyResponse(BaseModel):
    """Duty assignment response."""
    id: int
    invigilator_id: int
    invigilator_name: str
    subject_name: str
    exam_date: str
    start_time: str
    end_time: str
    hall_id: int
    hall_number: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InvigilatorDashboardResponse(BaseModel):
    """Invigilator dashboard data."""
    invigilator: InvigilatorResponse
    upcoming_duties: List[DutyResponse]
    total_duties_assigned: int
    has_duties: bool
