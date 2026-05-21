"""Student model — stores all student information required for exams."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.core.enums import SemesterEnum, GenderEnum


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint("year >= 1 AND year <= 4", name="check_year_range"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    register_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(50), nullable=False, index=True)
    semester = Column(String(2), nullable=False)  # Validated via Pydantic SemesterEnum
    section = Column(String(10), nullable=False)
    year = Column(Integer, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=False)
    gender = Column(String(10), nullable=False)  # Validated via Pydantic GenderEnum
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
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
    seating_arrangements = relationship(
        "SeatingArrangement", back_populates="student", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Student(id={self.id}, register_number='{self.register_number}')>"
