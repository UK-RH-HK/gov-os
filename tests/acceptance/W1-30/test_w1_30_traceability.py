"""Tests for the product-traceability family check: S3 (CAP-38.b).

S3: Registers the product-traceability family check: the commits of every closed
    ticket carry Implements: and Task: trailers that resolve.

These tests run ``gov check`` (not ``gov close``) to verify that a check in the
product-traceability family detects trailer violations on closed tickets.
"""

import json

import pytest

import w1_30_support as support

cli_support = support.cli_support
check_support = support.check_support

OWNER = support.OWNER
AGENT = support.AGENT
IMPL = support.IMPLEMENTER


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _project_with_closed_ticket(project, trailers, ticket_id="PROJ-tttt", wbs="W1-trace"):
    """A project with one ticket whose commits carry ``trailers`` and whose status is closed."""
    project.add_ticket(ticket_id, wbs)
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=trailers)
    text = (project.root / support.ticket_path(ticket_id)).read_text(encoding="utf-8")
    text = text.replace("status: in_progress", "status: closed")
    (project.root / support.ticket_path(ticket_id)).write_text(text, encoding="utf-8")
    project.commit("close ticket", who=OWNER)
    return ticket_id


# --------------------------------------------------------------------------
# S3: The product-traceability check is registered (CAP-38.b)
# --------------------------------------------------------------------------

def test_product_traceability_check_in_family(project, sandbox, interface):
    """KPI S3, CAP-38.b: a check is registered in the product-traceability family."""
    project.commit("fixture")
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, support.PRODUCT_TRACEABILITY)
    assert status is not None, \
        f"the product-traceability family should have a registered check; result: {result}"


def test_check_red_when_closed_ticket_lacks_implements_trailer(project, sandbox, interface):
    """KPI S3, CAP-38.b: a closed ticket whose commits lack Implements: is RED.

    Revised after implementation: the family's status included another check's
    state; this case now asserts on the product-traceability-trailers check entry.
    """
    _project_with_closed_ticket(
        project,
        trailers=("Task: PROJ-tttt", "Role: engineer"),
    )
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    checks = support.checks_of(result)
    trailer_check = [c for c in checks if c.get("id") == "product-traceability-trailers"]
    assert trailer_check, \
        f"product-traceability-trailers check should be registered; checks: {[c.get('id') for c in checks]}"
    assert trailer_check[0]["status"] == "RED", \
        f"product-traceability-trailers should be RED when Implements: is missing; got {trailer_check[0]}"
    check_text = json.dumps(trailer_check[0]).lower()
    assert "implements" in check_text, \
        f"the check output should name the missing trailer; got {trailer_check[0]}"


def test_check_red_when_closed_ticket_lacks_task_trailer(project, sandbox, interface):
    """KPI S3, CAP-38.b: a closed ticket whose commits lack Task: is RED.

    Revised after implementation: the family's status included another check's
    state; this case now asserts on the product-traceability-trailers check entry.
    """
    _project_with_closed_ticket(
        project,
        trailers=("Role: engineer", "Implements: CAP-01"),
    )
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    checks = support.checks_of(result)
    trailer_check = [c for c in checks if c.get("id") == "product-traceability-trailers"]
    assert trailer_check, \
        f"product-traceability-trailers check should be registered; checks: {[c.get('id') for c in checks]}"
    assert trailer_check[0]["status"] == "RED", \
        f"product-traceability-trailers should be RED when Task: is missing; got {trailer_check[0]}"
    check_text = json.dumps(trailer_check[0]).lower()
    assert "task" in check_text, \
        f"the check output should name the missing trailer; got {trailer_check[0]}"


def test_check_green_when_trailers_present_and_resolve(project, sandbox, interface):
    """KPI S3, CAP-38.b: a closed ticket with valid Implements: and Task: trailers is GREEN."""
    _project_with_closed_ticket(
        project,
        trailers=("Task: PROJ-tttt", "Role: engineer", "Implements: CAP-01"),
    )
    project.add_decision("CAP-01", "ACTIVE")
    project.commit("decision", who=OWNER)
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    checks = support.checks_of(result)
    trailer_check = [c for c in checks if c.get("id") == "product-traceability-trailers"]
    assert trailer_check, \
        f"product-traceability-trailers check should be registered; checks: {[c.get('id') for c in checks]}"
    assert trailer_check[0]["status"] == "GREEN", \
        f"product-traceability-trailers should be GREEN with valid trailers; got {trailer_check[0]}"


def test_check_red_when_implements_does_not_resolve(project, sandbox, interface):
    """KPI S3, CAP-38.b: Implements: names a non-existent record → RED.

    Revised after implementation: the family's status included another check's
    state; this case now asserts on the product-traceability-trailers check entry.
    """
    _project_with_closed_ticket(
        project,
        trailers=("Task: PROJ-tttt", "Role: engineer", "Implements: NO-SUCH-RECORD"),
    )
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    checks = support.checks_of(result)
    trailer_check = [c for c in checks if c.get("id") == "product-traceability-trailers"]
    assert trailer_check, \
        f"product-traceability-trailers check should be registered; checks: {[c.get('id') for c in checks]}"
    assert trailer_check[0]["status"] == "RED", \
        f"product-traceability-trailers should be RED when Implements: does not resolve; got {trailer_check[0]}"


