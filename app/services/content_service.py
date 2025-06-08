import logging
from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import select, func
import requests
from app.models.content_model import Content
from app.models.course_content import CourseContent
from app.schemas.content_schema import ContentCreate, ContentUpdate, ContentResponse, CreateCoursesContent, CreateCoursesContentResponse
from app.services.base_service import AppService, AppDataAccess
from uuid import UUID
from playwright.sync_api import sync_playwright
import tempfile
import os
from app.models.courses_model import Course
from app.models.assignments_model import Assignment
from app.models.enrollments_model import Enrollment
from sqlalchemy import or_
logger = logging.getLogger('content_service')

class ContentDataAccess(AppDataAccess):
    def __init__(self, session: Session):
        super().__init__(session)

    def create_content(self, content: ContentCreate):
        item = Content(
            title=content.title,
            description=content.description,
            file_url=content.file_url,
            file_type=content.file_type,
            file_size=content.file_size,
            created_at=datetime.now(timezone.utc).timestamp(),
            updated_at=datetime.now(timezone.utc).timestamp()
        )

        self.session.add(item)
        self.session.flush()
        self.session.refresh(item)
        return item

    def create_courses_content(self, content_uuid: UUID, assignment_uuid: UUID, course_uuid: UUID, order: int = 0):
        item = CourseContent(
            content_uuid=content_uuid,
            course_uuid=course_uuid,
            assignment_uuid=assignment_uuid,
            order=order,
            created_at=datetime.now(timezone.utc).timestamp(),
            updated_at=datetime.now(timezone.utc).timestamp()
        )
        self.session.add(item)
        self.session.flush()
        self.session.refresh(item)
        return item
    
    def get_content_by_uuid(self, uuid: UUID):
        courses_subquery = (
            select(func.array_agg(CourseContent.course_uuid))
            .where(CourseContent.content_uuid == Content.uuid)
            .correlate(Content)
            .scalar_subquery()
        )
        item = self.session.query(
            Content.uuid,
            Content.title,
            Content.description,
            Content.file_url,
            Content.file_type,
            Content.file_size,
            Content.created_at,
            Content.updated_at,
            courses_subquery.label('courses_list')
        )
        item = item.filter(Content.uuid == uuid)
        item = item.first() 
        return item if item else None
    
    def get_all_contents(self, skip: int = 0, limit: int = 100, course_uuid: str = None, course_code: str = None, assignment_name: str = None, search: str = None, _current_user_uuid: str = None):
        # Subconsulta para obtener los UUIDs de los cursos
        courses_subquery = (
            select(func.array_agg(CourseContent.course_uuid))
            .where(CourseContent.content_uuid == Content.uuid)
            .correlate(Content)
            .scalar_subquery()
        )
        
        # Consulta principal con la subconsulta
        items = self.session.query(
            Content.uuid,
            Content.title,
            Content.description,
            Content.file_url,
            Content.file_type,
            Content.file_size,
            Content.created_at,
            Content.updated_at,
            courses_subquery.label('courses_list')
        ).outerjoin(
            CourseContent, 
            Content.uuid == CourseContent.content_uuid
        )
        
        if course_uuid:
            items = items.filter(Content.course_contents.any(CourseContent.course_uuid == course_uuid))
        if course_code:
            items = items.filter(Content.course_contents.any(CourseContent.course.has(Course.code.ilike(f"%{course_code}%"))))
        if assignment_name:
            items = items.filter(Content.course_contents.any(CourseContent.assignment.has(Assignment.title.ilike(f"%{assignment_name}%"))))
        if search:
            items = items.filter(
                or_(
                    Content.title.ilike(f"%{search}%"),
                    Content.course_contents.any(CourseContent.course.has(Course.name.ilike(f"%{search}%"))),
                    Content.course_contents.any(CourseContent.assignment.has(Assignment.title.ilike(f"%{search}%"))),
                    Content.course_contents.any(CourseContent.course.has(Course.code.ilike(f"%{search}%")))
                )
            )
        if _current_user_uuid:
            items = items.filter(Content.course_contents.any(CourseContent.course.has(Course.enrollments.any(Enrollment.student_uuid == _current_user_uuid))))

        items = items.group_by(Content.uuid)
        items = items.order_by(Content.created_at.desc())
        items = items.offset(skip).limit(limit)
        
        items = items.all()
        return items if items else None
    
    def update_content(self, uuid: UUID, content: ContentUpdate):
        item = self.get_content_by_uuid(uuid)
        if not item:
            return None
        
        update_data = content.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        
        item.updated_at = datetime.now(timezone.utc).timestamp()
        self.session.flush()
        return item
    
    def delete_content(self, uuid: UUID):
        item = self.get_content_by_uuid(uuid)
        if not item:
            return None
        self.session.delete(item)
        self.session.flush()
        return item

