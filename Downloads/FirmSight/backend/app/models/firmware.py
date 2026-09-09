import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from app.storage.database import Base


def generate_id() -> str:
    return uuid.uuid4().hex[:12]


class Firmware(Base):
    __tablename__ = "firmware"

    id = Column(String, primary_key=True, default=generate_id)
    filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    sha256 = Column(String, nullable=False, index=True)
    architecture = Column(String, default="unknown")
    endianness = Column(String, default="unknown")
    binary_type = Column(String, default="unknown")
    is_demo = Column(Boolean, default=False)
    extraction_status = Column(String, default="pending")
    analysis_status = Column(String, default="pending")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
