"""Database initialization — creates tables and seeds default admin."""

from app.db.database import engine, Base, SessionLocal
from app.models import *  # Import all models so Base knows about them
from app.core.config import settings
from app.core.security import hash_password
from app.models.admin import Admin


def init_db():
    """Create all tables and seed default admin if not exists."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if seating_locked exists on exams table, if not, add it
        from sqlalchemy import text
        try:
            db.execute(text("SELECT seating_locked FROM exams LIMIT 1"))
        except Exception:
            db.rollback()
            try:
                db.execute(text("ALTER TABLE exams ADD COLUMN seating_locked BOOLEAN DEFAULT 0"))
                db.commit()
                print("[INIT] Added seating_locked column to exams table")
            except Exception as e:
                db.rollback()
                print(f"[INIT] Failed to add column: {e}")

        # Seed default admin
        existing = db.query(Admin).filter(Admin.username == settings.DEFAULT_ADMIN_USERNAME).first()
        if not existing:
            admin = Admin(
                username=settings.DEFAULT_ADMIN_USERNAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                full_name=settings.DEFAULT_ADMIN_NAME,
            )
            db.add(admin)
            db.commit()
            print(f"[INIT] Default admin created: {settings.DEFAULT_ADMIN_USERNAME}")
        else:
            print("[INIT] Default admin already exists")
    finally:
        db.close()
