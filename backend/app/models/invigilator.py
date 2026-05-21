"""Invigilator model — faculty members who monitor exams."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base


class Invigilator(Base):
    __tablename__ = "invigilators"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    invigilator_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    total_duties = Column(Integer, default=0, nullable=False)
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
    duties = relationship(
        "InvigilatorDuty", back_populates="invigilator", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Invigilator(id={self.id}, invigilator_id='{self.invigilator_id}')>"
