"""InvigilatorDuty model — assigns invigilators to halls for exams."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, Date, Time, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class InvigilatorDuty(Base):
    __tablename__ = "invigilator_duties"
    __table_args__ = (
        # One invigilator per hall per time slot
        UniqueConstraint("hall_id", "exam_date", "start_time", "end_time", name="uq_slot_hall_invigilator"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    invigilator_id = Column(
        Integer,
        ForeignKey("invigilators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exam_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    hall_id = Column(
        Integer, ForeignKey("halls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    invigilator = relationship("Invigilator", back_populates="duties")
    hall = relationship("Hall", back_populates="invigilator_duties")

    def __repr__(self):
        return (
            f"<InvigilatorDuty(id={self.id}, invigilator={self.invigilator_id}, "
            f"date={self.exam_date}, hall={self.hall_id})>"
        )
