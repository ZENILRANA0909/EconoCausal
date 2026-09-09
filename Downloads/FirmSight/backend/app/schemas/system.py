from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel


class ToolStatusResponse(BaseModel):
    name: str
    available: bool
    path: str
    install_hint: str


class SystemInfoResponse(BaseModel):
    system: str
    release: str
    machine: str
    python_version: str
    demo_mode_recommended: bool


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    timestamp: datetime


class ActivityItem(BaseModel):
    id: str
    event_type: str
    message: str
    firmware_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    firmware_id: str
    filename: str
    sha256: str
    file_size_bytes: int
    architecture: str
    filesystem_type: str
    extraction_status: str
    file_count: int
    static_findings_count: int
    network_events_count: int
    threat_score: int
    threat_level: str
    threat_reasons: List[str]
    recommendations: List[str]
    is_demo: bool
    generated_at: datetime
