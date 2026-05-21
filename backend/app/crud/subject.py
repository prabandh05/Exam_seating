"""CRUD operations for Subject management."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


def get_subject_by_id(db: Session, subject_id: int) -> Optional[Subject]:
    """Get a subject by ID."""
    return db.query(Subject).filter(Subject.id == subject_id).first()


def get_subject_by_code(db: Session, subject_code: str) -> Optional[Subject]:
    """Get a subject by code."""
    return db.query(Subject).filter(Subject.subject_code == subject_code).first()


def get_subjects(
    db: Session,
    department: Optional[str] = None,
    semester: Optional[str] = None,
) -> List[Subject]:
    """Get all subjects with optional filters."""
    query = db.query(Subject)
    if department:
        query = query.filter(Subject.department == department)
    if semester:
        query = query.filter(Subject.semester == semester)
    return query.order_by(Subject.subject_code).all()


def create_subject(db: Session, data: SubjectCreate) -> Subject:
    """Create a new subject."""
    subject = Subject(
        subject_code=data.subject_code,
        subject_name=data.subject_name,
        department=data.department,
        semester=data.semester.value,
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def update_subject(db: Session, subject_id: int, data: SubjectUpdate) -> Optional[Subject]:
    """Update a subject."""
    subject = get_subject_by_id(db, subject_id)
    if not subject:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if "semester" in update_data and update_data["semester"] is not None:
        update_data["semester"] = update_data["semester"].value

    for field, value in update_data.items():
        setattr(subject, field, value)

    db.commit()
    db.refresh(subject)
    return subject


def delete_subject(db: Session, subject_id: int) -> bool:
    """Delete a subject."""
    subject = get_subject_by_id(db, subject_id)
    if not subject:
        return False
    db.delete(subject)
    db.commit()
    return True
