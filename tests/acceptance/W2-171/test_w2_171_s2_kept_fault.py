"""S2, review round 2, B-2 (finding F-2, S2, Interface items 1, 2 and 8): ``measure --kept <n>`` never prints a faulted
attempt's figures.

Item 8: "a faulted attempt's figures are never printed". Item 1: ``measure --kept <n>`` "prints the ``RETRIEVAL`` line of
item 8, writes nothing, exits 0 or 1 ``MS-KEPT``, never 3". ``MS-KEPT`` is the only refusal item 1 gives ``--kept``, so
the reading taken (the lead's) is: for an attempt folder holding ``FAULT``, ``measure --kept <n>`` exits 1, prints
``MS-KEPT``, prints no ``RETRIEVAL`` line, writes nothing and searches nothing, whatever the folder's kept outputs
(whole in number, as a degraded attempt's are) would re-score to. ``measure --kept 2`` on the same run (the clean
attempt-2 that counted) prints attempt-2's ``RETRIEVAL`` line and exits 0.

The causes covered (item 3's ``FAULT`` words): ``degraded`` (a bundle not reranked by the service, the pool's rerank
fallen back), ``exit`` (the measure exited non-zero) and ``store`` (the store's sha256 changed; the audit stops there,
so only attempt-1 exists). Also the minimal form: a measured, whole attempt whose folder is given a ``FAULT`` file and
loses its ``DONE`` (a faulted attempt has none), whose kept outputs are untouched.
"""

from __future__ import annotations

import pytest

import w2_171_scenario as S
import w2_171_world as W

SC = S.SCENARIOS["five"]
TARGET = "q12"


def fault_in_attempt_1(fault):
    """Edit: ``q12``'s question answered with ``fault`` at its first asking (attempt-1), cleanly at its second."""
    def edit(gov, docs):
        gov[docs[TARGET]["question"]]["by_occ"] = {"1": {"fault": fault}}
    return edit


def store_changes_in_attempt_1(world):
    def edit(gov, docs):
        gov[docs[TARGET]["question"]]["mutate_store"] = {"path": str(world.store), "data": "a page changed in the store"}
    return edit


def assert_refused_untouched(world, run, number, before_sets, before_calls):
    assert run.code == 1, run
    assert "MS-KEPT" in run.lines, run
    assert not any(x.startswith("RETRIEVAL") for x in run.lines), f"a faulted attempt's figures were printed: {run}"
    assert not any(x.startswith("STOPPED") for x in run.lines), run
    assert W.snapshot(world.sets) == before_sets, f"measure --kept {number} wrote something"
    assert len(world.gov_calls()) == before_calls, f"measure --kept {number} searched"
    assert world.git_status() == ""


@pytest.mark.parametrize("fault,cause", [("rerank", "degraded"), ("pool", "degraded"), ("exit", "exit")])
def test_s2_kept_of_a_faulted_attempt_is_ms_kept_and_prints_no_figures_while_the_counting_one_prints(
        world, fault, cause):
    """B-2 (F-2, items 1, 2, 8): attempt-1 faulted (``degraded`` or ``exit``) then attempt-2 counted: ``--kept 1`` exits
    1 with ``MS-KEPT`` and no ``RETRIEVAL`` line, writes and searches nothing; ``--kept 2`` prints attempt-2's line,
    exit 0."""
    SC.install(world, gov_edit=fault_in_attempt_1(fault))
    run = world.measure()
    assert run.code == 0, run
    assert (world.attempt_dir(1) / "FAULT").read_text().strip() == cause
    assert (world.run_dir / "COUNTS").read_text().strip() == "attempt-2"
    before_sets, before_calls = W.snapshot(world.sets), len(world.gov_calls())

    faulted = world.measure_kept(1)
    assert_refused_untouched(world, faulted, 1, before_sets, before_calls)

    counted = world.measure_kept(2)
    assert counted.code == 0, counted
    assert [x for x in counted.lines if x.startswith("RETRIEVAL")] == [S.Expected(SC, world).retrieval_line(2)], counted
    assert W.snapshot(world.sets) == before_sets, "measure --kept 2 wrote something"
    assert len(world.gov_calls()) == before_calls, "measure --kept 2 searched"


def test_s2_kept_of_an_attempt_that_faulted_on_the_store_is_ms_kept_and_prints_no_figures(world):
    """B-2, the ``store`` cause: the audit stopped (``STOPPED store``, no attempt-2); ``--kept 1`` is ``MS-KEPT``, exit
    1, no ``RETRIEVAL`` line, nothing written, nothing searched, ``STOPPED`` left as it was."""
    SC.install(world, gov_edit=store_changes_in_attempt_1(world))
    run = world.measure()
    assert run.code == 2 and "STOPPED store" in run.lines, run
    assert (world.attempt_dir(1) / "FAULT").read_text().strip() == "store"
    before_sets, before_calls = W.snapshot(world.sets), len(world.gov_calls())
    assert_refused_untouched(world, world.measure_kept(1), 1, before_sets, before_calls)
    assert (world.run_dir / "STOPPED").read_text().strip() == "store"


def test_s2_kept_of_a_folder_holding_fault_is_ms_kept_whatever_its_kept_outputs_would_score(make_world):
    """B-2, the minimal form: a measured, whole attempt (its kept outputs whole in number, scoring as planted) given a
    ``FAULT`` file and no ``DONE``: the folder holds ``FAULT``, so its figures are not printed."""
    world = make_world("measured:five")
    assert world.measure_kept(1).code == 0, "before the fault is planted the same outputs re-score"
    (world.attempt_dir(1) / "DONE").unlink()
    (world.attempt_dir(1) / "FAULT").write_text("degraded\n")
    before_sets, before_calls = W.snapshot(world.sets), len(world.gov_calls())
    assert_refused_untouched(world, world.measure_kept(1), 1, before_sets, before_calls)
