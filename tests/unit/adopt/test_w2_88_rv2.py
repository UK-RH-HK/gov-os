"""W2-88 run 5: review round 2's RV2-1 (A9's undo touches only what A9 did; HEAD_MOVED) and RV2-2 (PLAN.md's
unscanned list), as the engineer's own unit tests. In process, with a stand-in for ``gov.rebuild.command.run`` that
acts on the planted repository and then raises."""
from __future__ import annotations

import os
import subprocess

import pytest

from gov.adopt import refactor_plan
from gov.cli.errors import GovError

from .test_w2_88_fabric import ENV, git, planted
from .test_w2_88_run4 import expected_copies, run_a9

RETRIEVAL = "governance/project/retrieval.yaml"
BRIEF = "governance/kernel/templates/brief.md"


def out_of(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=ENV,
                          check=True).stdout


def fresh(tmp_path):
    """The planted repository without a tracked retrieval.yaml, so A9 installs one too."""
    root = planted(tmp_path)
    (root / RETRIEVAL).unlink()
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "no retrieval.yaml")
    return root


def copies():
    return [*expected_copies(), RETRIEVAL]


def indexed(root):
    return set(out_of(root, "ls-files").split())


def status(root):
    lines = out_of(root, "status", "--porcelain", "--untracked-files=all").splitlines()
    return sorted(line for line in lines if ".gov-runtime/" not in line)


def rebuild_doing(monkeypatch, act, raised):
    def stand_in(root, args, config):
        act(root)
        raise raised

    monkeypatch.setattr("gov.rebuild.command.run", stand_in)


def no_copy_left(root, keep=()):
    held = indexed(root)
    for rel in copies():
        if rel in keep:
            continue
        assert not os.path.lexists(root / rel), rel
        assert rel not in held, rel


# ---- RV2-1, Case A: HEAD did not move

def test_case_a_an_edit_and_a_staged_file_made_during_the_run_stay(tmp_path, monkeypatch):
    case_a(tmp_path, monkeypatch, GovError("REBUILD_FAILED", "stand-in", {}))


def test_case_a_after_an_interrupt_the_edit_and_the_staged_file_stay(tmp_path, monkeypatch):
    """Its own function, not a second row: ``tests/optin-lifted-breadth.txt`` keeps one row per parametrised case."""
    case_a(tmp_path, monkeypatch, KeyboardInterrupt())


def case_a(tmp_path, monkeypatch, raised):
    root = fresh(tmp_path)
    start = out_of(root, "rev-parse", "HEAD").strip()

    def act(repo):
        (repo / "a.md").write_bytes(b"edited during the run\n")
        (repo / "new.txt").write_text("staged during the run\n")
        git(repo, "add", "new.txt")

    rebuild_doing(monkeypatch, act, raised)
    with pytest.raises(type(raised)) as caught:
        run_a9(root, tmp_path / "out")
    if isinstance(raised, GovError):
        assert caught.value.code == "REBUILD_FAILED"
    assert out_of(root, "rev-parse", "HEAD").strip() == start
    assert (root / "a.md").read_bytes() == b"edited during the run\n"
    assert out_of(root, "diff", "--cached", "--name-only").split() == ["new.txt"]
    no_copy_left(root)
    assert not (root / ".claude").exists() and not (root / "governance/kernel").exists()
    assert status(root) == sorted([" M a.md", "A  new.txt"])


# ---- RV2-1, Case B: HEAD moved

def test_case_b_a_commit_during_the_run_is_head_moved_and_nothing_is_reset(tmp_path, monkeypatch):
    root = fresh(tmp_path)
    start = out_of(root, "rev-parse", "HEAD").strip()
    original = GovError("REBUILD_FAILED", "stand-in", {})

    def act(repo):
        (repo / "notes.md").write_text("notes\n")
        git(repo, "add", "notes.md")
        git(repo, "commit", "-q", "-m", "notes", "--", "notes.md")

    rebuild_doing(monkeypatch, act, original)
    with pytest.raises(GovError) as caught:
        run_a9(root, tmp_path / "out")
    new = out_of(root, "rev-parse", "HEAD").strip()
    assert new != start
    refusal = caught.value
    assert refusal.code == "HEAD_MOVED"
    assert refusal.details == {"started": start, "now": new, "cause": "REBUILD_FAILED"}
    assert start in refusal.message and new in refusal.message and "nothing was reset" in refusal.message
    assert refusal.__cause__ is original
    assert (root / "notes.md").read_text() == "notes\n"
    no_copy_left(root)
    assert out_of(root, "reflog", "-1", "--format=%H %gs").strip() == f"{new} commit: notes"
    assert status(root) == []


def test_case_b_a_copy_the_new_head_tracks_is_left_as_it_is(tmp_path, monkeypatch):
    root = fresh(tmp_path)
    start = out_of(root, "rev-parse", "HEAD").strip()

    def act(repo):
        (repo / "notes.md").write_text("notes\n")
        git(repo, "add", "notes.md")
        git(repo, "commit", "-q", "-m", "take", "--", "notes.md", BRIEF)

    rebuild_doing(monkeypatch, act, KeyboardInterrupt())
    with pytest.raises(GovError) as caught:
        run_a9(root, tmp_path / "out")
    new = out_of(root, "rev-parse", "HEAD").strip()
    assert caught.value.code == "HEAD_MOVED"
    assert caught.value.details == {"started": start, "now": new, "cause": "KeyboardInterrupt"}
    assert isinstance(caught.value.__cause__, KeyboardInterrupt)
    shipped = expected_copies()[BRIEF].read_bytes()
    assert (root / BRIEF).read_bytes() == shipped and BRIEF in indexed(root)
    assert BRIEF in out_of(root, "ls-tree", "-r", "--name-only", "HEAD").split()
    no_copy_left(root, keep=(BRIEF,))
    assert status(root) == []


