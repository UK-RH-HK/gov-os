"""W2-88 run 6: the narrow check's NC-1 (A9's own record commit: a refused commit undoes only what A9 did, never a
reset) and NC-2 (an interrupt the moment the copies' ``git add`` returns leaves no copy in the index), as the
engineer's own unit tests. In process, with stand-ins for the keyword index, the embedder and the code graph."""
from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

from gov.adopt import project
from gov.cli.errors import GovError

from .test_w2_88_fabric import ENV, git, stand_ins  # noqa: F401  (stand_ins is a fixture)
from .test_w2_88_run4 import expected_copies, run_a9
from .test_w2_88_rv2 import BRIEF, copies, fresh, indexed, no_copy_left, out_of, status

RECORD = "governance/adoption/A9-memory-fabric.md"
WORD = "nc1-hook-refuses-7f3q"
REPO = Path(__file__).resolve().parents[3]


def refusing_hook(root):
    hook = root / ".git/hooks/pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(f"#!/bin/sh\necho {WORD} >&2\nexit 1\n")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def acting_before_the_commit(monkeypatch, act):
    """A stand-in for ``gov.rebuild.command.run`` that acts, then calls the real one, so A9 reaches its commit."""
    import gov.rebuild.command as rebuild

    real = rebuild.run

    def stand_in(root, args, config):
        act(root)
        return real(root, args, config)

    monkeypatch.setattr(rebuild, "run", stand_in)


def edit_and_stage(repo):
    (repo / "a.md").write_bytes(b"edited during the run\n")
    (repo / "new.txt").write_text("staged during the run\n")
    git(repo, "add", "new.txt")


def no_project_commit(monkeypatch):
    """W2-23's ``project.commit`` and ``project.restore`` are not on A9's path."""
    def never(*args, **kwargs):
        raise AssertionError("A9 called W2-23's project.commit or project.restore")

    monkeypatch.setattr(project, "commit", never)
    monkeypatch.setattr(project, "restore", never)


def nothing_of_a9_left(root):
    no_copy_left(root)
    assert not os.path.lexists(root / RECORD) and RECORD not in indexed(root)
    assert not (root / ".claude").exists() and not (root / "governance/kernel").exists()
    assert not (root / "governance/adoption").exists()  # the folder A9 made for its record


# ---- NC-1: the record commit is refused

def test_a_refused_record_commit_undoes_only_a9_and_is_adopt_git_failed(tmp_path, stand_ins, monkeypatch):
    root = fresh(tmp_path)
    start = out_of(root, "rev-parse", "HEAD").strip()
    branch = out_of(root, "symbolic-ref", "HEAD").strip()
    reflog = out_of(root, "reflog", "--format=%gs")
    refusing_hook(root)
    no_project_commit(monkeypatch)
    acting_before_the_commit(monkeypatch, edit_and_stage)
    with pytest.raises(GovError) as caught:
        run_a9(root, tmp_path / "out")
    refusal = caught.value
    assert refusal.code == "ADOPT_GIT_FAILED"
    assert refusal.details["exit_code"] == 1
    assert "git commit" in refusal.message and WORD in refusal.message
    assert out_of(root, "rev-parse", "HEAD").strip() == start
    assert out_of(root, "symbolic-ref", "HEAD").strip() == branch
    assert out_of(root, "rev-parse", branch).strip() == start
    assert out_of(root, "reflog", "--format=%gs") == reflog  # no reset, no commit
    assert (root / "a.md").read_bytes() == b"edited during the run\n"
    assert out_of(root, "diff", "--cached", "--name-status").splitlines() == ["A\tnew.txt"]
    nothing_of_a9_left(root)
    assert status(root) == sorted([" M a.md", "A  new.txt"])


def test_a_refused_record_commit_after_head_moved_is_head_moved_with_its_cause(tmp_path, stand_ins, monkeypatch):
    root = fresh(tmp_path)
    start = out_of(root, "rev-parse", "HEAD").strip()
    no_project_commit(monkeypatch)

    def act(repo):
        (repo / "notes.md").write_text("notes\n")
        git(repo, "add", "notes.md")
        git(repo, "commit", "-q", "-m", "notes", "--", "notes.md")
        refusing_hook(repo)  # after the commit made during the run: only A9's record commit meets it

    acting_before_the_commit(monkeypatch, act)
    with pytest.raises(GovError) as caught:
        run_a9(root, tmp_path / "out")
    new = out_of(root, "rev-parse", "HEAD").strip()
    assert new != start
    assert caught.value.code == "HEAD_MOVED"
    assert caught.value.details == {"started": start, "now": new, "cause": "ADOPT_GIT_FAILED"}
    assert caught.value.__cause__.code == "ADOPT_GIT_FAILED" and caught.value.__cause__.details["exit_code"] == 1
    assert out_of(root, "reflog", "-1", "--format=%H %gs").strip() == f"{new} commit: notes"
    nothing_of_a9_left(root)
    assert status(root) == []


