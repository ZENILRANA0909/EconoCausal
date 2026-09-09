from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.storage.database import get_db
from app.schemas.network import NetworkEventResponse
from app.services.firmware_service import get_firmware_or_none
from app.services.network_service import generate_network_events_for_firmware, get_network_events
from app.services.activity_service import log_activity
from app.config.logging_config import logger

router = APIRouter(prefix="/firmware", tags=["network"])


@router.get("/{firmware_id}/network", response_model=list[NetworkEventResponse])
def get_network_activity(firmware_id: str, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")

    events = get_network_events(db, firmware_id)
    if not events:
        events = generate_network_events_for_firmware(db, firmware_record)
        logger.info(f"Generated {len(events)} simulated network events for {firmware_id}")
        log_activity(db, "network", f"Captured {len(events)} network events (simulated)", firmware_id)

    return [NetworkEventResponse.model_validate(item) for item in events]
