import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.firmware import Firmware
from app.services.analysis_service import get_static_findings, get_latest_extraction
from app.services.network_service import get_network_events
from app.services.threat_service import get_latest_threat_assessment, compute_and_store_threat_assessment

RECOMMENDATION_LIBRARY = {
    "credential_exposure": "Remove hardcoded credentials and private keys; use secure provisioning at manufacture time.",
    "credential_file": "Avoid shipping default password databases; enforce unique per-device credentials.",
    "network_service": "Disable unused network services such as Telnet/FTP; prefer encrypted management protocols.",
    "network_tool": "Review why network retrieval tools are bundled; restrict outbound connectivity where possible.",
    "reverse_shell": "Investigate immediately; this pattern strongly resembles a backdoor mechanism.",
    "backdoor_indicator": "Investigate immediately; string suggests an intentional backdoor mechanism.",
    "hardcoded_ip": "Confirm hardcoded network endpoints are legitimate and documented.",
    "hardcoded_url": "Confirm hardcoded URLs are legitimate, expected, and use HTTPS.",
    "permissions": "Avoid overly permissive file modes; apply least-privilege permissions.",
    "toolkit": "No action required unless BusyBox applets expose unnecessary attack surface.",
    "shell_reference": "No action required unless shell access is unintentionally exposed externally.",
}


def build_report(db: Session, firmware: Firmware) -> dict:
    extraction = get_latest_extraction(db, firmware.id)
    findings = get_static_findings(db, firmware.id)
    network_events = get_network_events(db, firmware.id)

    assessment = get_latest_threat_assessment(db, firmware.id)
    if assessment is None:
        assessment = compute_and_store_threat_assessment(db, firmware)

    categories_present = {item.category for item in findings}
    recommendations = [
        RECOMMENDATION_LIBRARY[category]
        for category in categories_present
        if category in RECOMMENDATION_LIBRARY
    ]
    if not recommendations:
        recommendations.append("No specific remediation required based on current findings.")

    return {
        "firmware_id": firmware.id,
        "filename": firmware.filename,
        "sha256": firmware.sha256,
        "file_size_bytes": firmware.file_size_bytes,
        "architecture": firmware.architecture,
        "filesystem_type": extraction.filesystem_type if extraction else "unknown",
        "extraction_status": firmware.extraction_status,
        "file_count": extraction.file_count if extraction else 0,
        "static_findings_count": len(findings),
        "network_events_count": len(network_events),
        "threat_score": assessment.score,
        "threat_level": assessment.level,
        "threat_reasons": json.loads(assessment.reasons),
        "recommendations": recommendations,
        "is_demo": firmware.is_demo,
        "generated_at": datetime.utcnow(),
    }
