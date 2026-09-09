import shutil
from pathlib import Path
from typing import List, Dict
from app.utils.process_runner import run_command


def is_capable_of_parsing() -> bool:
    return shutil.which("tcpdump") is not None


def parse_pcap_summary(pcap_path: Path, max_lines: int = 200) -> List[Dict]:
    if not pcap_path.exists() or not is_capable_of_parsing():
        return []

    result = run_command(["tcpdump", "-nn", "-r", str(pcap_path)], timeout_seconds=20)
    events: List[Dict] = []

    for line in result.stdout.splitlines()[:max_lines]:
        parts = line.split()
        if len(parts) < 3:
            continue
        events.append({
            "raw": line,
            "timestamp": parts[0] if parts else "",
            "protocol": "IP" if "IP" in line else "unknown",
        })

    return events
