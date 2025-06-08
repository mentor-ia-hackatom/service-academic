from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.models.enrollments_model import EnrollmentStatus
from app.schemas.students_schema import StudentBase
from app.schemas.courses_schema import CourseBase
from app.schemas.sections_schema import SectionBase

class EnrollmentBase(BaseModel):
    student_uuid: UUID
    course_uuid: UUID
    section_uuid: UUID
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    student_uuid: Optional[UUID] = None
    course_uuid: Optional[UUID] = None
    section_uuid: Optional[UUID] = None
    status: Optional[EnrollmentStatus] = None

class EnrollmentResponse(EnrollmentBase):
    uuid: UUID
    created_at: int
    updated_at: int
    student: StudentBase
    course: CourseBase
    section: SectionBase

    class Config:
        from_attributes = True 