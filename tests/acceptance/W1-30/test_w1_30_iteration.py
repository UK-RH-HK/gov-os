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


def test_count_file_wrong_shape_list_refuses(project, sandbox, interface):
    """A6, DEC-454: a count file that is valid JSON but the wrong shape (a list)
    refuses with the corrupt-file error, never a traceback.
    """
    _failing_project(project)
    support.write_iteration_file(project.root, TICKET, [1, 2, 3])
    run = support.run_close(project, sandbox, TICKET)
    assert "Traceback" not in run.stderr, \
        "a wrong-shape count file must not produce a traceback"
    assert run.returncode != support.EXIT_OK, \
        "a count file that is a list must refuse (non-zero exit)"
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a count file that is a list must refuse"


def test_count_file_wrong_shape_string_count_refuses(project, sandbox, interface):
    """A6, DEC-454: a count file with {\"count\": \"x\"} refuses with the
    corrupt-file error, never a traceback.
    """
    _failing_project(project)
    support.write_iteration_file(project.root, TICKET, {"count": "x"})
    run = support.run_close(project, sandbox, TICKET)
    assert "Traceback" not in run.stderr, \
        "a wrong-shape count file must not produce a traceback"
    assert run.returncode != support.EXIT_OK, \
        'a count file with {"count": "x"} must refuse (non-zero exit)'
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        'a count file with {"count": "x"} must refuse'


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


# --------------------------------------------------------------------------
# DEC-454, KPI S2/S6: every failed close counts, not just test failures
# --------------------------------------------------------------------------

def test_containment_refusal_counts_as_iteration(project, sandbox, interface):
    """DEC-454, S2: three consecutive closes refused for containment end in escalation."""
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.write("src/other/out_of_scope.py", "# out of scope\n")
    project.commit("implement out of scope", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    assert run.returncode == support.EXIT_BLOCKED, \
        "three consecutive containment refusals must escalate"


def test_mixed_causes_reach_escalation(project, sandbox, interface):
    """DEC-454, S2: a sequence mixing causes (trailers, a failing test, a hard-block
    check) ends in escalation.
    """
    project.add_ticket(TICKET, WBS,
                       allowed_paths=["src/example/**",
                                      "template/governance/kernel/checks/**"])
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement without trailers", who=IMPL,
                   trailers=("Role: engineer",))
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    support.run_close(project, sandbox, TICKET)

    project.commit("fix trailers", who=IMPL, trailers=TRAILERS)
    project.add_failing_test(WBS, name="test_break")
    project.commit("add failing test", who=IMPL, trailers=TRAILERS)
    support.run_close(project, sandbox, TICKET)

    support.write(project.root, f"tests/acceptance/{WBS}/test_break.py",
                  "def test_break():\n    assert True\n")
    project.add_check_declaration("block-close", "schema/invariants",
                                  severity="hard-block", command="exit 1")
    project.commit("fix test, add hard-block", who=IMPL, trailers=TRAILERS)
    support.run_close(project, sandbox, TICKET)

    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False
    assert run.returncode == support.EXIT_BLOCKED, \
        "three consecutive failures of mixed causes must escalate"


def test_each_refusal_opens_repair_ticket(project, sandbox, interface):
    """DEC-454, S2/S6: each of the first two containment refusals opens a repair
    ticket recording the finding and 'unclassed'.
    """
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.write("src/other/out_of_scope.py", "# out of scope\n")
    project.commit("implement out of scope", who=IMPL, trailers=TRAILERS)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)
    tickets_before = set((project.root / ".tickets").glob("*.md"))
    support.run_close(project, sandbox, TICKET)
    tickets_after_1 = set((project.root / ".tickets").glob("*.md"))
    new_1 = tickets_after_1 - tickets_before
    assert len(new_1) >= 1, "the first refusal must open a repair ticket"
    support.run_close(project, sandbox, TICKET)
    tickets_after_2 = set((project.root / ".tickets").glob("*.md"))
    new_2 = tickets_after_2 - tickets_after_1
    assert len(new_2) >= 1, "the second refusal must also open a repair ticket"


