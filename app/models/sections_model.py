from sqlalchemy import Column, String, BigInteger, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class Section(Base):
    __tablename__ = "sections"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    section_code = Column(String, nullable=False)
    description = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())

    # Relaciones
    course_sections = relationship("CourseSection", back_populates="section")
    enrollments = relationship("Enrollment", back_populates="section")
    assignments = relationship("Assignment", back_populates="section")
