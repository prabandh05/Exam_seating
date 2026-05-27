"""CRUD operations for Seating Arrangement."""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.seating import SeatingArrangement
from app.models.exam import Exam
from app.models.hall import Hall
from app.models.student import Student
from app.models.subject import Subject


def get_seating_by_id(db: Session, seating_id: int) -> Optional[SeatingArrangement]:
    return db.query(SeatingArrangement).filter(SeatingArrangement.id == seating_id).first()


def get_seating_by_exam(db: Session, exam_id: int) -> List[SeatingArrangement]:
    return (
        db.query(SeatingArrangement)
        .options(
            joinedload(SeatingArrangement.student),
            joinedload(SeatingArrangement.hall),
            joinedload(SeatingArrangement.exam).joinedload(Exam.subject),
        )
        .filter(SeatingArrangement.exam_id == exam_id)
        .order_by(SeatingArrangement.hall_id, SeatingArrangement.row_number, SeatingArrangement.column_number)
        .all()
    )


def get_seating_by_exam_hall(db: Session, exam_id: int, hall_id: int) -> List[SeatingArrangement]:
    return (
        db.query(SeatingArrangement)
        .options(joinedload(SeatingArrangement.student), joinedload(SeatingArrangement.exam).joinedload(Exam.subject), joinedload(SeatingArrangement.attendance))
        .filter(SeatingArrangement.exam_id == exam_id, SeatingArrangement.hall_id == hall_id)
        .order_by(SeatingArrangement.row_number, SeatingArrangement.column_number)
        .all()
    )


def get_student_seating(db: Session, student_id: int) -> List[SeatingArrangement]:
    return (
        db.query(SeatingArrangement)
        .options(
            joinedload(SeatingArrangement.hall),
            joinedload(SeatingArrangement.exam).joinedload(Exam.subject),
        )
        .filter(SeatingArrangement.student_id == student_id)
        .all()
    )


def create_seating(db: Session, exam_id: int, hall_id: int, student_id: int,
                    seat_number: str, row_number: int, column_number: int) -> SeatingArrangement:
    seating = SeatingArrangement(
        exam_id=exam_id, hall_id=hall_id, student_id=student_id,
        seat_number=seat_number, row_number=row_number, column_number=column_number,
    )
    db.add(seating)
    return seating


def bulk_create_seating(db: Session, seating_list: List[dict]) -> int:
    """Bulk create seating arrangements. Returns count created."""
    objects = [SeatingArrangement(**s) for s in seating_list]
    db.add_all(objects)
    db.commit()
    return len(objects)


def delete_seating_by_exam(db: Session, exam_id: int) -> int:
    count = db.query(SeatingArrangement).filter(SeatingArrangement.exam_id == exam_id).delete()
    db.commit()
    return count


def swap_seats(db: Session, seating_id_1: int, seating_id_2: int) -> bool:
    s1 = get_seating_by_id(db, seating_id_1)
    s2 = get_seating_by_id(db, seating_id_2)
    if not s1 or not s2:
        return False
    if s1.is_locked or s2.is_locked:
        return False
    # Swap student assignments
    s1.student_id, s2.student_id = s2.student_id, s1.student_id
    db.commit()
    return True


def lock_seat(db: Session, seating_id: int, is_locked: bool) -> Optional[SeatingArrangement]:
    seating = get_seating_by_id(db, seating_id)
    if not seating:
        return None
    seating.is_locked = is_locked
    db.commit()
    db.refresh(seating)
    return seating


def check_student_exam_conflict(db: Session, student_id: int, exam_id: int) -> bool:
    """Check if student is already assigned to this exam."""
    return db.query(SeatingArrangement).filter(
        SeatingArrangement.student_id == student_id,
        SeatingArrangement.exam_id == exam_id,
    ).first() is not None


def check_seat_occupied(db: Session, exam_id: int, hall_id: int, seat_number: str) -> bool:
    """Check if a specific seat is already occupied."""
    return db.query(SeatingArrangement).filter(
        SeatingArrangement.exam_id == exam_id,
        SeatingArrangement.hall_id == hall_id,
        SeatingArrangement.seat_number == seat_number,
    ).first() is not None
