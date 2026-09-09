from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.storage.database import get_db
from app.schemas.analysis import ExtractionResponse, StaticFindingResponse, AnalyzeRequest, AnalyzeResponse, FileTreeNode
from app.services.firmware_service import get_firmware_or_none
from app.services.analysis_service import run_extraction, run_static_analysis, get_static_findings, get_latest_extraction
from app.services.filesystem_service import build_file_tree, get_file_metadata
from app.services.activity_service import log_activity
from app.config.logging_config import logger
from pathlib import Path

router = APIRouter(prefix="/firmware", tags=["analysis"])


@router.post("/{firmware_id}/extract", response_model=ExtractionResponse)
def extract_firmware_endpoint(firmware_id: str, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    extraction = run_extraction(db, firmware_record)
    logger.info(f"Extraction completed for {firmware_id}: {extraction.file_count} files")
    log_activity(db, "extraction", f"Extraction completed with {extraction.file_count} files", firmware_id)
    return ExtractionResponse.model_validate(extraction)


@router.post("/{firmware_id}/analyze", response_model=AnalyzeResponse)
def analyze_firmware_endpoint(firmware_id: str, request: AnalyzeRequest, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    extraction = get_latest_extraction(db, firmware_id)
    if extraction is None:
        extraction = run_extraction(db, firmware_record)

    findings = run_static_analysis(db, firmware_record, extraction)
    logger.info(f"Static analysis completed for {firmware_id}: {len(findings)} findings")
    log_activity(db, "analysis", f"Static analysis found {len(findings)} indicators", firmware_id)

    return AnalyzeResponse(
        firmware_id=firmware_id,
        architecture=firmware_record.architecture,
        endianness=firmware_record.endianness,
        binary_type=firmware_record.binary_type,
        findings_count=len(findings),
        is_demo=firmware_record.is_demo,
        message="Static analysis completed",
    )


@router.get("/{firmware_id}/files", response_model=FileTreeNode)
def get_filesystem_tree(firmware_id: str, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    extraction = get_latest_extraction(db, firmware_id)
    if extraction is None:
        raise HTTPException(status_code=400, detail="Firmware has not been extracted yet")

    tree = build_file_tree(Path(extraction.extracted_path))
    return tree


@router.get("/{firmware_id}/findings", response_model=list[StaticFindingResponse])
def get_findings(firmware_id: str, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    findings = get_static_findings(db, firmware_id)
    return [StaticFindingResponse.model_validate(item) for item in findings]
