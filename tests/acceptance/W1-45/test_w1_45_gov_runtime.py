"""W1-45 -- the guard denies .gov-runtime/ other than scratch/** to the orchestrator (DEC-176).

DEC-176, amending DEC-156: everything under ``.gov-runtime/`` other than
``scratch/**`` stays denied to the orchestrator -- the freeze flag, the
snapshots, the findings file and the records file -- for file tools and Bash
writes, with any active ticket and with none, frozen or not.

``.gov-runtime/scratch/**`` (including ``scratch/orchestrator/``) stays writable
when not frozen.

Setting or lifting a freeze is the owner's action, not any agent role's.  The
W1-02 test ``test_no_agent_role_can_lift_the_freeze`` covers that invariant and
is not changed here.

KPIs tested here (guard / PreToolUse):

- DEC-176: ``.gov-runtime/`` other than ``scratch/**`` is denied to the
  orchestrator, for file tools and Bash writes, with any ticket and with none,
  frozen or not
- success 7 (confirmation): ``scratch/**`` stays writable for the orchestrator
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_tests = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_tests / "W1-02"))

import w1_02_support as support  # noqa: E402

ORCHESTRATOR = support.ORCHESTRATOR
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
TICKET = support.TICKET_ID

FILE_TOOLS = ["Edit", "Write"]

# Paths the guard must deny for the orchestrator (DEC-176).
# Each is under .gov-runtime/ and NOT under scratch/**.
GOV_RUNTIME_DENIED = {
    "findings": ".gov-runtime/findings.jsonl",
    "freeze-flag": ".gov-runtime/freeze",
    "records": ".gov-runtime/records.jsonl",
    "snapshots": ".gov-runtime/snapshots/snap.json",
}


# --------------------------------------------------------------------------
# File tools (Edit, Write) denied for .gov-runtime/ paths
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(GOV_RUNTIME_DENIED), ids=sorted(GOV_RUNTIME_DENIED))
def test_orchestrator_denied_gov_runtime_with_file_tools(project, write, case):
    """DEC-176: everything under .gov-runtime/ other than scratch/** is denied."""
    relpath = GOV_RUNTIME_DENIED[case]
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, ORCHESTRATOR, ORCHESTRATOR_TICKET, tool_name)
        support.assert_denied(result, f"{tool_name} on {relpath} by the orchestrator")


# --------------------------------------------------------------------------
# Bash writes denied
# --------------------------------------------------------------------------

BASH_GOV_RUNTIME_DENIED = {
    "redirect-to-findings": "echo changed >> .gov-runtime/findings.jsonl",
    "redirect-to-freeze": "echo > .gov-runtime/freeze",
    "redirect-to-records": "echo changed >> .gov-runtime/records.jsonl",
    "touch-snapshots": "touch .gov-runtime/snapshots/snap.json",
}


@pytest.mark.parametrize("case", sorted(BASH_GOV_RUNTIME_DENIED), ids=sorted(BASH_GOV_RUNTIME_DENIED))
def test_orchestrator_bash_denied_gov_runtime(project, bash_guard, case):
    """DEC-176: Bash writes to .gov-runtime/ other than scratch/** are denied."""
    command = BASH_GOV_RUNTIME_DENIED[case]
    result = bash_guard(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    support.assert_denied(result, f"Bash `{command}` by the orchestrator")


# --------------------------------------------------------------------------
# Denied with no active ticket
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(GOV_RUNTIME_DENIED), ids=sorted(GOV_RUNTIME_DENIED))
def test_orchestrator_denied_gov_runtime_without_ticket(project, write, case):
    """DEC-176: the denial holds with no active ticket."""
    relpath = GOV_RUNTIME_DENIED[case]
    result = write(project, relpath, ORCHESTRATOR, None)
    support.assert_denied(result, f"Write on {relpath} by the orchestrator without a ticket")


# --------------------------------------------------------------------------
# Denied while frozen
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(GOV_RUNTIME_DENIED), ids=sorted(GOV_RUNTIME_DENIED))
def test_orchestrator_denied_gov_runtime_while_frozen(project, write, case):
    """DEC-176: the denial holds while the repository is frozen."""
    support.set_freeze(project)
    relpath = GOV_RUNTIME_DENIED[case]
    result = write(project, relpath, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    support.assert_denied(result, f"Write on {relpath} by the orchestrator while frozen")


# --------------------------------------------------------------------------
# scratch/** stays writable (confirmation of existing behaviour)
# --------------------------------------------------------------------------

def test_scratch_stays_writable_for_orchestrator(project, write):
    """DEC-176 does not touch scratch.  .gov-runtime/scratch/** stays writable."""
    for relpath in (
        ".gov-runtime/scratch/note.txt",
        ".gov-runtime/scratch/orchestrator/checkpoint.json",
    ):
        result = write(project, relpath, ORCHESTRATOR, ORCHESTRATOR_TICKET)
        support.assert_allowed(result, f"Write on {relpath} by the orchestrator")
