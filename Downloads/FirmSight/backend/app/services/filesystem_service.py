import os
from pathlib import Path
from typing import Optional
from app.extraction.signatures import is_interesting_path


def build_file_tree(root_dir: Path, max_depth: int = 6):
    if not root_dir.exists():
        return {"name": root_dir.name or "/", "path": "/", "is_directory": True, "size_bytes": 0, "children": []}

    def build_node(current_path: Path, depth: int):
        relative = current_path.relative_to(root_dir)
        node = {
            "name": current_path.name or "/",
            "path": str(relative) if str(relative) != "." else "/",
            "is_directory": current_path.is_dir(),
            "size_bytes": 0,
            "children": [],
        }

        if current_path.is_dir():
            if depth >= max_depth:
                return node
            try:
                entries = sorted(os.listdir(current_path))
            except OSError:
                entries = []
            for entry_name in entries:
                child_path = current_path / entry_name
                node["children"].append(build_node(child_path, depth + 1))
        else:
            try:
                node["size_bytes"] = current_path.stat().st_size
            except OSError:
                node["size_bytes"] = 0

        return node

    return build_node(root_dir, 0)


def get_file_metadata(root_dir: Path, relative_path: str) -> Optional[dict]:
    target = (root_dir / relative_path).resolve()
    root_resolved = root_dir.resolve()
    if root_resolved != target and root_resolved not in target.parents:
        return None
    if not target.exists():
        return None

    stat_result = target.stat()
    return {
        "path": relative_path,
        "file_type": "directory" if target.is_dir() else (target.suffix or "file"),
        "size_bytes": stat_result.st_size,
        "permissions": oct(stat_result.st_mode)[-3:],
        "is_interesting": is_interesting_path(relative_path),
    }
