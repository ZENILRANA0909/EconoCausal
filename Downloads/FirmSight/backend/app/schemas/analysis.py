from datetime import datetime
from typing import List
from pydantic import BaseModel


class ExtractedFileEntry(BaseModel):
    path: str
    file_type: str
    size_bytes: int
    is_interesting: bool


class ExtractionResponse(BaseModel):
    id: str
    firmware_id: str
    status: str
    extracted_path: str
    file_count: int
    directory_count: int
    filesystem_type: str
    method: str
    created_at: datetime

    class Config:
        from_attributes = True


class FileTreeNode(BaseModel):
    name: str
    path: str
    is_directory: bool
    size_bytes: int = 0
    children: List["FileTreeNode"] = []


FileTreeNode.model_rebuild()


class StaticFindingResponse(BaseModel):
    id: str
    firmware_id: str
    severity: str
    category: str
    file_path: str
    finding: str
    evidence: str
    recommendation: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    force_demo: bool = False


class AnalyzeResponse(BaseModel):
    firmware_id: str
    architecture: str
    endianness: str
    binary_type: str
    findings_count: int
    is_demo: bool
    message: str
