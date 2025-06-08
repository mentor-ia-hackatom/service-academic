from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.schemas.students_schema import StudentBase
from app.schemas.assignments_schema import AssignmentBase

class SubmissionBase(BaseModel):
    assignment_uuid: UUID
    student_uuid: UUID
    content: Optional[str] = None
    grade: Optional[float] = None
    feedback: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionUpdate(BaseModel):
    assignment_uuid: Optional[UUID] = None
    student_uuid: Optional[UUID] = None
    content: Optional[str] = None
    grade: Optional[float] = None
    feedback: Optional[str] = None

class SubmissionResponse(SubmissionBase):
    uuid: UUID
    created_at: int
    updated_at: int
    student: StudentBase
    assignment: AssignmentBase

    class Config:
        from_attributes = True 