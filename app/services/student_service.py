import logging
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.students_model import Student
from app.models.enrollments_model import Enrollment
from app.schemas.students_schema import StudentCreate, StudentUpdate, StudentResponse
from app.services.base_service import AppDataAccess, AppService

logger = logging.getLogger('student_service')

class StudentDataAccess(AppDataAccess):
    def __init__(self, session: Session):
        super().__init__(session)

    def create_student(self, student: StudentCreate):
        item = Student(
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            created_at=datetime.now(timezone.utc).timestamp(),
            updated_at=datetime.now(timezone.utc).timestamp()
        )

        self.session.add(item)
        self.session.flush()
        return item

    def get_student_by_uuid(self, uuid: str):
        item = self.session.query(Student)
        item = item.filter(Student.uuid == uuid)
        item = item.first()
        return item if item else None
    
    def get_all_students(self, skip: int = 0, limit: int = 100, course_uuid: str = None):
        items = self.session.query(Student)
        if course_uuid:
            items = items.filter(Student.enrollments.any(Enrollment.course_uuid == course_uuid))
        items = items.order_by(Student.created_at.desc())
        items = items.offset(skip).limit(limit)
        return items
    
    def update_student(self, uuid: str, student: StudentUpdate):
        item = self.get_student_by_uuid(uuid)
        if not item:
            return None
        item.first_name = student.first_name
        item.last_name = student.last_name
        item.email = student.email
        item.updated_at = datetime.now(timezone.utc).timestamp()
        self.session.flush()
        return item
    
    def delete_student(self, uuid: str):
        item = self.get_student_by_uuid(uuid)
        if not item:
            return None
        self.session.delete(item)
        self.session.flush()
        return item

class StudentService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = StudentDataAccess(session)

    def create_student(self, student: StudentCreate):
        try:
            item = self.data_access.create_student(student)

            if not item:
                raise HTTPException(status_code=404, detail="Error creating student")
            
            self.session.commit()
            return StudentResponse(
                uuid=item.uuid,
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            logger.error(f"Error creating student: {e}")
            self.session.rollback()
            raise HTTPException(status_code=500, detail="Error creating student")
        
    def get_student_by_uuid(self, uuid: str):
        try:
            item = self.data_access.get_student_by_uuid(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Student not found")
            
            return StudentResponse(
                uuid=item.uuid,
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            logger.error(f"Error getting student by uuid: {e}")
            raise HTTPException(status_code=500, detail="Error getting student by uuid")
        
    def get_all_students(self, skip: int = 0, limit: int = 100, course_uuid: str = None):
        try:
            items = self.data_access.get_all_students(skip, limit, course_uuid)
            
            return [StudentResponse(
                uuid=item.uuid,
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                created_at=item.created_at,
                updated_at=item.updated_at
            ) for item in items]
        except Exception as e:
            logger.error(f"Error getting all students: {e}")
            raise HTTPException(status_code=500, detail="Error getting all students")
        
    def update_student(self, uuid: str, student: StudentUpdate):
        try:
            item = self.data_access.update_student(uuid, student)

            if not item:
                raise HTTPException(status_code=404, detail="Error updating student")
            
            self.session.commit()
            return StudentResponse(
                uuid=item.uuid,
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except Exception as e:
            logger.error(f"Error updating student: {e}")
            self.session.rollback()
            raise HTTPException(status_code=500, detail="Error updating student")
        
    def delete_student(self, uuid: str):
        try:
            item = self.data_access.delete_student(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Error deleting student")

            self.session.commit()
            return {
                "status": "success",
                "message": "Student deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting student: {e}")
            self.session.rollback()
            raise HTTPException(status_code=500, detail="Error deleting student") 