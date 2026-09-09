import re

IP_PATTERN = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+")
DOMAIN_PATTERN = re.compile(r"\b[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.(?:[a-zA-Z]{2,})\b")
PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")
PASSWORD_PATTERN = re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?[\w!@#$%^&*]{3,}")

SUSPICIOUS_COMMAND_KEYWORDS = {
    "telnetd": ("HIGH", "network_service", "Telnet daemon reference found"),
    "telnet": ("MEDIUM", "network_service", "Telnet client/service reference found"),
    "ftp": ("MEDIUM", "network_service", "FTP reference found"),
    "wget": ("MEDIUM", "network_tool", "wget usage found, often used for payload retrieval"),
    "curl": ("MEDIUM", "network_tool", "curl usage found, often used for payload retrieval"),
    "nc -e": ("CRITICAL", "reverse_shell", "Netcat reverse shell pattern found"),
    "nc -l": ("HIGH", "network_tool", "Netcat listener pattern found"),
    "netcat": ("HIGH", "network_tool", "netcat reference found"),
    "busybox": ("LOW", "toolkit", "BusyBox reference found (common but worth reviewing)"),
    "/bin/sh": ("LOW", "shell_reference", "Shell invocation reference found"),
    "chmod 777": ("MEDIUM", "permissions", "Overly permissive chmod usage found"),
    "backdoor": ("CRITICAL", "backdoor_indicator", "String literally referencing 'backdoor'"),
}

CREDENTIAL_FILE_MARKERS = ["passwd", "shadow"]


def scan_text_for_indicators(text: str):
    findings = []

    for match in set(IP_PATTERN.findall(text)):
        if match not in ("0.0.0.0", "127.0.0.1", "255.255.255.255"):
            findings.append({
                "severity": "MEDIUM",
                "category": "hardcoded_ip",
                "finding": "Hardcoded IP address found in firmware content",
                "evidence": match,
                "recommendation": "Confirm whether this IP is an expected update/telemetry endpoint.",
            })

    for match in list(set(URL_PATTERN.findall(text)))[:20]:
        findings.append({
            "severity": "MEDIUM",
            "category": "hardcoded_url",
            "finding": "Hardcoded URL found in firmware content",
            "evidence": match[:200],
            "recommendation": "Verify the destination is expected and served over HTTPS.",
        })

    if PRIVATE_KEY_PATTERN.search(text):
        findings.append({
            "severity": "CRITICAL",
            "category": "credential_exposure",
            "finding": "Embedded private key material detected",
            "evidence": "PEM private key header found",
            "recommendation": "Remove embedded private keys; provision keys at deployment time instead.",
        })

    for match in list(set(PASSWORD_PATTERN.findall(text)))[:10]:
        findings.append({
            "severity": "HIGH",
            "category": "credential_exposure",
            "finding": "Possible hardcoded password-related string",
            "evidence": str(match),
            "recommendation": "Do not hardcode credentials; use per-device provisioning.",
        })

    lowered = text.lower()
    for keyword, (severity, category, description) in SUSPICIOUS_COMMAND_KEYWORDS.items():
        if keyword in lowered:
            findings.append({
                "severity": severity,
                "category": category,
                "finding": description,
                "evidence": keyword,
                "recommendation": "Review this usage to confirm it is intentional and necessary.",
            })

    return findings
