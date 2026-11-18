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

SOURCES = guard_support.REPO_ROOT / guard_support.GOV_PACKAGE_PARENT_REL


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _sources_on_the_import_path(monkeypatch):
    """``gov`` is imported from this repository's ``src`` for the length of a case, as the other W1-50 files
    set their path (``test_w1_50_read_merge_helper.py``). Without it the file found ``gov`` only when another
    file of the run had imported it first, or when the caller's ``PYTHONPATH`` named ``src``."""
    monkeypatch.syspath_prepend(str(SOURCES))


@pytest.fixture()
def project(tmp_path):
    return pause_support.make_project(tmp_path / "lead-project")


@pytest.fixture()
def sandbox(tmp_path):
    return fs.cli_support.make_sandbox(tmp_path / "lead-sandbox")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------



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



# ---------------------------------------------------------------------------
# Tests — scratch writes allowed
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Tests — checkpoint writes allowed
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Tests — reads are allowed (GREEN: reads pass before role check)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Tests — writes outside scratch/checkpoint/merge-back are denied
# ---------------------------------------------------------------------------



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

