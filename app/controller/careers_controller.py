from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.utils.dataBase import get_db

## Services
from app.services.career_service import CareerService

## Schemas
from app.schemas.careers_schema import CareerCreate, CareerUpdate, CareerResponse


router = APIRouter(prefix="/careers", tags=["Careers"])

@router.post("/create", response_model=CareerResponse)
def create_career(career: CareerCreate, session: Session = Depends(get_db), request: Request = None):
    service = CareerService(session, request)
    return service.create_career(career)

@router.get("/get-all", response_model=list[CareerResponse])
def get_careers(session: Session = Depends(get_db), request: Request = None, skip: int = 0, limit: int = 100, search: str = None):
    service = CareerService(session, request)
    return service.get_all_careers(skip, limit, search)

@router.get("/{uuid}", response_model=CareerResponse)
def get_career(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = CareerService(session, request)
    return service.get_career_by_uuid(uuid)

@router.put("/update/{uuid}", response_model=CareerResponse)
def update_career(uuid: str, career: CareerUpdate, session: Session = Depends(get_db), request: Request = None):
    service = CareerService(session, request)
    return service.update_career(uuid, career)

@router.delete("/delete/{uuid}")
def delete_career(uuid: str, session: Session = Depends(get_db), request: Request = None):
    service = CareerService(session, request)
    return service.delete_career(uuid)