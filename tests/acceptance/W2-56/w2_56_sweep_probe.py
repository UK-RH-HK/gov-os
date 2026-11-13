"""A test run's folders, for the R3 follow-up (S1): run by ``test_w2_56_r3_sweep.py`` as a pytest session of its own.

Never collected by an ordinary run (its name has no ``test_`` prefix); pytest collects it only when it is named on
the command line. It runs from the repository's root, so every ``conftest.py`` on the way applies to it (the
repository's own ``tests/conftest.py`` among them), as to any suite under ``tests/acceptance/``.

``test_record_and_hold`` writes one JSON line to ``$W2_56_SWEEP_RECORD`` (written whole, then renamed, so a reader
never sees half a line):

- ``pid`` and ``pid_namespace``: this run's process as it sees itself, and its pid namespace (``/proc/self/ns/pid``);
- ``daemon_base``: ``$CODEINTEL_DAEMON_BASE`` as the run's cases see it (the run's own folder for its daemon
  folders), and whether that folder exists now;
- ``temp_root``: the run's temp root (``tempfile.gettempdir()``), and ``links``: the ``gov-path-*`` folders that hold
  an entry of the run's ``PATH`` (the folder of links for the tool off ``PATH``, where the run made one; today the
  entry is a folder inside it);
- ``watched``: for each path named in ``$W2_56_SWEEP_WATCH`` (a JSON list), whether it exists at this moment (the
  run's cases run after its start, so a folder its start removed reads ``false``).

With ``$W2_56_SWEEP_HOLD`` set, the case then waits until that file exists (at most ``$W2_56_SWEEP_HOLD_S`` seconds,
default 240), so the run stays live while the caller starts another; it never fails on the wait.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

LINKS_PREFIX = "gov-path-"


def _links(entries) -> list[str]:
    """The ``gov-path-*`` folders that hold an entry of ``PATH`` (the entry itself or a folder above it)."""
    found = []
    for entry in entries:
        for folder in (Path(entry), *Path(entry).parents):
            if folder.name.startswith(LINKS_PREFIX):
                if str(folder) not in found:
                    found.append(str(folder))
                break
    return found


def test_record_and_hold():
    base = os.environ.get("CODEINTEL_DAEMON_BASE")
    watch = json.loads(os.environ.get("W2_56_SWEEP_WATCH") or "[]")
    entries = [entry for entry in os.environ.get("PATH", "").split(os.pathsep) if entry]
    try:
        namespace = os.readlink("/proc/self/ns/pid")
    except OSError:
        namespace = None
    note = {
        "pid": os.getpid(),
        "pid_namespace": namespace,
        "daemon_base": base,
        "daemon_base_exists": bool(base) and os.path.isdir(base),
        "temp_root": tempfile.gettempdir(),
        "links": _links(entries),
        "watched": {path: os.path.lexists(path) for path in watch},
    }
    record = Path(os.environ["W2_56_SWEEP_RECORD"])
    part = record.with_name(record.name + ".part")
    part.write_text(json.dumps(note) + "\n", encoding="utf-8")
    os.replace(part, record)

    hold = os.environ.get("W2_56_SWEEP_HOLD")
    if hold:
        end = time.monotonic() + float(os.environ.get("W2_56_SWEEP_HOLD_S") or 240)
        while not os.path.exists(hold) and time.monotonic() < end:
            time.sleep(0.05)
