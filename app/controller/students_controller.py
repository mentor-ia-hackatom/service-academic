from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.utils.dataBase import get_db
from app.schemas.students_schema import StudentCreate, StudentUpdate, StudentResponse
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/create", response_model=StudentResponse)
def create_student(student: StudentCreate, session: Session = Depends(get_db), request: Request = None):
    service = StudentService(session, request)
    return service.create_student(student)

@router.get("/get-all", response_model=list[StudentResponse])
def get_students(
    skip: int = 0, 
    limit: int = 100, 
    course_uuid: str = None,
    session: Session = Depends(get_db), 
    request: Request = None
    ):
    service = StudentService(session, request)
    return service.get_all_students(skip, limit, course_uuid)

@router.get("/{uuid}", response_model=StudentResponse)
def get_student(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = StudentService(session, request)
    return service.get_student_by_uuid(uuid)

@router.put("/update/{uuid}", response_model=StudentResponse)
def update_student(uuid: str, student: StudentUpdate, session: Session = Depends(get_db), request: Request = None):
    service = StudentService(session, request)
    return service.update_student(uuid, student)

@router.delete("/delete/{uuid}")
def delete_student(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = StudentService(session, request)
    return service.delete_student(uuid) 