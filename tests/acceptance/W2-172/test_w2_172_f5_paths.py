"""F5: no change outside the ticket's paths. ``git diff --name-only <base>...HEAD`` of the branch this suite runs on, the base
being its merge-base with ``w2/integrate``, lists only paths the ticket's ``allowed_paths`` match (read as the close reads
them, ``gov.close.select.match``) or its own acceptance folder (``acceptance_tests.path``).

It judges only the ticket's own branch, ``w2/W2-172`` (DECIDED-NOT-DONE row 171): on any other branch (this tests' branch
``w2/W2-172-tests`` included) it is skipped, with the reason named, never passed silently; it is skipped too without the
``w2/integrate`` reference or the ticket file (a plain clone).
"""

from __future__ import annotations

import subprocess

import pytest
import yaml

import w2_172_world as W

TICKET = W.TREE / ".tickets" / "DAEO-p8tv.md"
BRANCH = "w2/W2-172"


def _git(*args):
    return subprocess.run(["git", "-C", str(W.TREE), *args], capture_output=True, text=True, timeout=60)


def test_f5_the_branch_changes_only_paths_the_ticket_allows():
    head = _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if head != BRANCH:
        pytest.skip(f"F5 judges only the ticket's branch {BRANCH} (this one is {head!r}): not judged here")
    if _git("rev-parse", "--verify", "--quiet", "w2/integrate^{commit}").returncode != 0:
        pytest.skip("F5 needs the w2/integrate reference, absent in this repository: not judged here")
    if not TICKET.is_file():
        pytest.skip("F5 needs the ticket file .tickets/DAEO-p8tv.md, absent here: not judged here")
    front = yaml.safe_load(TICKET.read_text(encoding="utf-8").split("\n---", 1)[0].removeprefix("---\n"))
    allowed = list(front["allowed_paths"])
    allowed.append(str(front["acceptance_tests"]["path"]).rstrip("/") + "/**")
    base = _git("merge-base", "HEAD", "w2/integrate")
    assert base.returncode == 0, base.stderr
    diff = _git("-c", "core.quotePath=false", "diff", "--name-only", "--no-renames", f"{base.stdout.strip()}...HEAD")
    assert diff.returncode == 0, diff.stderr
    from gov.close.select import match
    outside = [p for p in diff.stdout.splitlines() if p and not any(match(p, a) for a in allowed)]
    assert outside == [], outside
