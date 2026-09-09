from app.detection.threat_scoring import (
    score_from_static_findings,
    score_from_network_events,
    calculate_threat_level,
    calculate_threat_assessment,
)


def test_calculate_threat_level_boundaries():
    assert calculate_threat_level(0) == "LOW"
    assert calculate_threat_level(24) == "LOW"
    assert calculate_threat_level(25) == "MEDIUM"
    assert calculate_threat_level(49) == "MEDIUM"
    assert calculate_threat_level(50) == "HIGH"
    assert calculate_threat_level(74) == "HIGH"
    assert calculate_threat_level(75) == "CRITICAL"
    assert calculate_threat_level(100) == "CRITICAL"


def test_score_from_static_findings_weights_severity():
    findings = [{"severity": "CRITICAL"}, {"severity": "LOW"}]
    score, reasons = score_from_static_findings(findings)
    assert score == 28
    assert any("CRITICAL" in reason for reason in reasons)


def test_score_from_network_events_detects_telnet_port():
    events = [{"destination_port": 23}]
    score, reasons = score_from_network_events(events)
    assert score > 0
    assert any("Telnet" in reason for reason in reasons)


def test_score_from_network_events_empty_returns_zero():
    score, reasons = score_from_network_events([])
    assert score == 0
    assert reasons == []


def test_calculate_threat_assessment_is_explainable():
    findings = [{"severity": "CRITICAL"}, {"severity": "HIGH"}]
    events = [{"destination_port": 4444}]
    score, level, reasons = calculate_threat_assessment(findings, events)
    assert score > 0
    assert level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert len(reasons) > 0


def test_calculate_threat_assessment_no_findings_gives_low_score():
    score, level, reasons = calculate_threat_assessment([], [])
    assert score == 0
    assert level == "LOW"
    assert "No significant risk indicators identified" in reasons


def test_threat_score_never_exceeds_100():
    findings = [{"severity": "CRITICAL"} for _ in range(20)]
    events = [{"destination_port": 4444} for _ in range(10)]
    score, _level, _reasons = calculate_threat_assessment(findings, events)
    assert score <= 100
