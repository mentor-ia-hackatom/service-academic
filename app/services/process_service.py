import logging
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timezone
import statistics
from typing import List, Dict, Any
import json

## Models
from app.models import Student, Submission, Assignment, Enrollment, CourseContent

## Schemas
from app.schemas.prediction_model_schema import StudentData

## Services
from app.services.base_service import AppDataAccess, AppService
from app.services.course_service import CourseDataAccess
from app.services.student_service import StudentDataAccess
from app.services.enrollment_service import EnrollmentDataAccess

## Extras
import logging
import os
import requests

## Utils
from app.core.config import settings

logger = logging.getLogger('process_service')    

class ProcessDataAccess(AppDataAccess):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_student_performance_metrics(self, student_uuid: str, course_uuid: str) -> Dict[str, float]:
        """Calcula métricas de rendimiento del estudiante para un curso específico"""
        # Obtener todas las calificaciones del estudiante para el curso específico
        grades = self.session.query(Submission.grade).join(
            Assignment,
            Submission.assignment_uuid == Assignment.uuid
        ).filter(
            Submission.student_uuid == student_uuid,
            Assignment.course_uuid == course_uuid,
            Submission.grade.isnot(None)
        ).all()
        
        grades = [g[0] for g in grades]
        
        if not grades:
            return {
                "avg_grade": 0.0,
                "grade_stddev": 0.0
            }
        
        return {
            "avg_grade": sum(grades) / len(grades),
            "grade_stddev": statistics.stdev(grades) if len(grades) > 1 else 0.0
        }

    def get_student_submission_metrics(self, student_uuid: str, course_uuid: str) -> Dict[str, float]:
        """Calcula métricas relacionadas con las entregas del estudiante para un curso específico"""
        submissions = self.session.query(
            Submission,
            Assignment.due_date
        ).join(
            Assignment,
            Submission.assignment_uuid == Assignment.uuid
        ).filter(
            Submission.student_uuid == student_uuid,
            Assignment.course_uuid == course_uuid
        ).all()

        if not submissions:
            return {
                "retry_rate": 0.0,
                "avg_delivery_delay_days": 0.0,
                "avg_submission_time_diff_hours": 0.0,
                "late_submissions_count": 0,
                "missing_tasks": 0,
                "completed_tasks": 0,
                "total_tasks": 0
            }

        # Calcular métricas
        total_submissions = len(submissions)
        late_submissions = sum(1 for s, due in submissions if s.created_at > due)
        completed_tasks = len(set(s[0].assignment_uuid for s in submissions))
        
        # Obtener total de tareas asignadas para el curso específico
        total_tasks = self.session.query(Assignment).join(
            Enrollment,
            and_(
                Assignment.course_uuid == Enrollment.course_uuid,
                Assignment.section_uuid == Enrollment.section_uuid
            )
        ).filter(
            Enrollment.student_uuid == student_uuid,
            Assignment.course_uuid == course_uuid
        ).count()

        # Calcular retrasos promedio
        delays = []
        for submission, due_date in submissions:
            if due_date:
                delay = (submission.created_at - due_date) / (24 * 3600)  # Convertir a días
                delays.append(delay)

        avg_delay = sum(delays) / len(delays) if delays else 0.0

        # Calcular diferencia promedio entre envíos
        submission_times = sorted(s[0].created_at for s in submissions)
        time_diffs = []
        for i in range(1, len(submission_times)):
            diff = (submission_times[i] - submission_times[i-1]) / 3600  # Convertir a horas
            time_diffs.append(diff)

        avg_time_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0.0

        return {
            "retry_rate": (total_submissions - completed_tasks) / completed_tasks if completed_tasks > 0 else 0.0,
            "avg_delivery_delay_days": avg_delay,
            "avg_submission_time_diff_hours": avg_time_diff,
            "late_submissions_count": late_submissions,
            "missing_tasks": total_tasks - completed_tasks,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks
        }

    def get_student_engagement_metrics(self, student_uuid: str, course_uuid: str) -> Dict[str, Any]:
        """Calcula métricas de participación del estudiante para un curso específico"""
        # Obtener interacciones con recursos del curso
        resource_interactions = self.session.query(CourseContent).join(
            Enrollment,
            and_(
                CourseContent.course_uuid == Enrollment.course_uuid
            )
        ).filter(
            Enrollment.student_uuid == student_uuid,
            CourseContent.course_uuid == course_uuid
        ).count()

        # Nota: Estas métricas requerirían datos adicionales que no están en los modelos actuales
        # Por ahora retornamos valores por defecto para algunas métricas
        return {
            "total_login_time_hours": 0.0,
            "classes_attended": 0,
            "classes_missed": 0,
            "last_login_days_ago": 0.0,
            "resource_interactions": resource_interactions
        }

    def get_student_mentorship_metrics(self, student_uuid: str, course_uuid: str) -> Dict[str, int]:
        """Calcula métricas relacionadas con la mentoría para un curso específico"""
        # Nota: Estas métricas requerirían datos adicionales que no están en los modelos actuales
        # Por ahora retornamos valores por defecto
        return {
            "mentor_sessions_count": 0,
            "mentor_total_words_exchanged": 0,
            "mentor_before_task_help": 0,
            "mentor_after_low_grade": 0
        }

    def get_student_data(self, student_uuid: str, course_uuid: str) -> Dict[str, Any]:
        """Obtiene todos los datos del estudiante para el modelo de predicción en un curso específico"""
        performance = self.get_student_performance_metrics(student_uuid, course_uuid)
        submission = self.get_student_submission_metrics(student_uuid, course_uuid)
        engagement = self.get_student_engagement_metrics(student_uuid, course_uuid)
        mentorship = self.get_student_mentorship_metrics(student_uuid, course_uuid)

        return {
            **performance,
            **submission,
            **engagement,
            **mentorship
        }

class ProcessService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = ProcessDataAccess(session)

    def process_student_prediction_data(self) -> None:
        try:
            all_enrollments = EnrollmentDataAccess(self.session).get_all_enrollments(all=True)

            for enrollment in all_enrollments:
                student_uuid = enrollment.student_uuid
                course_uuid = enrollment.course_uuid

                logger.info(f"Getting student prediction data for student {student_uuid} in course {course_uuid}")

                course_data = CourseDataAccess(self.session).get_course_by_uuid(course_uuid)

                student_data = StudentDataAccess(self.session).get_student_by_uuid(student_uuid)

                data = self.data_access.get_student_data(student_uuid, course_uuid)

                # Verifcamos si el usuario existe en el microservicio de users
                user_response = requests.patch(
                    f"{settings.API_AUTH_URL}/internal/users_services/get_or_create_user", 
                    json={
                        "email": str(student_data.email),
                        "full_name": f'{student_data.first_name} {student_data.last_name}',
                        "uuid": str(student_uuid)
                    },
                    headers={
                        "Content-Type": "application/json",
                        "X-HTTP-PURPOSE": "internal"
                    }
                )
                
                if user_response.status_code != 200:
                    logger.error(f"Error getting user: {user_response.text}")
                    continue

                # Construir la URL con los query params
                url = f"{settings.API_PREDICTION_URL}/process/predictions/process_student_data"
                params = {
                    "user_uuid": str(student_uuid),
                    "course_id": str(course_data.code)
                }
                
                # Enviar los datos en el body como JSON
                response = requests.post(
                    url,
                    params=params,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code != 200:
                    logger.error(f"Error processing student prediction data: {response.text}")
                    continue

            logger.info(f"End process")
        except Exception as e:
            logger.error(f"Error getting student prediction data: {e}")