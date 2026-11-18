"""The queue's checks of a work branch before any run (W2-115b success 5 and 6), on ``<base>..<tip>``.

- **G-1, who wrote the acceptance tests** (MR-3, DEC-1050 (12)), ported from the landing tool's
  ``acceptance_authors``: a non-merge commit that changes a path under one of the acceptance places counts; a
  two-parent merge counts when its result there differs from git's own merge of its parents (``--remerge-diff``),
  an octopus merge when it differs from its first parent. A counted commit passes only with at least one ``Role:``
  trailer, each of them ``independent-test-designer`` or ``owner``.
- **The path notice** (audit 7 C-6): every path a non-merge commit changes outside the ticket's ``allowed_paths``
  and its own record places is listed; it never refuses.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from gov.util.gitenv import git_env

TEST_ROLES = ("independent-test-designer", "owner")
ACCEPTANCE = "tests/acceptance/"


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-c", "core.quotePath=false", "-C", str(root), *args], capture_output=True,
                          text=True, env=git_env(root))
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {' '.join(done.stderr.split())[:200]}")
    return done.stdout


def _under(path: str, places: list[str]) -> bool:
    return any(path == p.rstrip("/") or path.startswith(p.rstrip("/") + "/") for p in places if p.strip("/"))


def test_authors(root: Path, base: str, tip: str, places: list[str]) -> list[dict]:
    """The commits of ``base..tip`` that change ``places`` without the role that may: ``{"commit", "roles",
    "subject"}`` each. ``RuntimeError`` where git cannot read them (the caller refuses: fails closed)."""
    places = [p for p in places if p and p.strip("/")]
    touched = _git(root, "rev-list", "--full-history", "--no-merges", f"{base}..{tip}", "--", *places).split()
    for merge in _git(root, "rev-list", "--merges", f"{base}..{tip}").split():
        if len(_git(root, "rev-list", "--parents", "-n", "1", merge).split()) == 3:
            names = _git(root, "log", "-1", "--remerge-diff", "--format=", "--name-only", merge).splitlines()
        else:
            names = _git(root, "diff", "--name-only", f"{merge}^1", merge).splitlines()
        if any(_under(n, places) for n in names):
            touched.append(merge)
    bad = []
    for commit in touched:
        roles, _, subject = _git(root, "log", "-1", "--format=%(trailers:key=Role,valueonly,separator=%x1f)%x00%s",
                                 commit).rstrip("\n").partition("\x00")
        roles = [r.strip() for r in roles.split("\x1f") if r.strip()]
        if not roles or any(r not in TEST_ROLES for r in roles):
            bad.append({"commit": commit, "roles": roles, "subject": subject[:120]})
    return bad


def record_places(ticket: str, acceptance: str | None) -> list[str]:
    """A ticket's own record places: its ticket file, close record, checkpoints and acceptance suite."""
    own = [f".tickets/{ticket}.md", f"docs/close/{ticket}/", f"docs/checkpoints/{ticket}/"]
    return own + ([acceptance] if acceptance and acceptance.strip("/") else [])


def path_notices(root: Path, base: str, tip: str, allowed: list[str], own: list[str]) -> list[dict]:
    """``{"commit", "path"}`` for each path a non-merge commit of ``base..tip`` changes outside ``allowed`` (the
    ``allowed_paths`` grammar) and outside ``own`` (record places: a file, or a folder ending ``/``)."""
    from gov.close.select import match

    notices = []
    for commit in _git(root, "rev-list", "--no-merges", "--reverse", f"{base}..{tip}").split():
        names = _git(root, "diff-tree", "-z", "--no-commit-id", "--name-only", "-r", "--no-renames", "--root",
                     commit).split("\0")
        for path in sorted(filter(None, names)):
            if any(match(path, p) for p in allowed) or _under(path, own):
                continue
            notices.append({"commit": commit, "path": path})
    return notices
