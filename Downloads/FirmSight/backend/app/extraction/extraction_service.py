import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
from app.config.settings import settings
from app.extraction.binwalk_wrapper import run_binwalk_extraction, is_binwalk_available
from app.extraction.demo_filesystem import generate_demo_filesystem
from app.extraction.signatures import detect_filesystem_signature, is_interesting_path


@dataclass
class ExtractionOutcome:
    status: str
    extracted_path: str
    file_count: int
    directory_count: int
    filesystem_type: str
    method: str
    log_output: str
    is_demo: bool
    interesting_files: List[str] = field(default_factory=list)


def count_extracted_contents(root_dir: Path):
    file_count = 0
    directory_count = 0
    interesting = []
    for current_root, dirs, files in os.walk(root_dir):
        directory_count += len(dirs)
        for filename in files:
            file_count += 1
            full_path = Path(current_root) / filename
            relative = full_path.relative_to(root_dir)
            if is_interesting_path(str(relative)):
                interesting.append(str(relative))
    return file_count, directory_count, interesting


def extract_firmware(firmware_id: str, firmware_path: Path) -> ExtractionOutcome:
    output_dir = settings.extracted_dir / firmware_id
    filesystem_type = detect_filesystem_signature(firmware_path)

    if is_binwalk_available():
        result = run_binwalk_extraction(firmware_path, output_dir)
        if result.success:
            extraction_root = output_dir
            candidates = list(output_dir.glob("_*.extracted"))
            if candidates:
                extraction_root = candidates[0]
            file_count, directory_count, interesting = count_extracted_contents(extraction_root)
            if file_count > 0:
                return ExtractionOutcome(
                    status="completed",
                    extracted_path=str(extraction_root),
                    file_count=file_count,
                    directory_count=directory_count,
                    filesystem_type=filesystem_type,
                    method="binwalk",
                    log_output=result.raw_output,
                    is_demo=False,
                    interesting_files=interesting,
                )

    demo_root = output_dir / "demo_filesystem"
    created_count = generate_demo_filesystem(demo_root)
    file_count, directory_count, interesting = count_extracted_contents(demo_root)
    return ExtractionOutcome(
        status="completed",
        extracted_path=str(demo_root),
        file_count=file_count,
        directory_count=directory_count,
        filesystem_type=filesystem_type if filesystem_type != "unknown" else "SquashFS (simulated)",
        method="demo_synthetic",
        log_output="binwalk unavailable or produced no output; generated DEMO/SIMULATED filesystem",
        is_demo=True,
        interesting_files=interesting,
    )
