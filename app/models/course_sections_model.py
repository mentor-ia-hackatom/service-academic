from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class CourseSection(Base):
    __tablename__ = "course_sections"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_uuid = Column(UUID(as_uuid=True), ForeignKey("courses.uuid"), nullable=False)
    section_uuid = Column(UUID(as_uuid=True), ForeignKey("sections.uuid"), nullable=False)
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())

    # Relaciones
    course = relationship("Course", back_populates="course_sections")
    section = relationship("Section", back_populates="course_sections")
