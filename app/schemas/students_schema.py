from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class StudentBase(BaseModel):
    uuid: UUID
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True 

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

class StudentResponse(StudentBase):
    uuid: UUID
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True 