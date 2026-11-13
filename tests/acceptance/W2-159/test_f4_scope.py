"""F4: no change outside the ticket's paths, judged on W2-159's own branch only (``w2/W2-159``). There,
``git diff --name-only --no-renames <base>...HEAD``, the base being the branch's merge-base with ``w2/integrate``, lists
only paths the ticket's ``allowed_paths`` match (read as the close reads them, ``gov.close.select.match``) or its own
acceptance folder (``acceptance_tests.path``, ``tests/acceptance/W2-159/``, written by the test designer and merged
into the ticket's branch).

On any other checkout the case is skipped with its reason named, never red and never passed silently: another
ticket's branch (its own paths are not W2-159's), the merge queue's candidate merge (a detached HEAD), ``w2/integrate``
itself, a clone's checkout. Also skipped, with the reason, where the ``w2/integrate`` reference or the ticket file is
absent (a plain clone). The branch is read from the repository this file sits in (``support.TREE``), never from the
current directory or an environment variable. Read-only: git is asked only ``rev-parse``, ``symbolic-ref``,
``merge-base`` and ``diff``.

The judgement is ``judge_f4_paths(root)``: the one function the real case calls with ``support.TREE`` and the planted
cases call with each planted repository (revision of W2-160, DAEO-fd0p, DEC-1156 (6), PKG-W2-160-KNOWN-1; the form
W2-180 gave W2-170's F5).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

import w2_159_support as support

TICKET = support.TREE / ".tickets" / "DAEO-6lid.md"
OWN_BRANCH = "w2/W2-159"


def _front_matter(ticket: Path) -> dict:
    return yaml.safe_load(ticket.read_text(encoding="utf-8").split("\n---", 1)[0].removeprefix("---\n"))


def _allowed(front: dict) -> list[str]:
    """The ticket's ``allowed_paths`` and its acceptance folder (``acceptance_tests.path`` + ``/**``)."""
    allowed = list(front["allowed_paths"])
    allowed.append(str(front["acceptance_tests"]["path"]).rstrip("/") + "/**")
    return allowed


def judge_f4_paths(root: Path) -> None:
    """Judge ``root``'s checkout: skip (with the reason) unless HEAD is the branch ``w2/W2-159``; there, assert that
    every path changed against the merge-base with ``w2/integrate`` is allowed by W2-159's ticket."""
    root = Path(root)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", LC_ALL="C")

    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env, timeout=60)

    ticket = root / ".tickets" / "DAEO-6lid.md"
    if git("rev-parse", "--verify", "--quiet", "w2/integrate^{commit}").returncode != 0:
        pytest.skip("F4 needs the w2/integrate reference, absent in this repository: not judged here")
    if not ticket.is_file():
        pytest.skip("F4 needs the ticket file .tickets/DAEO-6lid.md, absent here: not judged here")
    head = git("symbolic-ref", "-q", "HEAD")
    ref = head.stdout.strip() if head.returncode == 0 else ""
    if not ref.startswith("refs/heads/"):
        pytest.skip(f"F4 judges only the branch {OWN_BRANCH}; this is a detached HEAD: not judged here")
    branch = ref.removeprefix("refs/heads/")
    if branch != OWN_BRANCH:
        pytest.skip(f"F4 judges only the branch {OWN_BRANCH}; this is the branch {branch}: not judged here")
    allowed = _allowed(_front_matter(ticket))
    assert allowed, f"no allowed_paths read from {ticket}"
    base = git("merge-base", "HEAD", "w2/integrate")
    assert base.returncode == 0 and base.stdout.strip(), f"w2/integrate does not resolve: {base.stderr}"
    diff = git("-c", "core.quotePath=false", "diff", "--name-only", "--no-renames", f"{base.stdout.strip()}...HEAD")
    assert diff.returncode == 0, f"git diff failed: {diff.stderr}"
    from gov.close.select import match
    outside = [p for p in diff.stdout.splitlines() if p and not any(match(p, a) for a in allowed)]
    assert outside == [], f"changed paths not matched by the ticket's allowed_paths {allowed}: {outside}"


def test_f4_the_branch_changes_only_the_tickets_allowed_paths():
    judge_f4_paths(support.TREE)


# -- the planted cases: each in its own repository under tmp_path, judged by the same function ----------------------
OUTSIDE = "docs/changes/W2-160-evidence.md"          # not W2-159's (W2-160's own evidence file)
INSIDE = "src/gov/session_watch/inside_w2_159.py"   # W2-159's ``src/gov/session_watch/**``


