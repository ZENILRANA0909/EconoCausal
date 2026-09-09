from typing import List, Dict, Tuple

SEVERITY_WEIGHTS = {
    "LOW": 3,
    "MEDIUM": 8,
    "HIGH": 15,
    "CRITICAL": 25,
}

NETWORK_RISK_PORTS = {
    23: ("Telnet activity detected on the network", 12),
    21: ("FTP activity detected on the network", 8),
    4444: ("Traffic to a commonly-used reverse-shell port", 20),
}


def score_from_static_findings(findings: List[Dict]) -> Tuple[int, List[str]]:
    score = 0
    reasons = []
    severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

    for finding in findings:
        severity = finding.get("severity", "LOW")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        score += SEVERITY_WEIGHTS.get(severity, 0)

    for severity, count in severity_counts.items():
        if count > 0:
            reasons.append(f"{count} {severity} static finding(s) detected")

    return score, reasons


def score_from_network_events(events: List[Dict]) -> Tuple[int, List[str]]:
    score = 0
    reasons = []
    seen_reasons = set()

    for event in events:
        destination_port = event.get("destination_port", 0)
        if destination_port in NETWORK_RISK_PORTS:
            reason_text, weight = NETWORK_RISK_PORTS[destination_port]
            score += weight
            if reason_text not in seen_reasons:
                reasons.append(reason_text)
                seen_reasons.add(reason_text)

    if len(events) > 4 and "Unusually high outbound connection count observed" not in reasons:
        score += 5
        reasons.append("Unusually high outbound connection count observed")

    return score, reasons


def calculate_threat_level(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


def calculate_threat_assessment(findings: List[Dict], network_events: List[Dict]):
    static_score, static_reasons = score_from_static_findings(findings)
    network_score, network_reasons = score_from_network_events(network_events)

    total_score = min(static_score + network_score, 100)
    reasons = static_reasons + network_reasons
    if not reasons:
        reasons.append("No significant risk indicators identified")

    level = calculate_threat_level(total_score)
    return total_score, level, reasons
