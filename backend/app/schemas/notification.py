"""Notification schemas — request/response models for the notification system."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.core.enums import NotificationTypeEnum, UserRoleEnum, SemesterEnum


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    type: NotificationTypeEnum
    target_role: Optional[UserRoleEnum] = None  # None = all roles
    target_department: Optional[str] = None  # None = all departments
    target_semester: Optional[SemesterEnum] = None  # None = all semesters


class NotificationResponse(BaseModel):
    """Schema for notification in API responses."""
    id: int
    title: str
    message: str
    type: NotificationTypeEnum
    target_role: Optional[UserRoleEnum] = None
    target_department: Optional[str] = None
    target_semester: Optional[SemesterEnum] = None
    is_read: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """List of notifications."""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int


class AdminDashboardStats(BaseModel):
    """Dashboard statistics for admin."""
    total_students: int
    total_invigilators: int
    total_halls: int
    total_exams: int
    upcoming_exams: int
    active_exams: int
    completed_exams: int
    total_seating_arrangements: int
    attendance_summary: dict
