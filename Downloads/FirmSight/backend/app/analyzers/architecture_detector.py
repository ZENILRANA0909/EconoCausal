import os
import shutil
from pathlib import Path
from dataclasses import dataclass
from app.utils.process_runner import run_command

ARCH_KEYWORDS = {
    "ARM64": ["aarch64", "arm64"],
    "ARM": ["arm", "elf32-littlearm", "elf32-bigarm"],
    "MIPS64": ["mips64"],
    "MIPS": ["mips"],
    "x86_64": ["x86-64", "x86_64", "amd64"],
    "x86": ["80386", "i386", "x86"],
    "PowerPC": ["powerpc", "ppc"],
}


@dataclass
class ArchitectureResult:
    architecture: str
    endianness: str
    binary_type: str
    executable_count: int


def _classify_text(text: str) -> str:
    lowered = text.lower()
    for arch_name, keywords in ARCH_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lowered:
                return arch_name
    return "unknown"


def _detect_endianness(text: str) -> str:
    lowered = text.lower()
    if "lsb" in lowered or "little" in lowered:
        return "little-endian"
    if "msb" in lowered or "big" in lowered:
        return "big-endian"
    return "unknown"


def detect_architecture_for_file(file_path: Path) -> ArchitectureResult:
    if shutil.which("file"):
        result = run_command(["file", str(file_path)], timeout_seconds=10)
        combined_output = result.stdout
        architecture = _classify_text(combined_output)
        endianness = _detect_endianness(combined_output)
        binary_type = "ELF" if "elf" in combined_output.lower() else "unknown"
        if architecture != "unknown":
            return ArchitectureResult(architecture, endianness, binary_type, 1)

    if shutil.which("readelf"):
        result = run_command(["readelf", "-h", str(file_path)], timeout_seconds=10)
        combined_output = result.stdout
        architecture = _classify_text(combined_output)
        endianness = _detect_endianness(combined_output)
        if architecture != "unknown":
            return ArchitectureResult(architecture, endianness, "ELF", 1)

    return ArchitectureResult("unknown", "unknown", "unknown", 0)


def detect_architecture_for_directory(root_dir: Path) -> ArchitectureResult:
    arch_votes = {}
    endianness_votes = {}
    executable_count = 0
    binary_type = "unknown"

    if not root_dir.exists():
        return ArchitectureResult("unknown", "unknown", "unknown", 0)

    for current_root, _dirs, files in os.walk(root_dir):
        for filename in files:
            full_path = Path(current_root) / filename
            if not os.access(full_path, os.X_OK) and full_path.suffix not in ("", ".so"):
                continue
            single_result = detect_architecture_for_file(full_path)
            if single_result.architecture != "unknown":
                executable_count += 1
                arch_votes[single_result.architecture] = arch_votes.get(single_result.architecture, 0) + 1
                endianness_votes[single_result.endianness] = endianness_votes.get(single_result.endianness, 0) + 1
                binary_type = single_result.binary_type

    if not arch_votes:
        return ArchitectureResult("unknown", "unknown", "unknown", executable_count)

    top_architecture = max(arch_votes, key=arch_votes.get)
    top_endianness = max(endianness_votes, key=endianness_votes.get) if endianness_votes else "unknown"
    return ArchitectureResult(top_architecture, top_endianness, binary_type, executable_count)
