"""
Application configuration using Pydantic BaseSettings.
Reads from environment variables or .env file.
Database URL is the only thing that needs to change to switch from SQLite to MySQL/PostgreSQL.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Exam Seating Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database — Change this single line to switch databases:
    # SQLite:      sqlite:///./exam_seating.db
    # PostgreSQL:  postgresql://user:password@localhost:5432/exam_seating
    # MySQL:       mysql+pymysql://user:password@localhost:3306/exam_seating
    DATABASE_URL: str = "sqlite:///./exam_seating.db"

    # JWT Authentication
    SECRET_KEY: str = "exam-seating-system-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # Default Admin (seeded on first run)
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    DEFAULT_ADMIN_EMAIL: str = "admin@examsystem.com"
    DEFAULT_ADMIN_NAME: str = "System Administrator"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Alternative dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: list[str] = [".csv", ".xlsx", ".xls"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
