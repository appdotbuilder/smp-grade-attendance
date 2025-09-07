from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from enum import Enum


# Enums for status values
class AttendanceStatus(str, Enum):
    HADIR = "hadir"  # Present
    ALPHA = "alpha"  # Absent without notice
    IZIN = "izin"  # Excused
    SAKIT = "sakit"  # Sick
    TERLAMBAT = "terlambat"  # Late


class GradeCategory(str, Enum):
    HARIAN = "harian"  # Daily Assessments - 30%
    UTS = "uts"  # Mid-term Exam - 30%
    UAS = "uas"  # Final Exam - 40%


# Persistent models (stored in database)
class Teacher(SQLModel, table=True):
    __tablename__ = "teachers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    nip: str = Field(unique=True, max_length=20, description="Teacher ID Number")
    name: str = Field(max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    classes: List["Class"] = Relationship(back_populates="homeroom_teacher")
    subject_assignments: List["TeacherSubject"] = Relationship(back_populates="teacher")
    grades: List["Grade"] = Relationship(back_populates="teacher")
    attendances: List["Attendance"] = Relationship(back_populates="teacher")


class Student(SQLModel, table=True):
    __tablename__ = "students"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    nis: str = Field(unique=True, max_length=20, description="Student ID Number")
    name: str = Field(max_length=100)
    date_of_birth: date
    gender: str = Field(max_length=1, regex="^[MF]$", description="M for Male, F for Female")
    address: Optional[str] = Field(default=None, max_length=500)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    class_id: int = Field(foreign_key="classes.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    class_: "Class" = Relationship(back_populates="students")
    grades: List["Grade"] = Relationship(back_populates="student")
    attendances: List["Attendance"] = Relationship(back_populates="student")


class Subject(SQLModel, table=True):
    __tablename__ = "subjects"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, max_length=10, description="Subject code")
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    teacher_assignments: List["TeacherSubject"] = Relationship(back_populates="subject")
    grades: List["Grade"] = Relationship(back_populates="subject")
    attendances: List["Attendance"] = Relationship(back_populates="subject")


class Class(SQLModel, table=True):
    __tablename__ = "classes"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, description="Class name like '7A', '8B', etc.")
    grade_level: int = Field(ge=7, le=9, description="Grade level 7-9 for SMP")
    academic_year: str = Field(max_length=9, description="Academic year like '2023/2024'")
    homeroom_teacher_id: Optional[int] = Field(default=None, foreign_key="teachers.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    homeroom_teacher: Optional[Teacher] = Relationship(back_populates="classes")
    students: List[Student] = Relationship(back_populates="class_")
    teacher_subjects: List["TeacherSubject"] = Relationship(back_populates="class_")


class TeacherSubject(SQLModel, table=True):
    __tablename__ = "teacher_subjects"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="teachers.id")
    subject_id: int = Field(foreign_key="subjects.id")
    class_id: int = Field(foreign_key="classes.id")
    academic_year: str = Field(max_length=9, description="Academic year like '2023/2024'")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    teacher: Teacher = Relationship(back_populates="subject_assignments")
    subject: Subject = Relationship(back_populates="teacher_assignments")
    class_: Class = Relationship(back_populates="teacher_subjects")


class Grade(SQLModel, table=True):
    __tablename__ = "grades"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    subject_id: int = Field(foreign_key="subjects.id")
    teacher_id: int = Field(foreign_key="teachers.id")
    category: GradeCategory = Field(description="Grade category")
    score: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    assessment_name: str = Field(max_length=200, description="Name of the assessment")
    assessment_date: date
    semester: int = Field(ge=1, le=2, description="Semester 1 or 2")
    academic_year: str = Field(max_length=9, description="Academic year like '2023/2024'")
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Student = Relationship(back_populates="grades")
    subject: Subject = Relationship(back_populates="grades")
    teacher: Teacher = Relationship(back_populates="grades")


