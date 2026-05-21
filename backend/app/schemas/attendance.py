"""Attendance schemas — request/response models for attendance management."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.core.enums import AttendanceStatusEnum


class MarkAttendanceRequest(BaseModel):
    """Mark attendance for a single student."""
    seating_id: int = Field(..., gt=0)
    status: AttendanceStatusEnum


class BulkAttendanceRequest(BaseModel):
    """Mark attendance for multiple students at once."""
    attendance_records: List[MarkAttendanceRequest]


class AttendanceResponse(BaseModel):
    """Attendance record in API response."""
    id: int
    seating_id: int
    student_name: str
    register_number: str
    seat_number: str
    hall_number: str
    status: AttendanceStatusEnum
    marked_by: Optional[int] = None
    marked_by_name: Optional[str] = None
    marked_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HallAttendanceResponse(BaseModel):
    """Attendance summary for a hall."""
    hall_id: int
    hall_number: str
    exam_id: int
    subject_name: str
    total_students: int
    present: int
    absent: int
    late: int
    attendance_percentage: float
    records: List[AttendanceResponse]


class AttendanceReportResponse(BaseModel):
    """Overall attendance report for an exam."""
    exam_id: int
    subject_name: str
    exam_date: str
    total_students: int
    total_present: int
    total_absent: int
    total_late: int
    overall_percentage: float
    hall_reports: List[HallAttendanceResponse]
