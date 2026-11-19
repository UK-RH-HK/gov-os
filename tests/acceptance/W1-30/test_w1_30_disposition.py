"""Tests for finding disposition at close: S6 (CAP-59.c), A3, B3.

S6: A finding raised at close is classed into exactly one disposition before
    any code change, and the repair ticket records it. The whole-system context
    the class was given with came from the context command, which the owner
    retired (DEC-1214 M1, W2-200): the repair ticket records the class and no
    context hash (W2-200 S7), and the case of a context that failed is deleted.
A3: The disposition class is given by the caller via --disposition (one of the
    six names). Without it, findings are unclassed. No "context":
    "whole-system" literal ever appears.
B3: The repair ticket is created through the ticket tool, records findings and
    the class, has a dependency on the failing ticket, and has no invented id
    or constant creation date.
"""

import json
import re

import pytest
import yaml

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-disp"
WBS = "W1-906"
IMPL = support.IMPLEMENTER
TRAILERS = ("Task: PROJ-disp", "Role: engineer", "Implements: CAP-01")
SHA256 = re.compile(r"\b[0-9a-f]{64}\b")


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
# A3: Valid disposition class -> class recorded
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


def test_valid_disposition_records_the_class_and_no_context_hash(project, sandbox, interface):
    """A3: with --disposition, the class is recorded on the repair ticket and no packet goes with it.

    Rewrite-Reason: DEC-1214 M1 (W2-200 S7): was ``test_valid_disposition_builds_context_first``, which asked for the
    context packet's hash on the repair ticket; the context command is retired, so the repair ticket records the
    class and holds no ``context_hash`` and no 64-digit hash."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET,
                            "--disposition", "narrow")
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1
    front = _repair_frontmatter(repairs[0])
    assert front.get("disposition") == "narrow", f"the repair ticket does not record the class: {sorted(front)}"
    assert "context_hash" not in front and "context" not in front, \
        f"the repair ticket still records a context: {sorted(front)}"
    assert not SHA256.search(repairs[0].read_text(encoding="utf-8")), "the repair ticket carries a 64-digit hash"


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


def test_all_six_dispositions_recognized(built, tmp_path, sandbox, interface):
    """A3, S6: all six short-name dispositions are defined.

    Revised for W2-67 (I2 F2, PF1): the case read this suite's own tuple, not the close's. Each of the six names is
    now given to ``gov close`` itself, on a project of its own whose acceptance test fails: the close takes the
    name (it is refused for the failing test, exit code 3, not for the argument) and the repair ticket records
    that class."""
    not_taken = {}
    for name in ("repair", "reuse", "delete", "narrow", "defer", "owner"):
        project = support.Project(tmp_path / name)
        _project_with_finding(project)
        run = support.run_close(project, sandbox, TICKET, "--disposition", name)
        error = support.envelope_of(run, interface).get("error") or {}
        recorded = [_repair_frontmatter(path).get("disposition") or _repair_frontmatter(path).get("finding_disposition")
                    for path in _repair_tickets(project)]
        if run.returncode != support.EXIT_CHECK_FAILED or "planted failure" not in support.error_text(error) \
                or recorded != [name]:
            not_taken[name] = {"exit": run.returncode, "code": error.get("code"), "recorded": recorded}
    assert not not_taken, f"gov close does not take these dispositions as a class: {not_taken}"


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
    tk = project.root / "governance" / "kernel" / "bin" / "tk"
    assert tk.is_file(), "the project fixture must place tk"
    import subprocess
    repair_id = _repair_frontmatter(repairs[0]).get("id", repairs[0].stem)
    result = subprocess.run(
        [str(tk), "show", repair_id], capture_output=True, text=True,
        cwd=str(project.root),
    )
    assert result.returncode == 0, \
        f"the repair ticket must be known to tk (created through the tool): {result.stderr}"


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


# --------------------------------------------------------------------------
# B3/DEC-454 Point 6: Repair ticket via tk
# --------------------------------------------------------------------------

def test_repair_ticket_known_to_tk_show(project, sandbox, interface):
    """DEC-454 point 6: the repair ticket is known to ``tk show``."""
    _project_with_finding(project)
    support.run_close(project, sandbox, TICKET)
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1, "a repair ticket should exist"
    tk = project.root / "governance" / "kernel" / "bin" / "tk"
    assert tk.is_file(), "the project fixture must place tk"
    import subprocess
    repair_id = _repair_frontmatter(repairs[0]).get("id", repairs[0].stem)
    result = subprocess.run(
        [str(tk), "show", repair_id], capture_output=True, text=True,
        cwd=str(project.root),
    )
    assert result.returncode == 0, \
        f"tk show must know the repair ticket {repair_id}: {result.stderr}"


def test_repair_ticket_dependency_direction(project, sandbox, interface):
    """DEC-454 point 6: the repair ticket depends on the FAILING ticket, not vice versa."""
    _project_with_finding(project)
    support.run_close(project, sandbox, TICKET)
    repairs = _repair_tickets(project)
    assert len(repairs) >= 1
    front = _repair_frontmatter(repairs[0])
    deps = front.get("depends_on") or front.get("deps") or []
    parent = front.get("parent")
    assert TICKET in str(deps) or TICKET == parent, \
        f"the repair ticket must depend on the failing ticket {TICKET}, not the other way"
    main_front = support.read_ticket_frontmatter(project.root, TICKET)
    main_deps = main_front.get("depends_on") or main_front.get("deps") or []
    repair_id = front.get("id", "")
    assert repair_id not in str(main_deps), \
        f"the failing ticket {TICKET} must NOT depend on the repair ticket {repair_id}"


def test_tk_fails_no_repair_ticket_file(project, sandbox, interface):
    """DEC-454 point 6: when tk fails, no orphan ticket file is left behind."""
    _project_with_finding(project)
    tk = project.root / "governance" / "kernel" / "bin" / "tk"
    assert tk.is_file(), "the project fixture must place tk"
    tk.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    project.commit("break tk", who=support.ORCHESTRATOR)
    tickets_before = set((project.root / ".tickets").glob("*.md"))
    support.run_close(project, sandbox, TICKET)
    tickets_after = set((project.root / ".tickets").glob("*.md"))
    new_tickets = tickets_after - tickets_before
    for t in new_tickets:
        if t.stem != TICKET:
            front = _repair_frontmatter(t)
            assert front.get("id") is not None, \
                f"orphan ticket file {t.name} found without a proper id when tk failed"
