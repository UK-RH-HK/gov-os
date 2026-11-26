"""V1: the stage computes every lite condition of CAP-44.h by code, each recorded ``met`` or ``not met`` with its
evidence; one planted failure makes exactly that condition ``not met`` and leaves the others as they were [CAP-44.h;
DEC-1227 D1 (a); DEC-1231].

The live tools (``gov doctor``, ``gov check``) are stood in through ``gov.adopt.verdict.compute(root, session,
tools=...)``; the harbour's real ones are not green (README, "The project"). The command line is held in
``test_w2_210_command.py``. Every case copies the adopted project the session fixture built.
"""

from __future__ import annotations

import pytest

import w2_210_support as d1

support = d1.support


def test_the_stage_is_in_the_commands_stage_list_after_a10_and_before_ma():
    """V1: ``VERDICT`` is in ``gov.adopt.command.STAGES``, after A10 (and MA, in no chain, stays after it)."""
    from gov.adopt import command

    stages = tuple(command.STAGES)
    assert "VERDICT" in stages, f"gov.adopt.command.STAGES does not list VERDICT: {stages}"
    assert stages.index("A10") < stages.index("VERDICT") < stages.index("MA"), stages


def test_the_cases_run_this_worktrees_gov(adopted):
    """Guard: a child started as the cases start ``gov``, and this process, import the package from this worktree."""
    import gov

    here = d1.REPO_ROOT.resolve()
    assert d1.Path(gov.__file__).resolve().is_relative_to(here / "src"), gov.__file__
    assert d1.gates.gov_file(adopted.sandbox).resolve().is_relative_to(here / "src")


def test_every_condition_is_met_on_the_adopted_project_with_the_tools_stood_in(adopted):
    """V1: the project of the Verify (every stage run, both gates passed, a closed ticket) gives every condition
    ``met``, named as README fixes them, in order: the verdict is ADOPTED_HEALTHY."""
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert list(d1.states(result)) == list(d1.CONDITIONS)
    assert set(d1.states(result).values()) == {"met"}, d1.states(result)
    assert result["verdict"] == "ADOPTED_HEALTHY"


def test_each_condition_gives_its_evidence_the_command_and_exit_or_the_record_and_path(adopted):
    """V1: ``evidence`` holds ``command``, ``exit`` and ``path``: the command run and its exit code, or the record
    read and its path (the keys that do not apply are null)."""
    project = adopted.project
    result = d1.compute(project, tools=d1.healthy_tools())
    for item in result["conditions"]:
        evidence = item["evidence"]
        assert isinstance(evidence, dict) and {"command", "exit", "path"} <= set(evidence), item
        assert isinstance(item.get("source"), str) and item["source"].strip(), item
        assert evidence["command"] is not None or evidence["path"] is not None, f"no evidence: {item}"
        if evidence["command"] is not None:
            assert isinstance(evidence["command"], str) and isinstance(evidence["exit"], int), item
        if evidence["path"] is not None:
            assert support.at_head(project, evidence["path"]) is not None, f"{item['name']}: {evidence['path']} is not committed"
    for stage in d1.STAGE_CONDITIONS:
        assert d1.condition(result, stage)["evidence"]["path"] == d1.RECORD[stage]
    assert d1.condition(result, d1.LITE_A7)["evidence"]["path"] == d1.RECORD["A7"]
    assert d1.condition(result, d1.LITE_A10)["evidence"]["path"] == d1.RECORD["A10"]
    assert d1.condition(result, d1.A5_REVIEW)["evidence"]["path"] in (d1.AUDITOR["A5"], d1.RECORD["A5"])
    assert d1.condition(result, d1.NATIVE)["evidence"]["path"] in (d1.RECORD["A3"], d1.RECORD["A6"])
    assert d1.condition(result, d1.TICKET_COND)["evidence"]["path"] == d1.CLOSE_REL
    for name, tool in ((d1.DOCTOR, "doctor"), (d1.RELEASE, "doctor"), (d1.CHECK, "check")):
        evidence = d1.condition(result, name)["evidence"]
        assert f"gov {tool}" in evidence["command"] and evidence["exit"] == 0, (name, evidence)


