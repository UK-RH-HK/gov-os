"""The nested run's plugin for ``test_w2_67_codegraph_folders.py`` (``-p w2_67_codegraph_probe``; W2-67 batch 8).

The daemon folders' place is read, never written here (revised by the test designer with W2-56's S1, DEC-1099 (1)):

- **Where the code index really put each folder.** Before the case's fixtures and again before its call, a pass-through
  stand-in named ``codebase-memory-mcp`` is put first on ``PATH``: it notes the ``CBM_RUNTIME_DIR`` it is given (the
  daemon folder ``gov.codeintel`` made for the project, in whatever process built it, with whatever ``TMPDIR`` that
  process had) and then runs the tool found on ``PATH`` without it, unchanged, or ends as a missing tool ends when
  there is none (W2-56 takes the real tool off ``PATH`` outside W1-16 and W1-20). The stand-in's path for its notes is
  written into it, since W1-27's ``gov`` runs get an environment built from scratch.
- **Another worker's folders.** While the case runs (its call, after its fixtures are set up), it plants the folders
  named in ``W2_67_CODEGRAPH_FOREIGN`` beside this process's own daemon folders (the folder that holds
  ``gov.codeintel.daemon_dir`` of any root here): another worker's daemon folders, made while this case runs.

It writes to ``W2_67_CODEGRAPH_SEEN`` one JSON line per daemon folder: when the call is over and before the case's
fixtures end, every folder the stand-in was given and the folder ``gov.codeintel`` names here for every git project
under the run's ``TMPDIR`` (all of them this run's), with whether it was there then (the proof that the case reached
the code index); and, once the case's own fixtures have ended (its clean-up done) and before the session's end, one
line per planted folder with whether it is still there. It removes nothing.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

TOOL = "codebase-memory-mcp"
_planted: list[Path] = []


def _seen() -> Path:
    return Path(os.environ["W2_67_CODEGRAPH_SEEN"])


def _stand_in_dir() -> Path:
    return _seen().parent / "w2-67-cbm-stand-in"


def _calls() -> Path:
    return _seen().parent / "w2-67-cbm-calls.txt"


def daemon_folder(root) -> Path:
    from gov.codeintel import daemon_dir

    return Path(daemon_dir(Path(root)))


def projects(top):
    """Every git project under ``top``: a folder holding ``.git``."""
    for dirpath, dirnames, filenames in os.walk(top):
        if ".git" in dirnames or ".git" in filenames:
            yield Path(dirpath)
        dirnames[:] = [name for name in dirnames if name not in (".git", ".gov-runtime", "__pycache__")]


def _put_stand_in_first():
    """The pass-through stand-in, first on PATH (again, if something took it off since)."""
    folder = _stand_in_dir()
    entries = [entry for entry in os.environ.get("PATH", "").split(os.pathsep) if entry and entry != str(folder)]
    real = shutil.which(TOOL, path=os.pathsep.join(entries))
    folder.mkdir(parents=True, exist_ok=True)
    run = f'exec "{real}" "$@"\n' if real else f'echo "{TOOL}: not found" >&2\nexit 127\n'
    script = folder / TOOL
    script.write_text(f'#!/bin/sh\nprintf \'%s\\n\' "$CBM_RUNTIME_DIR" >> "{_calls()}"\n{run}', encoding="utf-8")
    script.chmod(0o755)
    os.environ["PATH"] = os.pathsep.join([str(folder), *entries])


def _rows(case: str) -> list[dict]:
    given = _calls().read_text(encoding="utf-8").split() if _calls().is_file() else []
    named = {}
    for root in projects(tempfile.gettempdir()):
        try:
            named[str(daemon_folder(root))] = str(root)
        except Exception:
            pass
    roots = {hashlib.sha256(os.fsencode(Path(r).resolve())).hexdigest(): r for r in named.values()}
    rows = []
    for folder in sorted(set(given) | set(named)):
        root = named.get(folder) or next((r for h, r in roots.items() if h.startswith(Path(folder).name)), "")
        rows.append({"kind": "project", "case": case, "root": root, "folder": folder,
                     "there": Path(folder).is_dir()})
    return rows


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    _put_stand_in_first()
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    _put_stand_in_first()
    names = list(filter(None, os.environ.get("W2_67_CODEGRAPH_FOREIGN", "").split(",")))
    if names:
        base = daemon_folder(tempfile.gettempdir()).parent
        base.mkdir(mode=0o700, parents=True, exist_ok=True)
        for name in names:
            (base / name).mkdir(mode=0o700)       # never one that is there already
            (base / name / "cbm-daemon-planted").mkdir(mode=0o700)
            _planted.append(base / name)
    yield


@pytest.fixture(autouse=True)
def w2_67_planted_after_the_case():
    """Set up before the suite's own fixtures (a plugin's), so it ends after them: after the case's clean-up, before
    the session's end."""
    yield
    with _seen().open("a", encoding="utf-8") as seen:
        for path in _planted:
            seen.write(json.dumps({"kind": "foreign", "path": str(path),
                                   "there": (path / "cbm-daemon-planted").is_dir()}) + "\n")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    with _seen().open("a", encoding="utf-8") as seen:
        for row in _rows(item.nodeid):
            seen.write(json.dumps(row) + "\n")
    yield
