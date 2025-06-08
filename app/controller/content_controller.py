from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.services.content_service import ContentService
from app.schemas.content_schema import ContentCreate, ContentUpdate, ContentResponse, CreateCoursesContent, CreateCoursesContentResponse
from app.utils.dataBase import get_db
from uuid import UUID
from typing import List

router = APIRouter(
    prefix="/content",
    tags=["Contents"]
)

@router.post("/create", response_model=ContentResponse)
def create_content(content: ContentCreate, request: Request, db: Session = Depends(get_db)):
    service = ContentService(db, request)
    return service.create_content(content)

@router.post("/create-courses-content", response_model=list[CreateCoursesContentResponse])
def create_courses_content(content: CreateCoursesContent, request: Request, db: Session = Depends(get_db)):
    service = ContentService(db, request)
    return service.create_courses_content(content)

@router.get("/get-all", response_model=list[ContentResponse])
def get_all_contents(
    skip: int = 0, 
    limit: int = 100, 
    course_uuid: str = None, 
    course_code: str = None,
    assignment_name: str = None,
    search: str = None,
    request: Request = None, 
    db: Session = Depends(get_db)
):
    service = ContentService(db, request)
    return service.get_all_contents(skip, limit, course_uuid, course_code, assignment_name, search)

@router.get("/download/{content_uuid}")
def download_content(content_uuid: UUID, request: Request, db: Session = Depends(get_db)):
    service = ContentService(db, request)
    return service.download_content(content_uuid)

@router.get("/{content_uuid}", response_model=ContentResponse)
def get_content(content_uuid: UUID, request: Request, db: Session = Depends(get_db)):
    service = ContentService(db, request)
    return service.get_content_by_uuid(content_uuid)


@router.put("/update/{content_uuid}", response_model=ContentResponse)
def update_content(content_uuid: UUID, content: ContentUpdate, request: Request, db: Session = Depends(get_db)):
    service = ContentService(db, request)
    return service.update_content(content_uuid, content)

@router.delete("/delete/{content_uuid}")
def delete_content(content_uuid: UUID, request: Request, db: Session = Depends(get_db)):
    service = ContentService(db, request)
    return service.delete_content(content_uuid)