# Each plant: its name, what it does to the case's copy, the tools it stands in, the condition it must make not met,
# and what that condition's evidence must name. A plant commits (ordinary commits) or stands in a tool; nothing else.
def _a2_removed(project):
    d1.remove_record(project, d1.RECORD["A2"])


def _a1_changed(project):  # A2 stands on A1's record as it was: it no longer does
    d1.append_to(project, d1.RECORD["A1"])


def _a5_verdict_changed(project):
    d1.append_to(project, d1.AUDITOR["A5"])


def _a7_failed(project):
    d1.set_result(project, "A7", "fail")


def _a10_failed(project):
    d1.set_result(project, "A10", "fail")


def _a7_record_removed(project):
    d1.remove_record(project, d1.RECORD["A7"])


def _a7_not_on_a6(project):
    d1.write_front(project, d1.RECORD["A7"], lambda front: front.__setitem__("stands_on", "0" * 64),
                   "the A7 record stands on another A6 record", f"Task: {d1.TICKET}")


def _a10_not_on_a8(project):
    d1.write_front(project, d1.RECORD["A10"], lambda front: front.__setitem__("stands_on", "f" * 64),
                   "the A10 record stands on another A8 record", f"Task: {d1.TICKET}")


def _ticket_reopened(project):
    d1.write_ticket(project, status="open")
    d1.commit(project, "the ticket is open again")


def _close_with_a_failed_test(project):
    d1.write_close(project, passed=2, failed=1)
    d1.commit(project, "a close record with a failed test")


def _close_with_an_error(project):
    d1.write_close(project, passed=2, errors=1)
    d1.commit(project, "a close record with a test in error")


def _close_with_no_test_passed(project):
    d1.write_close(project, passed=0, skipped=3)
    d1.commit(project, "a close record in which no test passed")


def _no_ticket(project):
    d1.remove_record(project, d1.TICKET_REL)
    d1.remove_record(project, d1.CLOSE_REL)


def _names(path):
    return lambda evidence: evidence["path"] == path


def _runs(tool, exit_code):
    return lambda evidence: f"gov {tool}" in (evidence["command"] or "") and evidence["exit"] == exit_code


def _anything(evidence):
    return True


PLANTS = {
    "a-stage-record-removed": (_a2_removed, {}, "A2", _names(d1.RECORD["A2"])),
    "a-record-no-longer-stands-on-the-one-before": (_a1_changed, {}, "A2", _names(d1.RECORD["A2"])),
    "an-a5-verdict-changed": (_a5_verdict_changed, {}, d1.A5_REVIEW,
                              lambda e: e["path"] in (d1.AUDITOR["A5"], d1.RECORD["A5"])),
    "an-a7-record-with-result-fail": (_a7_failed, {}, d1.LITE_A7, _names(d1.RECORD["A7"])),
    "an-a10-record-with-result-fail": (_a10_failed, {}, d1.LITE_A10, _names(d1.RECORD["A10"])),
    "the-a7-record-removed": (_a7_record_removed, {}, d1.LITE_A7, _names(d1.RECORD["A7"])),
    "the-a7-record-not-on-the-a6-record": (_a7_not_on_a6, {}, d1.LITE_A7, _names(d1.RECORD["A7"])),
    "the-a10-record-not-on-the-a8-record": (_a10_not_on_a8, {}, d1.LITE_A10, _names(d1.RECORD["A10"])),
    "gov-doctor-drift": (lambda project: None, {"doctor": d1.doctor(lock="DRIFT")}, d1.RELEASE, _runs("doctor", 0)),
    "gov-doctor-exit-3": (lambda project: None, {"doctor": d1.doctor(exit_code=3, failing_part="canaries")},
                          d1.DOCTOR, _runs("doctor", 3)),
    "a-red-family": (lambda project: None, {"check": d1.check(red=("security",))}, d1.CHECK, _runs("check", 3)),
    "no-closed-ticket": (_ticket_reopened, {}, d1.TICKET_COND, _anything),
    "no-ticket-at-all": (_no_ticket, {}, d1.TICKET_COND, _anything),
    "a-close-record-with-a-failed-test": (_close_with_a_failed_test, {}, d1.TICKET_COND, _anything),
    "a-close-record-with-a-test-in-error": (_close_with_an_error, {}, d1.TICKET_COND, _anything),
    "a-close-record-in-which-no-test-passed": (_close_with_no_test_passed, {}, d1.TICKET_COND, _anything),
}


