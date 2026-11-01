"""The code index's daemon folders of the projects W1-27's cases build (W2-67 batch 8; TD1C-A, DEC-914 item 2).

Every run of the code index for a project makes ``/tmp/gov-cbm-<uid>/`` and the first 16 hex digits of the sha256 of
the project's resolved root (``gov.codeintel.daemon_dir``; DEC-338 puts the tool's lock and socket files there), and
nothing removed it (batch 1c: 11,014 such folders on 2026-10-23). A builder notes each project root before it
builds the project (``note``), with whether that folder was already there. When a case is over, the conftest's
autouse fixture calls ``release`` for the roots noted during the case: the folder of each is removed only if it was
not there before the project was built, and only once no process of the tool names it as its runtime directory
(the tool's daemon outlives the command that started it and stops by itself after its last session; one still
there after ``WAIT_S`` is stopped). Nothing else under ``/tmp/gov-cbm-<uid>`` is touched: never a folder of a root
this module was not given, so never another worker's, whatever it made while the case ran.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import signal
import time
from pathlib import Path

BASE = Path(f"/tmp/gov-cbm-{os.getuid()}")
WAIT_S = 60.0                   # how long the tool's daemon has to stop by itself once the case is over
STOP_S = 5.0                    # then, after each signal, how long it has to end
_NAME = re.compile(r"[0-9a-f]{16}")
_noted: list[tuple[Path, bool]] = []     # (daemon folder, there before the project was built), in this process


def daemon_folder(root) -> Path:
    """The daemon folder of the project at ``root``: ``gov.codeintel.daemon_dir``'s rule."""
    return BASE / hashlib.sha256(os.fsencode(Path(root).resolve())).hexdigest()[:16]


def note(root):
    """Before the project at ``root`` is built: its daemon folder goes when the case is over. Returns ``root``."""
    folder = daemon_folder(root)
    _noted.append((folder, os.path.lexists(folder)))
    return root


def mark() -> int:
    """Where the notes of a case begin."""
    return len(_noted)


def holders(folder) -> list[int]:
    """The processes whose environment names ``folder`` as the tool's runtime directory (``CBM_RUNTIME_DIR``)."""
    wanted, found = b"CBM_RUNTIME_DIR=" + os.fsencode(folder), []
    for proc in Path("/proc").iterdir():
        if proc.name.isdigit():
            try:
                if wanted in (proc / "environ").read_bytes().split(b"\0"):
                    found.append(int(proc.name))
            except OSError:     # ended, or not this user's
                pass
    return found


def _wait(folder, seconds) -> list[int]:
    deadline = time.monotonic() + seconds
    while (pids := holders(folder)) and time.monotonic() < deadline:
        time.sleep(0.2)
    return pids


def _stopped(folder):
    """Wait for the tool's processes of ``folder`` to end; stop those still there. Raises if one is left."""
    pids = _wait(folder, WAIT_S)
    for sent in (signal.SIGTERM, signal.SIGKILL):
        if not pids:
            return
        for pid in pids:
            try:
                os.kill(pid, sent)
            except ProcessLookupError:
                pass
        pids = _wait(folder, STOP_S)
    if pids:
        raise RuntimeError(f"the code index's processes {pids} of {folder} did not end: the folder is kept")


def release(since: int = 0):
    """Remove the daemon folder of each root noted from ``since`` on that was not there before its project was
    built, once no process holds it; then forget those notes."""
    noted, _noted[since:] = _noted[since:], []
    for folder, before in noted:
        if before or folder.parent != BASE or not _NAME.fullmatch(folder.name):
            continue
        if folder.is_symlink() or not folder.is_dir() or folder.stat().st_uid != os.getuid():
            continue
        _stopped(folder)
        shutil.rmtree(folder)
