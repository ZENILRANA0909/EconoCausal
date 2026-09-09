import pytest
from app.services.firmware_service import FirmwareValidationError, validate_upload


class FakeUploadFile:
    def __init__(self, filename):
        self.filename = filename


def test_validate_upload_rejects_bad_extension():
    with pytest.raises(FirmwareValidationError):
        validate_upload(FakeUploadFile("malware.exe"), 100)


def test_validate_upload_rejects_empty_file():
    with pytest.raises(FirmwareValidationError):
        validate_upload(FakeUploadFile("firmware.bin"), 0)


def test_validate_upload_rejects_oversized_file():
    from app.config.settings import settings
    oversized = (settings.max_upload_size_mb * 1024 * 1024) + 1
    with pytest.raises(FirmwareValidationError):
        validate_upload(FakeUploadFile("firmware.bin"), oversized)


def test_validate_upload_accepts_valid_bin_file():
    validate_upload(FakeUploadFile("firmware.bin"), 1024)


def test_upload_endpoint_returns_firmware_record(client, sample_firmware_bytes):
    response = client.post(
        "/api/firmware/upload",
        files={"file": ("router_fw.bin", sample_firmware_bytes, "application/octet-stream")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["firmware"]["filename"] == "router_fw.bin"
    assert len(body["firmware"]["sha256"]) == 64


def test_upload_endpoint_rejects_invalid_extension(client):
    response = client.post(
        "/api/firmware/upload",
        files={"file": ("payload.exe", b"not real firmware", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_get_firmware_by_id(client, uploaded_firmware_id):
    response = client.get(f"/api/firmware/{uploaded_firmware_id}")
    assert response.status_code == 200
    assert response.json()["id"] == uploaded_firmware_id


def test_get_firmware_not_found(client):
    response = client.get("/api/firmware/does-not-exist")
    assert response.status_code == 404


def test_list_firmware(client, uploaded_firmware_id):
    response = client.get("/api/firmware")
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()]
    assert uploaded_firmware_id in ids
