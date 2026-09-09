import json
from sqlalchemy.orm import Session
from app.models.firmware import Firmware
from app.models.threat import ThreatAssessment
from app.detection.threat_scoring import calculate_threat_assessment
from app.services.analysis_service import get_static_findings
from app.services.network_service import get_network_events


def compute_and_store_threat_assessment(db: Session, firmware: Firmware) -> ThreatAssessment:
    findings = get_static_findings(db, firmware.id)
    network_events = get_network_events(db, firmware.id)

    findings_as_dicts = [{"severity": item.severity} for item in findings]
    network_as_dicts = [{"destination_port": item.destination_port} for item in network_events]

    score, level, reasons = calculate_threat_assessment(findings_as_dicts, network_as_dicts)

    db.query(ThreatAssessment).filter(ThreatAssessment.firmware_id == firmware.id).delete()
    assessment = ThreatAssessment(
        firmware_id=firmware.id,
        score=score,
        level=level,
        reasons=json.dumps(reasons),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_latest_threat_assessment(db: Session, firmware_id: str):
    return (
        db.query(ThreatAssessment)
        .filter(ThreatAssessment.firmware_id == firmware_id)
        .order_by(ThreatAssessment.created_at.desc())
        .first()
    )
