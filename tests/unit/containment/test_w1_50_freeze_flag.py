"""Builder tests for W1-50: the freeze flag is compared around a Bash call
(DEC-407, DEC-409 rule 4).

Regression evidence only; the acceptance suite is
``tests/acceptance/W1-50/test_w1_50_freeze_flag_comparison.py``.  These
cover what that suite leaves to the builder: a restore that fails, a
call without a snapshot, a freeze that is not a readable file, and a
check that fails after the flag was compared.

Each test creates a small git repository in a temporary directory and
exercises ``take_snapshot`` and ``check_containment`` directly, without
running the kernel hooks.
"""

from __future__ import annotations

import json
import os
import subprocess

import pytest

from gov.guard import containment
from gov.guard.decide import FREEZE_FLAG, freeze_state

FINDINGS_REL = ".gov-runtime/findings.jsonl"
LINE = "FROZEN orchestrator 2026-10-04T08:15:30Z\n"
COMMAND = "python3 -m pytest tests/unit -q"


def _git(project, *args):
    proc = subprocess.run(
        ["git", "-C", str(project), "-c", "user.name=W1-50 test",
         "-c", "user.email=w1-50@test.invalid", "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=/dev/null", *args],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"


@pytest.fixture()
def project(tmp_path):
    """A minimal committed project that ignores ``.gov-runtime/``."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".gitignore").write_text(".gov-runtime/\n")
    (project / "README.md").write_text("# Test\n")
    _git(project, "init", "-q", "-b", "main")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "initial")
    return project


def _freeze(project, content=LINE):
    flag = project / FREEZE_FLAG
    flag.parent.mkdir(exist_ok=True)
    flag.write_text(content)
    return flag


def _check(project, tool_use_id="call-1"):
    return containment.check_containment(
        str(project), "engineer", "DAEO-t01", None, "session-1", None,
        COMMAND, tool_use_id)


def _flag_findings(project):
    path = project / FINDINGS_REL
    lines = path.read_text().splitlines() if path.exists() else []
    return [f for f in map(json.loads, lines) if FREEZE_FLAG in f["paths"]]


def test_a_restore_that_fails_is_said_in_the_finding_and_in_the_report(
        project, monkeypatch):
    flag = _freeze(project)
    containment.take_snapshot(str(project), "call-1")
    flag.unlink()

    def refuse(src, dst):
        raise OSError("no rename today")
    monkeypatch.setattr(containment.os, "replace", refuse)

    report = _check(project)

    [finding] = _flag_findings(project)
    assert finding["action"] == "flagged"
    assert "restore failed" in finding["reason"]
    assert "no rename today" in finding["reason"]
    assert finding["command"] == COMMAND and finding["role"] == "engineer"
    assert "restore failed" in report and FREEZE_FLAG in report
    assert [n for n in os.listdir(flag.parent) if n.startswith("freeze")] == []


def test_a_linked_runtime_folder_is_not_written_through(project, tmp_path):
    flag = _freeze(project)
    containment.take_snapshot(str(project), "call-1")
    elsewhere = tmp_path / "elsewhere"
    flag.unlink()
    os.rename(flag.parent, elsewhere)
    os.symlink(elsewhere, flag.parent)

    report = _check(project)

    [finding] = _flag_findings(project)
    assert finding["action"] == "flagged"
    assert "symbolic link" in finding["reason"] and "restore failed" in report
    assert not (elsewhere / "freeze").exists()


def test_a_call_without_a_snapshot_remembers_nothing(project):
    _freeze(project).unlink()

    assert _check(project, tool_use_id="") == ""
    assert _flag_findings(project) == []
    assert not os.path.lexists(project / FREEZE_FLAG)


def test_a_freeze_that_was_no_readable_file_is_restored_as_a_freeze(project):
    """A directory at the flag's path freezes (DEC-179) and has no line."""
    flag = project / FREEZE_FLAG
    flag.mkdir(parents=True)
    containment.take_snapshot(str(project), "call-1")
    flag.rmdir()

    report = _check(project)

    [finding] = _flag_findings(project)
    assert finding["action"] == "reverted" and "restored" in report
    assert freeze_state(str(project)) == "frozen"
    assert flag.read_text().startswith("FROZEN containment ")


def test_the_flag_is_restored_and_recorded_when_the_check_then_fails(
        project, monkeypatch):
    flag = _freeze(project)
    containment.take_snapshot(str(project), "call-1")
    flag.write_text("")

    def broken(root, *args, **kwargs):
        raise containment._GitError("git is gone")
    monkeypatch.setattr(containment, "_git", broken)

    with pytest.raises(containment._GitError):
        _check(project)

    assert flag.read_text() == LINE and (flag.stat().st_mode & 0o777) == 0o600
    assert [f["action"] for f in _flag_findings(project)] == ["reverted"]


def test_the_hook_s_reading_is_used_and_no_freeze_remembers_nothing(project):
    _freeze(project, "not a marker\n")
    containment.take_snapshot(str(project), "call-1", flag="unmarked")
    snap = json.loads(
        (project / containment.SNAPSHOT_DIR_REL / "call-1.json").read_text())
    assert snap["freeze"] is None

    _freeze(project)
    containment.take_snapshot(str(project), "call-2", flag="frozen")
    snap = json.loads(
        (project / containment.SNAPSHOT_DIR_REL / "call-2.json").read_text())
    assert snap["freeze"] == LINE
