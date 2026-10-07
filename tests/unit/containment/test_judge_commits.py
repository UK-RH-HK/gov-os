"""Unit tests for ``judge_commits`` and ``ContainmentError`` (DEC-453).

Regression evidence; the acceptance tests are in
``tests/acceptance/W1-50/test_w1_50_judge_commits.py``.
"""

from __future__ import annotations

import json
import subprocess

_GIT_IDENTITY = (
    "-c", "user.name=judge test",
    "-c", "user.email=judge@test.invalid",
    "-c", "commit.gpgsign=false",
    "-c", "core.hooksPath=/dev/null",
)

TICKET = "DAEO-t01"
TICKET_FILE = f".tickets/{TICKET}.md"


def _git(project, *args):
    proc = subprocess.run(
        ["git", "-C", str(project), *_GIT_IDENTITY, *args],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, (
        f"git {' '.join(args)} failed: {proc.stderr.strip()}"
    )
    return proc.stdout


def _make_project(tmp_path, status="in_progress"):
    project = tmp_path / "project"
    (project / ".tickets").mkdir(parents=True)
    (project / "src").mkdir()
    (project / "tests" / "acceptance" / "W1-01").mkdir(parents=True)
    (project / ".gitignore").write_text(".gov-runtime/\n")
    (project / "README.md").write_text("# Test\n")
    (project / "src" / "main.py").write_text("VALUE = 1\n")
    (project / "tests" / "acceptance" / "W1-01" / "test_one.py").write_text(
        "def test(): pass\n")
    project_path = project / TICKET_FILE
    project_path.write_text(
        f"---\nid: {TICKET}\nstatus: {status}\nwbs_id: T-01\n"
        "role: engineer\nallowed_paths:\n- src/**\n---\n# T-01 Test\n")
    _git(project, "init", "-q", "-b", "main")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "initial")
    return project


def _commit(project, path, *trailers, message="work"):
    target = project / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a") as f:
        f.write("changed\n")
    args = []
    for t in trailers:
        args += ["--trailer", t]
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", message, *args)
    return _git(project, "rev-parse", "HEAD").strip()


# ---- ContainmentError is a proper subclass ----

def test_containment_error_is_a_subclass_of_exception():
    from gov.guard.containment import ContainmentError
    assert issubclass(ContainmentError, Exception)
    assert ContainmentError is not Exception


# ---- empty list raises ----

def test_empty_list_raises(tmp_path):
    from gov.guard.containment import ContainmentError, judge_commits
    project = _make_project(tmp_path)
    import pytest
    with pytest.raises(ContainmentError):
        judge_commits(str(project), [])


# ---- not a repo raises ----

def test_not_a_repo_raises(tmp_path):
    from gov.guard.containment import ContainmentError, judge_commits
    empty = tmp_path / "empty"
    empty.mkdir()
    import pytest
    with pytest.raises(ContainmentError):
        judge_commits(str(empty), ["0" * 40])


# ---- unknown commit raises ----

def test_unknown_commit_raises(tmp_path):
    from gov.guard.containment import ContainmentError, judge_commits
    project = _make_project(tmp_path)
    import pytest
    with pytest.raises(ContainmentError):
        judge_commits(str(project), ["0" * 40])


# ---- a commit inside its paths passes ----

def test_engineer_inside_paths_passes(tmp_path):
    from gov.guard.containment import judge_commits
    project = _make_project(tmp_path)
    cid = _commit(project, "src/main.py",
                  f"Task: {TICKET}", "Role: engineer")
    findings = judge_commits(str(project), [cid])
    assert findings == []


# ---- a commit outside its paths is a finding ----

def test_engineer_outside_paths_is_finding(tmp_path):
    from gov.guard.containment import judge_commits
    project = _make_project(tmp_path)
    cid = _commit(project, "README.md",
                  f"Task: {TICKET}", "Role: engineer")
    findings = judge_commits(str(project), [cid])
    assert len(findings) == 1
    assert findings[0].commit == cid
    assert "README.md" in findings[0].paths


