"""Exam model — scheduled examinations with lifecycle management."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    subject_id = Column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    exam_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    exam_type = Column(String(20), nullable=False)  # Validated via ExamTypeEnum
    status = Column(String(20), nullable=False, default="draft")  # ExamStatusEnum
    department = Column(String(50), nullable=False)
    semester = Column(String(2), nullable=False)  # SemesterEnum
    created_by = Column(Integer, ForeignKey("admins.id"), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    # New flag to lock seating after publishing
    seating_locked = Column(Boolean, default=False, nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="exams")
    seating_arrangements = relationship(
        "SeatingArrangement", back_populates="exam", cascade="all, delete-orphan"
    )
    invigilator_duties = relationship(
        "InvigilatorDuty", back_populates="exam", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Exam(id={self.id}, date={self.exam_date}, status='{self.status}')>"
