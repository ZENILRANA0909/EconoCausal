from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from app.storage.database import Base
from app.models.firmware import generate_id


class ThreatAssessment(Base):
    __tablename__ = "threat_assessments"

    id = Column(String, primary_key=True, default=generate_id)
    firmware_id = Column(String, ForeignKey("firmware.id"), nullable=False, index=True)
    score = Column(Integer, default=0)
    level = Column(String, default="LOW")
    reasons = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
