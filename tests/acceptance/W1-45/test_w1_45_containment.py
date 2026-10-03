"""W1-45 -- the containment check records orchestrator changes without raising findings,
unless the change is under tests/acceptance/** (DEC-171).

DEC-156 + DEC-171: the orchestrator may write anywhere except
``tests/acceptance/**``, and a change outside the active ticket's
``allowed_paths`` is a record, not a containment finding, while a change under
``tests/acceptance/**`` stays a finding.

KPIs tested here (containment / PostToolUse):

- success 3: an orchestrator commit of non-acceptance files passes the guard
  [CAP-58.e]
- success 4: the containment check still records; a change outside the ticket's
  paths is a record, not a finding; a change under ``tests/acceptance/**``
  stays a finding (DEC-156, DEC-171) [CAP-58.e]
- success 5: other roles are still caught outside their ticket paths (DEC-112)
- failure 1: an orchestrator change under ``tests/acceptance/**`` is caught
- failure 2: no other role gains a silent pass outside its ticket paths
"""

from __future__ import annotations

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
WBS = support.TICKET_WBS_ID
ACCEPTANCE = support.ACCEPTANCE_REL
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
SOURCE = support.SOURCE_FILE


# --------------------------------------------------------------------------
# KPI success 4: a change outside the ticket's allowed_paths is a record, not a finding
# --------------------------------------------------------------------------

# Each path is outside the orchestrator's ticket paths (".claude/settings.json",
# "governance/project/bootstrap.md") but inside the repository and not under
# tests/acceptance/**.  Under DEC-171 these must be SILENT (records, not findings).
# Under the current code every one is CAUGHT as a containment finding.
RECORD_NOT_FINDING = {
    "readme": "README.md",
    "source": SOURCE,
    "docs": "docs/notes.md",
    "pyproject": "pyproject.toml",
    "unit-test": "tests/unit/guard/test_decide.py",
}


@pytest.mark.parametrize("case", sorted(RECORD_NOT_FINDING), ids=sorted(RECORD_NOT_FINDING))
def test_orchestrator_change_outside_ticket_paths_is_a_record_not_a_finding(project, after_bash, case):
    """KPI success 4.  DEC-171: the containment check records but does not raise a finding."""
    relpath = RECORD_NOT_FINDING[case]
    command = f"echo changed >> {relpath}"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET, changed=[relpath])
    support.assert_silent(result, f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}")


def test_orchestrator_in_scope_change_is_still_silent(project, after_bash):
    """KPI success 4.  A change inside the ticket's allowed_paths stays silent too."""
    command = "echo changed >> .claude/settings.json"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET, changed=[".claude/settings.json"])
    support.assert_silent(result, f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}")


# --------------------------------------------------------------------------
# KPI success 4 (cont.) / failure 1: tests/acceptance/** stays a finding
# --------------------------------------------------------------------------

def test_orchestrator_change_under_acceptance_stays_a_finding(project, after_bash):
    """KPI success 4, failure 1.  DEC-156: tests/acceptance/** is the one exclusion."""
    command = f"echo changed >> {ACCEPTANCE_FILE}"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET, changed=[ACCEPTANCE_FILE])
    what = f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}"
    support.assert_caught(result, ACCEPTANCE_FILE, what=what, action=support.REVERTED)


# --------------------------------------------------------------------------
# KPI success 3: an orchestrator commit of non-acceptance files is silent
# --------------------------------------------------------------------------

def test_orchestrator_commit_outside_ticket_paths_is_silent(project, after_bash):
    """KPI success 3.  DEC-156 + DEC-171: the commit carries a record, not a finding."""
    command = "echo changed >> README.md && git commit -qam work"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    support.assert_silent(result, f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}")


def test_orchestrator_commit_of_engineer_source_is_silent(project, after_bash):
    """KPI success 3.  The orchestrator commits verified work inside the engineer's ticket paths."""
    command = f"echo changed >> {SOURCE} && git commit -qam work"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    support.assert_silent(result, f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}")


def test_orchestrator_commit_touching_acceptance_is_caught(project, after_bash):
    """KPI success 3, failure 1.  A commit that touches tests/acceptance/** is caught."""
    command = f"echo changed >> {ACCEPTANCE_FILE} && git add {ACCEPTANCE_FILE} && git commit -qam work"
    result = after_bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    what = f"`{command}` by the orchestrator on {ORCHESTRATOR_TICKET}"
    support.assert_caught(result, ACCEPTANCE_FILE, what=what)


# --------------------------------------------------------------------------
# KPI success 5 / failure 2: the engineer's containment is unchanged
# --------------------------------------------------------------------------

def test_engineer_change_outside_ticket_paths_is_still_caught(project, after_bash):
    """KPI success 5, failure 2.  The orchestrator's scope does not affect other roles."""
    command = "echo changed >> README.md"
    result = after_bash(project, command, ENGINEER, TICKET, changed=["README.md"])
    support.assert_caught(result, "README.md", what=f"`{command}` by the engineer on {TICKET}")
