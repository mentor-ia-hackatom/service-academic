from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.utils.dataBase import get_db
from app.schemas.courses_schema import CourseCreate, CourseUpdate, CourseResponse
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/create", response_model=CourseResponse)
def create_course(course: CourseCreate, session: Session = Depends(get_db), request: Request = None):
    service = CourseService(session, request)
    return service.create_course(course)

@router.get("/get-all", response_model=list[CourseResponse])
def get_courses(skip: int = 0, limit: int = 100, search: str = None, course_code:str = None, student_uuid:str = None, session: Session = Depends(get_db), request: Request = None):
    service = CourseService(session, request)
    return service.get_all_courses(skip, limit, search, course_code, student_uuid)

@router.get("/{uuid}", response_model=CourseResponse)
def get_course(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = CourseService(session, request)
    return service.get_course_by_uuid(uuid)

@router.put("/update/{uuid}", response_model=CourseResponse)
def update_course(uuid: str, course: CourseUpdate, session: Session = Depends(get_db), request: Request = None):
    service = CourseService(session, request)
    return service.update_course(uuid, course)

@router.delete("/delete/{uuid}")
def delete_course(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = CourseService(session, request)
    return service.delete_course(uuid) 