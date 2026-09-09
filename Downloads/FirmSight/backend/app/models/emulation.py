from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from app.storage.database import Base
from app.models.firmware import generate_id


class EmulationSession(Base):
    __tablename__ = "emulation_sessions"

    id = Column(String, primary_key=True, default=generate_id)
    firmware_id = Column(String, ForeignKey("firmware.id"), nullable=False, index=True)
    mode = Column(String, default="unsupported")
    qemu_binary = Column(String, default="")
    status = Column(String, default="stopped")
    process_id = Column(Integer, default=0)
    is_demo = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    output_log = Column(String, default="")
