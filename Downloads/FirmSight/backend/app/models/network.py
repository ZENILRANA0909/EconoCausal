from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from app.storage.database import Base
from app.models.firmware import generate_id


class NetworkEvent(Base):
    __tablename__ = "network_events"

    id = Column(String, primary_key=True, default=generate_id)
    firmware_id = Column(String, ForeignKey("firmware.id"), nullable=False, index=True)
    source_ip = Column(String, default="")
    destination_ip = Column(String, default="")
    source_port = Column(Integer, default=0)
    destination_port = Column(Integer, default=0)
    protocol = Column(String, default="")
    is_dns = Column(Boolean, default=False)
    dns_query = Column(String, default="")
    http_destination = Column(String, default="")
    is_simulated = Column(Boolean, default=True)
    captured_at = Column(DateTime, default=datetime.utcnow)
