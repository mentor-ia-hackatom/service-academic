from datetime import datetime, timezone
from app.utils.dataBase import SessionLocal
from app.models.career_model import Career
from app.models.courses_model import Course
from app.models.periods_model import Period
from app.models.sections_model import Section
from app.models.students_model import Student
from app.models.enrollments_model import Enrollment, EnrollmentStatus
from app.models.assignments_model import Assignment
from app.models.submissions_model import Submission
from app.models.content_model import Content
from app.models.course_content import CourseContent
from app.models.course_sections_model import CourseSection
import random

def seed_data():
    db = SessionLocal()
    try:
        # Create technological careers
        career1 = Career(
            name="Ingeniería en Software",
            code="ISW-001",
            description="Carrera enfocada en desarrollo de software y aplicaciones"
        )
        career2 = Career(
            name="Ingeniería en Inteligencia Artificial",
            code="IAI-001",
            description="Carrera especializada en IA, machine learning y data science"
        )
        db.add_all([career1, career2])
        db.commit()

        # Create courses for Software Engineering
        courses_sw = [
            Course(
                name="Desarrollo Web Full Stack",
                code="DWS-101",
                description="Desarrollo de aplicaciones web completas",
                career_uuid=career1.uuid
            ),
            Course(
                name="Arquitectura de Software",
                code="ARS-201",
                description="Diseño y arquitectura de sistemas software",
                career_uuid=career1.uuid
            ),
            Course(
                name="DevOps y Cloud Computing",
                code="DCC-301",
                description="Despliegue y operación de aplicaciones en la nube",
                career_uuid=career1.uuid
            ),
            Course(
                name="Desarrollo Móvil",
                code="DMO-401",
                description="Desarrollo de aplicaciones móviles",
                career_uuid=career1.uuid
            )
        ]

        # Create courses for Artificial Intelligence
        courses_ai = [
            Course(
                name="Machine Learning",
                code="ML-101",
                description="Fundamentos de machine learning",
                career_uuid=career2.uuid
            ),
            Course(
                name="Deep Learning",
                code="DL-201",
                description="Redes neuronales y deep learning",
                career_uuid=career2.uuid
            ),
            Course(
                name="Procesamiento de Lenguaje Natural",
                code="NLP-301",
                description="Análisis y procesamiento de texto",
                career_uuid=career2.uuid
            ),
            Course(
                name="Computer Vision",
                code="CV-401",
                description="Procesamiento y análisis de imágenes",
                career_uuid=career2.uuid
            )
        ]

        db.add_all(courses_sw + courses_ai)
        db.commit()

        # Create period
        period = Period(
            name="2024-1",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 6, 30)
        )
        db.add(period)
        db.commit()

        # Create sections and associate them with courses
        course_sections = []
        for course in courses_sw + courses_ai:
            section = Section(
                name="Main Section",
                section_code=f"{course.code}-001",
                description=f"Sección principal del curso {course.name}",
                capacity=30
            )
            db.add(section)
            db.flush()  # Para obtener el UUID de la sección
            
            course_section = CourseSection(
                course_uuid=course.uuid,
                section_uuid=section.uuid
            )
            course_sections.append(course_section)
        
        db.add_all(course_sections)
        db.commit()

        # Create students
        students = []
        first_names = ["Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Miguel", "Sofía", "Diego", "Valentina",
                      "Andrés", "Camila", "José", "Isabella", "Fernando", "Lucía", "Ricardo", "Mariana", "Alejandro", "Gabriela"]
        last_names = ["Pérez", "González", "Rodríguez", "Martínez", "López", "García", "Hernández", "Díaz", "Torres", "Ramírez"]

        for i in range(20):
            student = Student(
                first_name=first_names[i],
                last_name=last_names[i % 10],
                email=f"{first_names[i].lower()}.{last_names[i % 10].lower()}@example.com"
            )
            students.append(student)
        db.add_all(students)
        db.commit()

        # Create enrollments
        enrollments = []
        for student in students:
            # Each student enrolls in 2 random courses
            random_courses = random.sample(courses_sw + courses_ai, 2)
            for course in random_courses:
                # Get the section for this course
                course_section = next(cs for cs in course_sections if cs.course_uuid == course.uuid)
                enrollment = Enrollment(
                    student_uuid=student.uuid,
                    course_uuid=course.uuid,
                    section_uuid=course_section.section_uuid,
                    status=EnrollmentStatus.ACTIVE
                )
                enrollments.append(enrollment)
        db.add_all(enrollments)
        db.commit()

        # Create assignments for each course
        assignments = []
        for course in courses_sw + courses_ai:
            # Get the section for this course
            course_section = next(cs for cs in course_sections if cs.course_uuid == course.uuid)
            for i in range(4):  # 4 assignments per course
                assignment = Assignment(
                    course_uuid=course.uuid,
                    section_uuid=course_section.section_uuid,
                    title=f"Assignment {i+1}: {course.name}",
                    description=f"Detailed description of assignment {i+1} for {course.name}",
                    due_date=int(datetime(2024, 3 + i, 15, tzinfo=timezone.utc).timestamp())
                )
                assignments.append(assignment)
        db.add_all(assignments)
        db.commit()

        # Create varied submissions
        submissions = []
        for assignment in assignments:
            # Get students enrolled in the course
            enrolled_students = [e.student_uuid for e in enrollments if e.course_uuid == assignment.course_uuid]
            
            for student_uuid in enrolled_students:
                # 70% probability that the student has submitted
                if random.random() < 0.7:
                    # 80% probability of having a grade
                    has_grade = random.random() < 0.8
                    grade = round(random.uniform(6.0, 10.0), 1) if has_grade else None
                    
                    submission = Submission(
                        assignment_uuid=assignment.uuid,
                        student_uuid=student_uuid,
                        content=f"Submission content for {assignment.title}",
                        grade=grade,
                        feedback="Good work!" if grade and grade >= 8.0 else "Needs improvement" if grade else None
                    )
                    submissions.append(submission)
        
        db.add_all(submissions)
        db.commit()

        # Create example content
        contents = [
            # Web Development
            Content(
                title="React Documentation",
                description="Official React.js documentation",
                file_url="https://react.dev/learn/installation",
                file_type="web",
                file_size=0
            ),
            Content(
                title="Node.js Documentation",
                description="Official Node.js documentation",
                file_url="https://nodejs.org/docs/latest/api/synopsis.html",
                file_type="web",
                file_size=0
            ),
            Content(
                title="Docker Documentation",
                description="Complete Docker guide",
                file_url="https://docs.docker.com/get-started/introduction/develop-with-containers/",
                file_type="web",
                file_size=0
            ),
            # Machine Learning
            Content(
                title="TensorFlow Tutorials",
                description="Official TensorFlow tutorials",
                file_url="https://www.tensorflow.org/tutorials/quickstart/beginner?hl=es-419",
                file_type="web",
                file_size=0
            ),
            Content(
                title="PyTorch Documentation",
                description="Official PyTorch documentation",
                file_url="https://docs.pytorch.org/docs/stable/community/design.html",
                file_type="web",
                file_size=0
            ),
            Content(
                title="Scikit-learn User Guide",
                description="Scikit-learn user guide",
                file_url="https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares",
                file_type="web",
                file_size=0
            ),
            # Mobile Development
            Content(
                title="Flutter Documentation",
                description="Official Flutter documentation",
                file_url="https://docs.flutter.dev/ui",
                file_type="web",
                file_size=0
            ),
            Content(
                title="React Native Guide",
                description="React Native guide",
                file_url="https://reactnative.dev/docs/getting-started",
                file_type="web",
                file_size=0
            ),
            # DevOps
            Content(
                title="Kubernetes Documentation",
                description="Official Kubernetes documentation",
                file_url="https://kubernetes.io/docs/concepts/",
                file_type="web",
                file_size=0
            ),
            Content(
                title="AWS - S3 Documentation",
                description="Amazon Web Services documentation",
                file_url="https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-userguide.pdf",
                file_type="pdf",
                file_size=1024000
            )
        ]
        db.add_all(contents)
        db.commit()

        # Associate content with courses
        course_contents = []
        for course in courses_sw + courses_ai:
            # Select relevant content based on the course
            relevant_contents = []
            if "Web" in course.name:
                relevant_contents = [contents[0], contents[1], contents[2]]  # React, Node.js, Docker
            elif "Machine Learning" in course.name:
                relevant_contents = [contents[3], contents[4], contents[5]]  # TensorFlow, PyTorch, Scikit-learn
            elif "Móvil" in course.name:
                relevant_contents = [contents[6], contents[7]]  # Flutter, React Native
            elif "DevOps" in course.name:
                relevant_contents = [contents[8], contents[9]]  # Kubernetes, AWS
            else:
                # For other courses, assign random content
                relevant_contents = random.sample(contents, 2)

            for i, content in enumerate(relevant_contents):
                course_content = CourseContent(
                    course_uuid=course.uuid,
                    content_uuid=content.uuid,
                    order=i
                )
                course_contents.append(course_content)

        db.add_all(course_contents)
        db.commit()

        # Associate content with some assignments
        for assignment in assignments:
            # 30% probability that the assignment has associated content
            if random.random() < 0.3:
                # Get relevant content for the course
                relevant_contents = [cc for cc in course_contents if cc.course_uuid == assignment.course_uuid]
                if relevant_contents:
                    selected_content = random.choice(relevant_contents)
                    course_content = CourseContent(
                        course_uuid=assignment.course_uuid,
                        content_uuid=selected_content.content_uuid,
                        assignment_uuid=assignment.uuid,
                        order=0
                    )
                    db.add(course_content)
        
        db.commit()

        print("Sample data inserted successfully!")
        print(f"Created:")
        print(f"- 2 careers")
        print(f"- 8 courses (4 per career)")
        print(f"- 8 sections")
        print(f"- 20 students")
        print(f"- {len(enrollments)} enrollments")
        print(f"- {len(assignments)} assignments")
        print(f"- {len(submissions)} submissions")
        print(f"- {len(contents)} contents")
        print(f"- {len(course_contents)} course-content relationships")

    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data() 