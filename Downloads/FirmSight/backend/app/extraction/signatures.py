from pathlib import Path
from typing import Optional

SIGNATURES = {
    b"\x68\x73\x71\x73": "SquashFS",
    b"\x30\x71\x73\x68": "SquashFS (be)",
    b"\x85\x19\x03\x20": "JFFS2",
    b"\x1f\x8b\x08": "GZIP",
    b"\x55\x45\x33\x00": "UBI",
    b"CramFs": "CramFS",
}

INTERESTING_PATH_MARKERS = [
    "etc/passwd",
    "etc/shadow",
    "etc/init.d",
    "etc/rc.d",
    "etc/config",
    "www",
    "bin",
    "sbin",
    "usr/bin",
    "usr/sbin",
    "var",
    "tmp",
]


def detect_filesystem_signature(file_path: Path, read_bytes: int = 4096) -> str:
    try:
        with open(file_path, "rb") as handle:
            header = handle.read(read_bytes)
    except OSError:
        return "unknown"

    for signature_bytes, name in SIGNATURES.items():
        if signature_bytes in header:
            return name
    return "unknown"


def is_interesting_path(relative_path: str) -> bool:
    normalized = relative_path.lower().lstrip("/")
    return any(normalized.startswith(marker) or f"/{marker}" in f"/{normalized}" for marker in INTERESTING_PATH_MARKERS)
