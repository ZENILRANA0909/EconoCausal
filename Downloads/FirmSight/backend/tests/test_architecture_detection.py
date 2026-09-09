from pathlib import Path
from app.analyzers.architecture_detector import detect_architecture_for_file, detect_architecture_for_directory, _classify_text, _detect_endianness


def test_classify_text_detects_arm():
    assert _classify_text("ELF 32-bit LSB executable, ARM") == "ARM"


def test_classify_text_detects_mips():
    assert _classify_text("ELF 32-bit MSB executable, MIPS") == "MIPS"


def test_classify_text_detects_x86_64():
    assert _classify_text("ELF 64-bit LSB executable, x86-64") == "x86_64"


def test_classify_text_returns_unknown_for_unrecognized():
    assert _classify_text("some random text with no architecture") == "unknown"


def test_detect_endianness_little():
    assert _detect_endianness("ELF 32-bit LSB executable") == "little-endian"


def test_detect_endianness_big():
    assert _detect_endianness("ELF 32-bit MSB executable") == "big-endian"


def test_detect_architecture_for_missing_directory_returns_unknown(tmp_path):
    missing_dir = tmp_path / "does_not_exist"
    result = detect_architecture_for_directory(missing_dir)
    assert result.architecture == "unknown"
    assert result.executable_count == 0


def test_detect_architecture_for_file_handles_nonexistent(tmp_path):
    fake_file = tmp_path / "fake_binary"
    fake_file.write_bytes(b"not a real binary")
    result = detect_architecture_for_file(fake_file)
    assert result.architecture in ("unknown", "ARM", "MIPS", "x86", "x86_64", "ARM64", "MIPS64", "PowerPC")
