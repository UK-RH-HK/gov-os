"""S2: one judged run a week (Interface I2, I4).

A standing run writes ``runs/<set>/<ISO year>-W<week>/DECLARATION.json`` and then ``USED`` before any search (the week folder is
``0700``); a second judged run of the set in the same ISO week exits 3, prints ``USED`` and writes nothing (the sets root and the
key folder byte-identical). A run stopped by the fault rule before its reader run started may start once more that week (its
folder is renamed ``<week>.stopped/``); a run whose reader run started, or a second restart, never runs again.

The whole run comes from the session's ``pass`` run (80 right; the gate asked); the week-rule table is planted week folders
with a busy gate (``GOV_MEMAUDIT_GATE_MAX_S=0``), which stops a run right after its pre-flight, before any search.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import stat

import pytest

import w2_187_world as W
from w2_187_world import S171, W171, W172

BUSY = {"GOV_MEMAUDIT_GATE_MAX_S": "0", "GOV_MEMAUDIT_GATE_POLL_S": "0"}
ROUNDING = ("need_right = ceil(95 n / 100); max_wrong = floor(5 n / 100); target_right = need_right; integer arithmetic; "
            "standing and fresh runs alike (DEC-1179 (2))")


def state(world):
    return W.tree_state(world.sets, world.runs_env)


def test_s2_a_run_writes_the_declaration_then_used_before_any_search(ran_std):
    world, run = ran_std("pass")
    assert run.code == 0, run
    declaration, used = world.std_week / "DECLARATION.json", world.std_week / "USED"
    assert declaration.is_file() and used.is_file()
    assert declaration.stat().st_mtime_ns < used.stat().st_mtime_ns, "DECLARATION.json before USED, by file time"
    first = min(c["t"] for c in world.searches())
    assert used.stat().st_mtime_ns / 1e9 <= first, "USED before the first search (the planted gov's own clock)"
    events = [e["event"] for e in world.std_ledger()]
    # I2 puts the standing pre-flight's ledger in the week folder, so its `preflight` line may come first
    head = events[:events.index("search")] if "search" in events else events
    assert [e for e in head if e != "preflight"] == ["declaration", "used"], f"the ledger before the first search: {events[:5]}"
    assert head.index("declaration") < head.index("used"), f"the ledger's first lines: {events[:5]}"
    assert set(head[:head.index("declaration")]) <= {"preflight"}, f"only the pre-flight before the declaration: {events[:5]}"
    assert stat.S_IMODE(os.stat(world.std_week).st_mode) == 0o700, "the week folder is mode 0700"


def test_s2_the_declaration_records_the_standard_the_set_the_live_count_and_the_95_percent_bar(ran_std):
    world, run = ran_std("pass")
    assert run.code == 0, run
    doc = world.std_json("DECLARATION.json")
    assert doc["audit"] == W.STD
    assert doc["audit_commit"] == world.audit_commit == doc["store_commit"]
    assert doc["gov_pin"] == W171.PIN and doc["ok"] is True and doc["nonstandard"] == [] and doc["decision"] is None
    assert doc["set_digest"] == world.std_digest()
    assert doc["settings"] == {"reranker": "shared", "pool": True, "bundle_tokens": 6000, "search_again_once": True}
    assert (doc["n"], doc["n_set"], doc["dropped"]) == (80, 80, 0)
    assert doc["bar"] == {"need_right": 76, "max_wrong": 4, "target_right": 76}
    assert doc["rounding"] == ROUNDING


def test_s2_the_run_is_preflight_measure_judge_figures_with_the_week_and_the_set_on_each_line(ran_std):
    world, run = ran_std("pass")
    assert run.code == 0, run
    steps = W172.step_lines(run)
    assert [name for name, _ in steps] == ["preflight", "measure", "judge", "figures"]
    for name, line in steps:
        flags = W172.flag_map(shlex.split(line)[3:])
        assert flags["--audit"] == W.STD and flags["--week"] == world.week, (name, line)
    assert run.lines[-1] == f"STANDING {world.week} right 80 of 80: passes", run.lines[-3:]


def test_s2_the_gate_is_asked_before_measure_and_before_judge_and_nowhere_else(ran_std):
    world, run = ran_std("pass")
    assert run.code == 0, run
    assert len(world.gate_calls()) == 2, world.gate_calls()


def test_s2_a_second_judged_run_the_same_week_exits_3_and_writes_nothing(copy_std):
    world = copy_std("pass")
    before = state(world)
    run = world.standing_run()
    assert run.code == 3 and run.lines == ["USED"], run
    assert state(world) == before, "the sets root and the key folder are byte-identical"
    assert world.searches() == [] and world.claude_calls() == []


def put_week(world, *, used=True, stopped=None, reader=False, figures=False, stopped_folder=False, preflight=False):
    folder = world.std_week
    folder.mkdir(parents=True, mode=0o700)
    if used:
        (folder / "USED").write_text("2026-11-10T10:00:00Z x 00\n", encoding="utf-8")
        (folder / "DECLARATION.json").write_text(json.dumps({"audit": W.STD, "n": 80}), encoding="utf-8")
    if stopped:
        (folder / "STOPPED").write_text(stopped + "\n", encoding="utf-8")
    if reader:
        (folder / "reader").mkdir()
    if figures:
        (folder / "FIGURES.json").write_text(json.dumps({"n": 80}), encoding="utf-8")
    if preflight:
        (folder / "PREFLIGHT.json").write_text(json.dumps({"mode": "standing", "ok": True}), encoding="utf-8")
    if stopped_folder:
        (world.std_runs / f"{world.week}.stopped").mkdir()


@pytest.mark.parametrize("case,kw", [
    ("used-and-no-stop", dict()),
    ("a-finished-run", dict(figures=True)),
    ("stopped-after-the-reader-started", dict(stopped="fault", reader=True)),
    ("stopped-but-already-restarted", dict(stopped="fault", stopped_folder=True)),
])
def test_s2_a_spent_week_is_refused_with_used_exit_3_and_nothing_written(make_world, case, kw):
    world = make_world(std="pass")
    put_week(world, **kw)
    before = state(world)
    run = world.standing_run(env=BUSY)
    assert run.code == 3 and run.lines == ["USED"], (case, run)
    assert state(world) == before, case
    assert world.searches() == []


def test_s2_a_run_stopped_before_its_reader_run_may_start_once_more_the_old_folder_is_kept(make_world):
    world = make_world(std="pass")
    put_week(world, stopped="fault")
    world.plan_gate(1)
    run = world.standing_run(gate=world.gate_stub, env=BUSY)
    assert run.code == 2 and "STOPPED measure gate busy" in run.lines, run
    old = world.std_runs / f"{world.week}.stopped"
    assert (old / "STOPPED").read_text().strip() == "fault" and (old / "USED").is_file(), "the stopped week is kept whole"
    assert not (world.std_week / "USED").exists(), "the restart's own run has not started its judged part"
    assert world.searches() == []


def test_s2_a_week_folder_without_used_is_reused_not_renamed(make_world):
    world = make_world(std="pass")
    put_week(world, used=False, preflight=True)
    world.plan_gate(1)
    run = world.standing_run(gate=world.gate_stub, env=BUSY)
    assert run.code == 2 and "STOPPED measure gate busy" in run.lines, run
    assert not (world.std_runs / f"{world.week}.stopped").exists()


def test_s2_the_next_iso_week_runs_again_and_leaves_the_earlier_week_untouched(make_world):
    world = make_world(std="pass")
    put_week(world, figures=True)
    earlier = W.tree_state(world.std_week)
    # a Monday of the next ISO week, with the audit commit fresh enough (the clock seam is the only clock)
    world.set_now(W.MONDAY)
    commit = world.repo_commit("2026-11-16T06:00:00+00:00", {"docs/std/new-note.md": "a note\n"}, "a commit for the next week")
    world.relink(commit)
    world.plan_gate(1)
    run = world.standing_run(gate=world.gate_stub, env=BUSY, now=W.MONDAY)
    assert run.code == 2 and "STOPPED measure gate busy" in run.lines, run
    assert world.week == "2026-W47" and world.std_week.parent == world.std_runs
    prior = world.std_runs / "2026-W46"
    assert W.tree_state(prior) == earlier, "the week already judged is untouched"
    assert (world.std_runs / "2026-W47").is_dir()
