import logging
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

## Models
from app.models.career_model import Career
from app.models.courses_model import Course
from app.models.enrollments_model import Enrollment

## Schemas
from app.schemas.careers_schema import CareerCreate, CareerUpdate, CareerResponse

## Services
from app.services.base_service import AppDataAccess, AppService

## Extras
import logging
from datetime import datetime, timezone

## Utils


logger = logging.getLogger('career_service')    


class CareerDataAccess(AppDataAccess):
    def __init__(self, session: Session):
        super().__init__(session)

    def create_career(self, career: CareerCreate):
        item = Career(
            name=career.name,
            code=career.code,
            description=career.description,
            created_at=datetime.now(timezone.utc).timestamp(),
            updated_at=datetime.now(timezone.utc).timestamp()
        )

        self.session.add(item)
        self.session.flush()
        self.session.refresh(item)
        return item

    def get_career_by_uuid(self, uuid: str):
        item = self.session.query(Career)
        item = item.filter(Career.uuid == uuid)
        item = item.first()
        return item if item else None
    
    def get_all_careers(self, skip: int = 0, limit: int = 100, search: str = None, _current_user_uuid: str = None):
        items = self.session.query(Career)
        if search:
            items = items.filter(
                or_(
                    Career.name.ilike(f"%{search}%"), 
                    Career.code.ilike(f"%{search}%")
                )
            )
        if _current_user_uuid:
            items = items.filter(
                Career.courses.any(
                    Course.enrollments.any(
                        Enrollment.student_uuid == _current_user_uuid
                    )
                )
            )

        items = items.order_by(Career.created_at.desc())
        items = items.offset(skip).limit(limit)
        items = items.all()
        return items
    
    def update_career(self, uuid: str, career: CareerUpdate):
        item = self.get_career_by_uuid(uuid)
        if not item:
            return None
        item.name = career.name
        item.code = career.code
        item.description = career.description
        item.updated_at = datetime.now(timezone.utc).timestamp()
        self.session.flush()
        return item
    
    def delete_career(self, uuid: str):
        item = self.get_career_by_uuid(uuid)
        if not item:
            return None
        self.session.delete(item)
        self.session.flush()
        return item

class CareerService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = CareerDataAccess(session)

    def create_career(self, career: CareerCreate):
        try:
            item = self.data_access.create_career(career)

            if not item:
                raise HTTPException(status_code=404, detail="Error creating career")
            
            self.session.commit()

            return CareerResponse(
                uuid=item.uuid,
                name=item.name,
                code=item.code,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at,
                courses=item.courses
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating career: {e}")
            raise HTTPException(status_code=500, detail="Error creating career")
        
    def get_career_by_uuid(self, uuid: str):
        try:
            item = self.data_access.get_career_by_uuid(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Career not found")
            
            return CareerResponse(
                uuid=item.uuid,
                name=item.name,
                code=item.code,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at,
                courses=item.courses
            )
        except Exception as e:
            logger.error(f"Error getting career by uuid: {e}")
            raise HTTPException(status_code=500, detail="Error getting career by uuid")
        
    def get_all_careers(self, skip: int = 0, limit: int = 100, search: str = None):
        try:
            items = self.data_access.get_all_careers(skip, limit, search, self.current_user_uuid)
            
            return [CareerResponse(
                uuid=item.uuid,
                name=item.name,
                code=item.code,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at,
                courses=item.courses
            ) for item in items]
        except Exception as e:
            logger.error(f"Error getting all careers: {e}")
            raise HTTPException(status_code=500, detail="Error getting all careers")
        
    def update_career(self, uuid: str, career: CareerUpdate):
        try:
            item = self.data_access.update_career(uuid, career)

            if not item:
                raise HTTPException(status_code=404, detail="Error updating career")
            
            self.session.commit()
            return CareerResponse(
                uuid=item.uuid,
                name=item.name,
                code=item.code,
                description=item.description,
                created_at=int(item.created_at),
                updated_at=int(item.updated_at),
                courses=item.courses
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating career: {e}")
            raise HTTPException(status_code=500, detail="Error updating career")
        
    def delete_career(self, uuid: str):
        try:
            item = self.data_access.delete_career(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Error deleting career")
            
            self.session.commit()
            return {
                "status": "success",
                "message": "Career deleted successfully"
            }
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting career: {e}")
            raise HTTPException(status_code=500, detail="Error deleting career")