from sqlalchemy import Column, String, BigInteger, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class Assignment(Base):
    __tablename__ = "assignments"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_uuid = Column(UUID(as_uuid=True), ForeignKey("courses.uuid"))
    section_uuid = Column(UUID(as_uuid=True), ForeignKey("sections.uuid"))
    title = Column(String, nullable=False)
    description = Column(Text)
    due_date = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())

    # Relaciones
    course = relationship("Course", back_populates="assignments")
    section = relationship("Section", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")
    course_contents = relationship("CourseContent", back_populates="assignment")
