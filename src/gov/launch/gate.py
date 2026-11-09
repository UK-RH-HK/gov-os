"""The start check every session start consults, and the machine-wide launch log (W2-20 S19, S21; DEC-1088 (5)(b),
DEC-899, P-1, P-8).

``check_start(kind="session", gpu_need_mib=None)`` returns the gate's reading (``gov.resources.gate.read``) when
the gate is open, and refuses with ``RESOURCE_GATE_SHUT`` (exit 3) and the reading in the error's details when it is
shut, naming every limit and its reading. ``gov launch`` runs it for every session, lead or worker; ``gov resources
--check`` is the same check.

An override (``gov launch ... --gate-override DEC-NNN``, or a ticket's ``plan_override`` for the plan's check) is
written as one line to ``~/.gov-os/machine/launch.log`` and the same line to standard error.
"""

from __future__ import annotations

import datetime
import io
import os
import re
import sys

from gov.cli.errors import GovError

GATE_SHUT = "RESOURCE_GATE_SHUT"
EXIT_GATE_SHUT = 3
LAUNCH_LOG = "launch.log"
DECISION = re.compile(r"DEC-\d+")
MIB = 1024 ** 2


def check_start(heavy: bool = False, *, kind: str = "session", gpu_need_mib: int | None = None,
                gpu_kind: str = "other") -> dict:
    """The gate for one start; ``heavy`` is kept for the 10-17 callers and means nothing now (DEC-983: no weights)."""
    from gov.resources.gate import describe, read

    need = None if not gpu_need_mib else int(gpu_need_mib) * MIB
    reading = read(kind=kind, gpu_need_bytes=need, gpu_kind=gpu_kind, read_gpu=bool(need))
    if not reading["gate"]["open"]:
        named = "; ".join(describe(reason) for reason in reading["gate"]["reasons"])
        raise GovError(GATE_SHUT, f"the resource gate is shut, no session starts: {named}", reading,
                       exit_code=EXIT_GATE_SHUT)
    return reading


def log_path():
    from gov.resources.config import machine_dir
    return machine_dir() / LAUNCH_LOG


def _stderr(line: str) -> None:
    stream = sys.stderr
    if stream is None:
        return
    try:
        try:
            descriptor = stream.fileno()
        except io.UnsupportedOperation:
            stream.write(line)
            return
        stream.flush()
        os.write(descriptor, line.encode(errors="replace"))
    except (OSError, ValueError):
        pass


def record(line: str) -> str:
    """Write one line to the launch log (with its time) and the same line to standard error; the line written.

    A log that cannot be written refuses: an override is never left unrecorded."""
    line = " ".join(line.split())
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    path = log_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as log:
            log.write(f"{stamp} {line}\n")
    except OSError as error:
        raise GovError("LAUNCH_REFUSED", f"the launch log {path} cannot be written ({error.strerror}): an override is "
                                         f"never left unrecorded") from None
    _stderr(line + "\n")
    return line


def override_decision(value: str | None) -> str | None:
    """The override's decision id, checked: ``DEC-`` and digits, or a refusal."""
    if value is None:
        return None
    if not isinstance(value, str) or not DECISION.fullmatch(value.strip()):
        raise GovError("LAUNCH_REFUSED", f"--gate-override takes a decision id (DEC-NNN), not {value!r} (DEC-899)")
    return value.strip()