class ContentService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = ContentDataAccess(session)

    def create_content(self, content: ContentCreate):
        try:
            item = self.data_access.create_content(content.model_dump(exclude_unset=True))
            
            if not item:
                raise HTTPException(status_code=404, detail="Error creating content")
            
            self.session.commit()
            return ContentResponse(
                uuid=item.uuid,
                title=item.title,
                description=item.description,
                file_url=item.file_url,
                file_type=item.file_type,
                file_size=item.file_size,
                created_at=int(item.created_at),
                updated_at=int(item.updated_at)
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating content: {e}")
            raise HTTPException(status_code=500, detail="Error creating content")
        
    def create_courses_content(self, content: CreateCoursesContent):
        try:
            items = []
            for index, content_uuid in enumerate(content.conents):
                item = self.data_access.create_courses_content(
                    content_uuid, 
                    content.assignment_uuid, 
                    content.course_uuid, 
                    index
                )
                if not item:
                    raise HTTPException(status_code=404, detail="Error creating courses content")
                items.append(item)
                
            self.session.commit()
            return [CreateCoursesContentResponse(
                uuid=item.uuid,
                content_uuid=item.content_uuid,
                course_uuid=item.course_uuid,
                assignment_uuid=item.assignment_uuid,
                order=item.order,
                created_at=int(item.created_at),
                updated_at=int(item.updated_at)
            ) for item in items]
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating courses content: {e}")
            raise HTTPException(status_code=500, detail="Error creating courses content")
        
    def get_content_by_uuid(self, uuid: UUID):
        try:
            item = self.data_access.get_content_by_uuid(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Content not found")
            
            return ContentResponse(
                uuid=item.uuid,
                title=item.title,
                description=item.description,
                file_url=item.file_url,
                file_type=item.file_type,
                file_size=item.file_size,
                created_at=int(item.created_at),
                updated_at=int(item.updated_at),
                courses=item.courses_list
            )
        except Exception as e:
            logger.error(f"Error getting content by uuid: {e}")
            raise HTTPException(status_code=500, detail="Error getting content by uuid")
        
    def get_all_contents(self, skip: int = 0, limit: int = 100, course_uuid: str = None, course_code: str = None, assignment_name: str = None, search: str = None):
        try:
            items = self.data_access.get_all_contents(skip, limit, course_uuid, course_code, assignment_name, search, self.current_user_uuid)
            
            if not items:
                raise HTTPException(status_code=404, detail="No contents found")
            
            return [ContentResponse(
                uuid=item.uuid,
                title=item.title,
                description=item.description,
                file_url=item.file_url,
                file_type=item.file_type,
                file_size=item.file_size,
                created_at=int(item.created_at),
                updated_at=int(item.updated_at),
                courses=item.courses_list
            ) for item in items]
        except Exception as e:
            logger.error(f"Error getting all contents: {e}")
            raise HTTPException(status_code=500, detail="Error getting all contents")
        
    def update_content(self, uuid: UUID, content: ContentUpdate):
        try:
            item = self.data_access.update_content(uuid, content)

            if not item:
                raise HTTPException(status_code=404, detail="Error updating content")
            
            self.session.commit()
            return ContentResponse(
                uuid=item.uuid,
                title=item.title,
                description=item.description,
                file_url=item.file_url,
                file_type=item.file_type,
                file_size=item.file_size,
                created_at=int(item.created_at),
                updated_at=int(item.updated_at)
            )
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating content: {e}")
            raise HTTPException(status_code=500, detail="Error updating content")
        
    def delete_content(self, uuid: UUID):
        try:
            item = self.data_access.delete_content(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Error deleting content")
            
            self.session.commit()
            return {
                "status": "success",
                "message": "Content deleted successfully"
            }
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting content: {e}")
            raise HTTPException(status_code=500, detail="Error deleting content")

    def download_content(self, uuid: UUID) -> StreamingResponse:
        try:
            item = self.data_access.get_content_by_uuid(uuid)

            if not item:
                raise HTTPException(status_code=404, detail="Content not found")
            
            if item.file_type == "web":
                with sync_playwright() as p:
                    # Iniciar el navegador
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    
                    try:
                        # Navegar a la página
                        page.goto(item.file_url, wait_until='networkidle')
                        
                        # Crear un archivo temporal para el PDF
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                            # Generar el PDF
                            page.pdf(
                                path=temp_file.name,
                                format='A4',
                                print_background=True,
                                margin={
                                    'top': '0mm',
                                    'right': '0mm',
                                    'bottom': '0mm',
                                    'left': '0mm'
                                }
                            )
                            
                            # Leer el archivo PDF
                            with open(temp_file.name, 'rb') as pdf_file:
                                pdf_content = pdf_file.read()
                            
                            # Eliminar el archivo temporal
                            os.unlink(temp_file.name)
                            
                            return StreamingResponse(
                                iter([pdf_content]),
                                media_type='application/pdf',
                                headers={
                                    'Content-Disposition': f'attachment; filename={item.title}.pdf'
                                }
                            )
                    finally:
                        browser.close()
            else:
                file = requests.get(item.file_url, stream=True)
                return StreamingResponse(
                    file.iter_content(chunk_size=8192),
                    media_type=file.headers.get('content-type', 'application/octet-stream'),
                    headers={
                        'Content-Disposition': f'attachment; filename={item.title}'
                    }
                )

        except Exception as e:
            logger.error(f"Error downloading content: {e}")
            raise HTTPException(status_code=500, detail="Error downloading content")