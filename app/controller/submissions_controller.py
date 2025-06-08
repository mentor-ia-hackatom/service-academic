from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.utils.dataBase import get_db
from app.schemas.submissions_schema import SubmissionCreate, SubmissionUpdate, SubmissionResponse
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/submissions", tags=["Submissions"])

@router.post("/create", response_model=SubmissionResponse)
def create_submission(submission: SubmissionCreate, session: Session = Depends(get_db), request: Request = None):
    service = SubmissionService(session, request)
    return service.create_submission(submission)

@router.get("/get-all", response_model=list[SubmissionResponse])
def get_submissions(
    skip: int = 0, 
    limit: int = 100, 
    assignment_uuid: str = None, 
    student_uuid: str = None, 
    course_uuid: str = None,
    course_code: str = None,
    assignment_name: str = None,
    search: str = None, 
    session: Session = Depends(get_db), 
    request: Request = None
    ):
    service = SubmissionService(session, request)
    return service.get_all_submissions(skip, limit, course_uuid, assignment_uuid, student_uuid, course_code, assignment_name, search)


@router.get("/{uuid}", response_model=SubmissionResponse)
def get_submission(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = SubmissionService(session, request)
    return service.get_submission_by_uuid(uuid)


@router.put("/update/{uuid}", response_model=SubmissionResponse)
def update_submission(uuid: str, submission: SubmissionUpdate, session: Session = Depends(get_db), request: Request = None):
    service = SubmissionService(session, request)
    return service.update_submission(uuid, submission)

@router.delete("/delete/{uuid}")
def delete_submission(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = SubmissionService(session, request)
    return service.delete_submission(uuid) 