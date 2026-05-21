"""Student portal API endpoints."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_student
from app.crud import seating as seating_crud
from app.crud import notification as notif_crud
from app.models.exam import Exam

router = APIRouter(prefix="/api/student", tags=["Student"])


@router.get("/dashboard")
def student_dashboard(user: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = user["user"]
    seatings = seating_crud.get_student_seating(db, student.id)
    upcoming = []
    for s in seatings:
        if s.exam and s.exam.exam_date >= date.today():
            upcoming.append({
                "exam_id": s.exam_id, "subject_name": s.exam.subject.subject_name if s.exam.subject else "",
                "subject_code": s.exam.subject.subject_code if s.exam.subject else "",
                "exam_date": str(s.exam.exam_date), "start_time": str(s.exam.start_time),
                "end_time": str(s.exam.end_time), "hall_number": s.hall.hall_number if s.hall else "",
                "seat_number": s.seat_number, "exam_type": s.exam.exam_type,
            })
    return {
        "student": {"id": student.id, "name": student.name, "register_number": student.register_number,
                     "department": student.department, "semester": student.semester, "section": student.section},
        "upcoming_exams": upcoming, "total_upcoming": len(upcoming),
    }


@router.get("/exams")
def get_student_exams(user: dict = Depends(require_student), db: Session = Depends(get_db)):
    seatings = seating_crud.get_student_seating(db, user["user_id"])
    exams = []
    for s in seatings:
        exams.append({
            "exam_id": s.exam_id, "subject_name": s.exam.subject.subject_name if s.exam and s.exam.subject else "",
            "subject_code": s.exam.subject.subject_code if s.exam and s.exam.subject else "",
            "exam_date": str(s.exam.exam_date) if s.exam else "", "start_time": str(s.exam.start_time) if s.exam else "",
            "end_time": str(s.exam.end_time) if s.exam else "", "exam_type": s.exam.exam_type if s.exam else "",
            "hall_number": s.hall.hall_number if s.hall else "", "seat_number": s.seat_number,
            "row_number": s.row_number, "column_number": s.column_number,
        })
    return {"exams": exams}


@router.get("/seating")
def get_student_seating(user: dict = Depends(require_student), db: Session = Depends(get_db)):
    seatings = seating_crud.get_student_seating(db, user["user_id"])
    result = []
    for s in seatings:
        result.append({
            "student_name": user["user"].name, "register_number": user["user"].register_number,
            "department": user["user"].department, "semester": user["user"].semester,
            "subject_name": s.exam.subject.subject_name if s.exam and s.exam.subject else "",
            "hall_number": s.hall.hall_number if s.hall else "",
            "seat_number": s.seat_number, "exam_date": str(s.exam.exam_date) if s.exam else "",
            "start_time": str(s.exam.start_time) if s.exam else "",
            "end_time": str(s.exam.end_time) if s.exam else "",
        })
    return {"seating_details": result}


@router.get("/notifications")
def get_notifications(user: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = user["user"]
    notifs = notif_crud.get_notifications(db, role="student", department=student.department, semester=student.semester)
    unread = notif_crud.get_unread_count(db, user["user_id"], "student")
    result = []
    for n in notifs:
        result.append({
            "id": n.id, "title": n.title, "message": n.message, "type": n.type,
            "created_at": n.created_at, "is_read": False,
        })
    return {"notifications": result, "total": len(result), "unread_count": unread}


@router.patch("/notifications/{notif_id}/read")
def mark_read(notif_id: int, user: dict = Depends(require_student), db: Session = Depends(get_db)):
    notif_crud.mark_notification_read(db, notif_id, user["user_id"], "student")
    return {"message": "Marked as read"}
