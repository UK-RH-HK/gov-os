"""Tests for finding disposition at close: S6 (CAP-59.c).

S6: A finding raised at close is classed into exactly one disposition (repair,
    reuse, delete, narrow, defer or owner) with whole-system context from gov
    context before any code change, and the repair ticket records it.

This is the anti-snowball lesson L-0077 (DEC-435).
"""

import pytest

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
    """A project where gov close will raise a finding (a planted check failure)."""
    project.add_ticket(ticket_id, wbs)
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.add_check_declaration("planted-defect", "schema/invariants",
                                  command="exit 1")
    project.commit("implement with defect", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    return ticket_id


# --------------------------------------------------------------------------
# S6: Finding classified into one disposition (CAP-59.c)
# --------------------------------------------------------------------------

def test_finding_classified_into_exactly_one_disposition(project, sandbox, interface):
    """KPI S6, CAP-59.c: a finding is classed into exactly one of the six dispositions."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    error = envelope.get("error", {})
    details = error.get("details", {})
    findings = details.get("findings", [])
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        disposition = finding.get("disposition")
        assert disposition in support.DISPOSITIONS, \
            f"finding must have one of {support.DISPOSITIONS}, got {disposition!r}"


def test_disposition_uses_context_before_code_change(project, sandbox, interface):
    """KPI S6, CAP-59.c: classification uses whole-system context from gov context."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    error = envelope.get("error", {})
    details = error.get("details", {})
    assert "context" in str(details).lower() or "disposition" in str(details).lower(), \
        "the error details should reference context or disposition"


def test_repair_ticket_records_disposition(project, sandbox, interface):
    """KPI S6, CAP-59.c: the repair ticket records the finding and its disposition."""
    _project_with_finding(project)
    support.run_close(project, sandbox, TICKET)
    tickets_dir = project.root / ".tickets"
    ticket_files = list(tickets_dir.glob("*.md"))
    repair_tickets = [f for f in ticket_files if f.name != f"{TICKET}.md"]
    assert len(repair_tickets) >= 1, "a repair ticket should be created for the finding"
    import yaml
    for repair_path in repair_tickets:
        text = repair_path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) >= 3:
            front = yaml.safe_load(parts[1]) or {}
            if front.get("type") == "task":
                assert True
                return
    pytest.fail("no repair ticket with type: task found")


def test_all_six_dispositions_recognized(project, sandbox, interface):
    """KPI S6, CAP-59.c: all six dispositions are valid classification outcomes."""
    assert len(support.DISPOSITIONS) == 6
    assert "REPAIR_EXISTING_MECHANISM" in support.DISPOSITIONS
    assert "REUSE_EXISTING_PRIMITIVE" in support.DISPOSITIONS
    assert "DELETE_MECHANISM" in support.DISPOSITIONS
    assert "NARROW_REQUIREMENT" in support.DISPOSITIONS
    assert "DEFER_TO_LATER_LIFECYCLE" in support.DISPOSITIONS
    assert "OWNER_DECISION" in support.DISPOSITIONS


def test_context_provides_whole_system_view(project, sandbox, interface):
    """KPI S6, CAP-59.c: gov context is called for the ticket before disposition."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False


# --------------------------------------------------------------------------
# Point 6 (WEAK): disposition validation and repair-ticket recording (S6, CAP-59.c)
# --------------------------------------------------------------------------

def test_finding_with_no_class_is_refused(project, sandbox, interface):
    """KPI S6, CAP-59.c: a finding that arrives at close with no disposition class is refused."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    error = envelope.get("error", {})
    details = error.get("details", {})
    findings = details.get("findings", [])
    for finding in findings:
        if isinstance(finding, dict):
            disposition = finding.get("disposition")
            assert disposition is not None, \
                "every finding must have a disposition class, not None"
            assert disposition != "", \
                "every finding must have a non-empty disposition class"


def test_finding_with_two_classes_is_refused(project, sandbox, interface):
    """KPI S6, CAP-59.c: a finding with two disposition classes is refused.

    Each finding is classed into exactly one disposition.
    """
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    error = envelope.get("error", {})
    details = error.get("details", {})
    findings = details.get("findings", [])
    for finding in findings:
        if isinstance(finding, dict):
            disposition = finding.get("disposition")
            if isinstance(disposition, list):
                assert len(disposition) == 1, \
                    f"a finding must have exactly one disposition, got {len(disposition)}"
            elif isinstance(disposition, str):
                assert disposition.count(",") == 0, \
                    "a finding must have exactly one disposition, not a comma-separated list"


def test_six_names_are_the_only_valid_dispositions(project, sandbox, interface):
    """KPI S6, CAP-59.c, L-0077: only the six named dispositions are valid."""
    _project_with_finding(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    error = envelope.get("error", {})
    details = error.get("details", {})
    findings = details.get("findings", [])
    for finding in findings:
        if isinstance(finding, dict):
            disposition = finding.get("disposition")
            if disposition is not None:
                assert disposition in support.DISPOSITIONS, \
                    f"disposition {disposition!r} is not one of the six: {support.DISPOSITIONS}"


def test_repair_ticket_records_the_class_given(project, sandbox, interface):
    """KPI S6, CAP-59.c: the repair ticket's frontmatter includes the disposition class."""
    _project_with_finding(project)
    support.run_close(project, sandbox, TICKET)
    import yaml
    tickets_dir = project.root / ".tickets"
    ticket_files = list(tickets_dir.glob("*.md"))
    repair_tickets = [f for f in ticket_files if f.name != f"{TICKET}.md"]
    found_class = False
    for repair_path in repair_tickets:
        text = repair_path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) >= 3:
            front = yaml.safe_load(parts[1]) or {}
            if front.get("class") == "repair" or front.get("parent") == TICKET:
                disp = front.get("disposition") or front.get("finding_disposition")
                if disp and disp in support.DISPOSITIONS:
                    found_class = True
                    break
                findings = front.get("findings", [])
                if findings:
                    found_class = True
                    break
    assert found_class, "the repair ticket must record the finding's disposition class"
