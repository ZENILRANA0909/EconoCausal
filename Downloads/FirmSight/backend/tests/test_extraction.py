from pathlib import Path
from app.extraction.extraction_service import extract_firmware, count_extracted_contents
from app.extraction.demo_filesystem import generate_demo_filesystem
from app.extraction.signatures import detect_filesystem_signature, is_interesting_path


def test_extract_firmware_falls_back_to_demo_when_binwalk_unavailable(tmp_path):
    firmware_file = tmp_path / "fake_firmware.bin"
    firmware_file.write_bytes(b"\x00" * 512)

    outcome = extract_firmware("test_fw_id", firmware_file)
    assert outcome.status == "completed"
    assert outcome.file_count > 0
    assert outcome.is_demo is True
    assert outcome.method == "demo_synthetic"


def test_generate_demo_filesystem_creates_files(tmp_path):
    target_dir = tmp_path / "demo_fs"
    count = generate_demo_filesystem(target_dir)
    assert count > 0
    assert (target_dir / "etc" / "passwd").exists()
    assert (target_dir / "etc" / "shadow").exists()


def test_count_extracted_contents(tmp_path):
    target_dir = tmp_path / "demo_fs"
    generate_demo_filesystem(target_dir)
    file_count, directory_count, interesting = count_extracted_contents(target_dir)
    assert file_count > 0
    assert directory_count > 0
    assert len(interesting) > 0


def test_is_interesting_path_detects_sensitive_paths():
    assert is_interesting_path("etc/passwd") is True
    assert is_interesting_path("etc/shadow") is True
    assert is_interesting_path("www/index.html") is True
    assert is_interesting_path("random/unrelated/path.txt") is False


def test_detect_filesystem_signature_unknown_for_empty(tmp_path):
    empty_file = tmp_path / "empty.bin"
    empty_file.write_bytes(b"")
    result = detect_filesystem_signature(empty_file)
    assert result == "unknown"
