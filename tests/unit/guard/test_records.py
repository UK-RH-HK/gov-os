"""Builder tests for the orchestrator records in containment (DEC-177).

Regression evidence only (DEC-136).  Tests the record-writing path in
``check_containment`` directly, without running the hook as a process.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.guard.containment import (  # noqa: E402
    RECORDS_REL,
    _make_finding,
    _write_records,
)


def _record_lines(root):
    p = os.path.join(root, RECORDS_REL)
    if not os.path.isfile(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [line for line in f.read().splitlines() if line.strip()]


def _git(project, *args):
    subprocess.run(
        ["git", "-C", str(project),
         "-c", "user.name=test", "-c", "user.email=t@x",
         "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
         *args],
        capture_output=True, text=True, check=True,
    )


def _make_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    tickets = project / ".tickets"
    tickets.mkdir()
    (tickets / "T-01.md").write_text(
        "---\nid: T-01\nstatus: in_progress\nwbs_id: W1-99\n"
        "role: orchestrator\nallowed_paths:\n- src/**\n---\n# T\n",
        encoding="utf-8",
    )
    (project / "README.md").write_text("# test\n", encoding="utf-8")
    (project / "src").mkdir()
    (project / "src" / "main.py").write_text("pass\n", encoding="utf-8")
    (project / ".gitignore").write_text(".gov-runtime/\n__pycache__/\n", encoding="utf-8")
    _git(project, "init", "-q", "-b", "main")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "init")
    return str(project)


# ---- _write_records writes valid JSON lines ----

class TestWriteRecords:

    def test_write_one_record(self, tmp_path):
        root = str(tmp_path)
        rec = _make_finding("s1", "orchestrator", "orchestrator", "T-01",
                            "echo changed >> README.md",
                            ["README.md"], "recorded",
                            "change outside ticket paths")
        _write_records(root, [rec])
        lines = _record_lines(root)
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["action"] == "recorded"
        assert data["paths"] == ["README.md"]
        assert data["session_id"] == "s1"

    def test_no_write_to_findings(self, tmp_path):
        root = str(tmp_path)
        rec = _make_finding("s1", "orchestrator", "orchestrator", "T-01",
                            "echo x >> README.md",
                            ["README.md"], "recorded",
                            "change outside ticket paths")
        _write_records(root, [rec])
        findings = os.path.join(root, ".gov-runtime", "findings.jsonl")
        assert not os.path.exists(findings)


# ---- check_containment routes orchestrator oos to records ----

class TestContainmentRecords:

    def test_orchestrator_oos_produces_record(self, tmp_path):
        """An orchestrator change outside ticket paths writes a record."""
        from gov.guard.containment import check_containment, take_snapshot
        project = _make_project(tmp_path)
        # Snapshot before.
        take_snapshot(project, "toolu_rec1", session_id="s1")
        # Modify a file outside ticket paths.
        with open(os.path.join(project, "README.md"), "a") as f:
            f.write("changed\n")
        before = len(_record_lines(project))
        report = check_containment(
            project_root=project,
            role="orchestrator",
            ticket_id="T-01",
            subagent_type=None,
            session_id="s1",
            agent_type=None,
            command="echo changed >> README.md",
            tool_use_id="toolu_rec1",
        )
        after = _record_lines(project)
        assert len(after) - before == 1
        data = json.loads(after[-1])
        assert data["action"] == "recorded"
        assert "README.md" in data["paths"]

    def test_orchestrator_in_scope_no_record(self, tmp_path):
        """A change inside the ticket's paths writes no record."""
        from gov.guard.containment import check_containment, take_snapshot
        project = _make_project(tmp_path)
        take_snapshot(project, "toolu_rec2", session_id="s1")
        with open(os.path.join(project, "src", "main.py"), "a") as f:
            f.write("# changed\n")
        before = len(_record_lines(project))
        check_containment(
            project_root=project,
            role="orchestrator",
            ticket_id="T-01",
            subagent_type=None,
            session_id="s1",
            agent_type=None,
            command="echo changed >> src/main.py",
            tool_use_id="toolu_rec2",
        )
        assert len(_record_lines(project)) == before

    def test_engineer_oos_no_record(self, tmp_path):
        """An engineer out-of-scope change writes a finding, not a record."""
        from gov.guard.containment import check_containment, take_snapshot
        project = _make_project(tmp_path)
        # Add an engineer ticket.
        (Path(project) / ".tickets" / "T-02.md").write_text(
            "---\nid: T-02\nstatus: in_progress\nwbs_id: W1-98\n"
            "role: engineer\nallowed_paths:\n- src/**\n---\n# T\n",
            encoding="utf-8",
        )
        _git(project, "add", "-A")
        _git(project, "commit", "-q", "-m", "add ticket")
        take_snapshot(project, "toolu_rec3", session_id="s1")
        with open(os.path.join(project, "README.md"), "a") as f:
            f.write("changed\n")
        before_rec = len(_record_lines(project))
        check_containment(
            project_root=project,
            role="engineer",
            ticket_id="T-02",
            subagent_type=None,
            session_id="s1",
            agent_type=None,
            command="echo changed >> README.md",
            tool_use_id="toolu_rec3",
        )
        assert len(_record_lines(project)) == before_rec
