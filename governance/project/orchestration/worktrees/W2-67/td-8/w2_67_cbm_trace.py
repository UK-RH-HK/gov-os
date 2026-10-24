"""Batch 8's tracer (``-p w2_67_cbm_trace``, this folder on PYTHONPATH): which case leaves which daemon folder.

After each test's call and before its fixtures end (a hook wrapper of ``pytest_runtest_teardown``, before its
``yield``), and again at the end of the session, every git project under the run's TMPDIR is mapped to the code
index's daemon folder of its resolved root (``/tmp/gov-cbm-<uid>/`` and the first 16 hex digits of the sha256 of
that root, ``gov.codeintel.daemon_dir``'s rule) and each folder that exists is written, with the case, to the JSON
lines file named by ``W2_67_CBM_TRACE``. TMPDIR is this test designer's own, so every project found is this run's.
It only reads: nothing under ``/tmp/gov-cbm-<uid>`` is written or removed.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

import pytest

BASE = Path(f"/tmp/gov-cbm-{os.getuid()}")
SKIP = {".git", ".gov-runtime", "node_modules", "__pycache__", ".venv"}


def _folder(root: Path) -> Path:
    return BASE / hashlib.sha256(os.fsencode(root.resolve())).hexdigest()[:16]


def _projects(top: Path):
    for dirpath, dirnames, filenames in os.walk(top):
        if ".git" in dirnames or ".git" in filenames:
            yield Path(dirpath)
        dirnames[:] = [name for name in dirnames if name not in SKIP]


def _holders(folder: Path) -> list[int]:
    """The processes whose environment names ``folder`` as the tool's runtime directory."""
    found, wanted = [], b"CBM_RUNTIME_DIR=" + os.fsencode(folder)
    for proc in Path("/proc").iterdir():
        if proc.name.isdigit():
            try:
                if wanted in (proc / "environ").read_bytes().split(b"\0"):
                    found.append(int(proc.name))
            except OSError:
                pass
    return found


def _write(item_id: str, when: str) -> None:
    log = os.environ.get("W2_67_CBM_TRACE")
    if not log:
        return
    top = Path(tempfile.gettempdir())
    rows = []
    for root in _projects(top):
        folder = _folder(root)
        if folder.exists():
            rows.append({"case": item_id, "when": when, "root": str(root), "folder": folder.name,
                         "entries": sorted(p.name for p in folder.rglob("*"))[:20], "holders": _holders(folder),
                         "worker": os.environ.get("PYTEST_XDIST_WORKER", "main")})
    with open(log, "a", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row) + "\n")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    _write(item.nodeid, "before-teardown")
    yield


def pytest_sessionfinish(session, exitstatus):
    _write("<session end>", "session-finish")
