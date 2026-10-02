"""Builder tests for DEC-132: owner defaults for the four open HEAD cases.

These cases are not covered by acceptance tests (the test designer left
them open on purpose).  DEC-132 says they are covered by builder tests
until acceptance tests exist.

The four cases:
1. Checking out a branch that points at the same commit is not a HEAD move.
2. Creating a new branch and committing on it in one call is flagged.
3. A merge that is not a fast-forward is flagged.
4. A HEAD move with no before-snapshot is flagged.

Each test creates a small git repository in a temporary directory and
exercises ``take_snapshot`` and ``check_containment`` directly, without
running the kernel hooks.
"""

from __future__ import annotations

import json
import os
import subprocess
import textwrap

import pytest

_GIT_IDENTITY = (
    "-c", "user.name=DEC-132 test",
    "-c", "user.email=dec-132@test.invalid",
    "-c", "commit.gpgsign=false",
    "-c", "core.hooksPath=/dev/null",
)

FINDINGS_REL = ".gov-runtime/findings.jsonl"


def _git(project, *args):
    proc = subprocess.run(
        ["git", "-C", str(project), *_GIT_IDENTITY, *args],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, (
        f"git {' '.join(args)} failed: {proc.stderr.strip()}"
    )
    return proc.stdout


def _head(project):
    commit = _git(project, "rev-parse", "HEAD").strip()
    proc = subprocess.run(
        ["git", "-C", str(project), "symbolic-ref", "-q", "--short", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    branch = proc.stdout.strip() if proc.returncode == 0 else ""
    return commit, branch


def _make_project(tmp_path):
    """A minimal committed project with tickets."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".gitignore").write_text(".gov-runtime/\n")
    (project / "README.md").write_text("# Test\n")
    tickets = project / ".tickets"
    tickets.mkdir()
    (tickets / "DAEO-t01.md").write_text(textwrap.dedent("""\
        ---
        id: DAEO-t01
        status: in_progress
        deps: []
        links: []
        created: 2026-09-30T22:49:58Z
        type: task
        priority: 1
        assignee: engineer
        external-ref: T-01
        tags: [test]
        wbs_id: T-01
        title: Test ticket
        class: implementation
        role: engineer
        depends_on: []
        allowed_paths:
        - src/**
        kpis:
          success:
          - test
          failure:
          - test
        profile: FULL
        acceptance_tests:
          path: tests/acceptance/T-01/
        ---
        # T-01 Test
    """))
    (project / "src").mkdir()
    (project / "src" / "main.py").write_text("VALUE = 1\n")
    _git(project, "init", "-q", "-b", "main")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "initial")
    return project


def _findings(project):
    path = project / FINDINGS_REL
    if not path.is_file():
        return []
    lines = path.read_text("utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


# ---------------------------------------------------------------
# Case 1: checkout branch at same commit is not a HEAD move
# ---------------------------------------------------------------

def test_checkout_branch_at_same_commit_is_not_a_head_move(tmp_path):
    """DEC-132 case 1: switching to a branch that points at the same
    commit does not count as a HEAD move."""
    from gov.guard.containment import take_snapshot, check_containment

    project = _make_project(tmp_path)

    # Create a branch at the same commit.
    _git(project, "branch", "other")

    take_snapshot(str(project), "toolu_case1")

    # Switch to the other branch (same commit).
    _git(project, "checkout", "-q", "other")

    old_head, _ = _head(project)
    report = check_containment(
        project_root=str(project),
        role="engineer",
        ticket_id="DAEO-t01",
        subagent_type=None,
        session_id="test-session",
        agent_type=None,
        command="git checkout other",
        tool_use_id="toolu_case1",
    )

    # The commit did not change, so no HEAD-move finding.
    findings = _findings(project)
    assert not findings, (
        f"case 1: a branch switch to the same commit produced findings: "
        f"{findings}"
    )
    assert report == "", f"case 1: unexpected report: {report!r}"


# ---------------------------------------------------------------
# Case 2: new branch + commit in one call is flagged
# ---------------------------------------------------------------

def test_new_branch_and_commit_is_flagged(tmp_path):
    """DEC-132 case 2: creating a new branch and committing on it in
    one call is flagged."""
    from gov.guard.containment import take_snapshot, check_containment

    project = _make_project(tmp_path)
    take_snapshot(str(project), "toolu_case2")

    # Create a new branch and commit.
    _git(project, "checkout", "-q", "-b", "feature")
    (project / "README.md").write_text("# Changed\n")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "feature commit")

    report = check_containment(
        project_root=str(project),
        role="engineer",
        ticket_id="DAEO-t01",
        subagent_type=None,
        session_id="test-session",
        agent_type=None,
        command="git checkout -b feature && ...",
        tool_use_id="toolu_case2",
    )

    findings = _findings(project)
    assert findings, "case 2: no finding for new branch + commit"
    actions = [f["action"] for f in findings]
    assert "flagged" in actions, (
        f"case 2: expected flagged, got {actions}"
    )
    assert report, "case 2: expected a report"


# ---------------------------------------------------------------
# Case 3: non-fast-forward merge is flagged
# ---------------------------------------------------------------

def test_non_ff_merge_is_flagged(tmp_path):
    """DEC-132 case 3: a merge that is not a fast-forward is flagged."""
    from gov.guard.containment import take_snapshot, check_containment

    project = _make_project(tmp_path)

    # Create divergent history.
    _git(project, "checkout", "-q", "-b", "feature")
    (project / "src" / "feature.py").write_text("feature\n")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "feature")

    _git(project, "checkout", "-q", "main")
    (project / "README.md").write_text("# Updated\n")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "main update")

    take_snapshot(str(project), "toolu_case3")

    # Non-fast-forward merge.
    _git(project, "merge", "--no-ff", "-q", "-m", "merge feature",
         "feature")

    report = check_containment(
        project_root=str(project),
        role="engineer",
        ticket_id="DAEO-t01",
        subagent_type=None,
        session_id="test-session",
        agent_type=None,
        command="git merge --no-ff feature",
        tool_use_id="toolu_case3",
    )

    findings = _findings(project)
    assert findings, "case 3: no finding for non-ff merge"
    actions = [f["action"] for f in findings]
    assert "flagged" in actions, (
        f"case 3: expected flagged, got {actions}"
    )
    assert report, "case 3: expected a report"


# ---------------------------------------------------------------
# Case 4: HEAD move with no before-snapshot is flagged
# ---------------------------------------------------------------

def test_head_move_without_snapshot_is_flagged(tmp_path):
    """DEC-132 case 4: a HEAD move when no before-snapshot was taken
    is flagged.  The check compares current HEAD with the last HEAD
    it recorded (in .gov-runtime/last_head.json)."""
    from gov.guard.containment import take_snapshot, check_containment

    project = _make_project(tmp_path)

    # Run one call so that last_head.json is populated.
    take_snapshot(str(project), "toolu_setup")
    check_containment(
        project_root=str(project),
        role="engineer",
        ticket_id="DAEO-t01",
        subagent_type=None,
        session_id="test-session",
        agent_type=None,
        command="ls",
        tool_use_id="toolu_setup",
    )

    # Make a commit that moves HEAD.
    (project / "README.md").write_text("# Changed\n")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "a commit")

    # No snapshot was taken. Call check_containment with a tool_use_id
    # that has no matching snapshot file.
    report = check_containment(
        project_root=str(project),
        role="engineer",
        ticket_id="DAEO-t01",
        subagent_type=None,
        session_id="test-session",
        agent_type=None,
        command="git commit -am work",
        tool_use_id="toolu_no_snapshot",
    )

    findings = _findings(project)
    # The check detects the HEAD move via last_head.json.
    flagged = [f for f in findings if f.get("action") == "flagged"]
    assert flagged, (
        "case 4: HEAD move without snapshot must be flagged"
    )
    assert report, "case 4: expected a report for the HEAD move"
    for f in findings:
        assert f.get("action") != "reverted", (
            "case 4: HEAD move without snapshot must never be reverted"
        )
    # The finding has all DEC-122 fields.
    for f in flagged:
        for field in ("time", "session_id", "agent_type", "role",
                      "ticket", "tool", "command", "paths", "action",
                      "reason"):
            assert field in f, (
                f"case 4: finding lacks field {field!r}: {f}"
            )
