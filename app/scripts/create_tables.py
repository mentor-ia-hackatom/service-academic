from app.utils.dataBase import Base, engine
from app.models.career_model import Career
from app.models.courses_model import Course
from app.models.periods_model import Period
from app.models.sections_model import Section
from app.models.students_model import Student
from app.models.enrollments_model import Enrollment
from app.models.assignments_model import Assignment
from app.models.submissions_model import Submission
from app.models.content_model import Content
from app.models.course_content import CourseContent
from app.models.course_sections_model import CourseSection

def create_tables():
    print("Eliminando tablas existentes...")
    Base.metadata.drop_all(bind=engine)
    print("Tablas eliminadas.")
    
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("¡Tablas creadas exitosamente!")

if __name__ == "__main__":
    create_tables() 