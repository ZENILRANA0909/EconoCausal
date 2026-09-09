from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from app.storage.database import Base
from app.models.firmware import generate_id


class ExtractionRecord(Base):
    __tablename__ = "extraction_records"

    id = Column(String, primary_key=True, default=generate_id)
    firmware_id = Column(String, ForeignKey("firmware.id"), nullable=False, index=True)
    status = Column(String, default="pending")
    extracted_path = Column(String, default="")
    file_count = Column(Integer, default=0)
    directory_count = Column(Integer, default=0)
    filesystem_type = Column(String, default="unknown")
    method = Column(String, default="binwalk")
    log_output = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class StaticFinding(Base):
    __tablename__ = "static_findings"

    id = Column(String, primary_key=True, default=generate_id)
    firmware_id = Column(String, ForeignKey("firmware.id"), nullable=False, index=True)
    severity = Column(String, default="LOW")
    category = Column(String, default="general")
    file_path = Column(String, default="")
    finding = Column(String, default="")
    evidence = Column(Text, default="")
    recommendation = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
