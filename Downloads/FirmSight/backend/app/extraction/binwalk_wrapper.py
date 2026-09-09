import shutil
from pathlib import Path
from dataclasses import dataclass
from app.utils.process_runner import run_command


@dataclass
class BinwalkResult:
    available: bool
    success: bool
    extracted_directory: str
    raw_output: str
    error: str = ""


def is_binwalk_available() -> bool:
    return shutil.which("binwalk") is not None


def run_binwalk_extraction(firmware_path: Path, output_dir: Path, timeout_seconds: int = 60) -> BinwalkResult:
    if not is_binwalk_available():
        return BinwalkResult(
            available=False,
            success=False,
            extracted_directory="",
            raw_output="",
            error="binwalk is not installed on this system",
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "binwalk",
        "--extract",
        "--directory",
        str(output_dir),
        str(firmware_path),
    ]
    result = run_command(command, timeout_seconds=timeout_seconds)

    if result.returncode not in (0,):
        return BinwalkResult(
            available=True,
            success=False,
            extracted_directory=str(output_dir),
            raw_output=result.stdout,
            error=result.stderr or "binwalk extraction failed",
        )

    return BinwalkResult(
        available=True,
        success=True,
        extracted_directory=str(output_dir),
        raw_output=result.stdout,
    )
