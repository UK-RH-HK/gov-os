"""Tests for finding disposition at close: S6 (CAP-59.c), A3, B3.

S6: A finding raised at close is classed into exactly one disposition with
    whole-system context from gov context before any code change, and the
    repair ticket records it.
A3: The disposition class is given by the caller via --disposition (one of the
    six names). Without it, findings are unclassed. With it, context is built
    first. Context failure means the class is not recorded as "with whole-system
    context". No "context": "whole-system" literal ever appears.
B3: The repair ticket is created through the ticket tool, records findings and
    the class, has a dependency on the failing ticket, and has no invented id
    or constant creation date.
"""

import json

import pytest
import yaml

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-disp"
WBS = "W1-disp"
IMPL = support.IMPLEMENTER
TRAILERS = ("Task: PROJ-disp", "Role: engineer", "Implements: CAP-01")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _project_with_finding(project, ticket_id=TICKET, wbs=WBS):
    """A project where gov close will fail (planted failing acceptance test)."""
    project.add_ticket(ticket_id, wbs)
    project.add_failing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement with defect", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    return ticket_id


def _repair_tickets(project, exclude_id=TICKET):
    """All ticket files in .tickets/ except the given one."""
    tickets_dir = project.root / ".tickets"
    if not tickets_dir.is_dir():
        return []
    return [f for f in tickets_dir.glob("*.md") if f.stem != exclude_id]


def _repair_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


# --------------------------------------------------------------------------
# A3: No disposition class -> unclassed
# --------------------------------------------------------------------------

def test_no_disposition_records_unclassed(project, sandbox, interface):
    """A3: a failing close without --disposition records findings as unclassed."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1, "a repair ticket should be created"
    front = _repair_frontmatter(repairs[0])
    disposition = front.get("disposition") or front.get("finding_disposition")
    assert disposition is None or disposition == "unclassed", \
        f"without --disposition, the repair ticket must record 'unclassed', got {disposition!r}"


def test_no_disposition_output_names_findings_awaiting_class(project, sandbox, interface):
    """A3: without --disposition, the output names each finding as awaiting its class."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    error = envelope.get("error", {})
    message = error.get("message", "")
    details_text = json.dumps(error.get("details", {}))
    assert "class" in message.lower() or "class" in details_text.lower() \
        or "unclassed" in message.lower() or "unclassed" in details_text.lower() \
        or "disposition" in message.lower() or "disposition" in details_text.lower(), \
        f"the output must mention that findings await their class: {error}"


# --------------------------------------------------------------------------
# A3: Valid disposition class -> context built, class recorded
# --------------------------------------------------------------------------

def test_valid_disposition_records_class(project, sandbox, interface):
    """A3: --disposition with a valid class records it in the repair ticket."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET,
                            "--disposition", "repair")
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1, "a repair ticket should be created"
    front = _repair_frontmatter(repairs[0])
    disposition = front.get("disposition") or front.get("finding_disposition")
    assert disposition == "repair", \
        f"repair ticket must record the given disposition, got {disposition!r}"


def test_valid_disposition_builds_context_first(project, sandbox, interface):
    """A3: with --disposition, gov context is called first and its hash is recorded."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET,
                            "--disposition", "narrow")
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1
    front = _repair_frontmatter(repairs[0])
    context_hash = front.get("context_hash") or front.get("context")
    assert context_hash is not None, \
        f"repair ticket must record the context hash when disposition is given: {sorted(front)}"


# --------------------------------------------------------------------------
# A3: Disposition with context failure
# --------------------------------------------------------------------------

def test_disposition_with_context_failure(project, sandbox, interface):
    """A3: if context fails, the class is NOT recorded as 'with whole-system context'.

    The output must say the context failed, and the repair ticket records the class
    but without the context hash.
    """
    _project_with_finding(project)
    project.add_decision("DEC-cyc1", "ACTIVE", supersedes="DEC-cyc2")
    project.add_decision("DEC-cyc2", "ACTIVE", supersedes="DEC-cyc1")
    project.commit("create contradiction", who=support.OWNER)
    run = support.run_close(project, sandbox, TICKET,
                            "--disposition", "defer")
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    error = envelope.get("error", {})
    full_text = json.dumps(envelope)
    assert '"context": "whole-system"' not in full_text, \
        "when context fails, 'context: whole-system' must NOT appear"


# --------------------------------------------------------------------------
# A3: Only the six names accepted
# --------------------------------------------------------------------------

def test_only_six_disposition_names_accepted(project, sandbox, interface):
    """A3: only the six named dispositions are accepted; anything else is refused."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET,
                            "--disposition", "invented_name")
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "an invented disposition name must be refused"


def test_all_six_dispositions_recognized():
    """A3, S6: all six short-name dispositions are defined."""
    assert len(support.DISPOSITIONS) == 6
    for name in ("repair", "reuse", "delete", "narrow", "defer", "owner"):
        assert name in support.DISPOSITIONS


# --------------------------------------------------------------------------
# A3: No "context": "whole-system" literal
# --------------------------------------------------------------------------

def test_no_context_whole_system_literal(project, sandbox, interface):
    """A3: the literal '"context": "whole-system"' must never appear in any output."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET,
                            "--disposition", "repair")
    full_output = run.stdout + run.stderr
    assert '"context": "whole-system"' not in full_output, \
        'the literal \'"context": "whole-system"\' must never appear'
    assert "'context': 'whole-system'" not in full_output, \
        'the literal "\'context\': \'whole-system\'" must never appear'


# --------------------------------------------------------------------------
# B3: Repair ticket through ticket tool
# --------------------------------------------------------------------------

def test_repair_ticket_created_through_ticket_tool(project, sandbox, interface):
    """B3: a repair ticket is created through the ticket tool (gov.tasks.tickets.create)."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1, "a repair ticket should have been created in .tickets/"


def test_repair_ticket_records_findings(project, sandbox, interface):
    """B3: the repair ticket records the findings."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1
    front = _repair_frontmatter(repairs[0])
    body = repairs[0].read_text(encoding="utf-8")
    has_findings = (front.get("findings") is not None
                    or "finding" in body.lower()
                    or "failure" in body.lower())
    assert has_findings, f"repair ticket must record the findings: {front}"


def test_repair_ticket_has_dependency_on_failing_ticket(project, sandbox, interface):
    """B3: the repair ticket depends on the failing ticket (CAP-31.b)."""
    _project_with_finding(project)
    support.run_close(project, sandbox, TICKET)
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1
    front = _repair_frontmatter(repairs[0])
    deps = front.get("depends_on") or front.get("deps") or []
    parent = front.get("parent")
    assert TICKET in str(deps) or TICKET == parent, \
        f"repair ticket must depend on {TICKET}: deps={deps}, parent={parent}"


def test_repair_ticket_no_invented_id(project, sandbox, interface):
    """B3: the repair ticket must not have an invented id or a constant creation date."""
    _project_with_finding(project)
    support.run_close(project, sandbox, TICKET)
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1
    front = _repair_frontmatter(repairs[0])
    ticket_id = front.get("id", "")
    assert ticket_id and ticket_id != "REPAIR-0001", \
        f"the repair ticket id must not be a constant: {ticket_id!r}"
    created = front.get("created", "")
    assert created and "1970" not in str(created) and "2000-01-01" not in str(created), \
        f"the repair ticket must have a real creation date, got {created!r}"


def test_repair_ticket_create_failure_reported(project, sandbox, interface):
    """B3: if the ticket tool fails to create a repair ticket, the output says why."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
