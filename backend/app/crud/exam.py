"""CRUD operations for Exam management."""

from datetime import date, datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.exam import Exam
from app.models.subject import Subject
from app.models.seating import SeatingArrangement
from app.schemas.exam import ExamCreate, ExamUpdate
from app.core.enums import ExamStatusEnum


def get_exam_by_id(db: Session, exam_id: int) -> Optional[Exam]:
    """Get an exam by ID with subject loaded."""
    return (
        db.query(Exam)
        .options(joinedload(Exam.subject))
        .filter(Exam.id == exam_id)
        .first()
    )


def get_exams(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    department: Optional[str] = None,
    semester: Optional[str] = None,
    exam_date: Optional[date] = None,
) -> Tuple[List[Exam], int]:
    """Get paginated list of exams with optional filters."""
    query = db.query(Exam).options(joinedload(Exam.subject))

    if status:
        query = query.filter(Exam.status == status)
    if department:
        query = query.filter(Exam.department == department)
    if semester:
        query = query.filter(Exam.semester == semester)
    if exam_date:
        query = query.filter(Exam.exam_date == exam_date)

    total = query.count()
    exams = (
        query.order_by(Exam.exam_date.desc(), Exam.start_time)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return exams, total


def create_exam(db: Session, data: ExamCreate, admin_id: int) -> Exam:
    """Create a new exam."""
    exam = Exam(
        subject_id=data.subject_id,
        exam_date=data.exam_date,
        start_time=data.start_time,
        end_time=data.end_time,
        exam_type=data.exam_type.value,
        status=data.status.value,
        department=data.department,
        semester=data.semester.value,
        created_by=admin_id,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


def update_exam(db: Session, exam_id: int, data: ExamUpdate) -> Optional[Exam]:
    """Update an exam."""
    exam = get_exam_by_id(db, exam_id)
    if not exam:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # Convert enum values
    if "exam_type" in update_data and update_data["exam_type"] is not None:
        update_data["exam_type"] = update_data["exam_type"].value
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = update_data["status"].value
    if "semester" in update_data and update_data["semester"] is not None:
        update_data["semester"] = update_data["semester"].value

    for field, value in update_data.items():
        setattr(exam, field, value)

    db.commit()
    db.refresh(exam)
    return exam


def delete_exam(db: Session, exam_id: int) -> bool:
    """Delete an exam."""
    exam = get_exam_by_id(db, exam_id)
    if not exam:
        return False
    db.delete(exam)
    db.commit()
    return True


def get_overlapping_exams(
    db: Session, exam_date: date, start_time, end_time, exclude_exam_id: Optional[int] = None
) -> List[Exam]:
    """Find exams that overlap with the given time slot on the same date."""
    query = db.query(Exam).filter(
        Exam.exam_date == exam_date,
        Exam.status.in_([ExamStatusEnum.PUBLISHED.value, ExamStatusEnum.ONGOING.value]),
        # Overlap: existing.start < new.end AND existing.end > new.start
        Exam.start_time < end_time,
        Exam.end_time > start_time,
    )
    if exclude_exam_id:
        query = query.filter(Exam.id != exclude_exam_id)
    return query.all()


def get_upcoming_exams(db: Session, limit: int = 10) -> List[Exam]:
    """Get upcoming published exams."""
    today = date.today()
    return (
        db.query(Exam)
        .options(joinedload(Exam.subject))
        .filter(
            Exam.exam_date >= today,
            Exam.status.in_([ExamStatusEnum.PUBLISHED.value, ExamStatusEnum.ONGOING.value]),
        )
        .order_by(Exam.exam_date, Exam.start_time)
        .limit(limit)
        .all()
    )


def get_exams_by_date(db: Session, exam_date: date) -> List[Exam]:
    """Get all exams on a specific date."""
    return (
        db.query(Exam)
        .options(joinedload(Exam.subject))
        .filter(Exam.exam_date == exam_date)
        .order_by(Exam.start_time)
        .all()
    )


def get_student_exam_count(db: Session, exam_id: int) -> int:
    """Get count of students assigned to an exam via seating."""
    return (
        db.query(SeatingArrangement)
        .filter(SeatingArrangement.exam_id == exam_id)
        .count()
    )
