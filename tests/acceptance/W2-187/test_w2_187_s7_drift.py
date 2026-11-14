"""S7: the monthly check against fitting (Interface I7), at each fresh run.

With a live standing set, a whole fresh audit compares its right-end-to-end per cent F with S, the mean ``pct`` of the live
set's last four standing measured lines. ``S - F >= 5`` writes a HISTORY line ``{"kind": "drift", "word": "STANDING_FITTED",
"S", "F", "set"}``, retires the standing set (a ``STANDING.jsonl`` line ``retired``, reason ``fitted``) so that a later
``standing run`` is ``STANDING_RETIRED`` (exit 1) and ``standing live`` says ``LIVE none``; ``F - S >= 5`` writes ``STANDING_STALE``
and retires nothing; fewer than four weekly figures print ``drift: not yet (k of 4)``. The fresh digest's twelve lines are
unchanged; with a live set a ``DRIFT S <s> F <f>: none|STANDING_FITTED|STANDING_STALE`` line (or ``DRIFT not yet (k of 4)``) follows.

The fresh audits are W2-171's planted ones (40 questions; F is 90.0, 92.5, 97.5 or 100.0), each beside four planted weekly
figures. The edge cases sit on the Interface's ``>= 5``: exactly 5.0 flags, 4.875 does not.
"""

from __future__ import annotations

import os
import re

import pytest

import w2_187_world as W
from w2_172_digest import by_word
from w2_187_world import S171

DRIFT = re.compile(r"DRIFT S (?P<s>\d+(?:\.\d+)?) F (?P<f>\d+(?:\.\d+)?): (?P<word>none|STANDING_FITTED|STANDING_STALE)")
NOT_YET = re.compile(r"DRIFT not yet \((?P<k>\d+) of 4\)")
CASES = {  # name: (S, F, the word)
    "fitted": (96.0, 90.0, "STANDING_FITTED"), "fitted_edge": (95.0, 90.0, "STANDING_FITTED"),
    "near_fitted": (94.875, 90.0, None), "stale": (90.0, 100.0, "STANDING_STALE"),
    "stale_edge": (92.5, 97.5, "STANDING_STALE"), "none": (95.0, 92.5, None),
}


def flags(world):
    return [x for x in world.history_kind("drift") if x.get("word") in ("STANDING_FITTED", "STANDING_STALE")]


def retired(world):
    return [x for x in world.standing_lines() if x["event"] == "retired"]


@pytest.mark.parametrize("name", sorted(CASES))
def test_s7_the_comparison_writes_the_flag_the_history_line_and_the_digest_line(ran_fresh, name):
    world, run = ran_fresh(name)
    assert run.code == 0, run
    s, f, word = CASES[name]
    scenario = {"fitted": "w187_miss4", "fitted_edge": "w187_miss4", "near_fitted": "w187_miss4", "stale": "clean",
                "stale_edge": "w187_miss1", "none": "w187_miss3"}[name]
    right, _ = S171.Expected(S171.SCENARIOS[scenario], world).right_wrong()
    assert 100 * right / 40 == f == W.FRESH_PCT[scenario], "the planted fresh audit's figure"
    lines = world.digest()
    by_word(lines[:12], strict=True)
    m = DRIFT.fullmatch(lines[12])
    assert m, f"the 13th line is the DRIFT line: {lines[12:]}"
    assert abs(float(m["s"]) - s) < 0.05 and abs(float(m["f"]) - f) < 0.05 and m["word"] == (word or "none"), lines[12]
    if word is None:
        assert flags(world) == [] and retired(world) == []
        return
    (hist,) = flags(world)
    assert hist["word"] == word and hist["set"] == W.STD and abs(hist["S"] - s) < 0.05 and abs(hist["F"] - f) < 0.05, hist
    if word == "STANDING_FITTED":
        (gone,) = retired(world)
        assert gone["reason"] == "fitted" and gone.get("set", W.STD) == W.STD, gone
    else:
        assert retired(world) == [], "a stale set is not retired: its checker looks at it"


