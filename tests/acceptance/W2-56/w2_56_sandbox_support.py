"""Support for W2-56's second half, the guard-alone outcome (DEC-1112 (1)): standard library, PyYAML, gov's constants.

Built on ``w2_56_support`` (the fixture project, the stand-in CLI, the launch helpers). What it adds:

- **The session's temp folder**, the ``TMPDIR`` the launcher handed the CLI.
- **The reranker's own setting** (W2-112): the socket is ``<HOME>/.cache/gov-os/rerank.sock``, read from
  ``gov.retrieval.rerank`` (``CACHE_REL``, ``SOCKET``) with the launcher's ``HOME``.
- **The guard**: the kernel's PreToolUse hook (``template/governance/kernel/hooks/pretooluse.py``), copied into the
  fixture project at ``governance/kernel/hooks/pretooluse.py`` (where its settings point) and run as the harness runs
  it: the call as event JSON on stdin, the session's role and ticket in ``GOV_ROLE`` and ``GOV_TICKET`` (W2-58's form).
- **A command in the session**: a stand-in plan step (``run``) that runs Python with the session's own environment
  (the one the launcher handed the CLI), the tree's ``src`` put on ``sys.path`` by the code itself (the launcher keeps
  ``PYTHONPATH`` from the session, S5).
- **A planted reranker** under the planted ``HOME``: its interpreter file, and a stand-in service on the socket (a
  thread of the test's own process; never the live service).

Emergency 2 (release 0.1.2): the launcher writes no sandbox block, and the helpers that read it are retired.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

import w2_56_support as s

GUARD_SOURCE = s.REPO_ROOT / "template/governance/kernel/hooks/pretooluse.py"
GUARD_REL = "governance/kernel/hooks/pretooluse.py"
REAL_TMP_ROOT = "/tmp"             # the launcher's temp root outside a test: a test's own root is projected onto it

# A ticket whose allowed paths hold a name pattern (S3) beside a folder and a single file.
PATTERN = s.Ticket("DAEO-zw64", s.ENGINEER, "W2-85", ("src/app/**", "tests/unit/test_batch*", "docs/one.md"))


# --------------------------------------------------------------------------
# The session's folders
# --------------------------------------------------------------------------


def under(path: str, folder: str) -> bool:
    path, folder = os.path.realpath(path), os.path.realpath(folder)
    return path == folder or path.startswith(folder.rstrip("/") + "/")


# --------------------------------------------------------------------------
# The reranker's setting (W2-112)
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# A command in the session (the stand-in's ``run`` step)
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Projects and launches
# --------------------------------------------------------------------------

def project(box: s.Box, extra=None, guard=False, tickets=(PATTERN,)) -> Path:
    files = {f".tickets/{ticket.tk}.md": s.ticket_text(ticket) for ticket in tickets}
    if guard:
        files[GUARD_REL] = GUARD_SOURCE.read_text(encoding="utf-8")
    files.update(extra or {})
    made = s.make_project(box, extra=files)
    s.install_stand_in_cli(box)
    s.set_plan(box)
    return made


def started(launch) -> dict:
    assert launch.returncode == 0 and launch.started, f"the launch did not start one session\n{launch.describe()}"
    return launch.settings()


def short_base(prefix: str) -> Path | None:
    """A short folder of the test's own (a Unix socket path holds at most 107 bytes): under /tmp when it is
    writable, else under the temp root; None when neither can be had."""
    for root in (REAL_TMP_ROOT, tempfile.gettempdir()):
        try:
            return Path(tempfile.mkdtemp(prefix=prefix, dir=root)).resolve()
        except OSError:
            continue
    return None


def remove(folder) -> None:
    if folder is not None:
        shutil.rmtree(folder, ignore_errors=True)


# --------------------------------------------------------------------------
# The guard (the kernel's PreToolUse hook, as the harness runs it)
# --------------------------------------------------------------------------

