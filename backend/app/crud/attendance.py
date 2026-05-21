"""CRUD operations for Attendance management."""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.attendance import Attendance
from app.models.seating import SeatingArrangement
from app.core.enums import AttendanceStatusEnum


def get_attendance_by_seating(db: Session, seating_id: int) -> Optional[Attendance]:
    return db.query(Attendance).filter(Attendance.seating_id == seating_id).first()


def get_attendance_by_exam(db: Session, exam_id: int) -> List[Attendance]:
    return (
        db.query(Attendance)
        .join(SeatingArrangement)
        .filter(SeatingArrangement.exam_id == exam_id)
        .all()
    )


def get_attendance_by_exam_hall(db: Session, exam_id: int, hall_id: int) -> List[Attendance]:
    return (
        db.query(Attendance)
        .join(SeatingArrangement)
        .filter(SeatingArrangement.exam_id == exam_id, SeatingArrangement.hall_id == hall_id)
        .all()
    )


def mark_attendance(db: Session, seating_id: int, status: AttendanceStatusEnum, marked_by: int) -> Attendance:
    existing = get_attendance_by_seating(db, seating_id)
    if existing:
        existing.status = status.value
        existing.marked_by = marked_by
        db.commit()
        db.refresh(existing)
        return existing
    
    attendance = Attendance(seating_id=seating_id, status=status.value, marked_by=marked_by)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def bulk_mark_attendance(db: Session, records: List[dict], marked_by: int) -> int:
    count = 0
    for record in records:
        mark_attendance(db, record["seating_id"], record["status"], marked_by)
        count += 1
    return count


def get_attendance_stats(db: Session, exam_id: int) -> dict:
    """Get attendance statistics for an exam."""
    seatings = db.query(SeatingArrangement).filter(SeatingArrangement.exam_id == exam_id).all()
    total = len(seatings)
    seating_ids = [s.id for s in seatings]
    
    attendances = db.query(Attendance).filter(Attendance.seating_id.in_(seating_ids)).all() if seating_ids else []
    
    present = sum(1 for a in attendances if a.status == AttendanceStatusEnum.PRESENT.value)
    absent = sum(1 for a in attendances if a.status == AttendanceStatusEnum.ABSENT.value)
    late = sum(1 for a in attendances if a.status == AttendanceStatusEnum.LATE.value)
    unmarked = total - len(attendances)
    
    return {
        "total": total, "present": present, "absent": absent,
        "late": late, "unmarked": unmarked,
        "percentage": round((present + late) / total * 100, 2) if total > 0 else 0
    }
