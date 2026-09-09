from datetime import datetime
from pydantic import BaseModel


class NetworkEventResponse(BaseModel):
    id: str
    firmware_id: str
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    is_dns: bool
    dns_query: str
    http_destination: str
    is_simulated: bool
    captured_at: datetime

    class Config:
        from_attributes = True
