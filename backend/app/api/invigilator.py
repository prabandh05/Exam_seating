"""Invigilator portal API endpoints."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.api.deps import require_invigilator, create_audit_log
from app.models.invigilator_duty import InvigilatorDuty
from app.models.exam import Exam
from app.models.hall import Hall
from app.models.seating import SeatingArrangement
from app.models.subject import Subject
from app.crud import seating as seating_crud
from app.crud import attendance as att_crud
from app.schemas.attendance import MarkAttendanceRequest, BulkAttendanceRequest
from app.core.enums import AttendanceStatusEnum

router = APIRouter(prefix="/api/invigilator", tags=["Invigilator"])


def _compute_zone(row_number: int, rows_per_zone: int = 3) -> str:
    """Compute zone label from row number. Zone A = rows 1-3, Zone B = rows 4-6, etc."""
    zone_idx = (row_number - 1) // rows_per_zone
    return chr(ord('A') + zone_idx)


@router.get("/dashboard")
def invigilator_dashboard(user: dict = Depends(require_invigilator), db: Session = Depends(get_db)):
    inv = user["user"]
    duties = (
        db.query(InvigilatorDuty)
        .options(joinedload(InvigilatorDuty.hall))
        .filter(InvigilatorDuty.invigilator_id == inv.id)
        .all()
    )
    upcoming = []
    past = []
    for d in duties:
        exams = db.query(Exam).options(joinedload(Exam.subject)).filter(
            Exam.exam_date == d.exam_date,
            Exam.start_time < d.end_time,
            Exam.end_time > d.start_time,
        ).all()
        
        subject_names = " / ".join([e.subject.subject_name for e in exams if e.subject])
        status = exams[0].status if exams else "unknown"
        
        duty_data = {
            "id": d.id, "invigilator_id": inv.id, "invigilator_name": inv.name,
            "subject_name": subject_names,
            "exam_date": str(d.exam_date), "start_time": str(d.start_time),
            "end_time": str(d.end_time), "hall_id": d.hall_id,
            "hall_number": d.hall.hall_number if d.hall else "", "created_at": d.created_at,
            "status": status,
        }
        if d.exam_date >= date.today():
            upcoming.append(duty_data)
        else:
            past.append(duty_data)
    return {
        "invigilator": inv, "upcoming_duties": upcoming, "past_duties": past,
        "total_duties_assigned": len(duties), "has_duties": len(duties) > 0,
    }


@router.get("/duties")
def get_duties(user: dict = Depends(require_invigilator), db: Session = Depends(get_db)):
    inv = user["user"]
    duties = (
        db.query(InvigilatorDuty)
        .options(joinedload(InvigilatorDuty.hall))
        .filter(InvigilatorDuty.invigilator_id == inv.id)
        .all()
    )
    result = []
    for d in duties:
        exams = db.query(Exam).options(joinedload(Exam.subject)).filter(
            Exam.exam_date == d.exam_date,
            Exam.start_time < d.end_time,
            Exam.end_time > d.start_time,
        ).all()
        
        subject_names = " / ".join([e.subject.subject_name for e in exams if e.subject])
        status = exams[0].status if exams else "unknown"

        result.append({
            "id": d.id,
            "subject_name": subject_names,
            "exam_date": str(d.exam_date),
            "start_time": str(d.start_time),
            "end_time": str(d.end_time),
            "hall_id": d.hall_id, "hall_number": d.hall.hall_number if d.hall else "",
            "status": status,
        })
    return {"duties": result}


@router.get("/duties/{duty_id}/seating")
def get_duty_seating(duty_id: int, user: dict = Depends(require_invigilator), db: Session = Depends(get_db)):
    inv = user["user"]
    duty = (
        db.query(InvigilatorDuty)
        .filter(InvigilatorDuty.id == duty_id, InvigilatorDuty.invigilator_id == inv.id)
        .first()
    )
    if not duty:
        raise HTTPException(404, "Duty not found")

    hall = db.query(Hall).filter(Hall.id == duty.hall_id).first()
    
    exams = db.query(Exam).options(joinedload(Exam.subject)).filter(
        Exam.exam_date == duty.exam_date,
        Exam.start_time < duty.end_time,
        Exam.end_time > duty.start_time,
    ).all()
    exam_ids = [e.id for e in exams]

    seatings = (
        db.query(SeatingArrangement)
        .options(joinedload(SeatingArrangement.student), joinedload(SeatingArrangement.exam).joinedload(Exam.subject), joinedload(SeatingArrangement.attendance))
        .filter(SeatingArrangement.exam_id.in_(exam_ids), SeatingArrangement.hall_id == duty.hall_id)
        .order_by(SeatingArrangement.row_number, SeatingArrangement.column_number)
        .all()
    )

    result = []
    for s in seatings:
        att_status = s.attendance.status if s.attendance else None
        result.append({
            "id": s.id, "seat_number": s.seat_number, "row_number": s.row_number,
            "column_number": s.column_number,
            "zone": _compute_zone(s.row_number),
            "student_name": s.student.name if s.student else "",
            "register_number": s.student.register_number if s.student else "",
            "department": s.student.department if s.student else "",
            "subject_name": s.exam.subject.subject_name if s.exam and s.exam.subject else "",
            "attendance_status": att_status,
        })

    subject_names = " / ".join([e.subject.subject_name for e in exams if e.subject])
    status = exams[0].status if exams else "unknown"

    exam_info = {
        "subject_name": subject_names,
        "exam_date": str(duty.exam_date),
        "start_time": str(duty.start_time),
        "end_time": str(duty.end_time),
        "status": status,
    }

    return {
        "seatings": result, "total": len(result),
        "hall_number": hall.hall_number if hall else "",
        "exam_info": exam_info,
    }


@router.post("/attendance/{duty_id}")
def mark_attendance(duty_id: int, data: BulkAttendanceRequest,
                    user: dict = Depends(require_invigilator), db: Session = Depends(get_db)):
    inv = user["user"]
    duty = db.query(InvigilatorDuty).filter(
        InvigilatorDuty.id == duty_id, InvigilatorDuty.invigilator_id == inv.id
    ).first()
    if not duty:
        raise HTTPException(404, "Duty not found")
    count = 0
    for rec in data.attendance_records:
        att_crud.mark_attendance(db, rec.seating_id, rec.status, inv.id)
        count += 1
    create_audit_log(db, inv.id, "invigilator", "mark_attendance", "attendance",
                     new_value={"duty_id": duty_id, "count": count})
    return {"message": f"Marked {count} attendance records"}


@router.post("/duties/{duty_id}/complete")
def mark_duty_complete(duty_id: int, user: dict = Depends(require_invigilator), db: Session = Depends(get_db)):
    """Mark a duty's exams as completed by the invigilator."""
    inv = user["user"]
    duty = db.query(InvigilatorDuty).filter(
        InvigilatorDuty.id == duty_id, InvigilatorDuty.invigilator_id == inv.id
    ).first()
    if not duty:
        raise HTTPException(404, "Duty not found")

    exams = db.query(Exam).filter(
        Exam.exam_date == duty.exam_date,
        Exam.start_time < duty.end_time,
        Exam.end_time > duty.start_time,
    ).all()

    if not exams:
        raise HTTPException(404, "Exams not found")

    for exam in exams:
        if exam.status == "completed":
            continue
        if exam.status not in ("published", "ongoing"):
            raise HTTPException(400, f"Cannot complete exam in '{exam.status}' status. Exam must be published or ongoing.")
        exam.status = "completed"
        db.add(exam)

    db.commit()

    create_audit_log(db, inv.id, "invigilator", "complete_exam", "exam", exams[0].id if exams else None,
                     new_value={"duty_id": duty_id})
    return {"message": "Exams marked as completed successfully"}


@router.get("/profile")
def get_profile(user: dict = Depends(require_invigilator)):
    inv = user["user"]
    return {
        "id": inv.id, "invigilator_id": inv.invigilator_id, "name": inv.name,
        "department": inv.department, "phone": inv.phone, "email": inv.email,
        "total_duties": inv.total_duties,
    }
