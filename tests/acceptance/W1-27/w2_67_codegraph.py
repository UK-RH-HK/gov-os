"""The code index's daemon folders of the projects W1-27's cases build (W2-67 batch 8; TD1C-A, DEC-914 item 2).

Every run of the code index for a project makes the project's daemon folder, ``gov.codeintel.daemon_dir(root)``
(DEC-338 puts the tool's lock and socket files there), and nothing removed it (batch 1c: 11,014 such folders under
``/tmp/gov-cbm-<uid>`` on 2026-10-23). The place is read from ``gov.codeintel`` in this process, never written here:
today ``/tmp/gov-cbm-<uid>/`` and the first 16 hex digits of the sha256 of the project's resolved root; after W2-56 a
place of the test session's own or under a launched session's temp folder (W2-56 S1; revised by the test designer,
DEC-1099 (1)). A builder notes each project root before it builds the project (``note``), with whether its folder was
already there. When a case is over, the conftest's autouse fixture calls ``release`` for the roots noted during the
case: the folder of each is removed only if it was not there before the project was built, only if it is still the
place ``gov.codeintel`` names for that root, and only once no process of the tool names it as its runtime directory
(the tool's daemon outlives the command that started it and stops by itself after its last session; one still there
after ``WAIT_S`` is stopped). Nothing else is touched: never a folder of a root this module was not given, so never
another worker's, whatever it made while the case ran.
"""

from __future__ import annotations

import os
import re
import shutil
import signal
import time
from pathlib import Path

WAIT_S = 60.0                   # how long the tool's daemon has to stop by itself once the case is over
STOP_S = 5.0                    # then, after each signal, how long it has to end
_NAME = re.compile(r"[0-9a-f]{8,64}")    # a daemon folder's name: hex digits of the root's hash
_noted: list[tuple[Path, Path, bool]] = []   # (root, daemon folder, there before the project was built), in this process


def daemon_folder(root) -> Path:
    """The daemon folder of the project at ``root``, as ``gov.codeintel.daemon_dir`` names it in this process."""
    from gov.codeintel import daemon_dir

    return Path(daemon_dir(Path(root)))


def note(root):
    """Before the project at ``root`` is built: its daemon folder goes when the case is over. Returns ``root``."""
    folder = daemon_folder(root)
    _noted.append((Path(root), folder, os.path.lexists(folder)))
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
    for root, folder, before in noted:
        if before or not _NAME.fullmatch(folder.name):
            continue
        try:
            if folder != daemon_folder(root):   # the place moved since the note: not provably this root's folder
                continue
        except Exception:
            continue
        if folder.is_symlink() or not folder.is_dir() or folder.stat().st_uid != os.getuid():
            continue
        _stopped(folder)
        shutil.rmtree(folder)
