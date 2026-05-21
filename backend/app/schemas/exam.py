"""Exam schemas — request/response models for exam management."""

from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.core.enums import ExamTypeEnum, ExamStatusEnum, SemesterEnum


class ExamBase(BaseModel):
    """Base exam fields."""
    subject_id: int = Field(..., gt=0)
    exam_date: date
    start_time: time
    end_time: time
    exam_type: ExamTypeEnum
    department: str = Field(..., min_length=1, max_length=50)
    semester: SemesterEnum

    @field_validator("end_time")
    @classmethod
    def end_time_after_start(cls, v, info):
        """Ensure end time is after start time."""
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("End time must be after start time")
        return v


class ExamCreate(ExamBase):
    """Schema for creating a new exam."""
    status: ExamStatusEnum = ExamStatusEnum.DRAFT


class ExamUpdate(BaseModel):
    """Schema for updating an exam."""
    subject_id: Optional[int] = Field(None, gt=0)
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    exam_type: Optional[ExamTypeEnum] = None
    status: Optional[ExamStatusEnum] = None
    department: Optional[str] = Field(None, min_length=1, max_length=50)
    semester: Optional[SemesterEnum] = None


class ExamResponse(BaseModel):
    """Schema for exam data in API responses."""
    id: int
    subject_id: int
    subject_name: str
    subject_code: str
    exam_date: date
    start_time: time
    end_time: time
    exam_type: ExamTypeEnum
    status: ExamStatusEnum
    department: str
    semester: SemesterEnum
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    total_students_assigned: int = 0

    model_config = {"from_attributes": True}


class ExamListResponse(BaseModel):
    """Paginated list of exams."""
    exams: List[ExamResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ExamStatusUpdate(BaseModel):
    """Schema for updating exam status only."""
    status: ExamStatusEnum
