from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.utils.dataBase import get_db
from app.schemas.sections_schema import SectionCreate, SectionUpdate, SectionResponse
from app.services.section_service import SectionService

router = APIRouter(prefix="/sections", tags=["Sections"])

@router.post("/create", response_model=SectionResponse)
def create_section(section: SectionCreate, session: Session = Depends(get_db), request: Request = None):
    service = SectionService(session, request)
    return service.create_section(section)

@router.get("/get-all", response_model=list[SectionResponse])
def get_sections(
        skip: int = 0, 
        limit: int = 100, 
        course_uuid: str = None, 
        search: str = None, 
        course_code: str = None, 
        student_uuid: str = None, 
        session: Session = Depends(get_db), 
        request: Request = None
    ):
    service = SectionService(session, request)
    return service.get_all_sections(skip, limit, course_uuid, search, course_code, student_uuid)



@router.get("/{uuid}", response_model=SectionResponse)
def get_section(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = SectionService(session, request)
    return service.get_section_by_uuid(uuid)

@router.put("/update/{uuid}", response_model=SectionResponse)
def update_section(uuid: str, section: SectionUpdate, session: Session = Depends(get_db), request: Request = None):
    service = SectionService(session, request)
    return service.update_section(uuid, section)

@router.delete("/delete/{uuid}")
def delete_section(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = SectionService(session, request)
    return service.delete_section(uuid) 