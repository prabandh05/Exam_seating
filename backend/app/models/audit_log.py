"""AuditLog model — tracks all system changes for accountability."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_role = Column(String(20), nullable=False)  # UserRoleEnum
    action = Column(String(50), nullable=False)  # AuditActionEnum
    entity_type = Column(String(50), nullable=False)  # e.g., "student", "exam", "seating"
    entity_id = Column(Integer, nullable=True)
    old_value = Column(Text, nullable=True)  # JSON string of old values
    new_value = Column(Text, nullable=True)  # JSON string of new values
    ip_address = Column(String(45), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, action='{self.action}', "
            f"entity='{self.entity_type}', user={self.user_id})>"
        )
