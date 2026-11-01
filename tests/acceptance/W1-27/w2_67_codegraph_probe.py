"""The nested run's plugin for ``test_w2_67_codegraph_folders.py`` (``-p w2_67_codegraph_probe``; W2-67 batch 8).

While the case runs (its call, after its fixtures are set up), it plants the folders named in
``W2_67_CODEGRAPH_FOREIGN`` under ``/tmp/gov-cbm-<uid>``: another worker's daemon folders, made while this case runs.
When the call is over and before the case's fixtures end, it writes to ``W2_67_CODEGRAPH_SEEN`` one JSON line for
every git project under the run's ``TMPDIR`` (all of them this run's) with the code index's daemon folder of its
root and whether it was there then: the proof that the case reached the code index. It removes nothing.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

import pytest

BASE = Path(f"/tmp/gov-cbm-{os.getuid()}")


def daemon_folder(root):
    return BASE / hashlib.sha256(os.fsencode(Path(root).resolve())).hexdigest()[:16]


def projects(top):
    """Every git project under ``top``: a folder holding ``.git``."""
    for dirpath, dirnames, filenames in os.walk(top):
        if ".git" in dirnames or ".git" in filenames:
            yield Path(dirpath)
        dirnames[:] = [name for name in dirnames if name not in (".git", ".gov-runtime", "__pycache__")]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    for name in filter(None, os.environ.get("W2_67_CODEGRAPH_FOREIGN", "").split(",")):
        BASE.mkdir(mode=0o700, exist_ok=True)
        (BASE / name).mkdir(mode=0o700)
        (BASE / name / "cbm-daemon-planted").mkdir(mode=0o700)
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    with open(os.environ["W2_67_CODEGRAPH_SEEN"], "a", encoding="utf-8") as seen:
        for root in projects(tempfile.gettempdir()):
            folder = daemon_folder(root)
            seen.write(json.dumps({"case": item.nodeid, "root": str(root), "folder": str(folder),
                                   "there": folder.is_dir()}) + "\n")
    yield
