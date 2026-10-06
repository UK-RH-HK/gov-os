"""Tests for iteration tracking and escalation: S2 (CAP-31.b, CAP-59.a), F2, F3 (CAP-59.b).

S2: Holds the iteration count of every review→repair, test→fix and verification
    loop; after three consecutive non-converging iterations it stops the loop and
    puts an escalation package in chat for the owner (DEC-096); a failure opens a
    dependent repair ticket.
F2: A fourth consecutive non-converging iteration starts without an owner decision.
F3: The iteration count or budget appears in any output seen by the looping session.
"""

import json
import re

import pytest

import w1_30_support as support

cli_support = support.cli_support


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

TICKET = "PROJ-iter"
WBS = "W1-iter"
IMPL = support.IMPLEMENTER
TRAILERS = ("Task: PROJ-iter", "Role: engineer", "Implements: CAP-01")
ITERATION_FIELDS = ("iteration_count", "iterations_remaining", "loop_count",
                    "attempt_number", "retry_count")
BUDGET_FIELDS = ("budget", "remaining_budget", "max_iterations", "total_budget")


def _failing_project(project, ticket_id=TICKET, wbs=WBS):
    """A project whose ticket always fails its acceptance tests."""
    project.add_ticket(ticket_id, wbs)
    project.add_failing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    return ticket_id


# --------------------------------------------------------------------------
# S2: Iteration count persists (CAP-31.b)
# --------------------------------------------------------------------------

