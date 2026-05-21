"""Attendance model — tracks student attendance during exams."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        # One attendance record per seating assignment
        UniqueConstraint("seating_id", name="uq_attendance_seating"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    seating_id = Column(
        Integer,
        ForeignKey("seating_arrangements.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    status = Column(String(10), nullable=False)  # AttendanceStatusEnum
    marked_by = Column(
        Integer, ForeignKey("invigilators.id", ondelete="SET NULL"), nullable=True
    )
    marked_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    seating = relationship("SeatingArrangement", back_populates="attendance")

    def __repr__(self):
        return f"<Attendance(id={self.id}, seating={self.seating_id}, status='{self.status}')>"
