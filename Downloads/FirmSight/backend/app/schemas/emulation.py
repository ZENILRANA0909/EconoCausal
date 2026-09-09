from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EmulateRequest(BaseModel):
    force_demo: bool = False


class EmulationResponse(BaseModel):
    id: str
    firmware_id: str
    mode: str
    qemu_binary: str
    status: str
    process_id: int
    is_demo: bool
    started_at: datetime
    stopped_at: Optional[datetime]
    output_log: str

    class Config:
        from_attributes = True
