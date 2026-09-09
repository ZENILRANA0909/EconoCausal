import os
import shutil
import tempfile
import pytest
from pathlib import Path

os.environ["FIRMSIGHT_ENV"] = "test"

TEST_ROOT = Path(tempfile.mkdtemp(prefix="firmsight_test_"))
os.environ["FIRMSIGHT_DATABASE_URL"] = f"sqlite:///{TEST_ROOT / 'test.db'}"

from app.config.settings import settings

settings.data_dir = TEST_ROOT / "data"
settings.uploads_dir = TEST_ROOT / "data" / "uploads"
settings.extracted_dir = TEST_ROOT / "data" / "extracted"
settings.pcap_dir = TEST_ROOT / "data" / "pcap"
settings.reports_dir = TEST_ROOT / "reports"
settings.logs_dir = TEST_ROOT / "logs"
settings.samples_dir = TEST_ROOT / "samples"
settings.ensure_directories()

from fastapi.testclient import TestClient
from app.main import app
from app.storage.database import init_db, SessionLocal


@pytest.fixture(scope="session", autouse=True)
def _initialize_database():
    init_db()
    yield
    shutil.rmtree(TEST_ROOT, ignore_errors=True)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_firmware_bytes():
    return bytes([0x7F, 0x45, 0x4C, 0x46]) + os.urandom(1024)


@pytest.fixture
def uploaded_firmware_id(client, sample_firmware_bytes):
    response = client.post(
        "/api/firmware/upload",
        files={"file": ("test_firmware.bin", sample_firmware_bytes, "application/octet-stream")},
    )
    assert response.status_code == 200
    return response.json()["firmware"]["id"]