class Attendance(SQLModel, table=True):
    __tablename__ = "attendances"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    teacher_id: int = Field(foreign_key="teachers.id")
    subject_id: Optional[int] = Field(
        default=None, foreign_key="subjects.id", description="Optional for per-subject attendance"
    )
    attendance_date: date
    status: AttendanceStatus = Field(description="Attendance status")
    notes: Optional[str] = Field(default=None, max_length=500, description="Additional notes")
    academic_year: str = Field(max_length=9, description="Academic year like '2023/2024'")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Student = Relationship(back_populates="attendances")
    teacher: Teacher = Relationship(back_populates="attendances")
    subject: Optional[Subject] = Relationship(back_populates="attendances")


# Non-persistent schemas (for validation, forms, API requests/responses)
class TeacherCreate(SQLModel, table=False):
    nip: str = Field(max_length=20)
    name: str = Field(max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)


class TeacherUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = Field(default=None)


class StudentCreate(SQLModel, table=False):
    nis: str = Field(max_length=20)
    name: str = Field(max_length=100)
    date_of_birth: date
    gender: str = Field(max_length=1, regex="^[MF]$")
    address: Optional[str] = Field(default=None, max_length=500)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    class_id: int


class StudentUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    date_of_birth: Optional[date] = Field(default=None)
    gender: Optional[str] = Field(default=None, max_length=1, regex="^[MF]$")
    address: Optional[str] = Field(default=None, max_length=500)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    class_id: Optional[int] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class SubjectCreate(SQLModel, table=False):
    code: str = Field(max_length=10)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class SubjectUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = Field(default=None)


class ClassCreate(SQLModel, table=False):
    name: str = Field(max_length=50)
    grade_level: int = Field(ge=7, le=9)
    academic_year: str = Field(max_length=9)
    homeroom_teacher_id: Optional[int] = Field(default=None)


class ClassUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=50)
    grade_level: Optional[int] = Field(default=None, ge=7, le=9)
    academic_year: Optional[str] = Field(default=None, max_length=9)
    homeroom_teacher_id: Optional[int] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class TeacherSubjectCreate(SQLModel, table=False):
    teacher_id: int
    subject_id: int
    class_id: int
    academic_year: str = Field(max_length=9)


class GradeCreate(SQLModel, table=False):
    student_id: int
    subject_id: int
    teacher_id: int
    category: GradeCategory
    score: Decimal = Field(ge=0, le=100)
    assessment_name: str = Field(max_length=200)
    assessment_date: date
    semester: int = Field(ge=1, le=2)
    academic_year: str = Field(max_length=9)
    notes: Optional[str] = Field(default=None, max_length=500)


class GradeUpdate(SQLModel, table=False):
    score: Optional[Decimal] = Field(default=None, ge=0, le=100)
    assessment_name: Optional[str] = Field(default=None, max_length=200)
    assessment_date: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)


class AttendanceCreate(SQLModel, table=False):
    student_id: int
    teacher_id: int
    subject_id: Optional[int] = Field(default=None)
    attendance_date: date
    status: AttendanceStatus
    notes: Optional[str] = Field(default=None, max_length=500)
    academic_year: str = Field(max_length=9)


class AttendanceUpdate(SQLModel, table=False):
    status: Optional[AttendanceStatus] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)


# Report schemas for data aggregation
class StudentGradesSummary(SQLModel, table=False):
    student_id: int
    student_name: str
    subject_id: int
    subject_name: str
    harian_avg: Optional[Decimal] = Field(default=None)
    uts_score: Optional[Decimal] = Field(default=None)
    uas_score: Optional[Decimal] = Field(default=None)
    final_grade: Optional[Decimal] = Field(default=None)
    semester: int
    academic_year: str


class StudentAttendanceSummary(SQLModel, table=False):
    student_id: int
    student_name: str
    total_days: int
    hadir_count: int
    alpha_count: int
    izin_count: int
    sakit_count: int
    terlambat_count: int
    attendance_percentage: Decimal
    month: int
    year: int


class ClassGradesSummary(SQLModel, table=False):
    class_id: int
    class_name: str
    subject_id: int
    subject_name: str
    student_count: int
    average_grade: Decimal
    highest_grade: Decimal
    lowest_grade: Decimal
    semester: int
    academic_year: str


class ClassAttendanceSummary(SQLModel, table=False):
    class_id: int
    class_name: str
    total_students: int
    total_days: int
    overall_attendance_percentage: Decimal
    month: int
    year: int
