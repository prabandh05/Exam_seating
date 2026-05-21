"""CRUD operations for Notification management."""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationRead
from app.schemas.notification import NotificationCreate
from app.core.enums import UserRoleEnum


def create_notification(db: Session, data: NotificationCreate, admin_id: int) -> Notification:
    notif = Notification(
        title=data.title, message=data.message, type=data.type.value,
        target_role=data.target_role.value if data.target_role else None,
        target_department=data.target_department,
        target_semester=data.target_semester.value if data.target_semester else None,
        created_by=admin_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_notifications(db: Session, role: Optional[str] = None, department: Optional[str] = None,
                       semester: Optional[str] = None, limit: int = 50) -> List[Notification]:
    query = db.query(Notification)
    if role:
        query = query.filter((Notification.target_role == role) | (Notification.target_role == None))
    if department:
        query = query.filter((Notification.target_department == department) | (Notification.target_department == None))
    if semester:
        query = query.filter((Notification.target_semester == semester) | (Notification.target_semester == None))
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


def get_all_notifications(db: Session) -> List[Notification]:
    return db.query(Notification).order_by(Notification.created_at.desc()).all()


def delete_notification(db: Session, notif_id: int) -> bool:
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        return False
    db.delete(notif)
    db.commit()
    return True


def mark_notification_read(db: Session, notif_id: int, user_id: int, user_role: str) -> NotificationRead:
    existing = db.query(NotificationRead).filter(
        NotificationRead.notification_id == notif_id,
        NotificationRead.user_id == user_id,
        NotificationRead.user_role == user_role,
    ).first()
    if existing:
        return existing
    
    read = NotificationRead(notification_id=notif_id, user_id=user_id, user_role=user_role)
    db.add(read)
    db.commit()
    db.refresh(read)
    return read


def get_unread_count(db: Session, user_id: int, user_role: str) -> int:
    total = db.query(Notification).filter(
        (Notification.target_role == user_role) | (Notification.target_role == None)
    ).count()
    read = db.query(NotificationRead).filter(
        NotificationRead.user_id == user_id, NotificationRead.user_role == user_role
    ).count()
    return max(0, total - read)
