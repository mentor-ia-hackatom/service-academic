from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class AssignmentBase(BaseModel):
    uuid: UUID
    section_uuid: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[int] = None

    class Config:
        from_attributes = True 

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    section_uuid: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[int] = None

class AssignmentResponse(AssignmentBase):
    uuid: UUID
    course_uuid: UUID
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True 