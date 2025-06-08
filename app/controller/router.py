from fastapi import APIRouter
from app.controller.careers_controller import router as careers_router
from app.controller.courses_controller import router as courses_router
from app.controller.sections_controller import router as sections_router
from app.controller.students_controller import router as students_router
from app.controller.assignments_controller import router as assignments_router
from app.controller.enrollments_controller import router as enrollments_router
from app.controller.submissions_controller import router as submissions_router
from app.controller.content_controller import router as content_router
from app.controller.process_controller import router as process_router

api_router = APIRouter()
api_router.include_router(careers_router)
api_router.include_router(courses_router)
api_router.include_router(sections_router)
api_router.include_router(students_router)
api_router.include_router(assignments_router)
api_router.include_router(enrollments_router)
api_router.include_router(submissions_router)
api_router.include_router(content_router)
api_router.include_router(process_router)