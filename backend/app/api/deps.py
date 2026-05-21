"""Shared API dependencies — DB session, auth guards, audit logging."""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import json

from app.db.database import get_db
from app.core.security import decode_access_token
from app.core.enums import UserRoleEnum, AuditActionEnum
from app.models.admin import Admin
from app.models.student import Student
from app.models.invigilator import Invigilator
from app.models.audit_log import AuditLog

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """Extract and verify the current user from JWT token."""
    token_data = decode_access_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = token_data["user_id"]
    role = token_data["role"]

    # Verify user still exists and is active
    if role == UserRoleEnum.ADMIN.value:
        user = db.query(Admin).filter(Admin.id == user_id, Admin.is_active == True).first()
    elif role == UserRoleEnum.INVIGILATOR.value:
        user = db.query(Invigilator).filter(Invigilator.id == user_id, Invigilator.is_active == True).first()
    elif role == UserRoleEnum.STUDENT.value:
        user = db.query(Student).filter(Student.id == user_id, Student.is_active == True).first()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid role")

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return {"user_id": user_id, "role": role, "user": user}


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role."""
    if current_user["role"] != UserRoleEnum.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def require_invigilator(current_user: dict = Depends(get_current_user)) -> dict:
    """Require invigilator role."""
    if current_user["role"] != UserRoleEnum.INVIGILATOR.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invigilator access required")
    return current_user


def require_student(current_user: dict = Depends(get_current_user)) -> dict:
    """Require student role."""
    if current_user["role"] != UserRoleEnum.STUDENT.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student access required")
    return current_user


def create_audit_log(db: Session, user_id: int, user_role: str, action: str,
                     entity_type: str, entity_id: int = None,
                     old_value: dict = None, new_value: dict = None,
                     ip_address: str = None):
    """Create an audit log entry."""
    log = AuditLog(
        user_id=user_id, user_role=user_role, action=action,
        entity_type=entity_type, entity_id=entity_id,
        old_value=json.dumps(old_value) if old_value else None,
        new_value=json.dumps(new_value) if new_value else None,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
