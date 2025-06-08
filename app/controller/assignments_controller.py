from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.utils.dataBase import get_db
from app.schemas.assignments_schema import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from app.services.assignment_service import AssignmentService

router = APIRouter(prefix="/assignments", tags=["Assignments"])

@router.post("/create", response_model=AssignmentResponse)
def create_assignment(assignment: AssignmentCreate, session: Session = Depends(get_db), request: Request = None):
    service = AssignmentService(session, request)
    return service.create_assignment(assignment)

@router.get("/get-all", response_model=list[AssignmentResponse])
def get_assignments(
    skip: int = 0, 
    limit: int = 100, 
    course_uuid: str = None, 
    search: str = None,
    course_code: str = None,
    student_uuid: str = None,
    session: Session = Depends(get_db), 
    request: Request = None
    ):
    service = AssignmentService(session, request)
    return service.get_all_assignments(skip, limit, course_uuid, search, course_code, student_uuid)

@router.get("/{uuid}", response_model=AssignmentResponse)
def get_assignment(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = AssignmentService(session, request)
    return service.get_assignment_by_uuid(uuid)


@router.put("/update/{uuid}", response_model=AssignmentResponse)
def update_assignment(uuid: str, assignment: AssignmentUpdate, session: Session = Depends(get_db), request: Request = None):
    service = AssignmentService(session, request)
    return service.update_assignment(uuid, assignment)

@router.delete("/delete/{uuid}")
def delete_assignment(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = AssignmentService(session, request)
    return service.delete_assignment(uuid) 