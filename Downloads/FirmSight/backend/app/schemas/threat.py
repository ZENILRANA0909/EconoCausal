from datetime import datetime
from typing import List
from pydantic import BaseModel


class ThreatAssessmentResponse(BaseModel):
    firmware_id: str
    score: int
    level: str
    reasons: List[str]
    created_at: datetime