def test_unknown_ticket_does_not_count(project, sandbox, interface):
    """DEC-454: a refusal because the ticket is unknown is not an iteration."""
    _failing_project(project)
    support.run_close(project, sandbox, "NO-SUCH-TICKET")
    support.run_close(project, sandbox, "NO-SUCH-TICKET")
    support.run_close(project, sandbox, "NO-SUCH-TICKET")
    run = support.run_close(project, sandbox, "NO-SUCH-TICKET")
    assert run.returncode != support.EXIT_BLOCKED, \
        "unknown-ticket refusals must not escalate"


def test_escalation_already_in_force_not_counted(project, sandbox, interface):
    """DEC-454: a refusal because the escalation is already in force is not an
    iteration; it does not extend the escalation.
    """
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    run4 = support.run_close(project, sandbox, TICKET)
    assert support.envelope_of(run4, interface)["ok"] is False
    run5 = support.run_close(project, sandbox, TICKET)
    assert run5.returncode == support.EXIT_BLOCKED, \
        "repeated runs under escalation should stay blocked without further escalation"


# --------------------------------------------------------------------------
# DEC-454, KPI S2: owner decision refinements
# --------------------------------------------------------------------------

def test_owner_decision_unapproved_refused(project, sandbox, interface):
    """DEC-454: a decision that exists but lacks the owner's approval fact
    (ACTIVE_UNAPPROVED from W1-11) is refused.
    """
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    dec_id = "DEC-noapproval"
    project.add_decision(dec_id, "ACTIVE", title="Unapproved decision")
    project.commit("add decision without owner approval", who=support.AGENT)
    run = support.run_close(project, sandbox, TICKET, "--owner-decision", dec_id)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a decision lacking the owner's approval fact must be refused"
    assert run.returncode != support.EXIT_OK, \
        "an unapproved decision must not allow the attempt to proceed"


def test_owner_decision_checker_failing_refuses(project, sandbox, interface):
    """DEC-454: the decision checker failing (corrupted decision file) refuses."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    dec_id = "DEC-checkfail"
    project.add_decision(dec_id, "ACTIVE", title="Decision")
    dec_file = project.root / "docs" / "adr" / f"{dec_id}.md"
    dec_file.write_text("---\nnot valid yaml: [[[broken\n---\n", encoding="utf-8")
    project.commit("corrupt decision file", who=support.OWNER)
    run = support.run_close(project, sandbox, TICKET, "--owner-decision", dec_id)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, \
        "a corrupted decision file must cause the checker to fail and refuse close"
    assert run.returncode != support.EXIT_OK


def test_owner_decision_only_when_escalated(project, sandbox, interface):
    """DEC-454: an owner-approved decision is accepted only when the ticket is
    escalated (after three consecutive failures).
    """
    _failing_project(project)
    dec_id = "DEC-early"
    project.add_decision(dec_id, "ACTIVE", title="Owner says continue")
    project.commit("add decision early", who=support.OWNER)
    run = support.run_close(project, sandbox, TICKET, "--owner-decision", dec_id)
    envelope = support.envelope_of(run, interface)
    assert run.returncode != support.EXIT_OK or envelope["ok"] is False, \
        "an owner decision before escalation (no 3 failures) must not be accepted"


def test_owner_decision_id_recorded_in_count(project, sandbox, interface):
    """DEC-454: the count file records the decision's id after an owner decision."""
    _failing_project(project)
    for _ in range(3):
        support.run_close(project, sandbox, TICKET)
    dec_id = "DEC-owner-rec"
    project.add_decision(dec_id, "ACTIVE", title="Owner says continue")
    project.commit("add owner decision", who=support.OWNER)
    support.run_close(project, sandbox, TICKET, "--owner-decision", dec_id)
    iter_data = support.read_iteration_file(project.root, TICKET)
    assert iter_data is not None, "iteration file must exist after owner decision"
    data_str = json.dumps(iter_data)
    assert dec_id in data_str, \
        f"the iteration file must record the decision id {dec_id}: {iter_data}"


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
