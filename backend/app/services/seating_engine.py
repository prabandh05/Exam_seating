"""
Seating Engine — Smart seating arrangement with 6 modes.

Mode 1: Mixed Subject (Anti-Cheating) — interleave students from different exams
Mode 2: Same Subject — group same subject students together
Mode 3: Department-wise — group by department
Mode 4: Random — fully random shuffle
Mode 5: Alternate Seating — leave one seat empty between students (checkerboard pattern)
Mode 6: Skip Bench — leave one bench (2 seats) empty between benches
"""

import random
from typing import List, Dict, Tuple, Set, Optional
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.hall import Hall
from app.models.student import Student
from app.models.seating import SeatingArrangement
from app.crud.seating import delete_seating_by_exam
from app.services.conflict_manager import check_student_time_conflict
from app.core.enums import SeatingModeEnum


class SeatingEngine:
    """Smart seating arrangement engine supporting all 6 modes and shared room allocations."""

    def __init__(self, db: Session):
        self.db = db

    def _get_occupied_seats_for_hall(self, hall_id: int, exams: List[Exam]) -> Set[str]:
        """Get set of seat numbers occupied in a hall by overlapping exams (excluding current ones)."""
        occupied = set()
        exam_ids = [e.id for e in exams]
        
        for e in exams:
            seatings = (
                self.db.query(SeatingArrangement)
                .join(Exam)
                .filter(
                    SeatingArrangement.hall_id == hall_id,
                    Exam.exam_date == e.exam_date,
                    Exam.start_time < e.end_time,
                    Exam.end_time > e.start_time,
                    SeatingArrangement.exam_id.notin_(exam_ids)
                )
                .all()
            )
            for s in seatings:
                occupied.add(s.seat_number)
        return occupied

    def generate(self, exam_ids: List[int], hall_ids: List[int],
                 mode: SeatingModeEnum, clear_existing: bool = False) -> dict:
        """Main entry point for seating generation."""
        # Load exams and halls
        exams = self.db.query(Exam).filter(Exam.id.in_(exam_ids)).all()
        halls = self.db.query(Hall).filter(Hall.id.in_(hall_ids), Hall.is_enabled == True).all()

        if not exams:
            return {"success": False, "message": "No valid exams found", "total_students_assigned": 0,
                    "halls_used": 0, "conflicts_detected": [], "hall_details": []}
        if not halls:
            return {"success": False, "message": "No enabled halls found", "total_students_assigned": 0,
                    "halls_used": 0, "conflicts_detected": [], "hall_details": []}

        # Clear existing if requested
        if clear_existing:
            for eid in exam_ids:
                delete_seating_by_exam(self.db, eid)

        # Collect students for each exam who don't have conflicts
        exam_students: Dict[int, List[Student]] = {}
        for exam in exams:
            students = (
                self.db.query(Student)
                .filter(Student.department == exam.department, Student.semester == exam.semester,
                        Student.is_active == True)
                .all()
            )
            valid_students = []
            for s in students:
                # Check if they are already seated for this exam
                existing = self.db.query(SeatingArrangement).filter(
                    SeatingArrangement.student_id == s.id, SeatingArrangement.exam_id == exam.id
                ).first()
                if not existing:
                    # Check other overlapping exams for time conflict
                    conflict = check_student_time_conflict(self.db, s.id, exam)
                    if not conflict:
                        valid_students.append(s)
            exam_students[exam.id] = valid_students

        # Order / interleave the students based on the selected mode
        ordered_students: List[Tuple[int, Student]] = [] # list of (exam_id, student)

        if mode == SeatingModeEnum.MIXED_SUBJECT:
            # Interleave exams (round-robin)
            for eid in exam_students:
                random.shuffle(exam_students[eid])
            max_len = max(len(s) for s in exam_students.values()) if exam_students else 0
            for i in range(max_len):
                for eid in exam_students:
                    if i < len(exam_students[eid]):
                        ordered_students.append((eid, exam_students[eid][i]))

        elif mode == SeatingModeEnum.DEPARTMENT_WISE:
            # Group by department, then interleave
            dept_groups: Dict[str, List[Tuple[int, Student]]] = {}
            for eid, students in exam_students.items():
                for s in students:
                    dept_groups.setdefault(s.department, []).append((eid, s))
            for dept in dept_groups:
                random.shuffle(dept_groups[dept])
            max_len = max(len(s) for s in dept_groups.values()) if dept_groups else 0
            for i in range(max_len):
                for dept in dept_groups:
                    if i < len(dept_groups[dept]):
                        ordered_students.append(dept_groups[dept][i])

        elif mode == SeatingModeEnum.RANDOM:
            # Fully random shuffle
            for eid, students in exam_students.items():
                for s in students:
                    ordered_students.append((eid, s))
            random.shuffle(ordered_students)

        else:
            # SAME_SUBJECT, ALTERNATE_SEATING, or SKIP_BENCH
            # Just append exam-by-exam (optionally shuffled)
            for eid, students in exam_students.items():
                random.shuffle(students)
                for s in students:
                    ordered_students.append((eid, s))

        # Assign to halls
        student_idx = 0
        halls_used = 0
        hall_details = []
        conflicts = []

        for hall in sorted(halls, key=lambda h: h.capacity, reverse=True):
            if student_idx >= len(ordered_students):
                break

            # Find already occupied seats in this hall for overlapping exams
            occupied_seats = self._get_occupied_seats_for_hall(hall.id, exams)
            
            # Track how many seats are available in this hall
            effective_capacity = hall.capacity - len(occupied_seats)
            if effective_capacity <= 0:
                continue

            halls_used += 1
            hall_assigned = 0

            for row in range(1, hall.num_rows + 1):
                for col in range(1, hall.num_columns + 1):
                    if student_idx >= len(ordered_students):
                        break
                    if hall_assigned >= effective_capacity:
                        break

                    seat_number = f"R{row}C{col}"

                    # Skip occupied seats
                    if seat_number in occupied_seats:
                        continue

                    # Apply mode-specific skipping rules
                    if mode == SeatingModeEnum.ALTERNATE_SEATING:
                        # Alternate seating: place on odd columns only (1, 3, 5...)
                        # This leaves one empty seat between every two students in a row
                        if col % 2 == 0:
                            continue

                    elif mode == SeatingModeEnum.SKIP_BENCH:
                        # Skip Bench: each bench = 2 consecutive seats (cols 1-2, 3-4, 5-6...)
                        # Place students only on odd-indexed benches (bench 0, 2, 4...)
                        # Bench index: (col - 1) // 2  →  cols 1-2 = bench 0, cols 3-4 = bench 1, etc.
                        bench_idx = (col - 1) // 2
                        if bench_idx % 2 != 0:
                            continue

                    # Assign student to seat
                    exam_id, student = ordered_students[student_idx]
                    seating = SeatingArrangement(
                        exam_id=exam_id,
                        hall_id=hall.id,
                        student_id=student.id,
                        seat_number=seat_number,
                        row_number=row,
                        column_number=col,
                    )
                    self.db.add(seating)
                    student_idx += 1
                    hall_assigned += 1

                if student_idx >= len(ordered_students) or hall_assigned >= effective_capacity:
                    break

            hall_details.append({
                "hall_id": hall.id,
                "hall_number": hall.hall_number,
                "assigned": hall_assigned,
                "capacity": hall.capacity,
                "occupied_previously": len(occupied_seats),
            })

        if student_idx < len(ordered_students):
            unassigned = len(ordered_students) - student_idx
            conflicts.append(f"{unassigned} students could not be assigned due to insufficient hall capacity or seating layout constraints")

        self.db.commit()

        return {
            "success": True,
            "message": "Seating generated successfully",
            "total_students_assigned": student_idx,
            "halls_used": halls_used,
            "conflicts_detected": conflicts,
            "hall_details": hall_details,
        }
