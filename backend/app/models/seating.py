"""SeatingArrangement model — maps students to seats in halls for exams."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class SeatingArrangement(Base):
    __tablename__ = "seating_arrangements"
    __table_args__ = (
        # No seat duplication: one seat per exam in a hall
        UniqueConstraint("exam_id", "hall_id", "seat_number", name="uq_exam_hall_seat"),
        # One student per exam: prevents double assignment
        UniqueConstraint("exam_id", "student_id", name="uq_exam_student"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    exam_id = Column(
        Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hall_id = Column(
        Integer, ForeignKey("halls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id = Column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seat_number = Column(String(10), nullable=False)
    row_number = Column(Integer, nullable=False)
    column_number = Column(Integer, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    is_reserved = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    exam = relationship("Exam", back_populates="seating_arrangements")
    hall = relationship("Hall", back_populates="seating_arrangements")
    student = relationship("Student", back_populates="seating_arrangements")
    attendance = relationship(
        "Attendance", back_populates="seating", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<SeatingArrangement(id={self.id}, exam={self.exam_id}, "
            f"hall={self.hall_id}, seat='{self.seat_number}')>"
        )
