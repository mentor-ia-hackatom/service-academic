from sqlalchemy import Column, String, BigInteger, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class Submission(Base):
    __tablename__ = "submissions"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_uuid = Column(UUID(as_uuid=True), ForeignKey("assignments.uuid"))
    student_uuid = Column(UUID(as_uuid=True), ForeignKey("students.uuid"))
    content = Column(Text)
    grade = Column(Float)
    feedback = Column(Text)
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())

    # Relaciones
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")
