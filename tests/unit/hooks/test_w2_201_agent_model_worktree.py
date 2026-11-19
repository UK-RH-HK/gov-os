"""W2-201 (DAEO-k1us), a fix at the land (2026-11-19): a lead writes its feature as a ticket on its own branch, so the
ticket of a helper spawn is often in a worktree of the repository and not yet in the project's own ``.tickets/``. The
hook reads it there; a ticket in no worktree is still unreadable (Sonnet). Builder tests."""

from __future__ import annotations

import subprocess

import pytest

import test_w2_201_agent_model as base
from test_w2_201_agent_model import FABLE, bed, passes, refuses, run, substitution, ticket  # noqa: F401

GIT_ENV = {"PATH": "/usr/bin:/bin", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid", "HOME": "/nonexistent"}


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=GIT_ENV, timeout=60)


@pytest.fixture
def branch_bed(bed, tmp_path):
    """The project as a git repository, and one more worktree whose branch adds a C3 ticket and a C2 ticket."""
    git(bed, "init", "-q", "-b", "main")
    git(bed, "add", "-A")
    git(bed, "commit", "-q", "-m", "base")
    other = tmp_path / "lead-worktree"
    git(bed, "worktree", "add", "-q", "-b", "lead", str(other))
    ticket(other, "DAEO-c3br", ["src/gov/close/y.py"])
    ticket(other, "DAEO-c2br", ["src/gov/health/y.py"])
    return bed


def test_a_c3_ticket_that_is_only_in_another_worktree_is_read_there(branch_bed):
    substitution(branch_bed)
    passes(run(branch_bed, "engineer", FABLE, "Build it.\nTask: DAEO-c3br\n"))


def test_a_c2_ticket_in_another_worktree_is_still_refused_by_its_class(branch_bed):
    substitution(branch_bed)
    refuses(run(branch_bed, "engineer", FABLE, "Build it.\nTask: DAEO-c2br\n"), "DAEO-c2br", "C2")


def test_a_ticket_in_no_worktree_is_still_unreadable(branch_bed):
    substitution(branch_bed)
    refuses(run(branch_bed, "engineer", FABLE, "Build it.\nTask: DAEO-nope\n"), "DAEO-nope")


def test_the_project_s_own_ticket_wins_over_a_worktree_s_copy(branch_bed, tmp_path):
    substitution(branch_bed)
    ticket(tmp_path / "lead-worktree", "DAEO-c2aa", ["src/gov/close/z.py"])  # the branch's copy would be C3
    refuses(run(branch_bed, "engineer", FABLE, "Build it.\nTask: DAEO-c2aa\n"), "DAEO-c2aa", "C2")


def test_a_project_that_is_no_git_repository_reads_only_its_own_tickets(bed):
    substitution(bed)
    refuses(run(bed, "engineer", FABLE, "Build it.\nTask: DAEO-c3br\n"), "DAEO-c3br")
    assert base.HOOK.is_file()
