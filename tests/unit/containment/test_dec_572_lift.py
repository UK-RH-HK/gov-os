"""Unit tests for a merge commit's file that equals one parent's version
(DEC-572).

Regression evidence; the acceptance tests are in
``tests/acceptance/W1-50/test_w1_50_merge_commit_file_that_equals_one_parent_s_version.py``.
"""

from __future__ import annotations

from .test_judge_commits import TICKET_FILE, _commit, _git, _make_project

ORCHESTRATOR = ("Role: orchestrator", "Task: W1-INT")
ENGINEER = ("Role: engineer", "Task: DAEO-t01")


def _merge_taking(project, other, takes):
    """A merge commit of *other* into the checked-out branch that holds
    the ticket file exactly as the revision *takes* has it."""
    import subprocess
    subprocess.run(["git", "-C", str(project), "merge", "-q", "--no-ff",
                    "--no-commit", other], capture_output=True, check=False)
    _git(project, "checkout", "-q", takes, "--", TICKET_FILE)
    _git(project, "add", "--", TICKET_FILE)
    _git(project, "commit", "-q", "-m", f"Merge {other}",
         "--trailer", ORCHESTRATOR[0], "--trailer", ORCHESTRATOR[1])
    return _git(project, "rev-parse", "HEAD").strip()


def _both_sides(tmp_path, side=ORCHESTRATOR):
    """``main`` and ``side`` each changed the ticket file since the fork;
    ``main`` is checked out.  Returns (project, the side's commit)."""
    project = _make_project(tmp_path)
    _git(project, "checkout", "-q", "-b", "side")
    brought = _commit(project, TICKET_FILE, *side)
    _git(project, "checkout", "-q", "main")
    (project / TICKET_FILE).write_text(
        (project / TICKET_FILE).read_text() + "main\n")
    _commit(project, TICKET_FILE, *ORCHESTRATOR)
    return project, brought


def test_a_ticket_file_held_as_one_parent_has_it_is_no_finding(tmp_path):
    from gov.guard.containment import judge_commits
    project, _ = _both_sides(tmp_path)
    merge = _merge_taking(project, "side", "side")
    assert judge_commits(str(project), [merge]) == []


def test_a_worker_s_commit_that_brought_the_version_is_named(tmp_path):
    from gov.guard.containment import judge_commits
    project, brought = _both_sides(tmp_path, side=ENGINEER)
    merge = _merge_taking(project, "side", "side")
    (finding,) = judge_commits(str(project), [merge])
    assert finding.commit == merge and TICKET_FILE in finding.paths
    assert brought[:12] in finding.reason


def test_the_lift_is_not_applied_inside_the_lift(tmp_path):
    """A merge commit on the merged side that is itself the lifted shape
    is no finding alone, and does not pass as a commit that brought the
    version: the outer merge commit's finding names it."""
    from gov.guard.containment import judge_commits
    project, _ = _both_sides(tmp_path)
    _git(project, "checkout", "-q", "-b", "inner", "main~1")
    (project / TICKET_FILE).write_text(
        (project / TICKET_FILE).read_text() + "inner\n")
    _commit(project, TICKET_FILE, *ORCHESTRATOR, message="inner")
    _git(project, "checkout", "-q", "side")
    inner = _merge_taking(project, "inner", "inner")
    _git(project, "checkout", "-q", "main")
    merge = _merge_taking(project, "side", "side")
    assert judge_commits(str(project), [inner]) == []
    (finding,) = judge_commits(str(project), [merge])
    assert TICKET_FILE in finding.paths and inner[:12] in finding.reason


def test_no_lift_beyond_the_bound_of_git_processes(tmp_path, monkeypatch):
    from gov.guard import containment
    project, _ = _both_sides(tmp_path)
    merge = _merge_taking(project, "side", "side")
    monkeypatch.setattr(containment, "_LIFT_PROCESSES", 7)
    assert containment.judge_commits(str(project), [merge]) == []
    monkeypatch.setattr(containment, "_LIFT_PROCESSES", 6)
    (finding,) = containment.judge_commits(str(project), [merge])
    assert finding.paths == [TICKET_FILE]
