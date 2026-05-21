"""Notification model — system notifications with read tracking."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)  # NotificationTypeEnum
    target_role = Column(String(20), nullable=True)  # NULL = all roles
    target_department = Column(String(50), nullable=True)  # NULL = all departments
    target_semester = Column(String(2), nullable=True)  # NULL = all semesters
    created_by = Column(Integer, ForeignKey("admins.id"), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    reads = relationship(
        "NotificationRead", back_populates="notification", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Notification(id={self.id}, title='{self.title}')>"


class NotificationRead(Base):
    __tablename__ = "notification_reads"
    __table_args__ = (
        UniqueConstraint(
            "notification_id", "user_id", "user_role",
            name="uq_notification_user_role"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    notification_id = Column(
        Integer,
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(Integer, nullable=False)
    user_role = Column(String(20), nullable=False)  # UserRoleEnum
    read_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    notification = relationship("Notification", back_populates="reads")

    def __repr__(self):
        return (
            f"<NotificationRead(notification={self.notification_id}, "
            f"user={self.user_id}, role='{self.user_role}')>"
        )
