import logging
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import or_

from app.models.courses_model import Course
from app.models.enrollments_model import Enrollment
from app.schemas.courses_schema import CourseCreate, CourseUpdate, CourseResponse
from app.services.base_service import AppDataAccess, AppService

logger = logging.getLogger('course_service')

class CourseDataAccess(AppDataAccess):
    def __init__(self, session: Session):
        super().__init__(session)

    def create_course(self, course: CourseCreate):
        item = Course(
            name=course.name,
            code=course.code,
            description=course.description,
            created_at=datetime.now(timezone.utc).timestamp(),
            updated_at=datetime.now(timezone.utc).timestamp()
        )

        self.session.add(item)
        self.session.flush()
        self.session.refresh(item)
        return item

    def get_course_by_uuid(self, uuid: str):
        item = self.session.query(Course)
        item = item.filter(Course.uuid == uuid)
        item = item.first()
        return item if item else None
    
    def get_all_courses(self, skip: int = 0, limit: int = 100, search: str = None, course_code: str = None, student_uuid: str = None, _current_user_uuid: str = None):
        items = self.session.query(Course)
        if search:
            items = items.filter(
                or_(
                    Course.name.ilike(f"%{search}%"), 
                    Course.code.ilike(f"%{search}%")
                )
            )
        if course_code:
            items = items.filter(Course.code.ilike(f"%{course_code}%"))

        if student_uuid:
            items = items.filter(
                Course.enrollments.any(
                    Enrollment.student_uuid == student_uuid
                )
            )
        if _current_user_uuid:
            items = items.filter(
                Course.enrollments.any(
                    Enrollment.student_uuid == _current_user_uuid
                )
            )
        items = items.order_by(Course.created_at.desc())
        items = items.offset(skip).limit(limit)
        items = items.all()
        return items if items else None
    
    def update_course(self, uuid: str, course: CourseUpdate):
        item = self.get_course_by_uuid(uuid)
        if not item:
            return None
        item.name = course.name
        item.code = course.code
        item.description = course.description
        item.updated_at = datetime.now(timezone.utc).timestamp()
        self.session.flush()
        return item
    
    def delete_course(self, uuid: str):
        item = self.get_course_by_uuid(uuid)
        if not item:
            return None
        self.session.delete(item)
        self.session.flush()
        return item

class CourseService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = CourseDataAccess(session)

    def create_course(self, course: CourseCreate):
        try:
            item = self.data_access.create_course(course)

            if not item:
                raise HTTPException(status_code=404, detail="Error creating course")
            
            self.session.commit()
            return CourseResponse(
                uuid=item.uuid,
                name=item.name,
                code=item.code,
                description=item.description,
                created_at=int(item.created_at),
                updated_at=int(item.updated_at)
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating course: {e}")
            raise HTTPException(status_code=500, detail="Error creating course")
        
    def get_course_by_uuid(self, uuid: str):
        try:
            item = self.data_access.get_course_by_uuid(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Course not found")
            
            return CourseResponse(
                uuid=item.uuid,
                career_uuid=item.career_uuid,
                name=item.name,
                code=item.code,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at,
                assignments=item.assignments
            )
        except Exception as e:
            logger.error(f"Error getting course by uuid: {e}")
            raise HTTPException(status_code=500, detail="Error getting course by uuid")
        
    def get_all_courses(self, skip: int = 0, limit: int = 100, search: str = None, course_code: str = None, student_uuid: str = None):
        try:
            items = self.data_access.get_all_courses(skip, limit, search, course_code, student_uuid, self.current_user_uuid)
            
            return [CourseResponse(
                uuid=item.uuid,
                career_uuid=item.career_uuid,
                name=item.name,
                code=item.code,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at,
                assignments=item.assignments
            ) for item in items]
        except Exception as e:
            logger.error(f"Error getting all courses: {e}")
            raise HTTPException(status_code=500, detail="Error getting all courses")
        
    def update_course(self, uuid: str, course: CourseUpdate):
        try:
            item = self.data_access.update_course(uuid, course)

            if not item:
                raise HTTPException(status_code=404, detail="Error updating course")
            
            self.session.commit()
            return CourseResponse(
                uuid=item.uuid,
                name=item.name,
                code=item.code,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating course: {e}")
            raise HTTPException(status_code=500, detail="Error updating course")
        
    def delete_course(self, uuid: str):
        try:
            item = self.data_access.delete_course(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Error deleting course")
            
            self.session.commit()
            return {
                "status": "success",
                "message": "Course deleted successfully"
            }
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting course: {e}")
            raise HTTPException(status_code=500, detail="Error deleting course") 