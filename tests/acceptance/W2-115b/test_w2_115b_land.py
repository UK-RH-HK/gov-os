"""Success lines 1, 2 and 8 on one green landing: ticket A on ``develop`` (README, "The planted runs": green)."""

from __future__ import annotations

import json

import pytest

import w2_115b_support as support
from w2_115b_support import A, B


@pytest.fixture(scope="module")
def green(landing):
    return landing("green")


@pytest.fixture()
def result(green):
    """The answer, read in the case itself: on the base every case fails here, with no envelope (README)."""
    return lambda: support.answer(green.run, support.EXIT_LANDED)


# -- success line 1: merge, one impact-selected run, the branch moved to the tested merge with close commits -----

def test_the_green_ticket_lands_and_exits_0(green, result):
    result = result()
    assert result.get("onto") == "develop"
    assert result.get("candidates") == [A.id]
    assert result.get("landed") == [A.id]
    assert result.get("culprits") == [] and result.get("refused") == [] and result.get("reds") == []


def test_the_tested_merge_s_parents_are_the_old_head_and_the_branch_tip(green, result):
    result = result()
    tested = result.get("tested")
    assert tested and support.rev(green.root, tested) == tested, f"no tested merge in the answer: {tested!r}"
    assert support.parents(green.root, tested) == [green.old_head, green.tips[A.id]]


def test_the_head_reaches_the_tested_merge_through_one_close_commit_per_ticket(green, result):
    result = result()
    closes = support.assert_landed_through_close_commits(green, result, "develop", green.old_head)
    assert list(closes) == [A.id]


def test_the_run_s_junit_holds_the_own_suite_and_the_importer_and_no_unreached_suite(green, result):
    result()
    ran = support.files_of(support.queue_junit(green))
    assert A.suite_file in ran, f"the ticket's own suite is not in the run's JUnit: {sorted(ran)}"
    assert support.USES_WIDGET[0] in ran, f"the suite that imports the changed module did not run: {sorted(ran)}"
    assert support.GIZMO[0] not in ran and B.suite_file not in ran, f"a suite nothing reaches ran: {sorted(ran)}"


def test_the_branch_s_own_commit_without_a_task_trailer_counts_in_the_change(green, result):
    result = result()
    ran = support.files_of(support.queue_junit(green))
    assert support.USES_HELPER[0] in ran, (
        "the test that imports the module only the branch's untrailered commit changed did not run: "
        f"{sorted(ran)}")
    suites = (result.get("selection") or {}).get("suites") or []
    assert any(support.USES_HELPER[0].startswith(s.rstrip("/")) for s in suites), f"not selected: {suites}"


def test_the_root_s_working_tree_follows_the_integration_branch(green, result):
    result = result()
    root = green.root
    assert support.git(root, "symbolic-ref", "--short", "HEAD").strip() == "develop"
    assert support.rev(root, "HEAD") == result.get("head")
    assert support.git(root, "status", "--porcelain") == "", "the root's working tree is not the new head's"
    assert (root / support.module_rel("widget")).read_text(encoding="utf-8").startswith("# CHANGED")
    assert support.front_matter((root / A.ticket_rel).read_text(encoding="utf-8")).get("status") == "closed"


# -- success line 2: the ticket closes at the land ------------------------------------------------------------------

def test_the_close_record_holds_the_queue_s_keys(green, result):
    result = result()
    front = support.close_record(green, result["head"], A.id)
    missing = [k for k in support.RECORD_KEYS if k not in front]
    assert not missing, f"the close record lacks {missing}: {sorted(front)}"
    assert front["close"] == "queue"
    assert isinstance(front["selection"], dict) and front["selection"].get("suites")
    assert front["reds"] == [] and front["culprits"] == []
    assert front["base"] == green.old_head


def test_the_close_record_names_the_tested_merge_the_run_s_counts_and_the_queue_s_record(green, result):
    result = result()
    front = support.close_record(green, result["head"], A.id)
    assert front.get("commit") == result.get("tested")
    assert front.get("runs") == result.get("runs") and result.get("runs"), "the runs are not the queue run's"
    passed = sum(r.get("passed", 0) for r in front["runs"])
    assert passed == len(support.queue_junit(green)), "the runs' counts are not the run's"
    assert front.get("queue") == result.get("record")


def test_the_ticket_is_closed_at_the_new_head_in_the_same_landing(green, result):
    result = result()
    assert support.status_at(green.root, result["head"], A.id) == "closed"
    assert support.status_at(green.root, result["tested"], A.id) == "open"


def test_only_the_queue_s_run_ran_the_planted_tests(green, result):
    result = result()
    for test, module in (("test_aa", "widget"), ("test_uses_widget", "widget"), ("test_uses_helper", "helper")):
        runs = green.told_runs(test)
        assert len(runs) == 1, f"{test} ran {len(runs)} time(s), not once (the queue's run alone)"
        assert runs[0]["seen"][support.module_rel(module)].startswith("# CHANGED"), \
            f"{test} did not run on the merged result"
    assert green.told_runs("test_gizmo") == [] and green.told_runs("test_bb") == []


# -- success line 8: minutes, measured ------------------------------------------------------------------------------

def test_the_queue_s_record_is_written_and_holds_the_answer(green, result):
    result = result()
    rel = result.get("record") or ""
    assert rel.startswith(support.QUEUE_RECORD_PREFIX) and rel.endswith("/queue.json"), f"record: {rel!r}"
    assert rel.count("/") == 3, f"the record is not at .gov-runtime/queue/<stamp>/queue.json: {rel}"
    path = green.root / rel
    assert path.is_file(), f"no queue record at {rel}"
    data = json.loads(path.read_text(encoding="utf-8"))
    held = data.get("result") if isinstance(data.get("result"), dict) else data
    assert held == result, "the queue's record does not hold the answer's result"


def test_the_seconds_of_each_step_and_the_total(green, result):
    result = result()
    held = json.loads((green.root / result["record"]).read_text(encoding="utf-8"))
    held = held.get("result") if isinstance(held.get("result"), dict) else held
    for where, seconds in (("answer", result.get("seconds")), ("record", held.get("seconds"))):
        assert isinstance(seconds, dict) and set(support.STEPS) <= set(seconds), f"{where}: {seconds!r}"
        for step in support.STEPS:
            value = seconds[step]
            assert isinstance(value, (int, float)) and not isinstance(value, bool), f"{where} {step}: {value!r}"
            assert value >= 0, f"{where} {step} is negative: {value}"
        assert seconds["total"] >= max(seconds[s] for s in support.STEPS[:-1]), f"{where}: {seconds}"


# -- failure line 2 ----------------------------------------------------------------------------------------------

def test_green_closed_exactly_when_merged(green, result):
    result()
    support.assert_closed_iff_merged(green, "develop")
    assert support.status_at(green.root, "develop", B.id) == "open"
