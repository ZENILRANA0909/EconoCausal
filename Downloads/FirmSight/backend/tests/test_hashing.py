import hashlib
from pathlib import Path
from app.utils.hashing import sha256_of_file, sha256_of_bytes


def test_sha256_of_bytes_matches_hashlib():
    data = b"firmsight test data"
    expected = hashlib.sha256(data).hexdigest()
    assert sha256_of_bytes(data) == expected


def test_sha256_of_file_matches_hashlib(tmp_path):
    file_path = tmp_path / "sample.bin"
    content = b"\x00\x01\x02firmware content sample"
    file_path.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    assert sha256_of_file(file_path) == expected


def test_sha256_is_deterministic(tmp_path):
    file_path = tmp_path / "sample2.bin"
    file_path.write_bytes(b"identical content")
    first = sha256_of_file(file_path)
    second = sha256_of_file(file_path)
    assert first == second
