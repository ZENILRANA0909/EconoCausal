from pathlib import Path
from sqlalchemy.orm import Session
from app.models.firmware import Firmware
from app.models.analysis import ExtractionRecord, StaticFinding
from app.analyzers.architecture_detector import detect_architecture_for_file, detect_architecture_for_directory
from app.analyzers.static_analyzer import analyze_extracted_filesystem
from app.extraction.extraction_service import extract_firmware
from app.services.firmware_service import get_firmware_path


def run_extraction(db: Session, firmware: Firmware) -> ExtractionRecord:
    firmware_path = get_firmware_path(firmware)
    outcome = extract_firmware(firmware.id, firmware_path)

    record = ExtractionRecord(
        firmware_id=firmware.id,
        status=outcome.status,
        extracted_path=outcome.extracted_path,
        file_count=outcome.file_count,
        directory_count=outcome.directory_count,
        filesystem_type=outcome.filesystem_type,
        method=outcome.method,
        log_output=outcome.log_output,
    )
    db.add(record)

    firmware.extraction_status = outcome.status
    firmware.is_demo = firmware.is_demo or outcome.is_demo

    directory_arch = detect_architecture_for_directory(Path(outcome.extracted_path))
    if directory_arch.architecture != "unknown":
        firmware.architecture = directory_arch.architecture
        firmware.endianness = directory_arch.endianness
        firmware.binary_type = directory_arch.binary_type

    db.commit()
    db.refresh(record)
    return record


def run_static_analysis(db: Session, firmware: Firmware, extraction: ExtractionRecord):
    db.query(StaticFinding).filter(StaticFinding.firmware_id == firmware.id).delete()

    raw_findings = analyze_extracted_filesystem(Path(extraction.extracted_path))

    if firmware.architecture == "unknown":
        file_arch = detect_architecture_for_file(Path(extraction.extracted_path))
        if file_arch.architecture != "unknown":
            firmware.architecture = file_arch.architecture
            firmware.endianness = file_arch.endianness
            firmware.binary_type = file_arch.binary_type

    stored_findings = []
    for item in raw_findings:
        finding = StaticFinding(
            firmware_id=firmware.id,
            severity=item.get("severity", "LOW"),
            category=item.get("category", "general"),
            file_path=item.get("file_path", ""),
            finding=item.get("finding", ""),
            evidence=item.get("evidence", ""),
            recommendation=item.get("recommendation", ""),
        )
        db.add(finding)
        stored_findings.append(finding)

    firmware.analysis_status = "completed"
    db.commit()
    for finding in stored_findings:
        db.refresh(finding)
    return stored_findings


def get_static_findings(db: Session, firmware_id: str):
    return (
        db.query(StaticFinding)
        .filter(StaticFinding.firmware_id == firmware_id)
        .order_by(StaticFinding.created_at.desc())
        .all()
    )


def get_latest_extraction(db: Session, firmware_id: str):
    return (
        db.query(ExtractionRecord)
        .filter(ExtractionRecord.firmware_id == firmware_id)
        .order_by(ExtractionRecord.created_at.desc())
        .first()
    )
