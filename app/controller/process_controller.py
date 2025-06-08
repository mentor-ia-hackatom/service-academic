from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.services.process_service import ProcessService
from app.utils.dataBase import get_db
from sqlalchemy.orm import Session
from fastapi import Request, Depends
import logging

logger = logging.getLogger('process_controller')

router = APIRouter(prefix="/internal/process", tags=["Internal Process"])

@router.get("/process-student-data")
def process_student_data(background_tasks: BackgroundTasks, session: Session = Depends(get_db), request: Request = None):
    service = ProcessService(session, request)
    try:
        background_tasks.add_task(service.process_student_prediction_data)
    except Exception as e:
        logger.error(f"Error processing student data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Student data processing started"}