# ---- RV2-1: what the undo leaves

def test_a_copy_whose_bytes_changed_during_the_run_is_left_as_it_is(tmp_path, monkeypatch):
    root = fresh(tmp_path)
    rebuild_doing(monkeypatch, lambda repo: (repo / BRIEF).write_bytes(b"mine\n"),
                  GovError("REBUILD_FAILED", "stand-in", {}))
    with pytest.raises(GovError) as caught:
        run_a9(root, tmp_path / "out")
    assert caught.value.code == "REBUILD_FAILED"
    assert (root / BRIEF).read_bytes() == b"mine\n"
    no_copy_left(root, keep=(BRIEF,))
    assert BRIEF not in indexed(root)  # A9's staged blob is unstaged; the file is the user's, untracked
    assert status(root) == [f"?? {BRIEF}"]
    assert not (root / ".claude").exists()


def test_a_copy_that_replaced_a_tracked_file_gets_that_file_back(tmp_path, monkeypatch):
    root = fresh(tmp_path)
    (root / BRIEF).parent.mkdir(parents=True)
    (root / BRIEF).write_bytes(b"the repository's own brief\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "own brief")
    seen = []
    rebuild_doing(monkeypatch, lambda repo: seen.append((repo / BRIEF).read_bytes()),
                  GovError("FABRIC_INCOMPLETE", "stand-in", {}))
    with pytest.raises(GovError) as caught:
        run_a9(root, tmp_path / "out")
    assert caught.value.code == "FABRIC_INCOMPLETE"
    assert seen == [expected_copies()[BRIEF].read_bytes()]  # A9 did replace it
    assert (root / BRIEF).read_bytes() == b"the repository's own brief\n"
    assert BRIEF in indexed(root)
    no_copy_left(root, keep=(BRIEF,))
    assert status(root) == []


def test_the_folders_a9_made_are_removed_only_when_empty(tmp_path, monkeypatch):
    root = fresh(tmp_path)
    extra = root / ".claude/skills/retrieval/extra.txt"
    rebuild_doing(monkeypatch, lambda repo: extra.write_text("made during the run\n"),
                  GovError("DIGESTS_INCOMPLETE", "stand-in", {}))
    with pytest.raises(GovError):
        run_a9(root, tmp_path / "out")
    assert extra.read_text() == "made during the run\n"
    assert not (root / ".claude/skills/discovery").exists() and not (root / "governance/kernel").exists()
    no_copy_left(root)
    assert status(root) == ["?? .claude/skills/retrieval/extra.txt"]


def test_a_failure_inside_install_after_some_copies_leaves_the_same_way(tmp_path, monkeypatch):
    root = fresh(tmp_path)
    late = "governance/kernel/templates/role-cto.md"  # the last template: written after the skills and brief.md
    (root / late).parent.mkdir(parents=True)
    os.symlink("../../../a.md", root / late)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "a tracked link where a copy goes")
    called = []
    monkeypatch.setattr("gov.rebuild.command.run", lambda *a: called.append(a))
    with pytest.raises(GovError) as caught:
        run_a9(root, tmp_path / "out")
    assert caught.value.code == "ADOPT_INSTALL_PATH_UNSAFE" and called == []
    assert os.path.islink(root / late)
    no_copy_left(root, keep=(late,))
    assert not (root / ".claude").exists()
    assert status(root) == []


def test_a_refusal_with_head_unmoved_resets_nothing(tmp_path, monkeypatch):
    """No ``reset`` in the reflog: the undo never moves the branch."""
    root = fresh(tmp_path)
    before = out_of(root, "reflog", "--format=%gs")
    rebuild_doing(monkeypatch, lambda repo: None, GovError("REBUILD_FAILED", "stand-in", {}))
    with pytest.raises(GovError):
        run_a9(root, tmp_path / "out")
    assert out_of(root, "reflog", "--format=%gs") == before
    no_copy_left(root)
    assert status(root) == []


# ---- RV2-2: PLAN.md's unscanned list

def test_partial_unscanned_paths_are_a_list_after_their_own_line(tmp_path):
    refactor_plan.plan({"secrets_scanned": True, "secrets": [], "secrets_unscanned": ["huge.txt", "big.txt"],
                        "paths": ["huge.txt", "big.txt", "a.md"]}, None, tmp_path)
    lines = (tmp_path / "refactor-plan/PLAN.md").read_text().splitlines()
    at = lines.index("Unscanned paths:")
    assert lines[at + 1:at + 3] == ["- `huge.txt`", "- `big.txt`"]
    assert not any(line.startswith("Unscanned paths:") and line != "Unscanned paths:" for line in lines)


def test_no_scan_at_all_stays_one_line(tmp_path):
    refactor_plan.plan({"secrets_scanned": False, "secrets": [], "secrets_unscanned": [], "paths": ["a", "b"],
                        "secrets_unscanned_reason": "planted"}, None, tmp_path)
    lines = (tmp_path / "refactor-plan/PLAN.md").read_text().splitlines()
    assert "Unscanned paths: all 2 tracked files" in lines
