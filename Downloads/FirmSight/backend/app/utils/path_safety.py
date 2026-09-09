from pathlib import Path


class PathTraversalError(Exception):
    pass


def resolve_within_base(base_dir: Path, relative_path: str) -> Path:
    base_resolved = base_dir.resolve()
    candidate = (base_dir / relative_path).resolve()
    if base_resolved != candidate and base_resolved not in candidate.parents:
        raise PathTraversalError(f"Path escapes allowed base directory: {relative_path}")
    return candidate


def safe_filename(filename: str) -> str:
    cleaned = Path(filename).name
    cleaned = cleaned.replace("..", "_")
    allowed = "".join(
        char if char.isalnum() or char in ("_", "-", ".") else "_"
        for char in cleaned
    )
    return allowed or "unnamed_file"
