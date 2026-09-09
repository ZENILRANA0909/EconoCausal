import os
import signal
import subprocess
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional
from app.utils.tool_detection import get_available_qemu_binaries

ARCH_TO_SYSTEM_QEMU = {
    "ARM": "qemu-system-arm",
    "ARM64": "qemu-system-aarch64",
    "MIPS": "qemu-system-mips",
    "MIPS64": "qemu-system-mips",
    "x86_64": "qemu-system-x86_64",
    "x86": "qemu-system-x86_64",
}

ARCH_TO_USER_QEMU = {
    "ARM": "qemu-arm",
    "MIPS": "qemu-mips",
}


@dataclass
class EmulationLaunchResult:
    success: bool
    mode: str
    qemu_binary: str
    process_id: int
    message: str
    is_demo: bool


class QemuProcessRegistry:
    def __init__(self):
        self._processes: Dict[str, subprocess.Popen] = {}

    def register(self, session_id: str, process: subprocess.Popen) -> None:
        self._processes[session_id] = process

    def get(self, session_id: str) -> Optional[subprocess.Popen]:
        return self._processes.get(session_id)

    def stop(self, session_id: str, timeout_seconds: int = 5) -> bool:
        process = self._processes.get(session_id)
        if process is None:
            return False
        if process.poll() is not None:
            self._processes.pop(session_id, None)
            return True
        try:
            process.terminate()
            process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
        self._processes.pop(session_id, None)
        return True

    def is_running(self, session_id: str) -> bool:
        process = self._processes.get(session_id)
        if process is None:
            return False
        return process.poll() is None


registry = QemuProcessRegistry()


def determine_emulation_mode(architecture: str) -> str:
    available = set(get_available_qemu_binaries())
    if ARCH_TO_SYSTEM_QEMU.get(architecture) in available:
        return "full_system"
    if ARCH_TO_USER_QEMU.get(architecture) in available:
        return "user_mode"
    return "unsupported"


def launch_emulation(session_id: str, architecture: str, target_binary: Optional[Path]) -> EmulationLaunchResult:
    mode = determine_emulation_mode(architecture)

    if mode == "unsupported":
        return EmulationLaunchResult(
            success=False,
            mode="unsupported",
            qemu_binary="",
            process_id=0,
            message=f"No suitable QEMU binary installed for architecture '{architecture}'. Running in DEMO mode.",
            is_demo=True,
        )

    if mode == "user_mode" and target_binary and target_binary.exists():
        binary_name = ARCH_TO_USER_QEMU[architecture]
        command = [binary_name, str(target_binary)]
    elif mode == "full_system":
        binary_name = ARCH_TO_SYSTEM_QEMU[architecture]
        command = [binary_name, "-nographic", "-M", "help"]
    else:
        return EmulationLaunchResult(
            success=False,
            mode="unsupported",
            qemu_binary="",
            process_id=0,
            message="No bootable/executable target available for this firmware. Running in DEMO mode.",
            is_demo=True,
        )

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid if hasattr(os, "setsid") else None,
        )
    except FileNotFoundError:
        return EmulationLaunchResult(
            success=False,
            mode="unsupported",
            qemu_binary=command[0],
            process_id=0,
            message=f"{command[0]} not found despite detection. Running in DEMO mode.",
            is_demo=True,
        )
    except OSError as exc:
        return EmulationLaunchResult(
            success=False,
            mode="unsupported",
            qemu_binary=command[0],
            process_id=0,
            message=f"Failed to launch QEMU: {exc}. Running in DEMO mode.",
            is_demo=True,
        )

    registry.register(session_id, process)
    time.sleep(0.3)

    if process.poll() is not None and process.returncode != 0:
        return EmulationLaunchResult(
            success=False,
            mode=mode,
            qemu_binary=command[0],
            process_id=0,
            message="QEMU exited immediately, firmware likely not directly bootable. Running in DEMO mode.",
            is_demo=True,
        )

    return EmulationLaunchResult(
        success=True,
        mode=mode,
        qemu_binary=command[0],
        process_id=process.pid,
        message="Emulation started",
        is_demo=False,
    )


def stop_emulation(session_id: str) -> bool:
    return registry.stop(session_id)


def is_emulation_running(session_id: str) -> bool:
    return registry.is_running(session_id)
