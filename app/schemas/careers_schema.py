from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.schemas.courses_schema import CourseBase

class CareerBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class CareerCreate(CareerBase):
    pass

class CareerUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class CareerResponse(CareerBase):
    uuid: UUID
    created_at: int
    updated_at: int
    courses: list[CourseBase] = []

    class Config:
        from_attributes = True 