# --------------------------------------------------------------------------
# DEC-454 Point 12: Traceability refinements
# --------------------------------------------------------------------------

def test_traceability_git_failure_is_check_failure(project, sandbox, interface):
    """DEC-454 point 12: a git failure is a check failure, not a silent pass.

    Revised after implementation: the family's status included another check's
    state; this case now asserts on the product-traceability-trailers check entry.
    """
    _project_with_closed_ticket(
        project,
        trailers=("Task: PROJ-tttt", "Role: engineer", "Implements: CAP-01"),
    )
    head_file = project.root / ".git" / "HEAD"
    original = head_file.read_text(encoding="utf-8")
    head_file.write_text("corrupt content\n", encoding="utf-8")
    run = support.run_check(project, sandbox)
    head_file.write_text(original, encoding="utf-8")
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    checks = support.checks_of(result)
    trailer_check = [c for c in checks if c.get("id") == "product-traceability-trailers"]
    assert trailer_check, \
        f"product-traceability-trailers check should be registered; checks: {[c.get('id') for c in checks]}"
    assert trailer_check[0]["status"] != "GREEN", \
        f"a git failure must be a check failure, not GREEN; got {trailer_check[0]}"
    check_text = json.dumps(trailer_check[0]).lower()
    assert "git" in check_text or "error" in check_text, \
        f"the check output should name the git failure; got {trailer_check[0]}"


def test_traceability_commits_from_head_not_all_branches(project, sandbox, interface):
    """DEC-454 point 12: the check considers commits from HEAD, not all branches.

    Revised after implementation: the family's status included another check's
    state; this case now asserts on the product-traceability-trailers check entry.
    """
    ticket_id = "PROJ-head"
    wbs = "W1-head"
    trailers_head = ("Task: PROJ-head", "Role: engineer", "Implements: CAP-01")
    project.add_ticket(ticket_id, wbs)
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement on main", who=IMPL, trailers=trailers_head)
    text = (project.root / support.ticket_path(ticket_id)).read_text(encoding="utf-8")
    text = text.replace("status: in_progress", "status: closed")
    (project.root / support.ticket_path(ticket_id)).write_text(text, encoding="utf-8")
    project.commit("close ticket", who=OWNER)

    support.git(project.root, "checkout", "-b", "stale-branch")
    project.write("src/example/stale.py", "# stale branch\n")
    project.commit("commit on stale branch without Implements", who=IMPL,
                   trailers=("Task: PROJ-head", "Role: engineer"))
    support.git(project.root, "checkout", "main")

    project.add_decision("CAP-01", "ACTIVE")
    project.commit("decision", who=OWNER)
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    checks = support.checks_of(result)
    trailer_check = [c for c in checks if c.get("id") == "product-traceability-trailers"]
    assert trailer_check, \
        f"product-traceability-trailers check should be registered; checks: {[c.get('id') for c in checks]}"
    assert trailer_check[0]["status"] == "GREEN", \
        f"commits on other branches must not affect the check; got {trailer_check[0]}"


def test_traceability_unreadable_record_store_reported(project, sandbox, interface):
    """DEC-454 point 12: an unreadable record store is reported as an error.

    Revised after implementation: the family's status included another check's
    state; this case now asserts on the product-traceability-trailers check entry.
    """
    _project_with_closed_ticket(
        project,
        trailers=("Task: PROJ-tttt", "Role: engineer", "Implements: CAP-01"),
    )
    adr_dir = project.root / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)
    bad_file = adr_dir / "CAP-01.md"
    bad_file.write_text("---\nnot: valid: yaml: [[[broken\n---\n", encoding="utf-8")
    project.commit("corrupt record store", who=OWNER)
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    checks = support.checks_of(result)
    trailer_check = [c for c in checks if c.get("id") == "product-traceability-trailers"]
    assert trailer_check, \
        f"product-traceability-trailers check should be registered; checks: {[c.get('id') for c in checks]}"
    assert trailer_check[0]["status"] != "GREEN", \
        f"an unreadable record store must not produce GREEN; got {trailer_check[0]}"


def test_no_closed_ticket_not_applicable(project, sandbox, interface):
    """DEC-454 point 12, DEC-447: when no closed ticket exists, the check is 'not applicable'.

    Per DEC-447 and the W1-26 README, the check says {"not_applicable": true}
    and exits 2; the runner reports the check YELLOW with the reason. The
    product-traceability-trailers check is never GREEN when there are no closed
    tickets (DEC-425: nothing measured is never a pass).
    """
    project.write("src/example/feature.py", "# feature\n")
    project.commit("no tickets at all", who=OWNER)
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    checks = support.checks_of(result)
    trailer_check = [c for c in checks if c.get("id") == "product-traceability-trailers"]
    assert trailer_check, "product-traceability-trailers check should be registered"
    check_status = trailer_check[0].get("status")
    assert check_status != "GREEN", \
        f"DEC-425, DEC-447: not applicable is never green; got {check_status}"
    assert check_status != "RED", \
        f"DEC-447: not applicable is a warning, not red; got {check_status}"
    check_text = json.dumps(trailer_check[0]).lower()
    assert "no closed ticket" in check_text or "not applicable" in check_text, \
        f"the reason must name 'no closed ticket': {trailer_check[0]}"
