from sqlalchemy import Column, String, BigInteger, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class CourseContent(Base):
    __tablename__ = "course_contents"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_uuid = Column(UUID(as_uuid=True), ForeignKey("courses.uuid"), nullable=False)
    content_uuid = Column(UUID(as_uuid=True), ForeignKey("contents.uuid"), nullable=False)
    assignment_uuid = Column(UUID(as_uuid=True), ForeignKey("assignments.uuid"), nullable=True)
    order = Column(BigInteger, default=0)  # Para ordenar el contenido dentro de un curso
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())

    # Relaciones
    course = relationship("Course", back_populates="course_contents")
    content = relationship("Content", back_populates="course_contents")
    assignment = relationship("Assignment", back_populates="course_contents")
