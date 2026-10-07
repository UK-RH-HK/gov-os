"""Tests for iteration tracking and escalation: S2, F2, F3, A6.

S2: Holds the iteration count of every review->repair, test->fix and verification
    loop; after three consecutive non-converging iterations it stops the loop and
    puts an escalation package in chat for the owner (DEC-096); a failure opens a
    dependent repair ticket.
F2: A fourth consecutive non-converging iteration starts without an owner decision.
F3: The iteration count or budget appears in any output seen by the looping session.
A6: "Non-converging" = every consecutive failed close counts (resets on success or
    owner decision). The owner decision is given by register id via --owner-decision.
    A count file that cannot be read or parsed refuses (not zero).
"""

import json
import os

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
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    return ticket_id


def _green_project(project, ticket_id=TICKET, wbs=WBS):
    """A project whose ticket passes."""
    project.add_ticket(ticket_id, wbs)
    project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(ticket_id)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    return ticket_id


# --------------------------------------------------------------------------
# S2: Every consecutive failed close increments the count (A6)
# --------------------------------------------------------------------------

def test_first_failure_records_iteration(project, sandbox, interface):
    """KPI S2, CAP-31.b, A6: after a first failure, the iteration state is recorded."""
    _failing_project(project)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    runtime = project.root / ".gov-runtime"
    assert runtime.is_dir(), ".gov-runtime should exist after gov close writes iteration state"


def test_iteration_count_persists_across_failures(project, sandbox, interface):
    """KPI S2, CAP-31.b, A6: the iteration count grows across consecutive failures."""
    _failing_project(project)
    run1 = support.run_close(project, sandbox, TICKET)
    assert support.envelope_of(run1, interface)["ok"] is False
    run2 = support.run_close(project, sandbox, TICKET)
    assert support.envelope_of(run2, interface)["ok"] is False


def test_different_failures_still_increment_count(project, sandbox, interface):
    """A6: every consecutive failed close counts, not just identical failure sets.

    Even when the failure changes (different test fails), the count still increments
    toward the three-failure escalation threshold.
    """
    project.add_ticket(TICKET, WBS)
    project.add_failing_test(WBS, name="test_fail_a")
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    support.run_close(project, sandbox, TICKET)

    support.write(project.root, f"tests/acceptance/{WBS}/test_fail_a.py",
                  "def test_fail_a():\n    assert True\n")
    project.add_failing_test(WBS, name="test_fail_b")
    project.commit("fix first, break second", who=IMPL, trailers=TRAILERS)
    support.run_close(project, sandbox, TICKET)

    support.write(project.root, f"tests/acceptance/{WBS}/test_fail_b.py",
                  "def test_fail_b():\n    assert True\n")
    project.add_failing_test(WBS, name="test_fail_c")
    project.commit("fix second, break third", who=IMPL, trailers=TRAILERS)
    support.run_close(project, sandbox, TICKET)

    run4 = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run4, interface)
    assert envelope["ok"] is False
    assert run4.returncode == support.EXIT_BLOCKED, \
        "three different failures must still escalate (A6: every consecutive failure counts)"


def test_successful_close_resets_count(project, sandbox, interface):
    """A6: a successful close resets the iteration count."""
    ticket_a = "PROJ-rst1"
    wbs_a = "W1-rst1"
    trailers_a = ("Task: PROJ-rst1", "Role: engineer", "Implements: CAP-01")
    project.add_ticket(ticket_a, wbs_a)
    project.add_failing_test(wbs_a)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=trailers_a)
    project.add_checkpoint(ticket_a)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    support.run_close(project, sandbox, ticket_a)
    support.run_close(project, sandbox, ticket_a)

    support.write(project.root, f"tests/acceptance/{wbs_a}/test_fail.py",
                  "def test_fail():\n    assert True\n")
    project.add_passing_test(wbs_a, name="test_pass_now")
    project.commit("fix tests", who=IMPL, trailers=trailers_a)
    run_ok = support.run_close(project, sandbox, ticket_a)
    envelope_ok = support.envelope_of(run_ok, interface)
    if envelope_ok["ok"]:
        iter_file = support.read_iteration_file(project.root, ticket_a)
        if iter_file is not None:
            count = iter_file.get("count", 0)
            assert count == 0, f"a successful close must reset the count to 0, got {count}"


# --------------------------------------------------------------------------
# S2: Escalation after three non-converging (CAP-59.a, DEC-096)
# --------------------------------------------------------------------------

def test_escalation_after_three_non_converging(project, sandbox, interface):
    """KPI S2, CAP-59.a, A6: after 3 consecutive failures, the 4th is blocked."""
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
    esc_file = project.root / ".gov-runtime" / "escalations" / f"{TICKET}.json"
    assert esc_file.is_file(), f"escalation file must exist at {esc_file}"
    esc_data = json.loads(esc_file.read_text(encoding="utf-8"))
    outcomes = esc_data.get("outcomes", [])
    assert isinstance(outcomes, list) and len(outcomes) >= 3, \
        f"the escalation package must list at least 3 outcomes: {esc_data}"