# ---- no trailers judged as orchestrator ----

def test_no_trailers_judged_as_orchestrator(tmp_path):
    from gov.guard.containment import judge_commits
    project = _make_project(tmp_path)
    cid = _commit(project, "README.md")
    findings = judge_commits(str(project), [cid])
    assert findings == [], "README.md should be allowed for the orchestrator"


def test_no_trailers_acceptance_test_is_finding(tmp_path):
    from gov.guard.containment import judge_commits
    project = _make_project(tmp_path)
    cid = _commit(project, "tests/acceptance/W1-01/test_one.py")
    findings = judge_commits(str(project), [cid])
    assert len(findings) == 1
    assert "tests/acceptance/W1-01/test_one.py" in findings[0].paths


# ---- Role: owner is always a finding ----

def test_role_owner_is_finding(tmp_path):
    from gov.guard.containment import judge_commits
    project = _make_project(tmp_path)
    cid = _commit(project, "README.md", "Role: owner")
    findings = judge_commits(str(project), [cid])
    assert len(findings) == 1
    assert findings[0].commit == cid


# ---- read-only: nothing written ----

def test_read_only(tmp_path):
    from gov.guard.containment import judge_commits
    import os
    project = _make_project(tmp_path)
    cid = _commit(project, "README.md",
                  f"Task: {TICKET}", "Role: engineer")
    head_before = _git(project, "rev-parse", "HEAD").strip()

    runtime = project / ".gov-runtime"
    before_runtime = {}
    if runtime.is_dir():
        for dp, _, fns in os.walk(runtime):
            for fn in fns:
                full = os.path.join(dp, fn)
                rel = os.path.relpath(full, project)
                with open(full, "rb") as fh:
                    before_runtime[rel] = fh.read()

    judge_commits(str(project), [cid])

    assert _git(project, "rev-parse", "HEAD").strip() == head_before

    after_runtime = {}
    if runtime.is_dir():
        for dp, _, fns in os.walk(runtime):
            for fn in fns:
                full = os.path.join(dp, fn)
                rel = os.path.relpath(full, project)
                with open(full, "rb") as fh:
                    after_runtime[rel] = fh.read()
    assert before_runtime == after_runtime


# ---- mixed list returns only findings in order ----

def test_mixed_list_returns_findings_in_order(tmp_path):
    from gov.guard.containment import judge_commits
    project = _make_project(tmp_path)
    clean = _commit(project, "src/main.py",
                    f"Task: {TICKET}", "Role: engineer")
    finding = _commit(project, "README.md",
                      f"Task: {TICKET}", "Role: engineer")
    findings = judge_commits(str(project), [clean, finding])
    assert len(findings) == 1
    assert findings[0].commit == finding


# ---- freeze: everything is a finding ----

def test_freeze_makes_everything_a_finding(tmp_path):
    from gov.guard.containment import judge_commits
    project = _make_project(tmp_path)
    cid = _commit(project, "src/main.py",
                  f"Task: {TICKET}", "Role: engineer")
    freeze = project / ".gov-runtime" / "freeze"
    freeze.parent.mkdir(parents=True, exist_ok=True)
    freeze.write_bytes(b"FROZEN\n")
    findings = judge_commits(str(project), [cid])
    assert len(findings) == 1
    assert findings[0].commit == cid


# ---- _parse_log_output is used by _move_commits (regression) ----

def test_parse_log_output_used_by_move_commits(tmp_path):
    from gov.guard.containment import _move_commits
    project = _make_project(tmp_path)
    old = _git(project, "rev-parse", "HEAD").strip()
    cid = _commit(project, "src/main.py",
                  f"Task: {TICKET}", "Role: engineer")
    commits = _move_commits(str(project), old, cid)
    assert len(commits) == 1
    assert commits[0][0] == cid
    assert commits[0][2] == ["engineer"]
    assert commits[0][3] == [TICKET]
    assert "src/main.py" in commits[0][4]
