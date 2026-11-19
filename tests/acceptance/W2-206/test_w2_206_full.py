"""A6 S3, S4 and F2 (L2 §3 A6; DEC-1216 (5)): ``gov queue <T>... --full`` is step 5 widened to the nightly's own run.

Success lines 3 (A6 S3) and 4 (A6 S4), failure line 2 (A6 F2). README, "The planted runs": full_red, full_green,
full_plain, full_timeout.
"""

from __future__ import annotations

import pytest

import w2_206_support as support
from w2_206_support import A, base, kit

UNIT_TESTS = ("test_far", "test_gizmo", "test_uses_helper", "test_uses_widget")


@pytest.fixture(scope="module")
def full_red(landing):
    return landing("full_red")


@pytest.fixture(scope="module")
def full_green(landing):
    return landing("full_green")


@pytest.fixture(scope="module")
def full_plain(landing):
    return landing("full_plain")


@pytest.fixture(scope="module")
def full_timeout(landing):
    return landing("full_timeout")


def _full(landing):
    """``queue.json``'s ``full`` of a ``--full`` landing that landed."""
    held = support.queue_record(landing, kit.answer(landing.run, kit.EXIT_LANDED))
    full = held.get("full")
    assert isinstance(full, dict), f"queue.json holds no full run: its keys are {sorted(held)}"
    return full


# -- success line 3 (A6 S3) ---------------------------------------------------------------------------------------

def test_with_full_a_candidate_that_breaks_a_test_outside_its_selection_is_a_culprit_and_nothing_lands(full_red):
    result = kit.answer(full_red.run, kit.EXIT_NOT_ALL_LANDED)
    assert result.get("culprits") == [A.id] and result.get("landed") == [], f"the answer: {result}"
    assert support.FAR_NODE in (result.get("reds") or []), f"the unrelated red is not named: {result.get('reds')}"
    assert result.get("head") is None and result.get("closes") == []
    taken = full_red.extra["taken"]
    assert kit.heads(taken["after"]) == kit.heads(taken["before"]), "a branch moved"
    assert taken["after"]["files"] == taken["before"]["files"] and taken["after"]["status"] == ""
    far = [r for r in full_red.told_runs("test_far") if "CHANGED" in (r["seen"][support.module_rel("widget")] or "")]
    assert far and not any(r["ok"] for r in far), f"the unrelated test's runs with the change: {far}"


def test_without_full_the_same_candidate_lands_and_the_unrelated_test_is_not_run(full_red):
    kit.answer(full_red.run, kit.EXIT_NOT_ALL_LANDED)
    plain = full_red.extra["plain"]
    result = kit.answer(plain["run"], kit.EXIT_LANDED)
    assert result.get("landed") == [A.id], f"without --full the candidate did not land: {result}"
    ran = plain["after"]["told"].get("test_far.jsonl", 0) - plain["before"]["told"].get("test_far.jsonl", 0)
    assert ran == 0, f"fixture: the unrelated test is inside the candidate's selection (it ran {ran} time(s))"
    selection = kit.close_record(full_red, result["head"], A.id).get("selection")
    assert not support.says_full(selection), f"a landing without --full says full: {selection!r}"


def test_with_the_unrelated_test_green_full_lands_and_the_close_record_s_selection_says_full(full_green):
    result = kit.answer(full_green.run, kit.EXIT_LANDED)
    assert result.get("landed") == [A.id] and result.get("culprits") == [], f"the answer: {result}"
    closes = kit.assert_landed_through_close_commits(full_green, result, "main", full_green.old_head)
    assert list(closes) == [A.id] and kit.status_at(full_green.root, "main", A.id) == "closed"
    selection = kit.close_record(full_green, result["head"], A.id).get("selection")
    assert support.says_full(selection), f"the close record's selection does not say full: {selection!r}"


def test_the_full_run_runs_the_whole_tests_folder_of_the_tested_merge(full_green):
    result = kit.answer(full_green.run, kit.EXIT_LANDED)
    tested = result.get("tested")
    assert tested and kit.parents(full_green.root, tested) == [full_green.old_head, full_green.tips[A.id]]
    for test in UNIT_TESTS:
        told = full_green.told_runs(test)
        assert told and all(r["ok"] for r in told), f"{test} did not run green in the --full landing: {told}"
    helper = [r["seen"][support.module_rel("helper")] for r in full_green.told_runs("test_uses_helper")]
    assert all("CHANGED" in (text or "") for text in helper), "the full run ran on a tree without the change"


def test_queue_json_holds_the_full_run_its_runs_its_workers_and_its_cpus(full_green):
    full = _full(full_green)
    for key in ("runs", "workers", "cpus"):
        assert key in full, f"queue.json's full names no {key}: {sorted(full)}"
    runs = full["runs"]
    assert isinstance(runs, list) and runs and all(isinstance(r, dict) for r in runs), f"full.runs: {runs!r}"


def test_full_writes_no_nightly_record_into_the_project_tree(full_green, full_red):
    result = kit.answer(full_green.run, kit.EXIT_LANDED)
    kit.answer(full_red.run, kit.EXIT_NOT_ALL_LANDED)
    for landing in (full_green, full_red):
        assert not (landing.root / support.NIGHTLY_REL).exists(), f"{support.NIGHTLY_REL}/ is in the project tree"
        assert landing.extra["taken"]["after"]["status"] == "", \
            f"the root is not clean after --full:\n{landing.extra['taken']['after']['status']}"
    held = kit.git(full_green.root, "ls-tree", "-r", "--name-only", result["head"], "--", support.NIGHTLY_REL)
    assert held.strip() == "", f"the landed head holds a nightly record: {held}"


