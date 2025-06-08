from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class Course(Base):
    __tablename__ = "courses"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    career_uuid = Column(UUID(as_uuid=True), ForeignKey("careers.uuid"))
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())

    # Relaciones
    career = relationship("Career", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")
    course_sections = relationship("CourseSection", back_populates="course")
    course_contents = relationship("CourseContent", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")