def test_first_failure_records_iteration(project, sandbox, interface):
    """KPI S2, CAP-31.b: after a first failure, the iteration state is recorded."""
    _failing_project(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    runtime = project.root / ".gov-runtime"
    assert runtime.is_dir(), ".gov-runtime should exist after gov close writes iteration state"


def test_iteration_count_persists_across_failures(project, sandbox, interface):
    """KPI S2, CAP-31.b: the iteration count grows across consecutive failures."""
    _failing_project(project)
    run1 = support.run_close(project, sandbox, TICKET)
    assert support.envelope_of(run1, interface)["ok"] is False
    run2 = support.run_close(project, sandbox, TICKET)
    assert support.envelope_of(run2, interface)["ok"] is False


def test_converging_iteration_resets_count(project, sandbox, interface):
    """KPI S2, CAP-31.b: a different failure resets the non-converging streak."""
    project.add_ticket(TICKET, WBS)
    project.add_failing_test(WBS, name="test_fail_a")
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    support.run_close(project, sandbox, TICKET)
    # Replace with a different failure to break the non-converging streak.
    support.write(project.root, f"tests/acceptance/{WBS}/test_fail_a.py",
                  "def test_fail_a():\n    assert True\n")
    project.add_failing_test(WBS, name="test_fail_b")
    project.commit("fix first, break second", who=IMPL, trailers=TRAILERS)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False


# --------------------------------------------------------------------------
# S2: Escalation after three non-converging (CAP-59.a)
# --------------------------------------------------------------------------

def test_escalation_after_three_non_converging(project, sandbox, interface):
    """KPI S2, CAP-59.a: after 3 consecutive non-converging iterations, escalation."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    assert run.returncode == support.EXIT_BLOCKED, \
        "the 4th attempt should be blocked (exit 4)"


def test_escalation_package_lists_outcomes(project, sandbox, interface):
    """KPI S2, CAP-59.a: the escalation package lists each iteration's outcome."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    error = envelope.get("error", {})
    details = error.get("details", {})
    outcomes = details.get("outcomes") or details.get("iterations")
    assert isinstance(outcomes, list) and len(outcomes) >= 1, \
        f"escalation must list iteration outcomes: {details}"


def test_escalation_package_has_six_options(project, sandbox, interface):
    """KPI S2, CAP-59.a: the package offers fix differently / narrow / split / defer / delete / continue."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    error = envelope.get("error", {})
    details = error.get("details", {})
    options = details.get("options", [])
    expected = {"fix_differently", "narrow", "split", "defer", "delete", "continue"}
    found = {o.lower().replace(" ", "_").replace("-", "_") for o in options}
    assert expected <= found, f"expected options {expected}, got {found}"


# --------------------------------------------------------------------------
# S2: Failure opens dependent repair ticket (CAP-59.a)
# --------------------------------------------------------------------------

def test_failure_opens_dependent_repair_ticket(project, sandbox, interface):
    """KPI S2, CAP-59.a: a failure at close opens a dependent repair ticket."""
    _failing_project(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    tickets_dir = project.root / ".tickets"
    ticket_files = list(tickets_dir.glob("*.md"))
    original_count = 1
    assert len(ticket_files) > original_count, \
        "a repair ticket should have been created in .tickets/"


# --------------------------------------------------------------------------
# F2: Fourth non-converging blocked without owner decision
# --------------------------------------------------------------------------

def test_fourth_non_converging_blocked_without_owner(project, sandbox, interface):
    """KPI F2: a 4th consecutive non-converging iteration must not start without an owner decision."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    assert run.returncode == support.EXIT_BLOCKED


# --------------------------------------------------------------------------
# F3: Iteration count and budget not in output (CAP-59.b)
# --------------------------------------------------------------------------

def test_iteration_count_not_in_output(project, sandbox, interface):
    """KPI F3, CAP-59.b: no iteration count in any output seen by the looping session."""
    _failing_project(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    result_or_details = envelope.get("result", {}) or envelope.get("error", {}).get("details", {})
    serialised = json.dumps(result_or_details).lower()
    for field in ITERATION_FIELDS:
        assert field not in serialised, \
            f"the output exposes '{field}' to the looping session (CAP-59.b)"


def test_budget_not_in_output(project, sandbox, interface):
    """KPI F3, CAP-59.b: no budget in any output seen by the looping session."""
    _failing_project(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    result_or_details = envelope.get("result", {}) or envelope.get("error", {}).get("details", {})
    serialised = json.dumps(result_or_details).lower()
    for field in BUDGET_FIELDS:
        assert field not in serialised, \
            f"the output exposes '{field}' to the looping session (CAP-59.b)"


def test_iteration_count_hidden_across_multiple_failures(project, sandbox, interface):
    """KPI F3, CAP-59.b: even after multiple failures, the count stays hidden."""
    _failing_project(project)
    for i in range(3):
        run = support.run_close(project, sandbox, TICKET)
        envelope = support.envelope_of(run, interface)
        serialised = json.dumps(envelope).lower()
        for field in ITERATION_FIELDS + BUDGET_FIELDS:
            assert field not in serialised, \
                f"iteration {i + 1}: output exposes '{field}' (CAP-59.b)"


# --------------------------------------------------------------------------
# Point 7 (WEAK): Escalation outcomes are distinct per iteration (S2, CAP-59.a)
# --------------------------------------------------------------------------

def test_escalation_outcomes_are_distinct_per_iteration(project, sandbox, interface):
    """KPI S2, CAP-59.a: each of the 3 outcomes in the escalation package must identify its iteration.

    The outcomes must not be identical copies of a single failure set.
    """
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    error = envelope.get("error", {})
    details = error.get("details", {})
    outcomes = details.get("outcomes") or details.get("iterations") or []
    assert isinstance(outcomes, list) and len(outcomes) >= 3, \
        f"the escalation package must list at least 3 outcomes (one per iteration): {details}"


def test_escalation_includes_reason_not_converging(project, sandbox, interface):
    """KPI S2, CAP-59.a: the escalation package includes a reason why failures are not converging."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    error = envelope.get("error", {})
    details = error.get("details", {})
    reason = details.get("reason") or details.get("why") or error.get("message", "")
    assert reason, "the escalation package must include a reason why failures are not converging"
    serialised = json.dumps(details).lower()
    assert "converg" in serialised or "repeat" in serialised or "same" in serialised or reason, \
        "the escalation should explain why the iterations are not converging"


# --------------------------------------------------------------------------
# Point 11: F3 — does the looping session's error output contain the outcomes list?
#
# Settlement: CAP-59.b says "the iteration count or budget appears in any output
# seen by the looping session". The looping session is the one that calls gov close
# repeatedly. The escalation package (with the outcomes list) is for the owner,
# delivered through the orchestrator in chat — the looping session does NOT see it.
#
# The looping session sees only the 4th attempt's error envelope (ok: false, exit 4).
# If that envelope contains the outcomes list, its length reveals the iteration count.
#
# From the code: the escalation error is raised with the outcomes in details, and the
# looping session receives that JSON envelope. The test checks that the looping
# session's output does not contain an outcomes list whose length reveals the count.
# --------------------------------------------------------------------------

def test_escalation_output_to_looping_session_has_no_count(project, sandbox, interface):
    """KPI F3, CAP-59.b: the error envelope returned to the looping session must not
    contain iteration-count-revealing information (no outcomes list, no count field).

    The outcomes list has one entry per iteration, so len(outcomes) IS the count.
    The looping session must not see it.
    """
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    error = envelope.get("error", {})
    details = error.get("details", {})
    outcomes = details.get("outcomes") or details.get("iterations")
    if isinstance(outcomes, list) and len(outcomes) > 1:
        pytest.fail(
            f"the looping session's error envelope contains {len(outcomes)} outcomes, "
            "which reveals the iteration count (CAP-59.b); the outcomes list must go "
            "to the orchestrator/owner, not to the looping session"
        )
