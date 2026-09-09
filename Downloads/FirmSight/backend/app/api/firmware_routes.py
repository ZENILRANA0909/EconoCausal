from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.storage.database import get_db
from app.schemas.firmware import FirmwareResponse, FirmwareUploadResponse, FirmwareListItem
from app.services.firmware_service import save_uploaded_firmware, get_firmware_or_none, list_all_firmware, FirmwareValidationError
from app.services.activity_service import log_activity
from app.config.logging_config import logger

router = APIRouter(prefix="/firmware", tags=["firmware"])


@router.post("/upload", response_model=FirmwareUploadResponse)
async def upload_firmware(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw_bytes = await file.read()
    try:
        firmware_record = save_uploaded_firmware(db, file, raw_bytes)
    except FirmwareValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    logger.info(f"Firmware uploaded: {firmware_record.id} ({firmware_record.filename})")
    log_activity(db, "upload", f"Firmware '{firmware_record.filename}' uploaded", firmware_record.id)

    return FirmwareUploadResponse(
        firmware=FirmwareResponse.model_validate(firmware_record),
        message="Firmware uploaded successfully",
    )


@router.get("", response_model=list[FirmwareListItem])
def list_firmware(db: Session = Depends(get_db)):
    records = list_all_firmware(db)
    return [FirmwareListItem.model_validate(record) for record in records]


@router.get("/{firmware_id}", response_model=FirmwareResponse)
def get_firmware(firmware_id: str, db: Session = Depends(get_db)):
    firmware_record = get_firmware_or_none(db, firmware_id)
    if firmware_record is None:
        raise HTTPException(status_code=404, detail="Firmware not found")
    return FirmwareResponse.model_validate(firmware_record)
