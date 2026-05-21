"""CRUD operations for Hall/Classroom management."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.hall import Hall
from app.models.seating import SeatingArrangement
from app.schemas.hall import HallCreate, HallUpdate


def get_hall_by_id(db: Session, hall_id: int) -> Optional[Hall]:
    return db.query(Hall).filter(Hall.id == hall_id).first()


def get_hall_by_number(db: Session, hall_number: str) -> Optional[Hall]:
    return db.query(Hall).filter(Hall.hall_number == hall_number).first()


def get_halls(db: Session, is_enabled: Optional[bool] = None, floor_number: Optional[int] = None) -> List[Hall]:
    query = db.query(Hall)
    if is_enabled is not None:
        query = query.filter(Hall.is_enabled == is_enabled)
    if floor_number is not None:
        query = query.filter(Hall.floor_number == floor_number)
    return query.order_by(Hall.hall_number).all()


def create_hall(db: Session, data: HallCreate) -> Hall:
    hall = Hall(
        hall_number=data.hall_number, floor_number=data.floor_number,
        capacity=data.capacity, num_benches=data.num_benches,
        num_rows=data.num_rows, num_columns=data.num_columns,
    )
    db.add(hall)
    db.commit()
    db.refresh(hall)
    return hall


def update_hall(db: Session, hall_id: int, data: HallUpdate) -> Optional[Hall]:
    hall = get_hall_by_id(db, hall_id)
    if not hall:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(hall, field, value)
    db.commit()
    db.refresh(hall)
    return hall


def delete_hall(db: Session, hall_id: int) -> bool:
    hall = get_hall_by_id(db, hall_id)
    if not hall:
        return False
    db.delete(hall)
    db.commit()
    return True


def toggle_hall(db: Session, hall_id: int, is_enabled: bool) -> Optional[Hall]:
    hall = get_hall_by_id(db, hall_id)
    if not hall:
        return None
    hall.is_enabled = is_enabled
    db.commit()
    db.refresh(hall)
    return hall


def get_hall_occupancy(db: Session, hall_id: int, exam_id: int) -> int:
    return db.query(SeatingArrangement).filter(
        SeatingArrangement.hall_id == hall_id, SeatingArrangement.exam_id == exam_id
    ).count()
