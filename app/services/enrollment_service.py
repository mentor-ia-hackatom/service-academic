import logging
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import or_
from app.models.enrollments_model import Enrollment
from app.models.courses_model import Course
from app.models.assignments_model import Assignment
from app.models.students_model import Student
from app.schemas.enrollments_schema import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse
from app.services.base_service import AppDataAccess, AppService

logger = logging.getLogger('enrollment_service')

class EnrollmentDataAccess(AppDataAccess):
    def __init__(self, session: Session):
        super().__init__(session)

    def create_enrollment(self, enrollment: EnrollmentCreate):
        item = Enrollment(
            student_uuid=enrollment.student_uuid,
            course_uuid=enrollment.course_uuid,
            section_uuid=enrollment.section_uuid,
            status=enrollment.status,
            created_at=datetime.now(timezone.utc).timestamp(),
            updated_at=datetime.now(timezone.utc).timestamp()
        )

        self.session.add(item)
        self.session.flush()
        self.session.refresh(item)
        return item

    def get_enrollment_by_uuid(self, uuid: str):
        item = self.session.query(Enrollment)
        item = item.filter(Enrollment.uuid == uuid)
        item = item.first()
        return item if item else None
    
    def get_all_enrollments(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        course_code: str = None, 
        assignment_name: str = None,
        search: str = None,
        student_uuid: str = None, 
        course_uuid: str = None,
        section_uuid: str = None,
        _current_user_uuid: str = None,
        all: bool = False
    ):
        items = self.session.query(Enrollment)
        if course_code:
            items = items.filter(Enrollment.course.has(Course.code.ilike(f"%{course_code}%")))
        if course_uuid:
            items = items.filter(Enrollment.course_uuid == course_uuid)
        if assignment_name:
            items = items.filter(Enrollment.course.has(Course.assignments.any(Assignment.title.ilike(f"%{assignment_name}%"))))
        if search:
            items = items.filter(
                or_(
                    Enrollment.course.has(
                        Course.name.ilike(f"%{search}%")
                    ), 
                    or_(
                        Enrollment.student.has(Student.first_name.ilike(f"%{search}%")), 
                        Enrollment.student.has(Student.last_name.ilike(f"%{search}%"))
                    )
                )
            )
        if student_uuid:
            items = items.filter(Enrollment.student_uuid == student_uuid)
        if section_uuid:
            items = items.filter(Enrollment.section_uuid == section_uuid)
        if _current_user_uuid:
            items = items.filter(Enrollment.student_uuid == _current_user_uuid)
        items = items.order_by(Enrollment.created_at.desc())

        if not all:
            items = items.offset(skip).limit(limit)

        items = items.all()

        return items if items else None
    
    def update_enrollment(self, uuid: str, enrollment: EnrollmentUpdate):
        item = self.get_enrollment_by_uuid(uuid)
        if not item:
            return None
        item.student_uuid = enrollment.student_uuid
        item.course_uuid = enrollment.course_uuid
        item.section_uuid = enrollment.section_uuid
        item.status = enrollment.status
        item.updated_at = datetime.now(timezone.utc).timestamp()
        self.session.flush()
        return item
    
    def delete_enrollment(self, uuid: str):
        item = self.get_enrollment_by_uuid(uuid)
        if not item:
            return None
        self.session.delete(item)
        self.session.flush()
        return item

class EnrollmentService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = EnrollmentDataAccess(session)

    def create_enrollment(self, enrollment: EnrollmentCreate):
        try:
            item = self.data_access.create_enrollment(enrollment)

            if not item:
                raise HTTPException(status_code=404, detail="Error creating enrollment")
            self.session.commit()
            return EnrollmentResponse(
                uuid=item.uuid,
                course_uuid=item.course_uuid,
                student_uuid=item.student_uuid,
                section_uuid=item.section_uuid,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
                student=item.student,
                course=item.course,
                section=item.section
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating enrollment: {e}")
            raise HTTPException(status_code=500, detail="Error creating enrollment")
        
    def get_enrollment_by_uuid(self, uuid: str):
        try:
            item = self.data_access.get_enrollment_by_uuid(uuid)

            if not item:
                return HTTPException(status_code=404, detail="Enrollment not found")
            
            return EnrollmentResponse(
                uuid=item.uuid,
                course_uuid=item.course_uuid,
                student_uuid=item.student_uuid,
                section_uuid=item.section_uuid,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
                student=item.student,
                course=item.course,
                section=item.section
            )
        except Exception as e:
            logger.error(f"Error getting enrollment by uuid: {e}")
            raise HTTPException(status_code=500, detail="Error getting enrollment by uuid")
        
    def get_all_enrollments(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        course_code: str = None, 
        assignment_name: str = None,
        search: str = None,
        student_uuid: str = None, 
        course_uuid: str = None,
        section_uuid: str = None
    ):
        try:
            items = self.data_access.get_all_enrollments(skip, limit, course_code, assignment_name, search, student_uuid, course_uuid, section_uuid, self.current_user_uuid)

            if not items:
                return HTTPException(status_code=404, detail="No enrollments found")
            
            return [EnrollmentResponse(
                uuid=item.uuid,
                student_uuid=item.student_uuid,
                course_uuid=item.course_uuid,
                section_uuid=item.section_uuid,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at,
                student=item.student,
                course=item.course,
                section=item.section
            ) for item in items]
        except Exception as e:
            logger.error(f"Error getting all enrollments: {e}")
            raise HTTPException(status_code=500, detail="Error getting all enrollments")
        
    def update_enrollment(self, uuid: str, enrollment: EnrollmentUpdate):
        try:
            item = self.data_access.update_enrollment(uuid, enrollment)

            if not item:
                raise HTTPException(status_code=404, detail="Error updating enrollment")
            
            self.session.commit()
            return EnrollmentResponse(
                uuid=item.uuid,
                course_uuid=item.course_uuid,
                student_uuid=item.student_uuid,
                section_uuid=item.section_uuid,
                status=item.status,
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating enrollment: {e}")
            raise HTTPException(status_code=500, detail="Error updating enrollment")
        
    def delete_enrollment(self, uuid: str):
        try:
            item = self.data_access.delete_enrollment(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Error deleting enrollment")
            
            self.session.commit()
            return {
                "status": "success",
                "message": "Enrollment deleted successfully"
            }
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting enrollment: {e}")
            raise HTTPException(status_code=500, detail="Error deleting enrollment") 