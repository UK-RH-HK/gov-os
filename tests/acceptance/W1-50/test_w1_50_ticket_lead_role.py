"""KPI 3 — the ticket lead's own role (DEC-434, DEC-435).

"A ticket lead runs under its own role (``ticket-lead``), may write only its
checkpoint, scratch and merge-backs judged by the three-way rule. Writes to
source, tests, tickets, or documents are refused."

19 tests.  Before implementation every test that expects the guard to accept
``ticket-lead`` as a known role is red: ``ticket-lead`` is not in
``KNOWN_ROLES`` of ``src/gov/guard/decide.py``.

Red reason: the guard denies every write with "role 'ticket-lead' is not a
known role" (line 783 of ``decide.py``).  Read-only tools pass because reads
are allowed before the role check.  ``gov launch`` refuses ``ticket-lead``
because it is not in ``WORKER_ROLES`` of ``src/gov/launch/launcher.py``
(line 249) — this is correct, ticket leads are not launched workers.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_50_freeze_support as fs  # noqa: E402

guard_support = fs.guard_support
pause_support = fs.pause_support
launch_support = fs.launch_support

TICKET_LEAD = "ticket-lead"
TICKET = guard_support.TICKET_ID

SCRATCH_REL = ".gov-runtime/scratch/notes.md"
CHECKPOINT_REL = ".gov-runtime/scratch/lead/CHECKPOINT.md"
SRC_REL = "src/gov/guard/decide.py"
TESTS_REL = "tests/acceptance/W1-50/test_example.py"
TICKET_REL = ".tickets/DAEO-xnbx.md"
DOCS_REL = "docs/plan/WAVE_1_WBS.md"
GOVERNANCE_REL = "governance/project/roles.yaml"
TEMPLATE_REL = "governance/template/claude-settings.yaml"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def project(tmp_path):
    return pause_support.make_project(tmp_path / "lead-project")


@pytest.fixture()
def sandbox(tmp_path):
    return fs.cli_support.make_sandbox(tmp_path / "lead-sandbox")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _guard(project, sandbox, tool_name, rel, role=TICKET_LEAD, ticket=TICKET):
    """Run the guard hook with the given tool and relative path."""
    tool_input = guard_support.edit_tool_input(tool_name, Path(project) / rel)
    return guard_support.run_hook(project, tool_name, tool_input, sandbox, role=role, ticket=ticket)


def _guard_bash(project, sandbox, command, role=TICKET_LEAD, ticket=TICKET):
    return guard_support.run_hook(
        project, "Bash", guard_support.bash_tool_input(command),
        sandbox, role=role, ticket=ticket,
    )


def _assert_allowed(result, what):
    assert result.decision == "allow" and result.returncode == 0, \
        f"{what}: expected allow, got {result.decision}: {result.describe()}"


def _assert_denied(result, what, *, reason_fragment=None):
    assert result.decision == "deny", f"{what}: expected deny, got {result.decision}: {result.describe()}"
    assert result.returncode == 0, f"{what}: the guard failed (exit 2) instead of deciding: {result.describe()}"
    if reason_fragment:
        assert reason_fragment in result.stdout.lower(), (
            f"{what}: denial reason does not contain {reason_fragment!r}: {result.stdout[:300]}"
        )


# ---------------------------------------------------------------------------
# Tests — ticket-lead must be in KNOWN_ROLES
# ---------------------------------------------------------------------------

def test_ticket_lead_in_known_roles(project, sandbox):
    """``ticket-lead`` must be in ``KNOWN_ROLES`` so the guard does not deny it
    outright.  Currently it is NOT present, so this test is red.
    """
    result = _guard(project, sandbox, "Write", SCRATCH_REL)
    not_known = "not a known role" in result.stdout.lower()
    assert not not_known, (
        f"the guard denies ticket-lead as 'not a known role' — "
        f"ticket-lead must be added to KNOWN_ROLES (DEC-434)"
    )


# ---------------------------------------------------------------------------
# Tests — scratch writes allowed
# ---------------------------------------------------------------------------

def test_ticket_lead_may_write_scratch(project, sandbox):
    """Scratch is allowed for every known role (``_is_in_scratch`` check).

    Red because ticket-lead is not yet in KNOWN_ROLES.
    """
    result = _guard(project, sandbox, "Write", SCRATCH_REL)
    _assert_allowed(result, "ticket-lead writing scratch")


def test_ticket_lead_may_write_scratch_via_bash(project, sandbox):
    """Bash writes to scratch are allowed."""
    command = f"echo x > {Path(project) / SCRATCH_REL}"
    result = _guard_bash(project, sandbox, command)
    _assert_allowed(result, "ticket-lead bash write to scratch")


# ---------------------------------------------------------------------------
# Tests — checkpoint writes allowed
# ---------------------------------------------------------------------------

def test_ticket_lead_may_write_checkpoint(project, sandbox):
    """The lead's checkpoint is under scratch (DP-L2, DEC-434): no
    ``_get_allowed_paths`` patterns, the ``_is_in_scratch`` rule covers it.

    Red because ticket-lead is not yet in KNOWN_ROLES.
    """
    result = _guard(project, sandbox, "Write", CHECKPOINT_REL)
    _assert_allowed(result, "ticket-lead writing checkpoint")


# ---------------------------------------------------------------------------
# Tests — reads are allowed (GREEN: reads pass before role check)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool", ["Read", "Grep", "Glob"])
def test_ticket_lead_may_read(project, sandbox, tool):
    """Read-only tools are allowed for any role (guard allows READ_TOOLS
    before checking the role).  These tests should be GREEN already.
    """
    if tool == "Glob":
        tool_input = {"pattern": "src/**/*.py", "path": str(project)}
    elif tool == "Grep":
        tool_input = {"pattern": "def ", "path": str(project)}
    else:
        tool_input = {"file_path": str(project / SRC_REL)}
    result = guard_support.run_hook(project, tool, tool_input, sandbox,
                                    role=TICKET_LEAD, ticket=TICKET)
    _assert_allowed(result, f"ticket-lead {tool}")


def test_ticket_lead_may_run_read_only_bash(project, sandbox):
    """A Bash command with no write targets is allowed.

    GREEN: the guard extracts no write target → no path check → allow.
    """
    result = _guard_bash(project, sandbox, "git log --oneline -5")
    _assert_allowed(result, "ticket-lead read-only bash")


# ---------------------------------------------------------------------------
# Tests — writes outside scratch/checkpoint/merge-back are denied
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rel,label", [
    (SRC_REL, "source"),
    (TESTS_REL, "tests"),
    (TICKET_REL, "ticket file"),
    (DOCS_REL, "docs"),
    (GOVERNANCE_REL, "governance"),
    (TEMPLATE_REL, "template"),
])
def test_ticket_lead_denied_write_to(project, sandbox, rel, label):
    """The ticket lead may not write source, tests, tickets, docs, governance
    or template files (DEC-434, DEC-435).

    Before ``ticket-lead`` is in KNOWN_ROLES the denial reason is "not a
    known role".  After, it must be a path-based denial.
    """
    result = _guard(project, sandbox, "Write", rel)
    _assert_denied(result, f"ticket-lead write to {label}")


def test_ticket_lead_denied_bash_write_to_source(project, sandbox):
    """A Bash command that writes to source is denied."""
    command = f"echo x > {Path(project) / SRC_REL}"
    result = _guard_bash(project, sandbox, command)
    _assert_denied(result, "ticket-lead bash write to source")


# ---------------------------------------------------------------------------
# Tests — ticket-lead is NOT a worker role (GREEN: correct and stays so)
# ---------------------------------------------------------------------------

def test_ticket_lead_not_in_worker_roles():
    """``ticket-lead`` must NOT be in ``WORKER_ROLES`` of the launcher.

    Ticket leads are not launched as workers (DEC-236); they are the
    ticket's owner, not a worker session.  GREEN.
    """
    from gov.launch.launcher import WORKER_ROLES
    assert TICKET_LEAD not in WORKER_ROLES, (
        f"ticket-lead is in WORKER_ROLES: it must not be a launched worker (DEC-236)"
    )


def test_gov_launch_refuses_ticket_lead(tmp_path):
    """``gov launch ticket-lead <ticket>`` is refused."""
    project = launch_support.make_project(tmp_path / "launch-lead")
    sandbox = fs.cli_support.make_sandbox(tmp_path / "launch-lead-sandbox")
    cli = launch_support.install_stand_in_cli(sandbox)
    result = launch_support.launch(project, sandbox, cli, TICKET_LEAD, TICKET)
    launch_support.assert_refused(result, "not a worker role")


# ---------------------------------------------------------------------------
# Tests — ticket-lead cannot set or lift a freeze
# ---------------------------------------------------------------------------

def test_ticket_lead_cannot_set_freeze(project, sandbox):
    """``gov pause`` as ticket-lead is refused (not owner, not orchestrator).

    GREEN: the pause command checks GOV_ROLE against ORCHESTRATOR.
    """
    result = pause_support.pause(project, sandbox, role=TICKET_LEAD)
    assert result.returncode != 0, (
        f"gov pause as ticket-lead was not refused: {result.stdout[:200]}"
    )


# ---------------------------------------------------------------------------
# Tests — the ticket lead is stricter than the orchestrator
# ---------------------------------------------------------------------------

def test_ticket_lead_stricter_than_orchestrator(project, sandbox):
    """The orchestrator may write source files within its ticket's paths;
    the ticket lead may not.  This verifies the scope is narrower (DEC-435).
    """
    orch_result = _guard(project, sandbox, "Write", SRC_REL,
                         role=guard_support.ORCHESTRATOR,
                         ticket=guard_support.ORCHESTRATOR_TICKET_ID)
    lead_result = _guard(project, sandbox, "Write", SRC_REL,
                         role=TICKET_LEAD, ticket=TICKET)
    _assert_denied(lead_result, "ticket-lead write to source (vs orchestrator)")
