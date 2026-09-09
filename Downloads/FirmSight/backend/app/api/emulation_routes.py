from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.storage.database import get_db
from app.schemas.emulation import EmulateRequest, EmulationResponse
from app.services.firmware_service import get_firmware_or_none
from app.services.emulation_service import (
    start_emulation_session,
    stop_emulation_session,
    get_latest_emulation,
    refresh_emulation_status,
)
from app.services.activity_service import log_activity
from app.config.logging_config import logger

router = APIRouter(prefix="/firmware", tags=["emulation"])


@router.post("/{firmware_id}/emulate", response_model=EmulationResponse)
def emulate_firmware(firmware_id: str, request: EmulateRequest, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    session = start_emulation_session(db, firmware_record, force_demo=request.force_demo)
    logger.info(f"Emulation started for {firmware_id}: mode={session.mode} demo={session.is_demo}")
    log_activity(db, "emulation", f"Emulation started (mode={session.mode})", firmware_id)
    return EmulationResponse.model_validate(session)


@router.post("/{firmware_id}/stop", response_model=EmulationResponse)
def stop_firmware_emulation(firmware_id: str, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    session = get_latest_emulation(db, firmware_id)
    if session is None:
        raise HTTPException(status_code=400, detail="No emulation session found for this firmware")

    session = stop_emulation_session(db, session)
    logger.info(f"Emulation stopped for {firmware_id}")
    log_activity(db, "emulation", "Emulation stopped", firmware_id)
    return EmulationResponse.model_validate(session)


@router.get("/{firmware_id}/emulation-status", response_model=EmulationResponse)
def emulation_status(firmware_id: str, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    session = get_latest_emulation(db, firmware_id)
    if session is None:
        raise HTTPException(status_code=404, detail="No emulation session found for this firmware")

    session = refresh_emulation_status(db, session)
    return EmulationResponse.model_validate(session)
