import shutil
import subprocess
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class CaptureHandle:
    process: subprocess.Popen
    pcap_path: Path


def is_tcpdump_available() -> bool:
    return shutil.which("tcpdump") is not None


def start_capture(pcap_path: Path, interface: str = "any", timeout_seconds: int = 30) -> Optional[CaptureHandle]:
    if not is_tcpdump_available():
        return None

    pcap_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "tcpdump",
        "-i", interface,
        "-w", str(pcap_path),
        "-G", str(timeout_seconds),
        "-W", "1",
    ]
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (FileNotFoundError, PermissionError, OSError):
        return None

    return CaptureHandle(process=process, pcap_path=pcap_path)


def stop_capture(handle: CaptureHandle, timeout_seconds: int = 5) -> None:
    if handle.process.poll() is None:
        handle.process.terminate()
        try:
            handle.process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            handle.process.kill()
