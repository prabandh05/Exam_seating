"""Authentication schemas — login requests and token responses."""

from pydantic import BaseModel, Field
from app.core.enums import UserRoleEnum


class LoginRequest(BaseModel):
    """Login request for all user roles."""
    username: str = Field(..., min_length=1, max_length=50, description="Username or register number")
    password: str = Field(..., min_length=1, max_length=128, description="User password")
    role: UserRoleEnum = Field(..., description="User role (admin, invigilator, student)")


class TokenResponse(BaseModel):
    """JWT token response after successful login."""
    access_token: str
    token_type: str = "bearer"
    role: UserRoleEnum
    user_id: int
    name: str


class ChangePasswordRequest(BaseModel):
    """Password change request."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)


class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""
    email: str = Field(..., description="Registered email address")
    role: UserRoleEnum


class ResetPasswordRequest(BaseModel):
    """Reset password with token."""
    token: str
    new_password: str = Field(..., min_length=6, max_length=128)


class PasswordResetTokenResponse(BaseModel):
    """Response with reset token (dev mode - no email)."""
    message: str
    reset_token: str  # In production, this would be sent via email
