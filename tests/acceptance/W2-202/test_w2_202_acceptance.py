"""A3 (L2 §3 A3): acceptance at the landing.

Success lines 4 (A3 S1), 5 (A3 S2) and 6 (A3 S3), failure line 3 (A3 F1). README, "The planted runs": no_tests,
classes, accepted.
"""

from __future__ import annotations

import json

import pytest

import w2_202_support as support
from w2_202_support import A, N, X, kit, module_rel

NO_TESTS = "NO_ACCEPTANCE_TESTS"


def refused_codes(result):
    return {r.get("ticket"): r.get("code") for r in result.get("refused") or []}


# -- success line 4 (A3 S1) ---------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def no_tests(landing):
    return landing("no_tests")


def test_a_feature_ticket_whose_acceptance_folder_holds_no_test_is_refused_alone_and_nothing_moves(no_tests):
    result = kit.answer(no_tests.run, kit.EXIT_NOT_ALL_LANDED)
    assert refused_codes(result) == {N.id: NO_TESTS}, f"refused: {result.get('refused')!r}"
    assert result.get("landed") == [] and result.get("culprits") == []
    support.unchanged(no_tests.before, no_tests.extra["alone_after"])
    assert kit.status_at(no_tests.root, no_tests.old_head, N.id) == "open"


def test_the_refusal_comes_before_any_run(no_tests):
    """The check is one of the checks before any run (L2 §2 step 2): the alone run ran no planted test."""
    kit.answer(no_tests.run, kit.EXIT_NOT_ALL_LANDED)
    result = json.loads(no_tests.run["stdout"])["result"]
    assert result.get("tested") is None and not result.get("runs"), f"a run was made: {result.get('runs')!r}"


def test_in_a_batch_the_ticket_without_tests_is_out_and_the_other_lands(no_tests):
    batch = no_tests.extra["batch"]
    result = kit.answer(batch["run"], kit.EXIT_NOT_ALL_LANDED)
    assert refused_codes(result) == {N.id: NO_TESTS}, f"refused: {result.get('refused')!r}"
    assert result.get("landed") == [A.id] and result.get("culprits") == []
    root, head = no_tests.root, kit.rev(no_tests.root, "main")
    assert head == result.get("head") != no_tests.old_head
    assert kit.is_ancestor(root, no_tests.tips[A.id], head) and kit.status_at(root, head, A.id) == "closed"
    assert not kit.is_ancestor(root, no_tests.tips[N.id], head), "the refused ticket's work landed"
    assert kit.status_at(root, head, N.id) == "open"
    assert kit.show(root, head, f"docs/close/{N.id}/CL-{N.id}.md") is None
    assert kit.show(root, head, module_rel("mod_nn")) == kit.show(root, no_tests.old_head, module_rel("mod_nn"))


# -- success line 5 (A3 S2) ---------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def classes(landing):
    return landing("classes")


def test_a_ticket_judged_on_its_record_lands_without_a_test_folder_where_a_feature_ticket_is_refused(classes):
    result = kit.answer(classes.run, kit.EXIT_NOT_ALL_LANDED)
    assert refused_codes(result) == {N.id: NO_TESTS}, f"refused: {result.get('refused')!r}"
    landed = [t.id for t in support.RECORD_TICKETS]
    assert result.get("landed") == landed and result.get("culprits") == [], f"landed: {result.get('landed')!r}"
    kit.assert_landed_through_close_commits(classes, result, "main", classes.old_head)


@pytest.mark.parametrize("ticket", support.RECORD_TICKETS, ids=[t.kind for t in support.RECORD_TICKETS])
def test_each_class_judged_on_a_record_lands_and_closes(classes, ticket):
    result = kit.answer(classes.run, kit.EXIT_NOT_ALL_LANDED)
    root, head = classes.root, result["head"]
    assert ticket.id in (result.get("landed") or []), f"the {ticket.kind} ticket did not land: {result!r}"
    assert kit.is_ancestor(root, classes.tips[ticket.id], head)
    assert kit.status_at(root, head, ticket.id) == "closed"
    front = kit.close_record(classes, head, ticket.id)
    assert front.get("commit") == result.get("tested")
    assert kit.show(root, head, f"tests/acceptance/{ticket.wbs}/README.md") is None


