"""Hall model — exam halls/classrooms with seating capacity and layout."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class Hall(Base):
    __tablename__ = "halls"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="check_capacity_positive"),
        CheckConstraint("num_rows > 0", name="check_rows_positive"),
        CheckConstraint("num_columns > 0", name="check_columns_positive"),
        CheckConstraint("num_benches > 0", name="check_benches_positive"),
        CheckConstraint("floor_number >= 0", name="check_floor_non_negative"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    hall_number = Column(String(20), unique=True, nullable=False, index=True)
    floor_number = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    num_benches = Column(Integer, nullable=False)
    num_rows = Column(Integer, nullable=False)
    num_columns = Column(Integer, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
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
        "SeatingArrangement", back_populates="hall", cascade="all, delete-orphan"
    )
    invigilator_duties = relationship(
        "InvigilatorDuty", back_populates="hall", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Hall(id={self.id}, hall_number='{self.hall_number}', capacity={self.capacity})>"
