from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class SectionBase(BaseModel):
    uuid: UUID
    name: str
    capacity: int
    section_code: str
    description: str

    class Config:
        from_attributes = True 

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    course_uuid: Optional[UUID] = None
    name: Optional[str] = None
    capacity: Optional[int] = None
    section_code: Optional[str] = None
    description: Optional[str] = None

class SectionResponse(SectionBase):
    created_at: int
    updated_at: int
    
    class Config:
        from_attributes = True 