def test_an_interrupt_during_the_record_commit_undoes_only_a9_and_stays_an_interrupt(tmp_path, stand_ins, monkeypatch):
    root = fresh(tmp_path)
    start = out_of(root, "rev-parse", "HEAD").strip()
    acting_before_the_commit(monkeypatch, edit_and_stage)
    real = subprocess.run

    def interrupting(cmd, *args, **kwargs):
        if isinstance(cmd, list) and "commit" in cmd and "-m" in cmd:
            raise KeyboardInterrupt()
        return real(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", interrupting)
    with pytest.raises(KeyboardInterrupt):
        run_a9(root, tmp_path / "out")
    monkeypatch.setattr(subprocess, "run", real)
    assert out_of(root, "rev-parse", "HEAD").strip() == start
    assert (root / "a.md").read_bytes() == b"edited during the run\n"
    nothing_of_a9_left(root)
    assert status(root) == sorted([" M a.md", "A  new.txt"])


def test_a_successful_record_commit_is_unchanged(tmp_path, stand_ins, monkeypatch):
    root = fresh(tmp_path)
    start = out_of(root, "rev-parse", "HEAD").strip()
    no_project_commit(monkeypatch)
    done = run_a9(root, tmp_path / "out")
    assert done["ok"] is True and done["record"] == RECORD
    assert out_of(root, "rev-parse", "HEAD~1").strip() == start  # one commit
    assert out_of(root, "log", "-1", "--format=%s").strip() == "gov adopt --lite A9: memory fabric"
    changed = out_of(root, "show", "--name-only", "--format=", "HEAD").split()
    assert sorted(changed) == sorted([*copies(), RECORD])
    text = (root / RECORD).read_text(encoding="utf-8")
    assert text.startswith("---\nid: ADOPT-A9\n") and "\nsession: s\nstands_on: null\n" in text
    assert status(root) == []


def test_an_untracked_file_at_the_records_path_is_refused_and_kept_and_a9_undone(tmp_path, stand_ins, monkeypatch):
    root = fresh(tmp_path)
    start = out_of(root, "rev-parse", "HEAD").strip()
    mine = b"someone else's record\n"

    def act(repo):
        (repo / RECORD).parent.mkdir(parents=True)
        (repo / RECORD).write_bytes(mine)

    acting_before_the_commit(monkeypatch, act)
    with pytest.raises(GovError) as caught:
        run_a9(root, tmp_path / "out")
    assert caught.value.code == "ADOPT_WOULD_OVERWRITE" and caught.value.details["paths"] == [RECORD]
    assert (root / RECORD).read_bytes() == mine
    assert out_of(root, "rev-parse", "HEAD").strip() == start
    no_copy_left(root)
    assert not (root / ".claude").exists() and not (root / "governance/kernel").exists()
    assert status(root) == [f"?? {RECORD}"]


# ---- NC-2: an interrupt the moment the copies' git add returns

def interrupt_after_the_copies_add(monkeypatch, fired):
    planned = set(copies())
    real = subprocess.run

    def wrapped(cmd, *args, **kwargs):
        done = real(cmd, *args, **kwargs)
        if not fired and isinstance(cmd, list) and "add" in cmd and planned & set(cmd):
            fired.append(cmd)
            raise KeyboardInterrupt()
        return done

    monkeypatch.setattr(subprocess, "run", wrapped)
    return real


def test_an_interrupt_the_moment_the_copies_add_returns_leaves_no_copy_in_the_index(tmp_path, stand_ins, monkeypatch):
    root = fresh(tmp_path)
    start = out_of(root, "rev-parse", "HEAD").strip()
    fired = []
    real = interrupt_after_the_copies_add(monkeypatch, fired)
    with pytest.raises(KeyboardInterrupt):
        run_a9(root, tmp_path / "out")
    monkeypatch.setattr(subprocess, "run", real)
    assert fired, "the plant did not take"
    assert out_of(root, "rev-parse", "HEAD").strip() == start
    no_copy_left(root)
    assert not (root / ".claude").exists() and not (root / "governance/kernel").exists()
    assert status(root) == []


def test_an_interrupt_after_the_add_gives_a_replaced_tracked_file_back(tmp_path, stand_ins, monkeypatch):
    root = fresh(tmp_path)
    (root / BRIEF).parent.mkdir(parents=True)
    (root / BRIEF).write_bytes(b"the repository's own brief\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "own brief")
    fired = []
    real = interrupt_after_the_copies_add(monkeypatch, fired)
    with pytest.raises(KeyboardInterrupt):
        run_a9(root, tmp_path / "out")
    monkeypatch.setattr(subprocess, "run", real)
    assert fired, "the plant did not take"
    assert (root / BRIEF).read_bytes() == b"the repository's own brief\n"
    assert BRIEF in indexed(root)
    no_copy_left(root, keep=(BRIEF,))
    assert status(root) == []


# ---- W2-23's commit and restore stay as they were

def test_project_commit_and_restore_are_unchanged_since_01ec6d2a7():
    done = subprocess.run(["git", "-C", str(REPO), "diff", "--quiet", "01ec6d2a7", "--", "src/gov/adopt/project.py"],
                          capture_output=True, env=ENV)
    assert done.returncode == 0, done.stderr
