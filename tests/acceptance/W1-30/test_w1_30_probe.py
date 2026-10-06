"""Tests for the probe-record gate on FULL-profile tickets: S7 (CAP-38.f).

S7: A FULL-profile ticket closes only with a post-green probe record made by a
    fresh reviewer session other than the implementer, commissioned and judged by
    the orchestrator; the reviewer wrote nothing to the repository (DEC-137).
"""

import pytest

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-prob"
WBS = "W1-probe"
IMPL = support.IMPLEMENTER
TRAILERS = ("Task: PROJ-prob", "Role: engineer", "Implements: CAP-01")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _full_project_without_probe(project, ticket_id=TICKET, wbs=WBS):
    """A FULL-profile ticket that is green but has no probe record."""
    project.add_ticket(ticket_id, wbs, profile="FULL")
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    return ticket_id


def _full_project_with_probe(project, ticket_id=TICKET, wbs=WBS, **probe_kwargs):
    """A FULL-profile ticket that is green and has a probe record."""
    _full_project_without_probe(project, ticket_id, wbs)
    project.add_probe(ticket_id, **probe_kwargs)
    project.commit("add probe", who=support.ORCHESTRATOR)
    return ticket_id


# --------------------------------------------------------------------------
# S7: FULL ticket requires probe record (CAP-38.f)
# --------------------------------------------------------------------------

def test_full_ticket_requires_probe_record(project, sandbox, interface):
    """KPI S7, CAP-38.f: a FULL ticket without a probe record cannot close."""
    _full_project_without_probe(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a FULL ticket without a probe record must not close"
    assert run.returncode in (support.EXIT_GOV_ERROR, support.EXIT_BLOCKED), \
        f"expected exit 1 or 4, got {run.returncode}"


def test_full_ticket_closes_with_valid_probe(project, sandbox, interface):
    """KPI S7, CAP-38.f: a FULL ticket with a valid probe record closes."""
    _full_project_with_probe(project)
    run = support.run_close(project, sandbox, TICKET)
    result = support.result_of(run, interface)
    assert result is not None


def test_probe_from_non_implementer(project, sandbox, interface):
    """KPI S7, CAP-38.f: the probe reviewer must not be the implementer."""
    _full_project_without_probe(project)
    project.add_probe(TICKET,
                      reviewer_session="impl-001",
                      implementer_session="impl-001")
    project.commit("add probe same reviewer", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe where reviewer == implementer must be rejected"


def test_probe_reviewer_wrote_nothing(project, sandbox, interface):
    """KPI S7, CAP-38.f: the reviewer wrote nothing to the repository."""
    _full_project_without_probe(project)
    project.add_probe(TICKET, reviewer_wrote_nothing=False)
    project.commit("add probe reviewer wrote", who=support.ORCHESTRATOR)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a probe whose reviewer wrote to the repository must be rejected"


def test_standard_profile_closes_without_probe(project, sandbox, interface):
    """KPI S7, CAP-38.f: a STANDARD-profile ticket does not need a probe record."""
    ticket_id = "PROJ-std1"
    wbs = "W1-std"
    project.add_ticket(ticket_id, wbs, profile="STANDARD")
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL,
                   trailers=("Task: PROJ-std1", "Role: engineer", "Implements: CAP-01"))
    run = support.run_close(project, sandbox, ticket_id)
    result = support.result_of(run, interface)
    assert result is not None
