from sqlalchemy import Column, String, BigInteger
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class Career(Base):
    __tablename__ = "careers"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())

    # Relaciones
    courses = relationship("Course", back_populates="career")
