"""A suite that builds the code graph, for S1: run by ``test_w2_56_suite_daemon.py`` as a pytest session of its own.

Never collected by an ordinary run (its name has no ``test_`` prefix); pytest collects it only when it is named on
the command line. It runs from the repository's root, so every ``conftest.py`` on the way applies to it as to any
suite under ``tests/acceptance/``.

- ``test_the_tool_as_the_suite_sees_it`` records whether the code-graph tool is on PATH at test time.
- ``test_a_build_reaches_the_tool`` (two repositories) puts the stand-in tool first on PATH inside the test and asks
  ``gov.codeintel`` for the projects of a fresh git repository, which starts the tool with its daemon folder
  (``CBM_RUNTIME_DIR``); the stand-in records that folder. Any error is recorded, not raised.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

TOOL = "codebase-memory-mcp"


def _note(**fields) -> None:
    with Path(os.environ["W2_56_PROBE_RECORD"]).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(fields) + "\n")


def test_the_tool_as_the_suite_sees_it():
    _note(kind="which", found=shutil.which(TOOL))


@pytest.mark.parametrize("name", ("one", "two"))
def test_a_build_reaches_the_tool(tmp_path, monkeypatch, name):
    monkeypatch.setenv("PATH", os.environ["W2_56_PROBE_STANDIN"] + os.pathsep + os.environ.get("PATH", ""))
    root = tmp_path / f"repo-{name}"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    (root / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    from gov import codeintel

    error = None
    try:
        codeintel.projects(root)
    except Exception as exc:  # recorded for the test that reads the record
        error = f"{type(exc).__name__}: {exc}"
    _note(kind="build", root=str(root), error=error)
