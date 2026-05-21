"""
Conflict Manager — Detects and prevents all types of scheduling and seating conflicts.

Validates:
- One student → only one exam at a time
- One seat → only one student
- Hall capacity not exceeded
- One invigilator → no overlapping duties
- No duplicate seating assignments
- Exam time overlap detection
"""

from datetime import date, time
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.exam import Exam
from app.models.seating import SeatingArrangement
from app.models.hall import Hall
from app.models.invigilator_duty import InvigilatorDuty
from app.models.student import Student


def check_student_time_conflict(db: Session, student_id: int, exam: Exam) -> Optional[str]:
    """Check if a student has another exam at the same time."""
    existing = (
        db.query(SeatingArrangement)
        .join(Exam)
        .filter(
            SeatingArrangement.student_id == student_id,
            Exam.exam_date == exam.exam_date,
            Exam.start_time < exam.end_time,
            Exam.end_time > exam.start_time,
            Exam.id != exam.id,
        )
        .first()
    )
    if existing:
        student = db.query(Student).filter(Student.id == student_id).first()
        return (
            f"Student {student.name} ({student.register_number}) has a time conflict: "
            f"already assigned to exam ID {existing.exam_id} at the same time slot"
        )
    return None


def check_seat_duplication(db: Session, exam_id: int, hall_id: int, seat_number: str,
                            exclude_seating_id: Optional[int] = None) -> Optional[str]:
    """Check if a seat is already occupied."""
    query = db.query(SeatingArrangement).filter(
        SeatingArrangement.exam_id == exam_id,
        SeatingArrangement.hall_id == hall_id,
        SeatingArrangement.seat_number == seat_number,
    )
    if exclude_seating_id:
        query = query.filter(SeatingArrangement.id != exclude_seating_id)
    if query.first():
        return f"Seat {seat_number} in hall {hall_id} is already occupied for exam {exam_id}"
    return None


def check_hall_capacity(db: Session, hall_id: int, exam_id: int, additional: int = 1) -> Optional[str]:
    """Check if adding more students would exceed hall capacity."""
    hall = db.query(Hall).filter(Hall.id == hall_id).first()
    if not hall:
        return f"Hall {hall_id} not found"
    current = db.query(SeatingArrangement).filter(
        SeatingArrangement.hall_id == hall_id,
        SeatingArrangement.exam_id == exam_id,
    ).count()
    if current + additional > hall.capacity:
        return f"Hall {hall.hall_number} capacity ({hall.capacity}) would be exceeded (current: {current}, adding: {additional})"
    return None


def check_invigilator_time_conflict(db: Session, invigilator_id: int, exam: Exam) -> Optional[str]:
    """Check if an invigilator has overlapping duties."""
    existing = (
        db.query(InvigilatorDuty)
        .join(Exam)
        .filter(
            InvigilatorDuty.invigilator_id == invigilator_id,
            Exam.exam_date == exam.exam_date,
            Exam.start_time < exam.end_time,
            Exam.end_time > exam.start_time,
            Exam.id != exam.id,
        )
        .first()
    )
    if existing:
        return f"Invigilator {invigilator_id} has overlapping duty for exam {existing.exam_id}"
    return None


def check_student_duplicate_assignment(db: Session, student_id: int, exam_id: int,
                                        exclude_seating_id: Optional[int] = None) -> Optional[str]:
    """Check if student is already assigned to this exam."""
    query = db.query(SeatingArrangement).filter(
        SeatingArrangement.student_id == student_id,
        SeatingArrangement.exam_id == exam_id,
    )
    if exclude_seating_id:
        query = query.filter(SeatingArrangement.id != exclude_seating_id)
    if query.first():
        return f"Student {student_id} is already assigned to exam {exam_id}"
    return None


def validate_seating_arrangement(db: Session, exam_id: int) -> List[str]:
    """Run all conflict checks on an existing seating arrangement."""
    conflicts = []
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        return ["Exam not found"]

    seatings = db.query(SeatingArrangement).filter(SeatingArrangement.exam_id == exam_id).all()

    # Check hall capacities
    hall_counts = {}
    for s in seatings:
        hall_counts[s.hall_id] = hall_counts.get(s.hall_id, 0) + 1
    for hall_id, count in hall_counts.items():
        hall = db.query(Hall).filter(Hall.id == hall_id).first()
        if hall and count > hall.capacity:
            conflicts.append(f"Hall {hall.hall_number} over capacity: {count}/{hall.capacity}")

    # Check student time conflicts
    for s in seatings:
        conflict = check_student_time_conflict(db, s.student_id, exam)
        if conflict:
            conflicts.append(conflict)

    # Check for duplicate seat assignments
    seat_map = {}
    for s in seatings:
        key = (s.hall_id, s.seat_number)
        if key in seat_map:
            conflicts.append(f"Duplicate seat {s.seat_number} in hall {s.hall_id}")
        seat_map[key] = s.student_id
def check_exam_hall_time_conflict(db: Session, hall_id: int, exam_date: date, start_time: time, end_time: time, exclude_exam_id: Optional[int] = None) -> Optional[str]:
    """Check if a hall's total seats are already fully occupied during the given date/time slot."""
    hall = db.query(Hall).filter(Hall.id == hall_id).first()
    if not hall:
        return f"Hall {hall_id} not found"
    
    query = (
        db.query(SeatingArrangement)
        .join(Exam)
        .filter(
            SeatingArrangement.hall_id == hall_id,
            Exam.exam_date == exam_date,
            Exam.start_time < end_time,
            Exam.end_time > start_time,
        )
    )
    if exclude_exam_id is not None:
        query = query.filter(SeatingArrangement.exam_id != exclude_exam_id)
        
    occupied_count = query.count()
    if occupied_count >= hall.capacity:
        return f"Hall {hall.hall_number} is fully occupied ({occupied_count}/{hall.capacity}) on {exam_date} during {start_time}-{end_time}"
    return None