def test_s7_fewer_than_four_weekly_figures_print_not_yet_and_flag_nothing(ran_fresh):
    world, run = ran_fresh("not_yet")
    assert run.code == 0, run
    lines = world.digest()
    by_word(lines[:12], strict=True)
    m = NOT_YET.fullmatch(lines[12])
    assert m and m["k"] == "2", lines[12:]
    assert flags(world) == [] and retired(world) == []


def test_s7_a_fitted_set_is_retired_for_good_no_standing_run_no_live_set(copy_fresh):
    world = copy_fresh("fitted")
    live = world.standing_live()
    assert live.code == 1 and live.lines[-1] == "LIVE none", live
    before = W.tree_state(world.sets, world.runs_env)
    run = world.standing_run()
    assert run.code == 1 and "STANDING_RETIRED" in run.lines, run
    assert world.searches() == [] and W.tree_state(world.sets, world.runs_env) == before, "nothing is searched or written"


def test_s7_a_stale_set_stays_live_and_a_later_standing_run_is_not_refused_for_it(ran_fresh):
    world, run = ran_fresh("stale")
    assert run.code == 0, run
    live = world.standing_live()
    assert live.code == 0 and live.lines[-1] == f"LIVE {W.STD}", live


def test_s7_the_fresh_runs_measure_and_judge_search_the_store_links_store_though_the_repositorys_own_is_at_another_commit(
        make_world):
    """Review round 1's F-A (the CTO's fix of 2026-11-14): S7 compares the fresh F with the standing S, so both are measured on
    the same store. Beside a live standing set with four weekly figures (S 96.0), the repository holds its own store built at
    the base commit and the store link's is at the audit commit; the planted ``gov`` answers from the store of the folder it
    runs in. The fresh run's ``measure`` and ``judge`` (and ``preflight``, should it search) search from the link's work tree:
    every one of their logged searches ran there; the run ends with its twelve lines and the DRIFT line (F 100.0: none).
    The ``pool`` step's searches are not judged here (the fix names the pre-flight, the measure and the judge)."""
    world = make_world(scenario="clean", standing=True)
    world.plant_history(*[world.std_line(f"2026-W{w}", 96.0) for w in (42, 43, 44, 45)])
    world.plan_launch({})
    world.plant_earlier(W.W171.EARLIER, pool={"n": 2, "hit5": 0, "full": 0})
    assert world.link_head() == world.audit_commit != world.base_commit
    world.plant_repo_store(world.base_commit)
    world.write_x_plan(store_from="root")
    run = world.go(gate=world.gate_stub)
    assert run.code == 0, run
    link = os.path.realpath(world.link)
    roots = world.search_roots("preflight", "measure", "judge")
    assert len([s for s, _ in roots if s == "measure"]) >= 40, roots[:5]
    assert len([s for s, _ in roots if s == "judge"]) >= 2, "the two second searches (q10, q20) are the judge's"
    outside = sorted({(s, r) for s, r in roots if r != link})
    assert outside == [], f"the fresh run's searches ran outside the link's work tree: {outside}"
    lines = world.digest()
    by_word(lines[:12], strict=True)
    m = DRIFT.fullmatch(lines[12])
    assert m and m["word"] == "none" and abs(float(m["s"]) - 96.0) < 0.05 and abs(float(m["f"]) - 100.0) < 0.05, lines[12:]


def test_s7_a_fresh_run_with_no_live_standing_set_keeps_its_twelve_lines_and_writes_no_drift(make_world):
    world = make_world(scenario="clean")
    world.plan_launch({})
    world.plant_earlier(W.W171.EARLIER, pool={"n": 2, "hit5": 0, "full": 0})
    run = world.go(gate=world.gate_stub)
    assert run.code == 0, run
    assert len(world.digest()) == 12 and world.history_kind("drift") == []
    assert all("kind" not in x for x in world.history()), "with no live set the lines are today's, without kind"
