"""Authentication endpoints for all three user roles."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.core.enums import UserRoleEnum
from app.models.admin import Admin
from app.models.student import Student
from app.models.invigilator import Invigilator
from app.schemas.auth import (
    LoginRequest, TokenResponse, ChangePasswordRequest,
    ForgotPasswordRequest, PasswordResetTokenResponse,
)
from app.api.deps import get_current_user, create_audit_log

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Unified login for admin, invigilator, and student."""
    user = None
    name = ""

    if data.role == UserRoleEnum.ADMIN:
        user = db.query(Admin).filter(Admin.username == data.username, Admin.is_active == True).first()
        if user:
            name = user.full_name
    elif data.role == UserRoleEnum.INVIGILATOR:
        user = db.query(Invigilator).filter(
            Invigilator.invigilator_id == data.username, Invigilator.is_active == True
        ).first()
        if user:
            name = user.name
    elif data.role == UserRoleEnum.STUDENT:
        user = db.query(Student).filter(
            Student.register_number == data.username, Student.is_active == True
        ).first()
        if user:
            name = user.name

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.id, data.role)
    create_audit_log(db, user.id, data.role.value, "login", data.role.value, user.id)

    return TokenResponse(
        access_token=token, role=data.role, user_id=user.id, name=name,
    )


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change password for current user."""
    user = current_user["user"]
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    user.password_hash = hash_password(data.new_password)
    db.commit()
    create_audit_log(db, current_user["user_id"], current_user["role"], "change_password",
                     current_user["role"], current_user["user_id"])

    return {"message": "Password changed successfully"}


@router.post("/forgot-password", response_model=PasswordResetTokenResponse)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generate a password reset token (dev mode — returns token directly)."""
    import secrets
    user = None

    if data.role == UserRoleEnum.ADMIN:
        user = db.query(Admin).filter(Admin.email == data.email).first()
    elif data.role == UserRoleEnum.INVIGILATOR:
        user = db.query(Invigilator).filter(Invigilator.email == data.email).first()
    elif data.role == UserRoleEnum.STUDENT:
        user = db.query(Student).filter(Student.email == data.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

    # In production, send this via email. For dev, return directly.
    reset_token = secrets.token_urlsafe(32)
    return PasswordResetTokenResponse(
        message="Password reset token generated. In production, this would be sent via email.",
        reset_token=reset_token,
    )
