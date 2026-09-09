import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CommandResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


def run_command(
    command: List[str],
    timeout_seconds: int = 30,
    cwd: Optional[str] = None,
) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=cwd,
            shell=False,
        )
        return CommandResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            command=command,
            returncode=-1,
            stdout=exc.stdout or "" if isinstance(exc.stdout, str) else "",
            stderr="Command timed out",
            timed_out=True,
        )
    except FileNotFoundError:
        return CommandResult(
            command=command,
            returncode=-2,
            stdout="",
            stderr=f"Executable not found: {command[0]}",
        )
