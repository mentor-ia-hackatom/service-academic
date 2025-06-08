from sqlalchemy import Column, BigInteger, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class EnrollmentStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"

class Enrollment(Base):
    __tablename__ = "enrollments"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_uuid = Column(UUID(as_uuid=True), ForeignKey("students.uuid"))
    course_uuid = Column(UUID(as_uuid=True), ForeignKey("courses.uuid"))
    section_uuid = Column(UUID(as_uuid=True), ForeignKey("sections.uuid"))
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())

    # Relaciones
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    section = relationship("Section", back_populates="enrollments")
