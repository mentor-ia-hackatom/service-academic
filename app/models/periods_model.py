from sqlalchemy import Column, String, BigInteger, Date
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.utils.dataBase import Base

class Period(Base):
    __tablename__ = "periods"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp())
    updated_at = Column(BigInteger, default=datetime.now(timezone.utc).timestamp(), onupdate=datetime.now(timezone.utc).timestamp())
