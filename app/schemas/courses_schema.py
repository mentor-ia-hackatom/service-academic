from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.schemas.assignments_schema import AssignmentBase

class CourseBase(BaseModel):
    uuid: UUID
    name: str
    code: str
    description: Optional[str] = None
    career_uuid: UUID

    class Config:
        from_attributes = True 

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    career_uuid: Optional[UUID] = None

class CourseResponse(CourseBase):
    uuid: UUID
    created_at: int
    updated_at: int
    assignments: list[AssignmentBase] = []

    class Config:
        from_attributes = True 