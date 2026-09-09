import platform
import shutil
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ToolStatus:
    name: str
    available: bool
    path: str
    install_hint: str


INSTALL_HINTS = {
    "python3": "Included with the OS or install from python.org",
    "binwalk": "macOS: brew install binwalk | Linux: sudo apt install binwalk",
    "file": "macOS: preinstalled | Linux: sudo apt install file",
    "readelf": "macOS: brew install binutils | Linux: sudo apt install binutils",
    "tcpdump": "macOS: preinstalled (may need sudo) | Linux: sudo apt install tcpdump",
    "qemu-system-arm": "macOS: brew install qemu | Linux: sudo apt install qemu-system-arm",
    "qemu-system-aarch64": "macOS: brew install qemu | Linux: sudo apt install qemu-system-arm",
    "qemu-system-mips": "macOS: brew install qemu | Linux: sudo apt install qemu-system-mips",
    "qemu-system-mipsel": "macOS: brew install qemu | Linux: sudo apt install qemu-system-mips",
    "qemu-system-x86_64": "macOS: brew install qemu | Linux: sudo apt install qemu-system-x86",
    "qemu-arm": "macOS: brew install qemu | Linux: sudo apt install qemu-user",
    "qemu-mips": "macOS: brew install qemu | Linux: sudo apt install qemu-user",
    "qemu-mipsel": "macOS: brew install qemu | Linux: sudo apt install qemu-user",
}

CORE_TOOLS: List[str] = [
    "python3",
    "binwalk",
    "file",
    "readelf",
    "tcpdump",
]

QEMU_TOOLS: List[str] = [
    "qemu-system-arm",
    "qemu-system-aarch64",
    "qemu-system-mips",
    "qemu-system-mipsel",
    "qemu-system-x86_64",
    "qemu-arm",
    "qemu-mips",
    "qemu-mipsel",
]


def detect_tool(tool_name: str) -> ToolStatus:
    resolved_path = shutil.which(tool_name)
    return ToolStatus(
        name=tool_name,
        available=resolved_path is not None,
        path=resolved_path or "",
        install_hint=INSTALL_HINTS.get(tool_name, "See project README for installation instructions"),
    )


def detect_all_tools() -> Dict[str, ToolStatus]:
    results: Dict[str, ToolStatus] = {}
    for tool_name in CORE_TOOLS + QEMU_TOOLS:
        results[tool_name] = detect_tool(tool_name)
    return results


def get_available_qemu_binaries() -> List[str]:
    return [name for name in QEMU_TOOLS if shutil.which(name) is not None]


def get_platform_info() -> Dict[str, str]:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "is_linux": str(platform.system() == "Linux"),
        "is_macos": str(platform.system() == "Darwin"),
    }
