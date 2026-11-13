"""Whether a job's process is gone, asked of its pid alone (DEC-1073 (4)): the one function ``gov wait`` and the helper
watch share. A signal 0 to the pid, and a process state of ``Z`` (a zombie) counts as gone."""

from __future__ import annotations

import os
from pathlib import Path

MAX_PID = 2 ** 22  # Linux's own ceiling; a larger number in a pid file is no pid


def read_pid(pid_file) -> int | None:
    """The pid in ``pid_file`` (its digits, as ``launch_worker.sh`` wrote them); None without a file or a usable number."""
    try:
        with open(pid_file, "rb") as stream:
            digits = "".join(ch for ch in stream.read(20).decode("ascii", "ignore") if ch.isdigit())
    except OSError:
        return None
    return int(digits) if digits and 0 < int(digits) <= MAX_PID else None


def _state(pid: int) -> str:
    """The process state letter from ``/proc/<pid>/stat`` (the text after the last closing bracket); "" if unreadable."""
    try:
        text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    after = text.rpartition(")")[2].split()
    return after[0] if after else ""


def gone(pid: int) -> bool:
    """True when ``pid`` has exited: no such process, or one that is a zombie. A process we may not signal is alive."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        pass
    except OSError:
        return False
    return _state(pid) in ("Z", "X")