def _git(repo: Path, *args: str, home: Path) -> str:
    """One git call in the planted repository, with nothing of the true home's git config read."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    date = "2026-11-01T00:00:00+00:00"
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="Planted", GIT_COMMITTER_NAME="Planted",
               GIT_AUTHOR_EMAIL="planted@example.invalid", GIT_COMMITTER_EMAIL="planted@example.invalid",
               GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    done = subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                           *args], capture_output=True, text=True, env=env, timeout=60)
    if done.returncode != 0:
        raise AssertionError(f"planting failed: git {' '.join(args)}: {done.stderr}")
    return done.stdout


def _plant(tmp_path: Path, *, branch: str, path: str, detach_merge: bool = False) -> Path:
    """A ``git init`` repository: ``w2/integrate`` holds a base commit and W2-159's ticket file (copied from this
    tree); ``branch`` (``w2/integrate`` itself, or a branch off it) holds one more commit adding ``path``. With
    ``detach_merge``: the branch is made, then HEAD is detached at ``w2/integrate`` and ``branch`` merged with
    ``--no-ff`` (the merge queue's candidate merge). Nothing of the true home's git config is read."""
    if not TICKET.is_file():
        pytest.skip("the planted cases copy the ticket file .tickets/DAEO-6lid.md, absent here: not judged here")
    home = tmp_path / "home"
    home.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", home=home)
    _git(repo, "checkout", "-q", "-b", "w2/integrate", home=home)
    (repo / ".tickets").mkdir()
    (repo / ".tickets" / TICKET.name).write_text(TICKET.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "-A", home=home)
    _git(repo, "commit", "-q", "-m", "base", home=home)
    if branch != "w2/integrate":
        _git(repo, "checkout", "-q", "-b", branch, home=home)
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text("changed\n", encoding="utf-8")
    _git(repo, "add", "-A", home=home)
    _git(repo, "commit", "-q", "-m", f"adds {path}", home=home)
    if detach_merge:
        _git(repo, "checkout", "-q", "--detach", "w2/integrate", home=home)
        _git(repo, "merge", "-q", "--no-ff", "-m", "candidate merge", branch, home=home)
    return repo


def _skipped(repo: Path) -> str:
    with pytest.raises(pytest.skip.Exception) as info:
        judge_f4_paths(repo)
    return info.value.msg


def test_f4_the_planted_paths_are_outside_and_inside_the_ticket_s_paths():
    from gov.close.select import match
    allowed = _allowed(_front_matter(TICKET))
    assert not any(match(OUTSIDE, a) for a in allowed), (OUTSIDE, allowed)
    assert any(match(INSIDE, a) for a in allowed), (INSIDE, allowed)


def test_f4_planted_w2_159_branch_with_a_change_outside_its_paths_fails(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-159", path=OUTSIDE)
    with pytest.raises(AssertionError) as info:
        judge_f4_paths(repo)
    assert OUTSIDE in str(info.value)


def test_f4_planted_w2_159_branch_with_a_change_inside_its_paths_passes(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-159", path=INSIDE)
    judge_f4_paths(repo)


def test_f4_planted_other_ticket_branch_with_the_same_change_is_skipped_with_its_reason(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-160", path=OUTSIDE)
    reason = _skipped(repo)
    assert "w2/W2-160" in reason, reason


def test_f4_planted_candidate_merge_on_a_detached_head_is_skipped_with_its_reason(tmp_path):
    repo = _plant(tmp_path, branch="w2/W2-160", path=OUTSIDE, detach_merge=True)
    head = subprocess.run(["git", "-C", str(repo), "symbolic-ref", "-q", "HEAD"], capture_output=True, text=True)
    assert head.returncode != 0, "the planted candidate merge must stand on a detached HEAD"
    merged = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%p"], capture_output=True, text=True)
    assert len(merged.stdout.split()) == 2, "the planted candidate merge must be a merge commit"
    reason = _skipped(repo)
    assert "detached HEAD" in reason, reason


def test_f4_planted_integrate_branch_itself_is_skipped_with_its_reason(tmp_path):
    repo = _plant(tmp_path, branch="w2/integrate", path=OUTSIDE)
    reason = _skipped(repo)
    assert "this is the branch w2/integrate" in reason, reason
