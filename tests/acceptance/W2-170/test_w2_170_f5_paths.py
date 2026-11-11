"""F5: no change outside the ticket's paths. ``git diff --name-only <base>...HEAD`` of the branch this suite runs on,
the base being its merge-base with ``w2/integrate``, lists only paths the ticket's ``allowed_paths`` match (read as
the close reads them, ``gov.close.select.match``) or its own acceptance folder (``acceptance_tests.path``, written by
the test designer and merged into the ticket's branch). Skipped, with the reason named, where the reference or the
ticket file is absent (a plain clone): never passed silently.
"""

from __future__ import annotations

import subprocess

import pytest
import yaml

import w2_170_world as W

TICKET = W.TREE / ".tickets" / "DAEO-61vm.md"


def _git(*args):
    return subprocess.run(["git", "-C", str(W.TREE), *args], capture_output=True, text=True, timeout=60)


def test_f5_the_branch_changes_only_paths_the_ticket_allows():
    if _git("rev-parse", "--verify", "--quiet", "w2/integrate^{commit}").returncode != 0:
        pytest.skip("F5 needs the w2/integrate reference, absent in this repository: not judged here")
    if not TICKET.is_file():
        pytest.skip("F5 needs the ticket file .tickets/DAEO-61vm.md, absent here: not judged here")
    front = yaml.safe_load(TICKET.read_text(encoding="utf-8").split("\n---", 1)[0].removeprefix("---\n"))
    allowed = list(front["allowed_paths"])
    folder = str(front["acceptance_tests"]["path"]).rstrip("/")
    allowed.append(folder + "/**")
    base = _git("merge-base", "HEAD", "w2/integrate")
    assert base.returncode == 0, base.stderr
    diff = _git("-c", "core.quotePath=false", "diff", "--name-only", "--no-renames", f"{base.stdout.strip()}...HEAD")
    assert diff.returncode == 0, diff.stderr
    from gov.close.select import match
    outside = [p for p in diff.stdout.splitlines() if p and not any(match(p, a) for a in allowed)]
    assert outside == [], outside
