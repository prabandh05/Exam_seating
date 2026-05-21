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


@router.get("/dashboard")
def invigilator_dashboard(user: dict = Depends(require_invigilator), db: Session = Depends(get_db)):
    inv = user["user"]
    duties = (
        db.query(InvigilatorDuty)
        .options(joinedload(InvigilatorDuty.exam).joinedload(Exam.subject), joinedload(InvigilatorDuty.hall))
        .filter(InvigilatorDuty.invigilator_id == inv.id)
        .all()
    )
    upcoming = []
    for d in duties:
        if d.exam and d.exam.exam_date >= date.today():
            upcoming.append({
                "id": d.id, "invigilator_id": inv.id, "invigilator_name": inv.name,
                "exam_id": d.exam_id, "subject_name": d.exam.subject.subject_name if d.exam.subject else "",
                "exam_date": str(d.exam.exam_date), "start_time": str(d.exam.start_time),
                "end_time": str(d.exam.end_time), "hall_id": d.hall_id,
                "hall_number": d.hall.hall_number if d.hall else "", "created_at": d.created_at,
            })
    return {
        "invigilator": inv, "upcoming_duties": upcoming,
        "total_duties_assigned": len(duties), "has_duties": len(duties) > 0,
    }


@router.get("/duties")
def get_duties(user: dict = Depends(require_invigilator), db: Session = Depends(get_db)):
    duties = (
        db.query(InvigilatorDuty)
        .options(joinedload(InvigilatorDuty.exam).joinedload(Exam.subject), joinedload(InvigilatorDuty.hall))
        .filter(InvigilatorDuty.invigilator_id == user["user_id"])
        .all()
    )
    result = []
    for d in duties:
        result.append({
            "id": d.id, "exam_id": d.exam_id,
            "subject_name": d.exam.subject.subject_name if d.exam and d.exam.subject else "",
            "exam_date": str(d.exam.exam_date) if d.exam else "",
            "start_time": str(d.exam.start_time) if d.exam else "",
            "end_time": str(d.exam.end_time) if d.exam else "",
            "hall_id": d.hall_id, "hall_number": d.hall.hall_number if d.hall else "",
            "status": d.exam.status if d.exam else "",
        })
    return {"duties": result}


@router.get("/duties/{duty_id}/seating")
def get_duty_seating(duty_id: int, user: dict = Depends(require_invigilator), db: Session = Depends(get_db)):
    duty = db.query(InvigilatorDuty).filter(
        InvigilatorDuty.id == duty_id, InvigilatorDuty.invigilator_id == user["user_id"]
    ).first()
    if not duty:
        raise HTTPException(404, "Duty not found")
    seatings = seating_crud.get_seating_by_exam_hall(db, duty.exam_id, duty.hall_id)
    result = []
    for s in seatings:
        att_status = s.attendance.status if s.attendance else None
        result.append({
            "id": s.id, "seat_number": s.seat_number, "row_number": s.row_number,
            "column_number": s.column_number,
            "student_name": s.student.name if s.student else "",
            "register_number": s.student.register_number if s.student else "",
            "department": s.student.department if s.student else "",
            "attendance_status": att_status,
        })
    return {"seatings": result, "total": len(result)}


@router.post("/attendance/{duty_id}")
def mark_attendance(duty_id: int, data: BulkAttendanceRequest,
                    user: dict = Depends(require_invigilator), db: Session = Depends(get_db)):
    duty = db.query(InvigilatorDuty).filter(
        InvigilatorDuty.id == duty_id, InvigilatorDuty.invigilator_id == user["user_id"]
    ).first()
    if not duty:
        raise HTTPException(404, "Duty not found")
    count = 0
    for rec in data.attendance_records:
        att_crud.mark_attendance(db, rec.seating_id, rec.status, user["user_id"])
        count += 1
    create_audit_log(db, user["user_id"], "invigilator", "mark_attendance", "attendance",
                     new_value={"duty_id": duty_id, "count": count})
    return {"message": f"Marked {count} attendance records"}


@router.get("/profile")
def get_profile(user: dict = Depends(require_invigilator)):
    inv = user["user"]
    return {
        "id": inv.id, "invigilator_id": inv.invigilator_id, "name": inv.name,
        "department": inv.department, "phone": inv.phone, "email": inv.email,
        "total_duties": inv.total_duties,
    }
