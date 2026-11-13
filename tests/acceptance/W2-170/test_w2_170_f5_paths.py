"""F5: no change outside the ticket's paths, judged on W2-170's own branch only (``w2/W2-170``). There,
``git diff --name-only <base>...HEAD``, the base being the branch's merge-base with ``w2/integrate``, lists only paths
the ticket's ``allowed_paths`` match (read as the close reads them, ``gov.close.select.match``) or its own acceptance
folder (``acceptance_tests.path``, written by the test designer and merged into the ticket's branch).

On any other checkout the case is skipped with its reason named, never red and never passed silently: another
ticket's branch (its own paths are not W2-170's), the merge queue's candidate merge (a detached HEAD), ``w2/integrate``
itself, a clone's checkout. Also skipped, with the reason, where the ``w2/integrate`` reference or the ticket file is
absent (a plain clone). The branch is read from the repository this file sits in (``W.TREE``), never from the current
directory or an environment variable.

The judgement is ``judge_f5_paths(root)``: the one function the case calls with ``W.TREE`` and the planted cases call
with each planted repository (revision of W2-180, DAEO-weh2, PKG-W2-171-F5-1).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

import w2_170_world as W

TICKET = W.TREE / ".tickets" / "DAEO-61vm.md"
OWN_BRANCH = "w2/W2-170"


def judge_f5_paths(root: Path) -> None:
    """Judge ``root``'s checkout: skip (with the reason) unless HEAD is the branch ``w2/W2-170``; there, assert that
    every path changed against the merge-base with ``w2/integrate`` is allowed by W2-170's ticket."""
    root = Path(root)

    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60)

    ticket = root / ".tickets" / "DAEO-61vm.md"
    if git("rev-parse", "--verify", "--quiet", "w2/integrate^{commit}").returncode != 0:
        pytest.skip("F5 needs the w2/integrate reference, absent in this repository: not judged here")
    if not ticket.is_file():
        pytest.skip("F5 needs the ticket file .tickets/DAEO-61vm.md, absent here: not judged here")
    head = git("symbolic-ref", "-q", "HEAD")
    ref = head.stdout.strip() if head.returncode == 0 else ""
    if not ref.startswith("refs/heads/"):
        pytest.skip(f"F5 judges only the branch {OWN_BRANCH}; this is a detached HEAD: not judged here")
    branch = ref.removeprefix("refs/heads/")
    if branch != OWN_BRANCH:
        pytest.skip(f"F5 judges only the branch {OWN_BRANCH}; this is the branch {branch}: not judged here")
    front = yaml.safe_load(ticket.read_text(encoding="utf-8").split("\n---", 1)[0].removeprefix("---\n"))
    allowed = list(front["allowed_paths"])
    folder = str(front["acceptance_tests"]["path"]).rstrip("/")
    allowed.append(folder + "/**")
    base = git("merge-base", "HEAD", "w2/integrate")
    assert base.returncode == 0, base.stderr
    diff = git("-c", "core.quotePath=false", "diff", "--name-only", "--no-renames", f"{base.stdout.strip()}...HEAD")
    assert diff.returncode == 0, diff.stderr
    from gov.close.select import match
    outside = [p for p in diff.stdout.splitlines() if p and not any(match(p, a) for a in allowed)]
    assert outside == [], outside


def test_f5_the_branch_changes_only_paths_the_ticket_allows():
    judge_f5_paths(W.TREE)


# -- the planted cases: each in its own repository under tmp_path, judged by the same function ----------------------
OUTSIDE = "docs/changes/W2-171-evidence.md"          # not W2-170's (W2-171's own evidence file)
INSIDE = "src/gov/memaudit/inside_w2_170.py"        # W2-170's ``src/gov/memaudit/**``


def _plant(tmp_path: Path, *, branch: str, path: str, detach_merge: bool = False) -> Path:
    """A ``git init`` repository: ``w2/integrate`` holds a base commit and W2-170's ticket file (copied from this
    tree); ``branch`` (``w2/integrate`` itself, or a branch off it) holds one more commit adding ``path``. With
    ``detach_merge``: the branch is made, then HEAD is detached at ``w2/integrate`` and ``branch`` merged with
    ``--no-ff`` (the merge queue's candidate merge). Nothing of the true home's git config is read."""
    if not TICKET.is_file():
        pytest.skip("the planted cases copy the ticket file .tickets/DAEO-61vm.md, absent here: not judged here")
    home = tmp_path / "home"
    home.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    ident = ["-c", "user.name=Planted", "-c", "user.email=planted@example.invalid", "-c", "commit.gpgsign=false",
             "-c", "core.hooksPath=/dev/null"]

    def git(*args):
        return W.git(repo, *ident, *args, home=home)

    git("init", "-q")
    git("checkout", "-q", "-b", "w2/integrate")
    (repo / ".tickets").mkdir()
    (repo / ".tickets" / TICKET.name).write_text(TICKET.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    if branch != "w2/integrate":
        git("checkout", "-q", "-b", branch)
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text("changed\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", f"adds {path}")
    if detach_merge:
        git("checkout", "-q", "--detach", "w2/integrate")
        git("merge", "-q", "--no-ff", "-m", "candidate merge", branch)
    return repo


def _skipped(repo: Path):
    with pytest.raises(pytest.skip.Exception) as info:
        judge_f5_paths(repo)
    return info.value.msg


def test_f5_the_planted_paths_are_outside_and_inside_the_ticket_s_paths():
    from gov.close.select import match
    front = yaml.safe_load(TICKET.read_text(encoding="utf-8").split("\n---", 1)[0].removeprefix("---\n"))
    allowed = list(front["allowed_paths"]) + [str(front["acceptance_tests"]["path"]).rstrip("/") + "/**"]
    assert not any(match(OUTSIDE, a) for a in allowed), (OUTSIDE, allowed)
    assert any(match(INSIDE, a) for a in allowed), (INSIDE, allowed)


def test_f5_planted_w2_170_branch_with_a_change_outside_its_paths_fails(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-170", path=OUTSIDE)
    with pytest.raises(AssertionError) as info:
        judge_f5_paths(repo)
    assert OUTSIDE in str(info.value)


def test_f5_planted_w2_170_branch_with_a_change_inside_its_paths_passes(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-170", path=INSIDE)
    judge_f5_paths(repo)


def test_f5_planted_other_ticket_branch_with_the_same_change_is_skipped_with_its_reason(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-171", path=OUTSIDE)
    reason = _skipped(repo)
    assert "w2/W2-171" in reason, reason


def test_f5_planted_candidate_merge_on_a_detached_head_is_skipped_with_its_reason(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-171", path=OUTSIDE, detach_merge=True)
    head = subprocess.run(["git", "-C", str(repo), "symbolic-ref", "-q", "HEAD"], capture_output=True, text=True)
    assert head.returncode != 0, "the planted candidate merge must stand on a detached HEAD"
    merged = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%p"], capture_output=True, text=True)
    assert len(merged.stdout.split()) == 2, "the planted candidate merge must be a merge commit"
    reason = _skipped(repo)
    assert "detached HEAD" in reason, reason


def test_f5_planted_integrate_branch_itself_is_skipped_with_its_reason(tmp_path):
    repo = _plant(tmp_path, branch="w2/integrate", path=OUTSIDE)
    reason = _skipped(repo)
    assert "this is the branch w2/integrate" in reason, reason
