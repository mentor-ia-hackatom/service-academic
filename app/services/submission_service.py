import logging
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import or_
from app.models.submissions_model import Submission
from app.models.assignments_model import Assignment
from app.models.courses_model import Course
from app.models.students_model import Student
from app.schemas.submissions_schema import SubmissionCreate, SubmissionUpdate, SubmissionResponse
from app.services.base_service import AppDataAccess, AppService

logger = logging.getLogger('submission_service')

class SubmissionDataAccess(AppDataAccess):
    def __init__(self, session: Session):
        super().__init__(session)

    def create_submission(self, submission: SubmissionCreate):
        item = Submission(
            assignment_uuid=submission.assignment_uuid,
            student_uuid=submission.student_uuid,
            content=submission.content,
            grade=submission.grade,
            feedback=submission.feedback,
            created_at=datetime.now(timezone.utc).timestamp(),
            updated_at=datetime.now(timezone.utc).timestamp()
        )

        self.session.add(item)
        self.session.flush()
        self.session.refresh(item)
        return item

    def get_submission_by_uuid(self, uuid: str):
        item = self.session.query(Submission)
        item = item.filter(Submission.uuid == uuid)
        item = item.first()
        return item if item else None
    
    def get_all_submissions(
        self, 
        skip: int = 0, 
        limit: int = 100,
        course_uuid: str = None,
        assignment_uuid: str = None, 
        student_uuid: str = None,
        course_code: str = None,
        assignment_name: str = None,
        search: str = None,
        _current_user_uuid: str = None
    ):
        items = self.session.query(Submission)
        if course_uuid:
            items = items.filter(
                Submission.assignment.any(
                    Assignment.course_uuid == course_uuid
                )
            )
        if assignment_uuid:
            items = items.filter(Submission.assignment_uuid == assignment_uuid)
        if student_uuid:
            items = items.filter(Submission.student_uuid == student_uuid)
        if course_code:
            items = items.filter(Submission.assignment.has(Assignment.course.has(Course.code.ilike(f"%{course_code}%"))))
        if assignment_name:
            items = items.filter(Submission.assignment.has(Assignment.title.ilike(f"%{assignment_name}%")))
        if search:
            items = items.filter(
                or_(
                    Submission.assignment.has(Assignment.title.ilike(f"%{search}%")), 
                    Submission.student.has(Student.first_name.ilike(f"%{search}%")), 
                    Submission.student.has(Student.last_name.ilike(f"%{search}%")),
                    Submission.assignment.has(
                        Assignment.course.has(
                            or_(
                                Course.name.ilike(f"%{search}%"),
                                Course.code.ilike(f"%{search}%")
                            )
                        )
                    )
                )
            )
        if _current_user_uuid:
            items = items.filter(Submission.student_uuid == _current_user_uuid)
        items = items.order_by(Submission.created_at.desc())
        items = items.offset(skip).limit(limit)
        items = items.all()
        return items if items else None
    
    def update_submission(self, uuid: str, submission: SubmissionUpdate):
        item = self.get_submission_by_uuid(uuid)
        if not item:
            return None
        item.assignment_uuid = submission.assignment_uuid   
        item.student_uuid = submission.student_uuid
        item.content = submission.content
        item.grade = submission.grade
        item.feedback = submission.feedback
        item.updated_at = datetime.now(timezone.utc).timestamp()
        self.session.flush()
        return item
    
    def delete_submission(self, uuid: str):
        item = self.get_submission_by_uuid(uuid)
        if not item:
            return None
        self.session.delete(item)
        self.session.flush()
        return item

class SubmissionService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = SubmissionDataAccess(session)

    def create_submission(self, submission: SubmissionCreate):
        try:
            item = self.data_access.create_submission(submission)

            if not item:
                raise HTTPException(status_code=404, detail="Error creating submission")
            
            self.session.commit()
            return SubmissionResponse(
                uuid=item.uuid,
                assignment_uuid=item.assignment_uuid,
                student_uuid=item.student_uuid,
                content=item.content,
                grade=item.grade,
                feedback=item.feedback,
                created_at=item.created_at,
                updated_at=item.updated_at,
                student=item.student,
                assignment=item.assignment
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating submission: {e}")
            raise HTTPException(status_code=500, detail="Error creating submission")
        
    def get_submission_by_uuid(self, uuid: str):
        try:
            item = self.data_access.get_submission_by_uuid(uuid)

            if not item:
                return HTTPException(status_code=404, detail="Submission not found")
            
            return SubmissionResponse(
                uuid=item.uuid,
                assignment_uuid=item.assignment_uuid,
                student_uuid=item.student_uuid,
                content=item.content,
                grade=item.grade,
                feedback=item.feedback,
                created_at=item.created_at,
                updated_at=item.updated_at,
                student=item.student,
                assignment=item.assignment
            )
        except Exception as e:
            logger.error(f"Error getting submission by uuid: {e}")
            raise HTTPException(status_code=500, detail="Error getting submission by uuid")
        
    def get_all_submissions(
        self, 
        skip: int = 0, 
        limit: int = 100,
        course_uuid: str = None,
        assignment_uuid: str = None, 
        student_uuid: str = None,
        course_code: str = None,
        assignment_name: str = None,
        search: str = None
    ):
        try:
            items = self.data_access.get_all_submissions(skip, limit, course_uuid, assignment_uuid, student_uuid, course_code, assignment_name, search, self.current_user_uuid)

            if not items:
                return HTTPException(status_code=404, detail="No submissions found")
            
            return [SubmissionResponse(
                uuid=item.uuid,
                assignment_uuid=item.assignment_uuid,
                student_uuid=item.student_uuid,
                content=item.content,
                grade=item.grade,
                feedback=item.feedback,
                created_at=item.created_at,
                updated_at=item.updated_at,
                student=item.student,
                assignment=item.assignment
            ) for item in items]
        except Exception as e:
            logger.error(f"Error getting all submissions: {e}")
            raise HTTPException(status_code=500, detail="Error getting all submissions")
        
    def update_submission(self, uuid: str, submission: SubmissionUpdate):
        try:
            item = self.data_access.update_submission(uuid, submission)

            if not item:
                raise HTTPException(status_code=404, detail="Error updating submission")
            
            self.session.commit()
            return SubmissionResponse(
                uuid=item.uuid,
                assignment_uuid=item.assignment_uuid,
                student_uuid=item.student_uuid,
                content=item.content,
                grade=item.grade,
                feedback=item.feedback,
                created_at=item.created_at,
                updated_at=item.updated_at,
                student=item.student,
                assignment=item.assignment
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating submission: {e}")
            raise HTTPException(status_code=500, detail="Error updating submission")
        
    def delete_submission(self, uuid: str):
        try:
            item = self.data_access.delete_submission(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Error deleting submission")
            
            self.session.commit()
            return {
                "status": "success",
                "message": "Submission deleted successfully"
            }
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting submission: {e}")
            raise HTTPException(status_code=500, detail="Error deleting submission") 