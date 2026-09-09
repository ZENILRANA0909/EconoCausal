import pytest
from pathlib import Path
from app.utils.path_safety import resolve_within_base, safe_filename, PathTraversalError


def test_resolve_within_base_allows_valid_path(tmp_path):
    result = resolve_within_base(tmp_path, "subdir/file.txt")
    assert str(result).startswith(str(tmp_path.resolve()))


def test_resolve_within_base_blocks_traversal(tmp_path):
    with pytest.raises(PathTraversalError):
        resolve_within_base(tmp_path, "../../etc/passwd")


def test_safe_filename_removes_traversal_sequences():
    assert ".." not in safe_filename("../../etc/passwd")


def test_safe_filename_strips_directory_components():
    result = safe_filename("/absolute/path/firmware.bin")
    assert result == "firmware.bin"


def test_safe_filename_handles_empty_input():
    result = safe_filename("")
    assert result == "unnamed_file"
