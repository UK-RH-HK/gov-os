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


def test_s7_a_fresh_run_with_no_live_standing_set_keeps_its_twelve_lines_and_writes_no_drift(make_world):
    world = make_world(scenario="clean")
    world.plan_launch({})
    world.plant_earlier(W.W171.EARLIER, pool={"n": 2, "hit5": 0, "full": 0})
    run = world.go(gate=world.gate_stub)
    assert run.code == 0, run
    assert len(world.digest()) == 12 and world.history_kind("drift") == []
    assert all("kind" not in x for x in world.history()), "with no live set the lines are today's, without kind"
