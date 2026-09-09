from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.hash_utils import calculate_sha256


UPLOAD_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "uploads"
)

ALLOWED_EXTENSIONS = {
    ".bin",
    ".img",
    ".fw",
    ".hex",
    ".rom",
}

MAX_FILE_SIZE = 128 * 1024 * 1024


async def save_firmware(file: UploadFile) -> dict:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided",
        )

    filename = Path(file.filename).name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported firmware type: {extension}",
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = UPLOAD_DIR / filename

    if destination.exists():
        raise HTTPException(
            status_code=409,
            detail="A firmware file with this name already exists",
        )

    total_size = 0

    try:
        with destination.open("wb") as output:

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:

                    destination.unlink(
                        missing_ok=True
                    )

                    raise HTTPException(
                        status_code=413,
                        detail="Firmware file is larger than 128 MB",
                    )

                output.write(chunk)

        sha256 = calculate_sha256(destination)

    except HTTPException:
        raise

    except Exception as error:

        destination.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process firmware: {error}",
        )

    finally:
        await file.close()

    return {
        "filename": filename,
        "size_bytes": total_size,
        "extension": extension,
        "sha256": sha256,
        "path": str(destination),
    }
