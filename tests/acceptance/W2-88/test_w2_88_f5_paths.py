"""The path case (DEC-1155): the branch changes only the ticket's ``allowed_paths`` (or its own acceptance folder, which the
test designer writes and merges into the ticket's branch). Judged on the branch ``w2/W2-88`` only: on any other checkout the
case is skipped with its reason named (the branch found), never red and never passed silently. Paths are compared with the
close's own glob matcher (``gov.close.select.match``) against the ticket's ``allowed_paths``, never by a text search of a path.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

import w2_88_support as W

OWN_BRANCH = "w2/W2-88"
TICKET_NAME = "DAEO-2bdu.md"
OUTSIDE = "docs/changes/W2-171-evidence.md"      # another ticket's evidence file
INSIDE = "src/gov/adopt/assess.py"               # this ticket's own


def _git(root, *args, env=None):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60, env=env)


def judge(root: Path) -> None:
    root = Path(root)
    ticket = root / ".tickets" / TICKET_NAME
    if _git(root, "rev-parse", "--verify", "--quiet", "w2/integrate^{commit}").returncode != 0:
        pytest.skip("this check needs the w2/integrate reference, absent here: not judged here")
    if not ticket.is_file():
        pytest.skip(f"this check needs {ticket.relative_to(root)}, absent here: not judged here")
    found = _git(root, "symbolic-ref", "-q", "HEAD")
    ref = found.stdout.strip() if found.returncode == 0 else ""
    if not ref.startswith("refs/heads/"):
        pytest.skip(f"this check judges only the branch {OWN_BRANCH}; this is a detached HEAD: not judged here")
    branch = ref.removeprefix("refs/heads/")
    if branch != OWN_BRANCH:
        pytest.skip(f"this check judges only the branch {OWN_BRANCH}; this is the branch {branch}: not judged here")
    front = yaml.safe_load(ticket.read_text(encoding="utf-8").split("\n---", 1)[0].removeprefix("---\n"))
    allowed = list(front["allowed_paths"]) + [str(front["acceptance_tests"]["path"]).rstrip("/") + "/**"]
    base = _git(root, "merge-base", "HEAD", "w2/integrate")
    assert base.returncode == 0, base.stderr
    diff = _git(root, "-c", "core.quotePath=false", "diff", "--name-only", "--no-renames", f"{base.stdout.strip()}...HEAD")
    assert diff.returncode == 0, diff.stderr
    from gov.close.select import match
    outside = [p for p in diff.stdout.splitlines() if p and not any(match(p, a) for a in allowed)]
    assert outside == [], f"the branch changes paths the ticket does not allow: {outside}"


def test_f5_the_branch_changes_only_the_tickets_allowed_paths():
    judge(W.REPO_ROOT)


def _plant(tmp_path, branch, path):
    ticket = W.REPO_ROOT / ".tickets" / TICKET_NAME
    if not ticket.is_file():
        pytest.skip(f"the planted cases copy {TICKET_NAME}, absent here: not judged here")
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "PATH": "/usr/bin:/bin"}
    ident = ["-c", "user.name=Planted", "-c", "user.email=planted@example.invalid", "-c", "commit.gpgsign=false"]

    def git(*args):
        done = subprocess.run(["git", "-C", str(repo), *ident, *args], capture_output=True, text=True, env=env, timeout=60)
        assert done.returncode == 0, done.stderr
    git("init", "-q", "-b", "w2/integrate")
    (repo / ".tickets").mkdir()
    (repo / ".tickets" / TICKET_NAME).write_text(ticket.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    if branch != "w2/integrate":
        git("checkout", "-q", "-b", branch)
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text("changed\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", f"adds {path}")
    return repo


def test_f5_a_planted_branch_with_a_change_outside_the_paths_fails(tmp_path):
    with pytest.raises(AssertionError) as info:
        judge(_plant(tmp_path, OWN_BRANCH, OUTSIDE))
    assert OUTSIDE in str(info.value)


def test_f5_a_planted_branch_with_a_change_inside_the_paths_passes(tmp_path):
    judge(_plant(tmp_path, OWN_BRANCH, INSIDE))


def test_f5_another_tickets_branch_is_skipped_with_the_branch_named(tmp_path):
    repo = _plant(tmp_path, "w2/W2-171", OUTSIDE)
    with pytest.raises(pytest.skip.Exception) as info:
        judge(repo)
    assert "w2/W2-171" in info.value.msg, info.value.msg