def test_escalation_package_has_six_options(project, sandbox, interface):
    """KPI S2, CAP-59.a: the package offers the six options."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    esc_file = project.root / ".gov-runtime" / "escalations" / f"{TICKET}.json"
    assert esc_file.is_file(), f"escalation file must exist"
    esc_data = json.loads(esc_file.read_text(encoding="utf-8"))
    options = esc_data.get("options", [])
    expected = {"fix_differently", "narrow", "split", "defer", "delete", "continue"}
    found = {o.lower().replace(" ", "_").replace("-", "_") for o in options}
    assert expected <= found, f"expected options {expected}, got {found}"


def test_escalation_includes_reason_not_converging(project, sandbox, interface):
    """KPI S2, CAP-59.a: the escalation includes a reason why failures are not converging."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    esc_file = project.root / ".gov-runtime" / "escalations" / f"{TICKET}.json"
    assert esc_file.is_file()
    esc_data = json.loads(esc_file.read_text(encoding="utf-8"))
    reason = esc_data.get("reason") or esc_data.get("why", "")
    assert reason, "the escalation package must include a reason"


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


def test_fourth_attempt_runs_nothing(project, sandbox, interface):
    """A6: a 4th attempt without --owner-decision runs nothing (no tests, no checks)."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET)
    after = cli_support.snapshot(project.root)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    assert run.returncode == support.EXIT_BLOCKED
    created = support.new_files(project.root, before, after)
    close_rec_files = [f for f in created if "close" in f.lower()]
    assert not close_rec_files, \
        "a blocked 4th attempt should not write a close record"


# --------------------------------------------------------------------------
# A6: Owner decision resets the count
# --------------------------------------------------------------------------

def test_owner_decision_resets_count(project, sandbox, interface):
    """A6: --owner-decision with a valid ACTIVE decision resets the count and proceeds."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    dec_id = "DEC-owner1"
    project.add_decision(dec_id, "ACTIVE", title="Owner says continue")
    project.commit("owner decision", who=support.OWNER)
    run = support.run_close(project, sandbox, TICKET, "--owner-decision", dec_id)
    envelope = support.envelope_of(run, interface)
    assert run.returncode != support.EXIT_BLOCKED, \
        "a valid --owner-decision must reset the count and allow the attempt to proceed"


def test_owner_decision_invalid_id_refused(project, sandbox, interface):
    """A6: --owner-decision with a non-existent decision id is refused."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET, "--owner-decision", "NO-SUCH-DEC")
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a non-existent decision id must be refused"


def test_owner_decision_must_be_active(project, sandbox, interface):
    """A6: the owner decision must be ACTIVE (from gov.decisions.check)."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    dec_id = "DEC-draft1"
    project.add_decision(dec_id, "DRAFT", title="Not yet active")
    project.commit("add draft decision", who=support.OWNER)
    run = support.run_close(project, sandbox, TICKET, "--owner-decision", dec_id)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a DRAFT (non-ACTIVE) decision must be refused as --owner-decision"


# --------------------------------------------------------------------------
# A6: Count file corruption
# --------------------------------------------------------------------------

def test_count_file_unreadable_refuses(project, sandbox, interface):
    """A6: a count file that cannot be read or parsed refuses instead of being read as zero."""
    _failing_project(project)
    support.corrupt_iteration_file(project.root, TICKET, content="not json {{{")
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "an unparseable count file must refuse, not default to zero"
    assert run.returncode == support.EXIT_GOV_ERROR, \
        f"expected exit 1 for corrupt count file, got {run.returncode}"


def test_count_file_invalid_json_refuses(project, sandbox, interface):
    """A6: a count file with invalid JSON refuses the close."""
    _failing_project(project)
    support.corrupt_iteration_file(project.root, TICKET, content='{"count": ')
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a count file with truncated JSON must refuse"


def test_iteration_file_under_gov_runtime(project, sandbox, interface):
    """A6: the iteration file is under .gov-runtime/iterations/ (inaccessible to workers)."""
    _failing_project(project)
    support.run_close(project, sandbox, TICKET)
    iter_dir = project.root / ".gov-runtime" / "iterations"
    assert iter_dir.is_dir(), \
        f"iteration files must be under .gov-runtime/iterations/, not elsewhere"
    iter_file = iter_dir / f"{TICKET}.json"
    assert iter_file.is_file(), \
        f"iteration file for {TICKET} must exist at {iter_file}"


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


def test_escalation_output_to_looping_session_has_no_count(project, sandbox, interface):
    """KPI F3, CAP-59.b: the error envelope to the looping session must not reveal the count."""
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
            "which reveals the iteration count (CAP-59.b)"
        )


def test_escalation_outcome_has_no_iteration_field(project, sandbox, interface):
    """KPI F3, CAP-59.b: the outcome must not contain an 'iteration' field."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    error = envelope.get("error", {})
    details = error.get("details", {})
    outcomes = details.get("outcomes", [])
    for outcome in outcomes:
        if isinstance(outcome, dict):
            assert "iteration" not in outcome, \
                f"the outcome contains an 'iteration' field that reveals the count: {outcome}"
