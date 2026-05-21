"""CRUD operations for Invigilator management."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.invigilator import Invigilator
from app.models.invigilator_duty import InvigilatorDuty
from app.schemas.invigilator import InvigilatorCreate, InvigilatorUpdate
from app.core.security import hash_password


def get_invigilator_by_id(db: Session, invigilator_db_id: int) -> Optional[Invigilator]:
    """Get an invigilator by database ID."""
    return db.query(Invigilator).filter(Invigilator.id == invigilator_db_id).first()


def get_invigilator_by_invigilator_id(db: Session, invigilator_id: str) -> Optional[Invigilator]:
    """Get an invigilator by their unique invigilator ID."""
    return db.query(Invigilator).filter(Invigilator.invigilator_id == invigilator_id).first()


def get_invigilator_by_email(db: Session, email: str) -> Optional[Invigilator]:
    """Get an invigilator by email."""
    return db.query(Invigilator).filter(Invigilator.email == email).first()


def get_invigilators(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    department: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Tuple[List[Invigilator], int]:
    """Get paginated list of invigilators with optional filters."""
    query = db.query(Invigilator)

    if department:
        query = query.filter(Invigilator.department == department)
    if is_active is not None:
        query = query.filter(Invigilator.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Invigilator.name.ilike(search_term),
                Invigilator.invigilator_id.ilike(search_term),
                Invigilator.email.ilike(search_term),
            )
        )

    total = query.count()
    invigilators = (
        query.order_by(Invigilator.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return invigilators, total


def create_invigilator(db: Session, data: InvigilatorCreate) -> Invigilator:
    """Create a new invigilator."""
    invigilator = Invigilator(
        invigilator_id=data.invigilator_id,
        name=data.name,
        department=data.department,
        phone=data.phone,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(invigilator)
    db.commit()
    db.refresh(invigilator)
    return invigilator


def update_invigilator(
    db: Session, invigilator_db_id: int, data: InvigilatorUpdate
) -> Optional[Invigilator]:
    """Update an existing invigilator."""
    invigilator = get_invigilator_by_id(db, invigilator_db_id)
    if not invigilator:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invigilator, field, value)

    db.commit()
    db.refresh(invigilator)
    return invigilator


def delete_invigilator(db: Session, invigilator_db_id: int) -> bool:
    """Delete an invigilator by database ID."""
    invigilator = get_invigilator_by_id(db, invigilator_db_id)
    if not invigilator:
        return False
    db.delete(invigilator)
    db.commit()
    return True


def get_invigilator_duties(
    db: Session, invigilator_db_id: int
) -> List[InvigilatorDuty]:
    """Get all duties assigned to an invigilator."""
    return (
        db.query(InvigilatorDuty)
        .filter(InvigilatorDuty.invigilator_id == invigilator_db_id)
        .all()
    )


def assign_duty(
    db: Session,
    invigilator_db_id: int,
    exam_id: int,
    hall_id: int,
) -> InvigilatorDuty:
    """Assign an invigilator to a hall for an exam."""
    duty = InvigilatorDuty(
        invigilator_id=invigilator_db_id,
        exam_id=exam_id,
        hall_id=hall_id,
    )
    db.add(duty)

    # Increment total duties count
    invigilator = get_invigilator_by_id(db, invigilator_db_id)
    if invigilator:
        invigilator.total_duties += 1

    db.commit()
    db.refresh(duty)
    return duty


def get_duty_by_exam_hall(
    db: Session, exam_id: int, hall_id: int
) -> Optional[InvigilatorDuty]:
    """Check if a duty already exists for an exam-hall combination."""
    return (
        db.query(InvigilatorDuty)
        .filter(
            InvigilatorDuty.exam_id == exam_id,
            InvigilatorDuty.hall_id == hall_id,
        )
        .first()
    )
