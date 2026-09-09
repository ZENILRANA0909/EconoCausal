import os
from pathlib import Path
from typing import List, Dict
from app.analyzers.static_rules import scan_text_for_indicators, CREDENTIAL_FILE_MARKERS

MAX_FILE_READ_BYTES = 2_000_000
TEXT_LIKE_EXTENSIONS = {".sh", ".cgi", ".conf", ".cfg", ".txt", ".key", ".pem", "", ".init", ".rc"}


def _try_read_text(file_path: Path) -> str:
    try:
        if file_path.stat().st_size > MAX_FILE_READ_BYTES:
            return ""
        with open(file_path, "rb") as handle:
            raw = handle.read(MAX_FILE_READ_BYTES)
        return raw.decode("utf-8", errors="ignore")
    except OSError:
        return ""


def analyze_extracted_filesystem(root_dir: Path) -> List[Dict]:
    findings: List[Dict] = []
    if not root_dir.exists():
        return findings

    for current_root, _dirs, files in os.walk(root_dir):
        for filename in files:
            full_path = Path(current_root) / filename
            relative_path = str(full_path.relative_to(root_dir))
            lower_name = filename.lower()

            if lower_name in CREDENTIAL_FILE_MARKERS:
                severity = "CRITICAL" if lower_name == "shadow" else "MEDIUM"
                findings.append({
                    "severity": severity,
                    "category": "credential_file",
                    "file_path": relative_path,
                    "finding": f"Sensitive system file '{filename}' present in firmware image",
                    "evidence": relative_path,
                    "recommendation": "Ensure default/weak credentials are not shipped in production firmware.",
                })

            content = _try_read_text(full_path)
            if not content:
                continue

            indicator_findings = scan_text_for_indicators(content)
            for indicator in indicator_findings:
                indicator["file_path"] = relative_path
                findings.append(indicator)

    return findings
