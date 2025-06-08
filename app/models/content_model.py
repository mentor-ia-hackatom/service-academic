from sqlalchemy import Column, String, BigInteger, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class Content(Base):
    __tablename__ = "contents"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, doc, xlsx, txt, etc.
    file_size = Column(BigInteger)  # tamaño en bytes
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())

    # Relaciones
    course_contents = relationship("CourseContent", back_populates="content")
