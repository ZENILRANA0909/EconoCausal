import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.storage.database import get_db
from app.schemas.threat import ThreatAssessmentResponse
from app.schemas.system import ReportResponse
from app.services.firmware_service import get_firmware_or_none
from app.services.threat_service import compute_and_store_threat_assessment
from app.services.report_service import build_report
from app.services.activity_service import log_activity
from app.config.logging_config import logger

router = APIRouter(prefix="/firmware", tags=["threats"])


@router.get("/{firmware_id}/threats", response_model=ThreatAssessmentResponse)
def get_threat_assessment(firmware_id: str, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    assessment = compute_and_store_threat_assessment(db, firmware_record)
    logger.info(f"Threat assessment for {firmware_id}: {assessment.level} ({assessment.score})")
    log_activity(db, "threat_detection", f"Threat level {assessment.level} ({assessment.score}/100)", firmware_id)

    return ThreatAssessmentResponse(
        firmware_id=firmware_id,
        score=assessment.score,
        level=assessment.level,
        reasons=json.loads(assessment.reasons),
        created_at=assessment.created_at,
    )


@router.get("/{firmware_id}/report", response_model=ReportResponse)
def get_security_report(firmware_id: str, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    report = build_report(db, firmware_record)
    log_activity(db, "report", "Security report generated", firmware_id)
    return ReportResponse(**report)