def test_a_ticket_whose_record_its_class_s_gate_refuses_does_not_land(classes):
    """Judged on its record: X's record is no research record (the fixture checked that ``check_evidence``
    refuses it), so X does not land, is not closed, and the answer names it."""
    bad = classes.extra["bad"]
    run = bad["run"]
    assert run["code"] not in (0, None), f"the queue landed a ticket whose record is refused\n{kit.describe(run)}"
    assert X.id in run["stdout"], f"the answer does not name the ticket\n{kit.describe(run)}"
    assert kit.heads(bad["after"]) == kit.heads(bad["before"]), "a branch moved"
    assert kit.status_at(classes.root, "main", X.id) == "open"
    assert kit.show(classes.root, "main", f"docs/close/{X.id}/CL-{X.id}.md") is None


# -- success line 6 (A3 S3) and failure line 3 (A3 F1) ----------------------------------------------------------

@pytest.fixture(scope="module")
def accepted(landing):
    return landing("accepted")


def pairs(lines):
    """A line as (its KPI line, its result), whichever of the runner's names the record keeps."""
    return [(line.get("kpi") or line.get("id"), line.get("outcome") or line.get("result")) for line in lines or []]


def recorded_acceptance(accepted):
    result = kit.answer(accepted.run, kit.EXIT_LANDED)
    front = kit.close_record(accepted, result["head"], A.id)
    held = front.get("acceptance")
    assert isinstance(held, dict), f"the close record holds no acceptance: {sorted(front)}"
    return result, held


def test_the_close_record_holds_the_acceptance_folder_and_each_kpi_line_s_result(accepted):
    _, held = recorded_acceptance(accepted)
    assert str(held.get("folder") or "").strip("/") == A.acceptance.strip("/"), f"folder: {held.get('folder')!r}"
    assert pairs(held.get("lines")) == [("success-1", "pass"), ("failure-1", "pass")], f"lines: {held.get('lines')!r}"


def test_the_record_s_lines_equal_gov_accept_s_own_answer_on_the_tested_merge(accepted):
    result, held = recorded_acceptance(accepted)
    own = accepted.extra.get("accept")
    assert own and own["code"] == 0, f"fixture: gov accept did not run at the tested merge {result.get('tested')}"
    lines = json.loads(own["stdout"])["result"]["lines"]
    assert lines and pairs(held.get("lines")) == pairs(lines), \
        f"the record's lines {held.get('lines')!r} are not gov accept's {lines!r}"
    if all("kpi" in line for line in held["lines"]):   # the runner's own shape: then every figure of it too
        assert held["lines"] == lines


def test_no_test_of_the_acceptance_folder_ran_twice_in_the_landing(accepted):
    """Failure line 3: the acceptance run and the selection's run share no test. The acceptance run happened (the
    record holds its lines); the folder's test ran exactly once, on the tested merge; the selection's JUnit files
    name it at most once in all, and the selection names no path of the folder."""
    result, held = recorded_acceptance(accepted)
    assert pairs(held.get("lines")), "the acceptance run left no line"
    runs = accepted.told_runs("test_aa")
    assert len(runs) == 1 and runs[0]["ok"], f"the acceptance folder's test ran {len(runs)} time(s), not once"
    assert (runs[0]["seen"][module_rel("widget")] or "").startswith("# CHANGED"), "it did not run on the merge"
    suites = (result.get("selection") or {}).get("suites") or []
    inside = [s for s in suites if s.rstrip("/").startswith(A.acceptance.rstrip("/"))]
    assert not inside, f"the selection's run names the acceptance folder: {inside}"
    runtime, clone, named = accepted.root / ".gov-runtime", accepted.root / kit.CLONE_REL, 0
    for path in sorted(runtime.rglob("*.xml")):
        if clone not in path.parents:
            named += sum(1 for node in kit.junit_outcomes(path) if node.startswith(A.acceptance))
    assert named <= 1, f"the landing's JUnit files name the acceptance folder's test {named} times"


def test_the_selection_s_run_still_ran_the_tests_the_change_reaches(accepted):
    result, _ = recorded_acceptance(accepted)
    ran = kit.files_of(kit.queue_junit(accepted))
    assert kit.USES_WIDGET[0] in ran, f"the importer of the changed module is not in the run's JUnit: {sorted(ran)}"
    told = accepted.told_runs("test_uses_widget")
    assert len(told) == 1 and told[0]["ok"], f"test_uses_widget ran {len(told)} time(s)"
    assert result.get("landed") == [A.id]
