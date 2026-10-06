"""Tests for the product-traceability family check: S3 (CAP-38.b).

S3: Registers the product-traceability family check: the commits of every closed
    ticket carry Implements: and Task: trailers that resolve.

These tests run ``gov check`` (not ``gov close``) to verify that a check in the
product-traceability family detects trailer violations on closed tickets.
"""

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
    text = text.replace("status: open", "status: closed")
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
    """KPI S3, CAP-38.b: a closed ticket whose commits lack Implements: is RED."""
    _project_with_closed_ticket(
        project,
        trailers=("Task: PROJ-tttt", "Role: engineer"),
    )
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, support.PRODUCT_TRACEABILITY)
    assert status == "RED", \
        f"product-traceability should be RED when Implements: is missing; got {status}"


def test_check_red_when_closed_ticket_lacks_task_trailer(project, sandbox, interface):
    """KPI S3, CAP-38.b: a closed ticket whose commits lack Task: is RED."""
    _project_with_closed_ticket(
        project,
        trailers=("Role: engineer", "Implements: CAP-01"),
    )
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, support.PRODUCT_TRACEABILITY)
    assert status == "RED", \
        f"product-traceability should be RED when Task: is missing; got {status}"


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
    status = support.family_status(result, support.PRODUCT_TRACEABILITY)
    assert status == "GREEN", \
        f"product-traceability should be GREEN with valid trailers; got {status}"


def test_check_red_when_implements_does_not_resolve(project, sandbox, interface):
    """KPI S3, CAP-38.b: Implements: names a non-existent record → RED."""
    _project_with_closed_ticket(
        project,
        trailers=("Task: PROJ-tttt", "Role: engineer", "Implements: NO-SUCH-RECORD"),
    )
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    status = support.family_status(result, support.PRODUCT_TRACEABILITY)
    assert status == "RED", \
        f"product-traceability should be RED when Implements: does not resolve; got {status}"
