import logging
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import or_

from app.models.sections_model import Section
from app.models.course_sections_model import CourseSection
from app.models.courses_model import Course
from app.models.enrollments_model import Enrollment
from app.schemas.sections_schema import SectionCreate, SectionUpdate, SectionResponse
from app.services.base_service import AppDataAccess, AppService

logger = logging.getLogger('section_service')

class SectionDataAccess(AppDataAccess):
    def __init__(self, session: Session):
        super().__init__(session)

    def create_section(self, section: SectionCreate):
        item = Section(
            name=section.name,
            code=section.code,
            description=section.description,
            created_at=datetime.now(timezone.utc).timestamp(),
            updated_at=datetime.now(timezone.utc).timestamp()
        )

        self.session.add(item)
        self.session.flush()
        self.session.refresh(item)
        return item

    def get_section_by_uuid(self, uuid: str):
        item = self.session.query(Section)
        item = item.filter(Section.uuid == uuid)
        item = item.first()
        return item if item else None
    
    def get_all_sections(self, skip: int = 0, limit: int = 100, course_uuid: str = None, search: str = None, course_code: str = None, student_uuid: str = None, _current_user_uuid: str = None):
        items = self.session.query(Section)

        if course_uuid:
            items = items.filter(
                Section.course_sections.any(
                    CourseSection.course_uuid == course_uuid
                )
            )
        if search:
            items = items.filter(
                or_(
                    Section.name.ilike(f"%{search}%"), 
                    Section.section_code.ilike(f"%{search}%")
                )
            )
        if course_code:
            items = items.filter(
                Section.course_sections.any(
                    CourseSection.course.any(
                        Course.code.ilike(f"%{course_code}%")
                    )
                )
            )

        if _current_user_uuid:
            items = items.filter(
                Section.course_sections.any(
                    CourseSection.course.has(
                        Course.enrollments.any(
                            Enrollment.student_uuid == _current_user_uuid
                        )
                    )
                )
            )
        if student_uuid:
            items = items.filter(
                Section.course_sections.any(
                    CourseSection.course.has(
                        Course.enrollments.any(
                            Enrollment.student_uuid == student_uuid
                        )
                    )
                )
            )
        items = items.order_by(Section.created_at.desc())
        items = items.offset(skip).limit(limit)
        items = items.all()
        return items if items else None

    
    def update_section(self, uuid: str, section: SectionUpdate):
        item = self.get_section_by_uuid(uuid)
        if not item:
            return None
        item.name = section.name
        item.section_code = section.section_code
        item.description = section.description
        item.updated_at = datetime.now(timezone.utc).timestamp()
        self.session.flush()
        return item
    
    def delete_section(self, uuid: str):
        item = self.get_section_by_uuid(uuid)
        if not item:
            return None
        self.session.delete(item)
        self.session.flush()
        return item

class SectionService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = SectionDataAccess(session)

    def create_section(self, section: SectionCreate):
        try:
            item = self.data_access.create_section(section)

            if not item:
                raise HTTPException(status_code=404, detail="Error creating section")
            
            self.session.commit()
            return SectionResponse(
                uuid=item.uuid,
                name=item.name,
                section_code=item.section_code,
                capacity=item.capacity,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            logger.error(f"Error creating section: {e}")
            self.session.rollback()
            raise HTTPException(status_code=500, detail="Error creating section")
        
    def get_section_by_uuid(self, uuid: str):
        try:
            item = self.data_access.get_section_by_uuid(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Section not found")
            
            return SectionResponse(
                uuid=item.uuid,
                name=item.name,
                section_code=item.section_code,
                capacity=item.capacity,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            logger.error(f"Error getting section by uuid: {e}")
            raise HTTPException(status_code=500, detail="Error getting section by uuid")
        
    def get_all_sections(self, skip: int = 0, limit: int = 100, course_uuid: str = None, search: str = None, course_code: str = None, student_uuid: str = None):
        try:
            items = self.data_access.get_all_sections(skip, limit, course_uuid, search, course_code, student_uuid, self.current_user_uuid)
            
            return [SectionResponse(
                uuid=item.uuid,
                name=item.name,
                section_code=item.section_code,
                capacity=item.capacity,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at
            ) for item in items]
        except Exception as e:
            logger.error(f"Error getting all sections: {e}")
            raise HTTPException(status_code=500, detail="Error getting all sections")
        
    def update_section(self, uuid: str, section: SectionUpdate):
        try:
            item = self.data_access.update_section(uuid, section)

            if not item:
                raise HTTPException(status_code=404, detail="Error updating section")
            
            self.session.commit()
            return SectionResponse(
                uuid=item.uuid,
                name=item.name,
                section_code=item.section_code,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            logger.error(f"Error updating section: {e}")
            self.session.rollback()
            raise HTTPException(status_code=500, detail="Error updating section")
        
    def delete_section(self, uuid: str):
        try:
            item = self.data_access.delete_section(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Error deleting section")
            
            self.session.commit()
            return {
                "status": "success",
                "message": "Section deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting section: {e}")
            self.session.rollback()
            raise HTTPException(status_code=500, detail="Error deleting section") 
    