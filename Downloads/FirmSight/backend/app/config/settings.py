import os
from pathlib import Path
from pydantic_settings import BaseSettings

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    app_name: str = "FirmSight"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    environment: str = os.getenv("FIRMSIGHT_ENV", "development")
    host: str = os.getenv("FIRMSIGHT_HOST", "127.0.0.1")
    port: int = int(os.getenv("FIRMSIGHT_PORT", "8000"))

    data_dir: Path = PROJECT_ROOT / "data"
    uploads_dir: Path = PROJECT_ROOT / "data" / "uploads"
    extracted_dir: Path = PROJECT_ROOT / "data" / "extracted"
    pcap_dir: Path = PROJECT_ROOT / "data" / "pcap"
    reports_dir: Path = PROJECT_ROOT / "reports"
    logs_dir: Path = PROJECT_ROOT / "logs"
    samples_dir: Path = PROJECT_ROOT / "samples"

    database_url: str = os.getenv(
        "FIRMSIGHT_DATABASE_URL",
        f"sqlite:///{PROJECT_ROOT / 'data' / 'firmsight.db'}",
    )

    max_upload_size_mb: int = int(os.getenv("FIRMSIGHT_MAX_UPLOAD_MB", "128"))
    allowed_upload_extensions: tuple = (".bin", ".img", ".fw")

    emulation_timeout_seconds: int = int(os.getenv("FIRMSIGHT_EMULATION_TIMEOUT", "60"))
    network_capture_timeout_seconds: int = int(os.getenv("FIRMSIGHT_CAPTURE_TIMEOUT", "30"))

    cors_origins: list = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_prefix = "FIRMSIGHT_"

    def ensure_directories(self) -> None:
        for directory in (
            self.data_dir,
            self.uploads_dir,
            self.extracted_dir,
            self.pcap_dir,
            self.reports_dir,
            self.logs_dir,
            self.samples_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
