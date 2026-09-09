from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FirmwareResponse(BaseModel):
    id: str
    filename: str
    file_size_bytes: int
    sha256: str
    architecture: str
    endianness: str
    binary_type: str
    is_demo: bool
    extraction_status: str
    analysis_status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class FirmwareUploadResponse(BaseModel):
    firmware: FirmwareResponse
    message: str


class FirmwareListItem(BaseModel):
    id: str
    filename: str
    file_size_bytes: int
    architecture: str
    extraction_status: str
    analysis_status: str
    is_demo: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True
