"""CRUD operations for Student management."""

import math
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.core.security import hash_password


def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    """Get a student by database ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_register_number(db: Session, register_number: str) -> Optional[Student]:
    """Get a student by register number."""
    return db.query(Student).filter(Student.register_number == register_number).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Get a student by email."""
    return db.query(Student).filter(Student.email == email).first()


def get_students(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    department: Optional[str] = None,
    semester: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Tuple[List[Student], int]:
    """
    Get paginated list of students with optional filters.

    Returns:
        Tuple of (list of students, total count).
    """
    query = db.query(Student)

    # Apply filters
    if department:
        query = query.filter(Student.department == department)
    if semester:
        query = query.filter(Student.semester == semester)
    if is_active is not None:
        query = query.filter(Student.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Student.name.ilike(search_term),
                Student.register_number.ilike(search_term),
                Student.email.ilike(search_term),
            )
        )

    total = query.count()
    students = (
        query.order_by(Student.register_number)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return students, total


def create_student(db: Session, student_data: StudentCreate) -> Student:
    """Create a new student."""
    student = Student(
        register_number=student_data.register_number,
        name=student_data.name,
        department=student_data.department,
        semester=student_data.semester.value,
        section=student_data.section,
        year=student_data.year,
        email=student_data.email,
        phone=student_data.phone,
        gender=student_data.gender.value,
        password_hash=hash_password(student_data.password),
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student_id: int, student_data: StudentUpdate) -> Optional[Student]:
    """Update an existing student."""
    student = get_student_by_id(db, student_id)
    if not student:
        return None

    update_data = student_data.model_dump(exclude_unset=True)
    if "semester" in update_data and update_data["semester"] is not None:
        update_data["semester"] = update_data["semester"].value
    if "gender" in update_data and update_data["gender"] is not None:
        update_data["gender"] = update_data["gender"].value

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: int) -> bool:
    """Delete a student by ID."""
    student = get_student_by_id(db, student_id)
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True


def get_students_by_department_semester(
    db: Session, department: str, semester: str
) -> List[Student]:
    """Get all active students in a department and semester."""
    return (
        db.query(Student)
        .filter(
            Student.department == department,
            Student.semester == semester,
            Student.is_active == True,
        )
        .all()
    )


def bulk_create_students(db: Session, students_data: List[dict]) -> Tuple[int, int, List[dict]]:
    """
    Bulk create students from parsed CSV/Excel data.

    Returns:
        Tuple of (successful count, failed count, list of errors).
    """
    successful = 0
    failed = 0
    errors = []

    for idx, row in enumerate(students_data):
        try:
            # Check for duplicate register number
            existing = get_student_by_register_number(db, row.get("register_number", ""))
            if existing:
                errors.append({
                    "row": idx + 1,
                    "register_number": row.get("register_number"),
                    "error": "Duplicate register number"
                })
                failed += 1
                continue

            # Check for duplicate email
            existing_email = get_student_by_email(db, row.get("email", ""))
            if existing_email:
                errors.append({
                    "row": idx + 1,
                    "register_number": row.get("register_number"),
                    "error": "Duplicate email"
                })
                failed += 1
                continue

            student = Student(
                register_number=row["register_number"],
                name=row["name"],
                department=row["department"],
                semester=row["semester"],
                section=row.get("section", "A"),
                year=int(row.get("year", 1)),
                email=row["email"],
                phone=row.get("phone", ""),
                gender=row.get("gender", "male"),
                password_hash=hash_password(row.get("password", row["register_number"])),
            )
            db.add(student)
            db.flush()
            successful += 1
        except Exception as e:
            db.rollback()
            errors.append({
                "row": idx + 1,
                "register_number": row.get("register_number", "unknown"),
                "error": str(e)
            })
            failed += 1

    if successful > 0:
        db.commit()

    return successful, failed, errors