def test_a_red_outside_the_selection_that_is_red_at_the_base_is_a_known_base_red_and_full_lands(full_plain):
    result = kit.answer(full_plain.run, kit.EXIT_LANDED)
    assert result.get("landed") == [A.id] and result.get("culprits") == [], f"the answer: {result}"
    assert base.ids(result.get("base_reds")) == [support.KNOWN_FAR_NODE], f"base_reds: {result.get('base_reds')!r}"
    base.assert_base_red_recorded(full_plain, result, A.id, support.KNOWN_FAR_NODE, full_plain.old_head)


def test_a_red_of_the_full_run_that_is_green_alone_is_flaky_named_and_not_blocking(full_plain):
    result = kit.answer(full_plain.run, kit.EXIT_LANDED)
    assert support.ONCE_NODE in (result.get("flaky") or []), f"flaky: {result.get('flaky')!r}"
    assert support.ONCE_NODE not in (result.get("reds") or []) and result.get("landed") == [A.id]
    told = [r["ok"] for r in full_plain.told_runs("test_once")]
    assert told[:2] == [False, True], f"the flaky test's runs (red, then green alone): {told}"


# -- success line 4 (A6 S4) ---------------------------------------------------------------------------------------

def _started(landing):
    starts = support.rows(landing.told, support.STARTS)
    assert starts, "the run started no pytest in the planted project (on the base --full is unknown: exit 2)"
    return starts


def _pool_of_the_full_run(landing):
    """The xdist pools the unrelated test ran in (only the full run reaches it): each pool's size as a run of it saw
    it (``PYTEST_XDIST_WORKER_COUNT``); a run of it in no pool (alone) is not counted."""
    ran = [row for row in support.rows(landing.told, support.TEST_RUNS) if row["test"] == support.GIZMO_NODE]
    assert ran, "the full run did not run the test outside the selection"
    return {int(row["count"]) for row in ran if row["count"]}


def test_with_cpus_0_1_auto_workers_2_and_a_path_map_naming_12_the_full_run_s_pool_is_2(full_green):
    starts = _started(full_green)
    assert _pool_of_the_full_run(full_green) == {2}, \
        f"the full run's pool is not 2 workers: {_pool_of_the_full_run(full_green)}"
    assert "2" in support.pools(starts), f"no command of the run asks for -n 2: {support.pools(starts)}"


def test_with_the_planted_settings_queue_json_names_workers_2(full_green):
    full = _full(full_green)
    assert full.get("workers") == 2, f"queue.json's full.workers is {full.get('workers')!r}, not 2"


def test_no_command_the_full_run_starts_asks_for_auto_or_for_more_than_the_cap(full_green, full_plain):
    for landing, cap in ((full_green, 2), (full_plain, max(_one_slot(full_plain)))):
        asked = support.pools(_started(landing))
        assert asked or cap == 1, "no command of the run names a pool (-n)"
        assert not [n for n in asked if not n.isdigit()], f"a command asks for -n auto: {asked}"
        assert max(map(int, asked), default=1) <= cap, f"a command asks for more than {cap} workers: {asked}"


def _one_slot(landing):
    sizes = landing.extra["sizes"]
    return {sizes["sized"], sizes["for_count"]}


def test_with_neither_variable_the_pool_is_one_slot_s_workers_not_the_machine_s_cpu_count(full_plain):
    _started(full_plain)
    sizes, slot = full_plain.extra["sizes"], _one_slot(full_plain)
    pool = _pool_of_the_full_run(full_plain)
    assert (pool or 1 in slot) and pool <= slot, \
        f"the full run's pool {sorted(pool)} is not one slot's workers {sorted(slot)} (the machine has " \
        f"{sizes['cpus']} CPUs)"
    full = _full(full_plain)
    assert full.get("workers") in slot, f"queue.json's full.workers is {full.get('workers')!r}, not {sorted(slot)}"


# -- failure line 2 (A6 F2) ---------------------------------------------------------------------------------------

def test_a_full_run_that_reaches_its_time_limit_is_run_incomplete_with_exit_3(full_timeout):
    error = kit.refusal(full_timeout.run, "RUN_INCOMPLETE", kit.EXIT_NOT_ALL_LANDED)
    assert error.get("message"), "the refusal does not say why"
    assert full_timeout.told_runs("test_slow"), "fixture: the test that never ends was not started by the run"


def test_the_full_run_that_did_not_complete_lands_nothing(full_timeout):
    kit.refusal(full_timeout.run, "RUN_INCOMPLETE", kit.EXIT_NOT_ALL_LANDED)
    taken = full_timeout.extra["taken"]
    assert kit.heads(taken["after"]) == kit.heads(taken["before"]), "a branch moved"
    assert taken["after"]["files"] == taken["before"]["files"] and taken["after"]["status"] == ""
    assert kit.status_at(full_timeout.root, "main", A.id) == "open"
    assert kit.show(full_timeout.root, "main", f"docs/close/{A.id}/CL-{A.id}.md") is None