@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_one_planted_failure_makes_exactly_its_condition_not_met_and_leaves_the_others(adopted, plant):
    """V1: for each condition one planted failure makes exactly that condition ``not met``, names it (the evidence:
    the record, or the command and its exit code) and leaves every other condition as it was; the verdict is then
    NOT_ADOPTED_HEALTHY."""
    change, stand_ins, name, names_it = PLANTS[plant]
    project = adopted.project
    before = d1.compute(project, tools=d1.healthy_tools())
    assert d1.not_met(before) == [], d1.states(before)
    change(project)
    result = d1.compute(project, tools=d1.healthy_tools(**stand_ins))
    assert d1.not_met(result) == [name], d1.states(result)
    assert {n: s for n, s in d1.states(result).items() if n != name} == \
        {n: s for n, s in d1.states(before).items() if n != name}
    assert names_it(d1.condition(result, name)["evidence"]), d1.condition(result, name)
    assert result["verdict"] == "NOT_ADOPTED_HEALTHY"


def test_a_move_out_of_a_native_layout_without_both_grounds_makes_exactly_that_condition_not_met(native_copy):
    """V1: A3 refuses to write it, so the planted record is one whose native move lost its ``justification``
    before A4 stood on it; every stage record still stands on the one before. The project is otherwise the
    adopted one (whose own native move, with both grounds, is met)."""
    result = d1.compute(native_copy.project, tools=d1.healthy_tools())
    assert d1.not_met(result) == [d1.NATIVE], d1.states(result)
    assert d1.condition(result, d1.NATIVE)["evidence"]["path"] in (d1.RECORD["A3"], d1.RECORD["A6"])
    assert result["verdict"] == "NOT_ADOPTED_HEALTHY"


def test_a_missing_record_is_named_never_skipped(adopted):
    """V1: A8's record removed: A8 is ``not met`` and names the path (the A10 gate that stood on it may follow it)."""
    d1.remove_record(adopted.project, d1.RECORD["A8"])
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert "A8" in d1.not_met(result), d1.states(result)
    assert d1.condition(result, "A8")["evidence"]["path"] == d1.RECORD["A8"]
    assert "A8" in d1.states(result), "a missing record's condition is still in the record: never skipped"
    assert result["verdict"] == "NOT_ADOPTED_HEALTHY"


def test_an_unreadable_record_is_not_met_and_named(adopted):
    """V1: A4's record overwritten with text that has no frontmatter: A4 is ``not met`` and names the path (the
    record that stood on it may follow)."""
    support.write(adopted.project, d1.RECORD["A4"], "this is not a record\n")
    d1.commit(adopted.project, "the plan is overwritten")
    result = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert "A4" in d1.not_met(result), d1.states(result)
    assert d1.condition(result, "A4")["evidence"]["path"] == d1.RECORD["A4"]


def test_two_planted_failures_make_exactly_their_two_conditions_not_met(adopted):
    """V1: independent plants add up: A7's result and a RED family make exactly those two conditions ``not met``."""
    d1.set_result(adopted.project, "A7", "fail")
    result = d1.compute(adopted.project, tools=d1.healthy_tools(check=d1.check(red=("test",))))
    assert d1.not_met(result) == [d1.LITE_A7, d1.CHECK], d1.states(result)


def test_compute_reads_only_and_gives_the_same_answer_twice(adopted):
    """V1: ``compute`` writes nothing (the helper asserts HEAD and the tree) and is deterministic for one commit."""
    first = d1.compute(adopted.project, tools=d1.healthy_tools())
    second = d1.compute(adopted.project, tools=d1.healthy_tools())
    assert first == second
    assert first["commit"] == support.git(adopted.project, "rev-parse", "HEAD").strip()
