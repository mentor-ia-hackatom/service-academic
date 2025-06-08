import logging
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import or_
from app.models.assignments_model import Assignment
from app.models.courses_model import Course
from app.models.enrollments_model import Enrollment
from app.schemas.assignments_schema import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from app.services.base_service import AppDataAccess, AppService

logger = logging.getLogger('assignment_service')

class AssignmentDataAccess(AppDataAccess):
    def __init__(self, session: Session):
        super().__init__(session)

    def create_assignment(self, assignment: AssignmentCreate):
        item = Assignment(
            course_uuid=assignment.course_uuid,
            section_uuid=assignment.section_uuid,
            title=assignment.title,
            description=assignment.description,
            due_date=assignment.due_date,
            created_at=datetime.now(timezone.utc).timestamp(),
            updated_at=datetime.now(timezone.utc).timestamp()
        )

        self.session.add(item)
        self.session.flush()
        return item

    def get_assignment_by_uuid(self, uuid: str):
        item = self.session.query(Assignment)
        item = item.filter(Assignment.uuid == uuid)
        item = item.first()
        return item if item else None
    
    def get_all_assignments(self, skip: int = 0, limit: int = 100, course_uuid: str = None, search: str = None, course_code: str = None, student_uuid: str = None, _current_user_uuid: str = None):
        items = self.session.query(Assignment)
        if course_uuid:
            items = items.filter(Assignment.course_uuid == course_uuid)
        if search:
            items = items.filter(
                or_(
                    Assignment.title.ilike(f"%{search}%"), 
                    Assignment.description.ilike(f"%{search}%")
                )
            )
        if course_code:
            items = items.filter(
                Assignment.course.has(
                    Course.code.ilike(f"%{course_code}%")
                )
            )
        if student_uuid:
            items = items.filter(
                Assignment.course.has(
                    Course.enrollments.any(Enrollment.student_uuid == student_uuid)
                )
            )
        if _current_user_uuid:
            items = items.filter(
                Assignment.course.has(
                    Course.enrollments.any(Enrollment.student_uuid == _current_user_uuid)
                )
            )
        items = items.order_by(Assignment.created_at.desc())
        items = items.offset(skip).limit(limit)
        items = items.all()
        return items if items else None
    
    def update_assignment(self, uuid: str, assignment: AssignmentUpdate):
        item = self.get_assignment_by_uuid(uuid)
        if not item:
            return None
        item.title = assignment.title
        item.section_uuid = assignment.section_uuid
        item.description = assignment.description
        item.updated_at = datetime.now(timezone.utc).timestamp()
        self.session.flush()
        return item
    
    def delete_assignment(self, uuid: str):
        item = self.get_assignment_by_uuid(uuid)
        if not item:
            return None
        self.session.delete(item)
        self.session.flush()
        return item

class AssignmentService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = AssignmentDataAccess(session)

    def create_assignment(self, assignment: AssignmentCreate):
        try:
            item = self.data_access.create_assignment(assignment)

            if not item:
                raise HTTPException(status_code=404, detail="Error creating assignment")
            
            self.session.commit()
            return AssignmentResponse(
                uuid=item.uuid,
                course_uuid=item.course_uuid,
                section_uuid=item.section_uuid,
                title=item.title,
                description=item.description,
                due_date=item.due_date,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            logger.error(f"Error creating assignment: {e}")
            self.session.rollback()
            raise HTTPException(status_code=500, detail="Error creating assignment")
        
    def get_assignment_by_uuid(self, uuid: str):
        try:
            item = self.data_access.get_assignment_by_uuid(uuid)

            if not item:
                return HTTPException(status_code=404, detail="Assignment not found")
            
            return AssignmentResponse(
                uuid=item.uuid,
                course_uuid=item.course_uuid,
                section_uuid=item.section_uuid,
                title=item.title,
                description=item.description,
                due_date=item.due_date,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            logger.error(f"Error getting assignment by uuid: {e}")
            raise HTTPException(status_code=500, detail="Error getting assignment by uuid")
        
    def get_all_assignments(self, skip: int = 0, limit: int = 100, course_uuid: str = None, search: str = None, course_code: str = None, student_uuid: str = None):
        try:
            items = self.data_access.get_all_assignments(skip, limit, course_uuid, search, course_code, student_uuid, self.current_user_uuid)

            if not items:
                return HTTPException(status_code=404, detail="No assignments found")
            
            return [AssignmentResponse(
                uuid=item.uuid,
                course_uuid=item.course_uuid,
                section_uuid=item.section_uuid,
                title=item.title,
                description=item.description,
                created_at=item.created_at,
                updated_at=item.updated_at
            ) for item in items]
        except Exception as e:
            logger.error(f"Error getting all assignments: {e}")
            raise HTTPException(status_code=500, detail="Error getting all assignments")
        
    def update_assignment(self, uuid: str, assignment: AssignmentUpdate):
        try:
            item = self.data_access.update_assignment(uuid, assignment)

            if not item:
                raise HTTPException(status_code=404, detail="Error updating assignment")
            
            self.session.commit()
            return AssignmentResponse(
                uuid=item.uuid,
                course_uuid=item.course_uuid,
                section_uuid=item.section_uuid,
                title=item.title,
                description=item.description,
                due_date=item.due_date,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            logger.error(f"Error updating assignment: {e}")
            self.session.rollback()
            raise HTTPException(status_code=500, detail="Error updating assignment")
        
    def delete_assignment(self, uuid: str):
        try:
            item = self.data_access.delete_assignment(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Error deleting assignment")
            
            self.session.commit()
            return {
                "status": "success",
                "message": "Assignment deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting assignment: {e}")
            self.session.rollback()
            raise HTTPException(status_code=500, detail="Error deleting assignment") 