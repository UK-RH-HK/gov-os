"""W1-45 -- the containment check writes records to .gov-runtime/records.jsonl (DEC-177).

DEC-177, extending DEC-171: after a call in which the orchestrator (in a session
whose own role is orchestrator) changed a path outside its active ticket's
``allowed_paths`` (or with no active ticket), and not under
``tests/acceptance/**``, the containment check writes one JSON line for that call
to ``.gov-runtime/records.jsonl``, with the fields DEC-122 lists and
``action: "recorded"``, and writes nothing to ``.gov-runtime/findings.jsonl``.

- One line per call, however many paths changed.
- A change inside the active ticket's ``allowed_paths`` writes no record and no
  finding.
- A change under ``tests/acceptance/**`` stays a finding in ``findings.jsonl``,
  with DEC-122's actions unchanged.
- Other roles never produce a record line; their out-of-scope changes stay
  findings.

KPIs tested here (containment / PostToolUse):

- success 4 (extended by DEC-177): the record is one JSON line per call in
  ``.gov-runtime/records.jsonl``, with DEC-122's fields and
  ``action: "recorded"``
- success 4 (negative): in-scope changes write no record and no finding
- success 4 (negative): ``tests/acceptance/**`` stays a finding, not a record
- success 5 / failure 2: other roles' changes stay findings, never records
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_tests = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_tests / "W1-03"))

import w1_03_support as support  # noqa: E402

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
TICKET = support.TICKET_ID
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
SOURCE = support.SOURCE_FILE

RECORDS_REL = ".gov-runtime/records.jsonl"

# The fields of a record (DEC-122 + DEC-177).  Same as a finding, but action
# is "recorded" instead of "reverted" or "flagged".
RECORD_FIELDS = ("time", "session_id", "agent_type", "role", "ticket", "tool",
                 "command", "paths", "action", "reason")


# --------------------------------------------------------------------------
# Helpers for records.jsonl
# --------------------------------------------------------------------------

def record_lines(project):
    """Non-empty lines of ``.gov-runtime/records.jsonl``; empty when the file is absent."""
    path = Path(project) / RECORDS_REL
    if not path.is_file():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def assert_one_record(project, before_count, what):
    """Exactly one new record with ``action: "recorded"`` and DEC-122's fields."""
    lines = record_lines(project)
    new = lines[before_count:]
    assert len(new) == 1, (
        f"{what}: expected 1 new record in {RECORDS_REL}, got {len(new)}"
        + (f": {new}" if new else "")
    )
    try:
        data = json.loads(new[0])
    except ValueError:
        raise AssertionError(
            f"{what}: a line of {RECORDS_REL} is not JSON: {new[0][:300]!r}"
        ) from None
    assert isinstance(data, dict), (
        f"{what}: a line of {RECORDS_REL} is not a JSON object: {new[0][:300]!r}"
    )
    missing = [f for f in RECORD_FIELDS if f not in data]
    assert not missing, (
        f"{what}: the record lacks {', '.join(missing)}: {new[0][:400]!r}"
    )
    assert data["action"] == "recorded", (
        f"{what}: action is {data['action']!r}, not 'recorded'"
    )
    return data


def assert_no_record(project, before_count, what):
    """No new record was written to ``records.jsonl``."""
    lines = record_lines(project)
    new = lines[before_count:]
    assert not new, (
        f"{what}: expected no new records in {RECORDS_REL}, got {len(new)}: {new}"
    )


# --------------------------------------------------------------------------
# The record is written for an orchestrator change outside ticket paths
# --------------------------------------------------------------------------

# Each path is outside the orchestrator's ticket paths (".claude/settings.json",
# "governance/project/bootstrap.md") and is not under tests/acceptance/**.
OUTSIDE_TICKET = {
    "docs": "docs/notes.md",
    "pyproject": "pyproject.toml",
    "readme": "README.md",
    "source": SOURCE,
    "unit-test": "tests/unit/guard/test_decide.py",
}


@pytest.mark.parametrize("case", sorted(OUTSIDE_TICKET), ids=sorted(OUTSIDE_TICKET))
def test_orchestrator_change_outside_ticket_writes_a_record(project, after_bash, case):
    """DEC-177: one record per call when the orchestrator changes an out-of-scope path."""
    relpath = OUTSIDE_TICKET[case]
    records_before = len(record_lines(project))
    command = f"echo changed >> {relpath}"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET, changed=[relpath])
    what = f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}"
    support.assert_silent(result, what)
    assert_one_record(project, records_before, what)


