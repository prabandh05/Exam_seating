"""
Enumerators for the Exam Seating Management System.
All dropdown/selection fields use Python Enums to prevent invalid data entry.
"""

from enum import Enum


class SemesterEnum(str, Enum):
    """Valid semester values (1-8). Prevents arbitrary string/number input."""
    SEM_1 = "1"
    SEM_2 = "2"
    SEM_3 = "3"
    SEM_4 = "4"
    SEM_5 = "5"
    SEM_6 = "6"
    SEM_7 = "7"
    SEM_8 = "8"


class GenderEnum(str, Enum):
    """Gender options for student records."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ExamTypeEnum(str, Enum):
    """Types of examinations supported by the system."""
    INTERNAL = "internal"
    EXTERNAL = "external"
    SUPPLEMENTARY = "supplementary"
    MIDTERM = "midterm"


class ExamStatusEnum(str, Enum):
    """Lifecycle statuses for an exam."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SeatingModeEnum(str, Enum):
    """Seating arrangement modes available to admin."""
    MIXED_SUBJECT = "mixed_subject"       # Anti-cheating: alternate subjects
    SAME_SUBJECT = "same_subject"         # Group same subject together
    DEPARTMENT_WISE = "department_wise"    # Group by department
    RANDOM = "random"                     # Fully randomized
    ALTERNATE_SEATING = "alternate_seating" # Leave one seat empty
    SKIP_BENCH = "skip_bench"             # Leave alternate benches empty


class AttendanceStatusEnum(str, Enum):
    """Attendance states for a student in an exam."""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class UserRoleEnum(str, Enum):
    """User roles for authentication and authorization."""
    ADMIN = "admin"
    INVIGILATOR = "invigilator"
    STUDENT = "student"


class NotificationTypeEnum(str, Enum):
    """Types of notifications the system can send."""
    EXAM = "exam"
    SEATING = "seating"
    HALL_CHANGE = "hall_change"
    ATTENDANCE = "attendance"
    GENERAL = "general"


class AuditActionEnum(str, Enum):
    """Actions tracked in the audit log."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    GENERATE_SEATING = "generate_seating"
    MARK_ATTENDANCE = "mark_attendance"
    ASSIGN_DUTY = "assign_duty"
    EXPORT_REPORT = "export_report"
    BULK_UPLOAD = "bulk_upload"
    PUBLISH_EXAM = "publish_exam"
    CHANGE_PASSWORD = "change_password"
