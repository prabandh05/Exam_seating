"""Admin API endpoints — dashboard, students, subjects, halls, exams, seating, invigilators, reports."""

import math, io
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_admin, create_audit_log
from app.core.enums import ExamStatusEnum, SeatingModeEnum
from app.crud import student as student_crud
from app.crud import subject as subject_crud
from app.crud import hall as hall_crud
from app.crud import exam as exam_crud
from app.crud import seating as seating_crud
from app.crud import invigilator as inv_crud
from app.crud import attendance as att_crud
from app.crud import notification as notif_crud
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentListResponse
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse, SubjectListResponse
from app.schemas.hall import HallCreate, HallUpdate, HallResponse, HallListResponse, HallToggleRequest
from app.schemas.exam import ExamCreate, ExamUpdate, ExamResponse, ExamListResponse, ExamStatusUpdate
from app.schemas.seating import GenerateSeatingRequest, SeatingResponse, SeatingGenerationResult, ConflictCheckResponse, SeatSwapRequest, SeatLockRequest, ManualSeatAssignment
from app.schemas.invigilator import InvigilatorCreate, InvigilatorUpdate, InvigilatorResponse, InvigilatorListResponse, DutyAssignRequest
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationListResponse, AdminDashboardStats
from app.schemas.attendance import AttendanceReportResponse
from app.services.seating_engine import SeatingEngine
from app.services.conflict_manager import validate_seating_arrangement
from app.models.exam import Exam
from app.models.student import Student
from app.models.invigilator import Invigilator
from app.models.hall import Hall
from app.models.audit_log import AuditLog
from app.models.seating import SeatingArrangement

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ─── Dashboard ───
@router.get("/dashboard/stats")
def dashboard_stats(admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    total_students = db.query(Student).count()
    total_invs = db.query(Invigilator).count()
    total_halls = db.query(Hall).count()
    total_exams = db.query(Exam).count()
    upcoming = db.query(Exam).filter(Exam.exam_date >= date.today(), Exam.status.in_(["published", "ongoing"])).count()
    active = db.query(Exam).filter(Exam.status == "ongoing").count()
    completed = db.query(Exam).filter(Exam.status == "completed").count()
    total_seating = db.query(SeatingArrangement).count()
    return {
        "total_students": total_students, "total_invigilators": total_invs,
        "total_halls": total_halls, "total_exams": total_exams,
        "upcoming_exams": upcoming, "active_exams": active,
        "completed_exams": completed, "total_seating_arrangements": total_seating,
        "attendance_summary": {"present": 0, "absent": 0, "late": 0},
    }

# ─── Students ───
@router.get("/students")
def list_students(page: int = 1, page_size: int = 20, department: Optional[str] = None,
                  semester: Optional[str] = None, search: Optional[str] = None,
                  admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    students, total = student_crud.get_students(db, page, page_size, department, semester, search)
    return {"students": students, "total": total, "page": page,
            "page_size": page_size, "total_pages": math.ceil(total / page_size) if total else 0}

@router.post("/students", response_model=StudentResponse, status_code=201)
def create_student(data: StudentCreate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if student_crud.get_student_by_register_number(db, data.register_number):
        raise HTTPException(400, "Register number already exists")
    if student_crud.get_student_by_email(db, data.email):
        raise HTTPException(400, "Email already exists")
    s = student_crud.create_student(db, data)
    create_audit_log(db, admin["user_id"], "admin", "create", "student", s.id)
    return s

@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    s = student_crud.get_student_by_id(db, student_id)
    if not s: raise HTTPException(404, "Student not found")
    return s

@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, data: StudentUpdate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    s = student_crud.update_student(db, student_id, data)
    if not s: raise HTTPException(404, "Student not found")
    create_audit_log(db, admin["user_id"], "admin", "update", "student", student_id)
    return s

@router.delete("/students/{student_id}")
def delete_student(student_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if not student_crud.delete_student(db, student_id):
        raise HTTPException(404, "Student not found")
    create_audit_log(db, admin["user_id"], "admin", "delete", "student", student_id)
    return {"message": "Student deleted"}

@router.post("/students/bulk-upload")
async def bulk_upload_students(file: UploadFile = File(...), admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    import pandas as pd
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(400, "Only CSV and Excel files accepted")
    contents = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(400, f"Error reading file: {str(e)}")
    required = ["register_number", "name", "department", "semester", "email"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise HTTPException(400, f"Missing columns: {missing}")
    records = df.fillna("").to_dict("records")
    successful, failed, errors = student_crud.bulk_create_students(db, records)
    create_audit_log(db, admin["user_id"], "admin", "bulk_upload", "student", new_value={"successful": successful, "failed": failed})
    return {"total_processed": len(records), "successful": successful, "failed": failed, "errors": errors}

# ─── Subjects ───
@router.get("/subjects")
def list_subjects(department: Optional[str] = None, semester: Optional[str] = None,
                  admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    subjects = subject_crud.get_subjects(db, department, semester)
    return {"subjects": subjects, "total": len(subjects)}

@router.post("/subjects", response_model=SubjectResponse, status_code=201)
def create_subject(data: SubjectCreate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if subject_crud.get_subject_by_code(db, data.subject_code):
        raise HTTPException(400, "Subject code already exists")
    s = subject_crud.create_subject(db, data)
    create_audit_log(db, admin["user_id"], "admin", "create", "subject", s.id)
    return s

@router.put("/subjects/{subject_id}", response_model=SubjectResponse)
def update_subject(subject_id: int, data: SubjectUpdate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    s = subject_crud.update_subject(db, subject_id, data)
    if not s: raise HTTPException(404, "Subject not found")
    return s

@router.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if not subject_crud.delete_subject(db, subject_id):
        raise HTTPException(404, "Subject not found")
    return {"message": "Subject deleted"}

# ─── Halls ───
@router.get("/halls")
def list_halls(is_enabled: Optional[bool] = None, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    halls = hall_crud.get_halls(db, is_enabled)
    return {"halls": halls, "total": len(halls)}

@router.post("/halls", response_model=HallResponse, status_code=201)
def create_hall(data: HallCreate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if hall_crud.get_hall_by_number(db, data.hall_number):
        raise HTTPException(400, "Hall number already exists")
    h = hall_crud.create_hall(db, data)
    create_audit_log(db, admin["user_id"], "admin", "create", "hall", h.id)
    return h

@router.get("/halls/{hall_id}", response_model=HallResponse)
def get_hall(hall_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    h = hall_crud.get_hall_by_id(db, hall_id)
    if not h: raise HTTPException(404, "Hall not found")
    return h

@router.put("/halls/{hall_id}", response_model=HallResponse)
def update_hall(hall_id: int, data: HallUpdate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    h = hall_crud.update_hall(db, hall_id, data)
    if not h: raise HTTPException(404, "Hall not found")
    return h

@router.delete("/halls/{hall_id}")
def delete_hall(hall_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if not hall_crud.delete_hall(db, hall_id):
        raise HTTPException(404, "Hall not found")
    return {"message": "Hall deleted"}

@router.patch("/halls/{hall_id}/toggle")
def toggle_hall(hall_id: int, data: HallToggleRequest, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    h = hall_crud.toggle_hall(db, hall_id, data.is_enabled)
    if not h: raise HTTPException(404, "Hall not found")
    return h

# ─── Exams ───
@router.get("/exams")
def list_exams(page: int = 1, page_size: int = 20, status: Optional[str] = None,
               department: Optional[str] = None, semester: Optional[str] = None,
               admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    exams, total = exam_crud.get_exams(db, page, page_size, status, department, semester)
    result = []
    for e in exams:
        count = exam_crud.get_student_exam_count(db, e.id)
        result.append({
            "id": e.id, "subject_id": e.subject_id,
            "subject_name": e.subject.subject_name if e.subject else "",
            "subject_code": e.subject.subject_code if e.subject else "",
            "exam_date": e.exam_date, "start_time": e.start_time, "end_time": e.end_time,
            "exam_type": e.exam_type, "status": e.status,
            "department": e.department, "semester": e.semester,
            "created_by": e.created_by, "created_at": e.created_at, "updated_at": e.updated_at,
            "total_students_assigned": count,
        })
    return {"exams": result, "total": total, "page": page,
            "page_size": page_size, "total_pages": math.ceil(total / page_size) if total else 0}

@router.post("/exams", status_code=201)
def create_exam(data: ExamCreate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    subj = subject_crud.get_subject_by_id(db, data.subject_id)
    if not subj: raise HTTPException(400, "Subject not found")
    e = exam_crud.create_exam(db, data, admin["user_id"])
    create_audit_log(db, admin["user_id"], "admin", "create", "exam", e.id)
    return {"id": e.id, "message": "Exam created"}

@router.get("/exams/{exam_id}")
def get_exam(exam_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    e = exam_crud.get_exam_by_id(db, exam_id)
    if not e: raise HTTPException(404, "Exam not found")
    return {
        "id": e.id, "subject_id": e.subject_id,
        "subject_name": e.subject.subject_name if e.subject else "",
        "subject_code": e.subject.subject_code if e.subject else "",
        "exam_date": e.exam_date, "start_time": e.start_time, "end_time": e.end_time,
        "exam_type": e.exam_type, "status": e.status,
        "department": e.department, "semester": e.semester,
        "created_at": e.created_at, "updated_at": e.updated_at,
        "total_students_assigned": exam_crud.get_student_exam_count(db, e.id),
    }

@router.put("/exams/{exam_id}")
def update_exam(exam_id: int, data: ExamUpdate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    e = exam_crud.update_exam(db, exam_id, data)
    if not e: raise HTTPException(404, "Exam not found")
    create_audit_log(db, admin["user_id"], "admin", "update", "exam", exam_id)
    return {"message": "Exam updated"}

@router.delete("/exams/{exam_id}")
def delete_exam(exam_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if not exam_crud.delete_exam(db, exam_id):
        raise HTTPException(404, "Exam not found")
    return {"message": "Exam deleted"}

@router.patch("/exams/{exam_id}/status")
def update_exam_status(exam_id: int, data: ExamStatusUpdate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    from app.schemas.exam import ExamUpdate as EU
    # Update exam status
    e = exam_crud.update_exam(db, exam_id, EU(status=data.status))
    if not e:
        raise HTTPException(404, "Exam not found")
    # If publishing, lock seating
    if data.status == ExamStatusEnum.PUBLISHED:
        # Check if seating exists
        from app.crud.seating import get_seating_by_exam
        seatings = get_seating_by_exam(db, exam_id)
        if not seatings:
            raise HTTPException(status_code=400, detail="Cannot publish exam: No seating arrangements have been generated.")
        
        # Check if conflicts exist
        from app.services.conflict_manager import validate_seating_arrangement
        conflicts = validate_seating_arrangement(db, exam_id)
        if conflicts:
            raise HTTPException(status_code=400, detail=f"Cannot publish exam: Seating conflicts detected. {', '.join(conflicts)}")
            
        e.seating_locked = True
        db.add(e)
        db.commit()
    create_audit_log(db, admin["user_id"], "admin", "publish_exam", "exam", exam_id)
    return {"message": f"Exam status updated to {data.status.value}"}

# ─── Seating ───
# IMPORTANT: All static/literal-path routes MUST come BEFORE dynamic /{exam_id} routes

@router.post("/seating/generate")
def generate_seating(data: GenerateSeatingRequest, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    # Verify all exams are in draft and not locked
    exams = db.query(Exam).filter(Exam.id.in_(data.exam_ids)).all()
    for e in exams:
        if e.status != "draft":
            raise HTTPException(status_code=400, detail=f"Exam {e.id} is not in draft status; cannot generate seating.")
        if getattr(e, "seating_locked", False):
            raise HTTPException(status_code=400, detail=f"Exam {e.id} seating is locked.")
    # Check hall time conflicts for each hall and each exam
    from app.services.conflict_manager import check_exam_hall_time_conflict
    for hall_id in data.hall_ids:
        for e in exams:
            conflict = check_exam_hall_time_conflict(
                db,
                hall_id=hall_id,
                exam_date=e.exam_date,
                start_time=e.start_time,
                end_time=e.end_time,
                exclude_exam_id=e.id,
            )
            if conflict:
                raise HTTPException(status_code=400, detail=conflict)
    engine = SeatingEngine(db)
    result = engine.generate(data.exam_ids, data.hall_ids, data.mode, data.clear_existing)
    # Attach generated seatings per exam for frontend preview
    if result.get("success"):
        preview = []
        for eid in data.exam_ids:
            seatings = seating_crud.get_seating_by_exam(db, eid)
            for s in seatings:
                preview.append({
                    "exam_id": s.exam_id,
                    "hall_number": s.hall.hall_number if s.hall else "",
                    "seat_number": s.seat_number,
                    "row_number": s.row_number,
                    "column_number": s.column_number,
                    "student_name": s.student.name if s.student else "",
                    "register_number": s.student.register_number if s.student else "",
                    "department": s.student.department if s.student else "",
                    "subject_name": s.exam.subject.subject_name if s.exam and s.exam.subject else "",
                })
        result["preview_seatings"] = preview
    create_audit_log(db, admin["user_id"], "admin", "generate_seating", "seating",
                     new_value={"mode": data.mode.value, "exams": data.exam_ids})
    return result

@router.post("/seating/swap")
def swap_seats(data: SeatSwapRequest, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if not seating_crud.swap_seats(db, data.seating_id_1, data.seating_id_2):
        raise HTTPException(400, "Cannot swap: seats not found or locked")
    return {"message": "Seats swapped"}

# ─── Manual Seat Assignment (static routes BEFORE /{exam_id}) ───

@router.post("/seating/assign")
def manual_assign_seat(data: ManualSeatAssignment, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == data.exam_id).first()
    if not exam: raise HTTPException(404, "Exam not found")
    if exam.status != "draft" or getattr(exam, "seating_locked", False):
        raise HTTPException(400, "Exam seating is locked or not in draft status")

    # Check if student is already assigned to this exam
    existing_student = db.query(SeatingArrangement).filter(
        SeatingArrangement.exam_id == data.exam_id,
        SeatingArrangement.student_id == data.student_id
    ).first()
    if existing_student:
        raise HTTPException(400, "Student is already assigned to this exam")

    seat_number = f"R{data.row_number}C{data.column_number}"

    # Check if seat is occupied in this hall for overlapping exams
    conflict = (
        db.query(SeatingArrangement)
        .join(Exam)
        .filter(
            SeatingArrangement.hall_id == data.hall_id,
            SeatingArrangement.seat_number == seat_number,
            Exam.exam_date == exam.exam_date,
            Exam.start_time < exam.end_time,
            Exam.end_time > exam.start_time,
        )
        .first()
    )
    if conflict:
        raise HTTPException(400, "This seat is already occupied by another student")

    hall = db.query(Hall).filter(Hall.id == data.hall_id).first()
    if not hall: raise HTTPException(404, "Hall not found")

    current_occupied = db.query(SeatingArrangement).join(Exam).filter(
        SeatingArrangement.hall_id == data.hall_id,
        Exam.exam_date == exam.exam_date,
        Exam.start_time < exam.end_time,
        Exam.end_time > exam.start_time,
    ).count()
    if current_occupied >= hall.capacity:
        raise HTTPException(400, "Hall capacity exceeded")

    seating = SeatingArrangement(
        exam_id=data.exam_id,
        hall_id=data.hall_id,
        student_id=data.student_id,
        seat_number=seat_number,
        row_number=data.row_number,
        column_number=data.column_number,
    )
    db.add(seating)
    db.commit()
    db.refresh(seating)
    create_audit_log(db, admin["user_id"], "admin", "create", "seating", seating.id)
    return {"message": "Seat assigned manually", "seating_id": seating.id}

@router.delete("/seating/remove/{seating_id}")
def manual_remove_seat(seating_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    seating = db.query(SeatingArrangement).filter(SeatingArrangement.id == seating_id).first()
    if not seating: raise HTTPException(404, "Seating arrangement not found")

    exam = db.query(Exam).filter(Exam.id == seating.exam_id).first()
    if not exam or exam.status != "draft" or getattr(exam, "seating_locked", False):
        raise HTTPException(400, "Exam seating is locked or not in draft status")

    db.delete(seating)
    db.commit()
    create_audit_log(db, admin["user_id"], "admin", "delete", "seating", seating_id)
    return {"message": "Seat assignment removed"}

@router.get("/seating/halls/{hall_id}/layout")
def get_hall_layout(hall_id: int, exam_id: int, db: Session = Depends(get_db)):
    hall = db.query(Hall).filter(Hall.id == hall_id).first()
    if not hall:
        raise HTTPException(404, "Hall not found")

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(404, "Exam not found")

    # Get all seating in this hall for overlapping time slots
    seatings = (
        db.query(SeatingArrangement)
        .join(Exam)
        .filter(
            SeatingArrangement.hall_id == hall_id,
            Exam.exam_date == exam.exam_date,
            Exam.start_time < exam.end_time,
            Exam.end_time > exam.start_time,
        )
        .all()
    )

    seating_map = {}
    for s in seatings:
        seating_map[s.seat_number] = {
            "id": s.id,
            "exam_id": s.exam_id,
            "exam_name": s.exam.subject.subject_name if s.exam and s.exam.subject else "",
            "student_id": s.student_id,
            "student_name": s.student.name if s.student else "",
            "register_number": s.student.register_number if s.student else "",
            "department": s.student.department if s.student else "",
            "is_locked": s.is_locked,
        }

    # Find eligible unassigned students
    all_students = (
        db.query(Student)
        .filter(Student.department == exam.department, Student.semester == exam.semester, Student.is_active == True)
        .all()
    )

    unassigned_students = []
    from app.services.conflict_manager import check_student_time_conflict
    for s in all_students:
        already_seated = db.query(SeatingArrangement).filter(
            SeatingArrangement.student_id == s.id,
            SeatingArrangement.exam_id == exam_id,
        ).first()
        if not already_seated:
            conflict = check_student_time_conflict(db, s.id, exam)
            if not conflict:
                unassigned_students.append({
                    "id": s.id,
                    "name": s.name,
                    "register_number": s.register_number,
                    "department": s.department,
                })

    return {
        "hall": {
            "id": hall.id,
            "hall_number": hall.hall_number,
            "num_rows": hall.num_rows,
            "num_columns": hall.num_columns,
            "capacity": hall.capacity,
        },
        "seating_map": seating_map,
        "unassigned_students": unassigned_students,
    }

# ─── Dynamic routes with path params LAST ───

@router.get("/seating/{exam_id}")
def get_seating(exam_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    seatings = seating_crud.get_seating_by_exam(db, exam_id)
    result = []
    for s in seatings:
        result.append({
            "id": s.id, "exam_id": s.exam_id, "hall_id": s.hall_id,
            "hall_number": s.hall.hall_number if s.hall else "",
            "student_id": s.student_id,
            "student_name": s.student.name if s.student else "",
            "register_number": s.student.register_number if s.student else "",
            "department": s.student.department if s.student else "",
            "subject_name": s.exam.subject.subject_name if s.exam and s.exam.subject else "",
            "subject_code": s.exam.subject.subject_code if s.exam and s.exam.subject else "",
            "seat_number": s.seat_number, "row_number": s.row_number,
            "column_number": s.column_number, "is_locked": s.is_locked,
            "is_reserved": s.is_reserved, "created_at": s.created_at,
        })
    return {"seatings": result, "total": len(result)}

@router.patch("/seating/{seating_id}/lock")
def lock_seat(seating_id: int, data: SeatLockRequest, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    s = seating_crud.lock_seat(db, seating_id, data.is_locked)
    if not s: raise HTTPException(404, "Seating not found")
    return {"message": f"Seat {'locked' if data.is_locked else 'unlocked'}"}

@router.delete("/seating/{exam_id}")
def clear_seating(exam_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    count = seating_crud.delete_seating_by_exam(db, exam_id)
    return {"message": f"Cleared {count} seating arrangements"}

@router.get("/seating/{exam_id}/conflicts")
def check_conflicts(exam_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    conflicts = validate_seating_arrangement(db, exam_id)
    return {"has_conflicts": len(conflicts) > 0, "conflicts": conflicts, "total_conflicts": len(conflicts)}

# ─── Invigilators ───
@router.get("/invigilators")
def list_invigilators(page: int = 1, page_size: int = 20, department: Optional[str] = None,
                      search: Optional[str] = None, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    invs, total = inv_crud.get_invigilators(db, page, page_size, department, search)
    return {"invigilators": invs, "total": total, "page": page,
            "page_size": page_size, "total_pages": math.ceil(total / page_size) if total else 0}

@router.post("/invigilators", status_code=201)
def create_invigilator(data: InvigilatorCreate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if inv_crud.get_invigilator_by_invigilator_id(db, data.invigilator_id):
        raise HTTPException(400, "Invigilator ID already exists")
    if inv_crud.get_invigilator_by_email(db, data.email):
        raise HTTPException(400, "Email already exists")
    i = inv_crud.create_invigilator(db, data)
    create_audit_log(db, admin["user_id"], "admin", "create", "invigilator", i.id)
    return i

@router.get("/invigilators/{inv_id}")
def get_invigilator(inv_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    i = inv_crud.get_invigilator_by_id(db, inv_id)
    if not i: raise HTTPException(404, "Invigilator not found")
    return i

@router.put("/invigilators/{inv_id}")
def update_invigilator(inv_id: int, data: InvigilatorUpdate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    i = inv_crud.update_invigilator(db, inv_id, data)
    if not i: raise HTTPException(404, "Invigilator not found")
    return i

@router.delete("/invigilators/{inv_id}")
def delete_invigilator(inv_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if not inv_crud.delete_invigilator(db, inv_id):
        raise HTTPException(404, "Invigilator not found")
    return {"message": "Invigilator deleted"}

@router.post("/invigilators/assign")
def assign_duty(data: DutyAssignRequest, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if inv_crud.get_duty_by_exam_hall(db, data.exam_id, data.hall_id):
        raise HTTPException(400, "Duty already assigned for this exam-hall")
    exam = exam_crud.get_exam_by_id(db, data.exam_id)
    if not exam: raise HTTPException(404, "Exam not found")
    from app.services.conflict_manager import check_invigilator_time_conflict
    conflict = check_invigilator_time_conflict(db, data.invigilator_id, exam)
    if conflict: raise HTTPException(400, conflict)
    duty = inv_crud.assign_duty(db, data.invigilator_id, data.exam_id, data.hall_id)
    create_audit_log(db, admin["user_id"], "admin", "assign_duty", "invigilator_duty", duty.id)
    return {"message": "Duty assigned", "duty_id": duty.id}

@router.post("/invigilators/auto-assign")
def auto_assign_duties(exam_id: int = Query(...), admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    """Auto-assign invigilators to halls for an exam with workload balancing."""
    exam = exam_crud.get_exam_by_id(db, exam_id)
    if not exam: raise HTTPException(404, "Exam not found")
    seatings = seating_crud.get_seating_by_exam(db, exam_id)
    hall_ids = list(set(s.hall_id for s in seatings))
    if not hall_ids: raise HTTPException(400, "No seating arrangements found")
    invs, _ = inv_crud.get_invigilators(db, page=1, page_size=1000, is_active=True)
    if not invs: raise HTTPException(400, "No active invigilators")
    invs_sorted = sorted(invs, key=lambda x: x.total_duties)
    assigned = 0
    for hid in hall_ids:
        if inv_crud.get_duty_by_exam_hall(db, exam_id, hid):
            continue
        for inv in invs_sorted:
            from app.services.conflict_manager import check_invigilator_time_conflict
            if not check_invigilator_time_conflict(db, inv.id, exam):
                inv_crud.assign_duty(db, inv.id, exam_id, hid)
                assigned += 1
                invs_sorted = sorted(invs_sorted, key=lambda x: x.total_duties)
                break
    return {"message": f"Auto-assigned {assigned} duties", "assigned": assigned}

# ─── Attendance ───
@router.get("/attendance/{exam_id}")
def get_attendance(exam_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    stats = att_crud.get_attendance_stats(db, exam_id)
    return stats

# ─── Notifications ───
@router.get("/notifications")
def list_notifications(admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    notifs = notif_crud.get_all_notifications(db)
    return {"notifications": notifs, "total": len(notifs), "unread_count": 0}

@router.post("/notifications", status_code=201)
def create_notification(data: NotificationCreate, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    n = notif_crud.create_notification(db, data, admin["user_id"])
    return n

@router.delete("/notifications/{notif_id}")
def delete_notification(notif_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if not notif_crud.delete_notification(db, notif_id):
        raise HTTPException(404, "Notification not found")
    return {"message": "Notification deleted"}

# ─── Audit Logs ───
@router.get("/audit-logs")
def get_audit_logs(page: int = 1, page_size: int = 50, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    total = query.count()
    logs = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"logs": logs, "total": total, "page": page, "total_pages": math.ceil(total / page_size) if total else 0}

# ─── Reports (PDF/Excel) ───
@router.get("/reports/seating/{exam_id}/excel")
def export_seating_excel(exam_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    import openpyxl
    seatings = seating_crud.get_seating_by_exam(db, exam_id)
    if not seatings: raise HTTPException(404, "No seating data")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Seating Arrangement"
    ws.append(["Seat", "Register No", "Student Name", "Department", "Subject", "Hall", "Row", "Col"])
    for s in seatings:
        ws.append([s.seat_number, s.student.register_number if s.student else "",
                    s.student.name if s.student else "", s.student.department if s.student else "",
                    s.exam.subject.subject_name if s.exam and s.exam.subject else "",
                    s.hall.hall_number if s.hall else "", s.row_number, s.column_number])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=seating_exam_{exam_id}.xlsx"})

@router.get("/reports/attendance/{exam_id}/excel")
def export_attendance_excel(exam_id: int, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    import openpyxl
    seatings = seating_crud.get_seating_by_exam(db, exam_id)
    if not seatings: raise HTTPException(404, "No data")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendance"
    ws.append(["Register No", "Name", "Hall", "Seat", "Status"])
    for s in seatings:
        att_status = s.attendance.status if s.attendance else "unmarked"
        ws.append([s.student.register_number if s.student else "", s.student.name if s.student else "",
                    s.hall.hall_number if s.hall else "", s.seat_number, att_status])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=attendance_exam_{exam_id}.xlsx"})


