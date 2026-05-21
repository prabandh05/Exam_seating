"""Seating arrangement schemas — request/response models for seating management."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.core.enums import SeatingModeEnum


class GenerateSeatingRequest(BaseModel):
    """Request to auto-generate seating arrangement."""
    exam_ids: List[int] = Field(..., min_length=1, description="List of exam IDs to generate seating for")
    hall_ids: List[int] = Field(..., min_length=1, description="List of hall IDs to use")
    mode: SeatingModeEnum = Field(
        default=SeatingModeEnum.MIXED_SUBJECT,
        description="Seating arrangement mode"
    )
    clear_existing: bool = Field(
        default=False,
        description="Clear existing seating before generating"
    )


class ManualSeatAssignment(BaseModel):
    """Manual seat assignment for a single student."""
    exam_id: int = Field(..., gt=0)
    hall_id: int = Field(..., gt=0)
    student_id: int = Field(..., gt=0)
    row_number: int = Field(..., gt=0)
    column_number: int = Field(..., gt=0)


class SeatSwapRequest(BaseModel):
    """Request to swap two students' seats."""
    seating_id_1: int = Field(..., gt=0)
    seating_id_2: int = Field(..., gt=0)


class SeatMoveRequest(BaseModel):
    """Request to move a student to a different hall/seat."""
    seating_id: int = Field(..., gt=0)
    new_hall_id: int = Field(..., gt=0)
    new_row: int = Field(..., gt=0)
    new_column: int = Field(..., gt=0)


class SeatLockRequest(BaseModel):
    """Request to lock/unlock a seat."""
    is_locked: bool


class SeatingResponse(BaseModel):
    """Schema for seating arrangement in API responses."""
    id: int
    exam_id: int
    hall_id: int
    hall_number: str
    student_id: int
    student_name: str
    register_number: str
    department: str
    subject_name: str
    subject_code: str
    seat_number: str
    row_number: int
    column_number: int
    is_locked: bool
    is_reserved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class HallSeatingResponse(BaseModel):
    """All seating in a hall for a specific exam."""
    hall_id: int
    hall_number: str
    floor_number: int
    capacity: int
    num_rows: int
    num_columns: int
    total_assigned: int
    seats: List[SeatingResponse]


class SeatingGenerationResult(BaseModel):
    """Result of auto seating generation."""
    success: bool
    message: str
    total_students_assigned: int
    halls_used: int
    conflicts_detected: List[str]
    hall_details: List[dict]


class ConflictCheckResponse(BaseModel):
    """Result of conflict checking."""
    has_conflicts: bool
    conflicts: List[str]
    total_conflicts: int
