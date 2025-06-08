from pydantic import BaseModel, UUID4
from typing import Optional

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_url: str
    file_type: str
    file_size: Optional[int] = None

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None

class ContentResponse(ContentBase):
    uuid: UUID4
    created_at: int
    updated_at: int
    courses: Optional[list[UUID4]] = None

    class Config:
        from_attributes = True

class CreateCoursesContent(BaseModel):
    conents: list[UUID4]
    course_uuid: UUID4
    assignment_uuid: Optional[UUID4] = None

class CreateCoursesContentResponse(BaseModel):
    uuid: UUID4
    content_uuid: UUID4
    course_uuid: UUID4
    assignment_uuid: Optional[UUID4] = None
    order: int
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True