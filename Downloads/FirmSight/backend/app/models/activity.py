from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.storage.database import Base
from app.models.firmware import generate_id


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(String, primary_key=True, default=generate_id)
    event_type = Column(String, default="info")
    message = Column(String, default="")
    firmware_id = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