def test_record_has_dec_122_fields_and_action_recorded(project, after_bash):
    """DEC-177: the record carries every field DEC-122 defines, with action ``recorded``."""
    records_before = len(record_lines(project))
    command = "echo changed >> README.md"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET, changed=["README.md"])
    what = f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}"
    support.assert_silent(result, what)
    data = assert_one_record(project, records_before, what)
    # Spot-check individual fields beyond the structural assertion.
    assert data["session_id"] == result.session_id, (
        f"session_id is {data['session_id']!r}, not {result.session_id!r}"
    )
    assert data["tool"] == "Bash", f"tool is {data['tool']!r}, not 'Bash'"
    assert data["command"] == result.command, (
        f"command is {data['command']!r}, not {result.command!r}"
    )
    assert isinstance(data["paths"], list) and data["paths"], (
        f"paths is not a non-empty list: {data['paths']!r}"
    )
    assert isinstance(data["reason"], str) and data["reason"].strip(), (
        f"reason is empty: {data['reason']!r}"
    )
    assert data["time"], f"time is empty: {data['time']!r}"


def test_one_record_for_multiple_paths_changed(project, after_bash):
    """DEC-177: one record per call, however many paths changed."""
    records_before = len(record_lines(project))
    command = "echo changed >> README.md && echo changed >> pyproject.toml"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET,
                        changed=["README.md", "pyproject.toml"])
    what = f"`{command}` by the orchestrator"
    support.assert_silent(result, what)
    assert_one_record(project, records_before, what)


# --------------------------------------------------------------------------
# No record for a change inside the ticket's allowed_paths
# --------------------------------------------------------------------------

def test_in_scope_change_writes_no_record(project, after_bash):
    """DEC-177: a change inside the ticket's allowed_paths writes no record and no finding."""
    records_before = len(record_lines(project))
    command = "echo changed >> .claude/settings.json"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET,
                        changed=[".claude/settings.json"])
    what = f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}"
    support.assert_silent(result, what)
    assert_no_record(project, records_before, what)


# --------------------------------------------------------------------------
# tests/acceptance/** stays a finding, not a record
# --------------------------------------------------------------------------

def test_acceptance_change_writes_finding_not_record(project, after_bash):
    """DEC-177: tests/acceptance/** stays a finding in findings.jsonl, not a record."""
    records_before = len(record_lines(project))
    command = f"echo changed >> {ACCEPTANCE_FILE}"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET,
                        changed=[ACCEPTANCE_FILE])
    what = f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}"
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)
    assert_no_record(project, records_before, what)


# --------------------------------------------------------------------------
# Other roles never produce a record
# --------------------------------------------------------------------------

def test_engineer_change_outside_ticket_writes_finding_not_record(project, after_bash):
    """DEC-177: other roles never produce a record line; their changes stay findings."""
    records_before = len(record_lines(project))
    command = "echo changed >> README.md"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"])
    what = f"`{command}` by the engineer on {TICKET}"
    support.assert_caught(result, "README.md", what=what)
    assert_no_record(project, records_before, what)


# --------------------------------------------------------------------------
# Record with no active ticket
# --------------------------------------------------------------------------

def test_orchestrator_without_ticket_writes_a_record(project, after_bash):
    """DEC-177: with no active ticket, every non-acceptance change writes a record."""
    records_before = len(record_lines(project))
    command = "echo changed >> README.md"
    result = after_bash(project, command, ORCHESTRATOR, None, changed=["README.md"])
    what = f"`{command}` by the orchestrator without a ticket"
    support.assert_silent(result, what)
    assert_one_record(project, records_before, what)


# --------------------------------------------------------------------------
# Orchestrator subagent in orchestrator session also writes a record
# --------------------------------------------------------------------------

def test_orchestrator_subagent_in_orchestrator_session_writes_a_record(project, after_bash):
    """DEC-177 + DEC-178: in an orchestrator session, the subagent's out-of-scope
    change is also recorded (not a finding)."""
    records_before = len(record_lines(project))
    command = "echo changed >> README.md"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET,
                        changed=["README.md"], subagent=ORCHESTRATOR)
    what = f"`{command}` by an orchestrator subagent in an orchestrator session"
    support.assert_silent(result, what)
    assert_one_record(project, records_before, what)
