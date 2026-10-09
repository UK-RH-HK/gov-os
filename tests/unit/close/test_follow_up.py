"""The follow-up after W1-41 on ``gov close`` (DEC-569): the governance share, the test run ended whole at its
time limit, a run without a result, the repair ticket of long findings, a register entry, both kernel layouts."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from gov.cli.errors import GovError
from gov.close import command, state, tool
from gov.close.command import NOT_MEASURED, _governance_share, _one_test_run, _read_skill_versions, _started

ALL_NOT_MEASURED = {"measured": NOT_MEASURED, "estimated": NOT_MEASURED, "total": NOT_MEASURED}


# ---- the governance share (DEC-495): the counter's three figures, and never a refusal ----

def test_without_a_session_the_counter_is_not_asked(tmp_path, monkeypatch):
    monkeypatch.setattr("gov.telemetry.counter.measure", lambda *a: pytest.fail("the counter was asked"))
    assert _governance_share(tmp_path, "T-1", []) == ALL_NOT_MEASURED


def test_the_share_is_the_counters_and_nothing_else_of_its_record(tmp_path, monkeypatch):
    asked = []

    def measure(root, ticket, sessions):
        asked.append((ticket, sessions))
        return {"governance_share": {"measured": 0.25, "estimated": NOT_MEASURED, "total": NOT_MEASURED},
                "sessions": [{"session": "s-1", "model": "a text of the log"}]}

    monkeypatch.setattr("gov.telemetry.counter.measure", measure)
    assert _governance_share(tmp_path, "T-1", ["s-1"]) == {"measured": 0.25, "estimated": NOT_MEASURED,
                                                           "total": NOT_MEASURED}
    assert asked == [("T-1", ["s-1"])]


@pytest.mark.parametrize("error", [GovError("CCUSAGE_ABSENT", "ccusage is not on PATH", {}), OSError("no log")])
def test_a_counter_that_refuses_leaves_the_share_not_measured(tmp_path, monkeypatch, error):
    def measure(*given):
        raise error

    monkeypatch.setattr("gov.telemetry.counter.measure", measure)
    assert _governance_share(tmp_path, "T-1", ["s-1=engineer"]) == ALL_NOT_MEASURED


# ---- a test run (DEC-555) ----

def test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it(tmp_path):
    told = tmp_path / "told"
    child = f"import os, time; open({str(told)!r}, 'w').write(str(os.getpid())); time.sleep(60)"
    parent = f"import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', {child!r}]); time.sleep(60)"
    with pytest.raises(subprocess.TimeoutExpired):
        _started(tmp_path, [sys.executable, "-c", parent], dict(os.environ), timeout=2)
    pid = told.read_text(encoding="utf-8")
    deadline = time.time() + 2  # an ended process is reaped by whoever inherits it
    while time.time() < deadline and Path(f"/proc/{pid}").exists() \
            and Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rpartition(")")[2].split()[0] != "Z":
        time.sleep(0.05)
    state_of = Path(f"/proc/{pid}/stat")
    assert not state_of.exists() or state_of.read_text(encoding="utf-8").rpartition(")")[2].split()[0] == "Z"


@pytest.mark.parametrize("printed, findings", [("", 1), ("1 xfailed in 0.01s\n", 0), ("1 passed in 0.01s\n", 0)])
def test_a_run_that_ends_with_exit_code_0_and_no_result_is_a_finding(tmp_path, monkeypatch, printed, findings):
    monkeypatch.setattr("gov.close.command._started", lambda root, cmd, env, timeout=None: SimpleNamespace(
        returncode=0, stdout=printed, stderr=""))
    found, ran = _one_test_run(tmp_path, ["pytest"], {}, 60, "the test run of tests/x", "tests/x")
    assert len(found) == findings and ran["passed"] == (1 if "passed" in printed else 0)
    assert not found or "no result" in found[0] and "tests/x" in found[0]


def test_a_list_that_is_not_utf8_is_a_finding_of_its_own(tmp_path):
    tests = tmp_path / "tests" / "unit"
    tests.mkdir(parents=True)
    (tests / "test_a.py").write_text("def test_a():\n    assert True\n", encoding="utf-8")
    (tmp_path / "tests" / "acceptance").mkdir()
    (tmp_path / "tests" / "acceptance" / "serial-only.txt").write_bytes(b"# caf\xe9\n")
    with pytest.raises(command._Finding) as raised:
        command._run_tests(tmp_path, tmp_path / "tests", 60, workers=2)
    assert raised.value.code == "SERIAL_ONLY_LIST_UNREADABLE" and "serial-only.txt" in raised.value.message
    assert raised.value.not_measured


# ---- the repair ticket of long findings ----

def test_a_repair_ticket_holds_the_first_findings_that_one_argument_carries():
    findings = [f"finding {number:04d} " + "x" * 1000 for number in range(200)]
    held = tool.findings_held(findings)
    assert 0 < held < 200
    assert sum(len(f"- {finding}\n".encode()) for finding in findings[:held]) <= tool.FINDINGS_BYTES
    assert tool.findings_held(findings[:held]) == held and tool.findings_held([]) == 0


# ---- an owner's decision as an entry of the register (DEC-483) ----

REGISTER = "records/log.md"


def test_an_entry_is_a_level_3_heading_outside_fenced_blocks_up_to_the_next_heading(repo):
    text = ("# Log\n\n```\n### DEC-1 — In a block\n```\n\n### DEC-2 — Two\n- **Status:** ACCEPTED (owner)\n\n"
            "#### DEC-3 — Another level\n\n### DEC-20 — Twenty\n- **Status:** PROPOSED\n")
    commit = repo.commit("the register", "Role: owner", files={REGISTER: text})
    assert state._entries(repo.root, commit, REGISTER, "DEC-1") == []
    assert state._entries(repo.root, commit, REGISTER, "DEC-2") == [
        "### DEC-2 — Two\n- **Status:** ACCEPTED (owner)\n\n"]
    assert state._entries(repo.root, commit, REGISTER, "DEC-3") == []
    assert state._entries(repo.root, commit, "records/none.md", "DEC-2") is None


# ---- the skills of both layouts of the kernel ----

def test_the_skills_of_an_installed_kernel_are_listed_beside_the_templates(tmp_path):
    for rel, text in (("template/governance/kernel/skills/a/SKILL.md", '---\nname: alpha\nversion: "1.1"\n---\n'),
                      ("template/governance/kernel/skills/b/SKILL.md", '---\nname: beta\nversion: "2"\n---\n'),
                      ("governance/kernel/skills/a/SKILL.md", '---\nname: alpha\nversion: "1.0"\n---\n'),
                      ("governance/kernel/skills/b/SKILL.md", '---\nname: beta\nversion: "2"\n---\n'),
                      ("governance/kernel/vendor/pack/skills/v/SKILL.md", "---\nname: vendored\n---\n")):
        (tmp_path / rel).parent.mkdir(parents=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    assert _read_skill_versions(tmp_path) == [
        {"name": "alpha", "version": "1.1"}, {"name": "beta", "version": "2"},
        {"name": "alpha", "version": "1.0"}, {"name": "vendored", "version": "no version"}]
