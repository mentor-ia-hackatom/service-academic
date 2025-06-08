from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.utils.dataBase import get_db
from app.schemas.enrollments_schema import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("/create", response_model=EnrollmentResponse)
def create_enrollment(enrollment: EnrollmentCreate, session: Session = Depends(get_db), request: Request = None):
    service = EnrollmentService(session, request)
    return service.create_enrollment(enrollment)

@router.get("/get-all", response_model=list[EnrollmentResponse])
def get_enrollments(
    skip: int = 0, 
    limit: int = 100, 
    course_code: str = None, 
    assignment_name: str = None,
    search: str = None,
    student_uuid: str = None,
    course_uuid: str = None,
    section_uuid: str = None,
    session: Session = Depends(get_db), 
    request: Request = None
    ):
    service = EnrollmentService(session, request)
    return service.get_all_enrollments(skip, limit, course_code, assignment_name, search, student_uuid, course_uuid, section_uuid)

@router.get("/{uuid}", response_model=EnrollmentResponse)
def get_enrollment(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = EnrollmentService(session, request)
    return service.get_enrollment_by_uuid(uuid)

@router.put("/update/{uuid}", response_model=EnrollmentResponse)
def update_enrollment(uuid: str, enrollment: EnrollmentUpdate, session: Session = Depends(get_db), request: Request = None):
    service = EnrollmentService(session, request)
    return service.update_enrollment(uuid, enrollment)

@router.delete("/delete/{uuid}")
def delete_enrollment(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = EnrollmentService(session, request)
    return service.delete_enrollment(uuid) 