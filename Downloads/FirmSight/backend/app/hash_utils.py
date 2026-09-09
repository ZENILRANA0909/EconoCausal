import hashlib
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a firmware file.
    """

    sha256 = hashlib.sha256()

    with file_path.open("rb") as firmware:
        while True:
            chunk = firmware.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()
