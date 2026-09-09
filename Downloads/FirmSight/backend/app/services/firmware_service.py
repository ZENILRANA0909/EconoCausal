from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.firmware import Firmware
from app.utils.hashing import sha256_of_file
from app.utils.path_safety import safe_filename


class FirmwareValidationError(Exception):
    pass


def validate_upload(file: UploadFile, size_bytes: int) -> None:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in settings.allowed_upload_extensions:
        raise FirmwareValidationError(
            f"Unsupported file extension '{extension}'. Allowed: {', '.join(settings.allowed_upload_extensions)}"
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise FirmwareValidationError(
            f"File exceeds maximum allowed size of {settings.max_upload_size_mb}MB"
        )

    if size_bytes == 0:
        raise FirmwareValidationError("Uploaded file is empty")


def save_uploaded_firmware(db: Session, file: UploadFile, raw_bytes: bytes) -> Firmware:
    validate_upload(file, len(raw_bytes))

    cleaned_name = safe_filename(file.filename or "firmware.bin")
    firmware_record = Firmware(
        filename=cleaned_name,
        stored_filename="",
        file_size_bytes=len(raw_bytes),
        sha256="",
    )
    db.add(firmware_record)
    db.flush()

    stored_filename = f"{firmware_record.id}_{cleaned_name}"
    destination_path = settings.uploads_dir / stored_filename
    destination_path.write_bytes(raw_bytes)

    firmware_record.stored_filename = stored_filename
    firmware_record.sha256 = sha256_of_file(destination_path)
    db.commit()
    db.refresh(firmware_record)
    return firmware_record


def get_firmware_path(firmware: Firmware) -> Path:
    return settings.uploads_dir / firmware.stored_filename


def get_firmware_or_none(db: Session, firmware_id: str) -> Optional[Firmware]:
    return db.query(Firmware).filter(Firmware.id == firmware_id).first()


def list_all_firmware(db: Session):
    return db.query(Firmware).order_by(Firmware.uploaded_at.desc()).all()
