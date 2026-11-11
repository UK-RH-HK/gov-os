"""The start check every session start consults, and the machine-wide launch log (W2-20 S19, S21; DEC-1088 (5)(b),
DEC-899, P-1, P-8).

``check_start(gpu_need_mib=None, gpu_kind="other")`` returns the gate's reading (``gov.resources.gate.read``) when
the gate is open, and refuses with ``RESOURCE_GATE_SHUT`` (exit 3) and the reading in the error's details when it is
shut, naming every broken condition and its reading (``shut_text``). ``gov resources --check`` is this check; ``gov
launch`` runs it for every session, lead or worker, and refuses with ``LAUNCH_REFUSED``.

An override (``gov launch ... --gate-override DEC-NNN``, or a ticket's ``plan_override`` for the plan's check) is
written as one line to ``~/.gov-os/machine/launch.log`` (``record``); the launcher prints its own line on standard
error.

``StartLock`` is the machine-wide lock a launch holds from its start check until its session is registered (review
F1), so launches that start together are counted against each other.
"""

from __future__ import annotations

import datetime
import fcntl
import io
import os
import re
import sys
import time

from gov.cli.errors import GovError

GATE_SHUT = "RESOURCE_GATE_SHUT"
EXIT_GATE_SHUT = 3
LAUNCH_LOG = "launch.log"
START_LOCK = "launch.lock"
START_LOCK_WAIT_S, START_LOCK_POLL_S = 300.0, 0.05
DECISION = re.compile(r"DEC-\d+")
MIB = 1024 ** 2


def shut_text(reading: dict) -> str:
    """The broken conditions in words: ``memory: reading 1073741824, limit 4294967296; config: heavy_slots: ...``."""
    from gov.resources.gate import describe
    return "; ".join(describe(reason) for reason in reading["gate"]["reasons"])


def check_start(*, gpu_need_mib: int | None = None, gpu_kind: str = "other") -> dict:
    """The start check of one new session (or a job that declares a GPU need); the GPU is read only for a need."""
    from gov.resources.gate import read

    reading = read(True, gpu_need_mib=gpu_need_mib or None, gpu_kind=gpu_kind)
    if not reading["gate"]["open"]:
        raise GovError(GATE_SHUT, f"the resource gate is shut: {shut_text(reading)}", reading,
                       exit_code=EXIT_GATE_SHUT)
    return reading


class StartLock:
    """The machine-wide start lock (review F1): an exclusive ``flock`` on ``~/.gov-os/machine/launch.lock``, taken
    before the start check and given back once the started session is in the registry (or the launch ends without
    one), so launches that start together are each judged with the others already counted. The descriptor is never
    inherited by the session (``O_CLOEXEC``; ``Popen`` closes the rest). A lock that cannot be taken within
    ``wait_s`` refuses the launch: never a check run unlocked."""

    def __init__(self, wait_s: float = START_LOCK_WAIT_S):
        from gov.resources.config import machine_dir

        path = machine_dir() / START_LOCK
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o666)
        except OSError as error:
            raise GovError("LAUNCH_REFUSED", f"the machine-wide start lock {path} cannot be opened "
                                             f"({error.strerror}): no start check runs unlocked (W2-20)") from None
        deadline = time.monotonic() + wait_s
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    os.close(fd)
                    raise GovError("LAUNCH_REFUSED", f"the machine-wide start lock {path} was held by another launch "
                                                     f"for {wait_s:g} s: no start check runs unlocked (W2-20)") from None
                time.sleep(START_LOCK_POLL_S)
            except OSError as error:
                os.close(fd)
                raise GovError("LAUNCH_REFUSED", f"the machine-wide start lock {path} cannot be taken "
                                                 f"({error.strerror}) (W2-20)") from None
        self.fd: int | None = fd

    def release(self) -> None:
        """Give the lock back; a second call does nothing."""
        fd, self.fd = self.fd, None
        if fd is not None:
            os.close(fd)


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


def record(line: str, *, stderr: bool = False) -> str:
    """Write one line to the launch log (with its time), and with ``stderr`` the same line to standard error; the
    line written. A log that cannot be written refuses: an override is never left unrecorded."""
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
    if stderr:
        _stderr(line + "\n")
    return line


def override_decision(value: str | None) -> str | None:
    """The override's decision id, checked: ``DEC-`` and digits, or a refusal."""
    if value is None:
        return None
    if not isinstance(value, str) or not DECISION.fullmatch(value.strip()):
        raise GovError("LAUNCH_REFUSED", f"--gate-override takes a decision id (DEC-NNN), not {value!r} (DEC-899)")
    return value.strip()
