"""S8: the two cadences and below 95 % (Interface I8, I4, I12).

* The standing cadence is W2-172 S5's computed rule, unchanged, over the live set's own standing lines (``tests/acceptance/
  W2-172/test_w2_172_s5_due.py`` itself runs unchanged for the no-live-set case); a fresh start never makes a standing run due.
* The fresh cadence: ``due --fresh`` prints ``MODE fresh``, ``DUE yes|no next <date>`` and ``REASON first|28d|miss|wait``:
  first Monday on or after (the last fresh start's date + 28 days); a standing miss makes it due on a Monday with no fresh start
  that ISO week, and it stays due every Monday until a standing run passes. With no live set it answers as ``due``.
* A standing miss is a HISTORY line ``miss`` with its counts and the digest's ``P1 memory below 95 %`` line.
* The repair: two consecutive misses, or one miss 5 points or more below the last passing figure, write ``MEMORY_REPAIR open``;
  ``status --repair`` exits 1 (``REPAIR open since <week>``) while it is open and 0 (``REPAIR none``) after a later pass or
  ``--residual DEC-<n>`` (``REPAIR residual DEC-<n>``); a malformed id is exit 4.

The Monday of the clock seam: 2026-11-16 (ISO 2026-W47); 2026-11-23 is W48. Readings: a miss is judged on a Monday against the
standing line of an earlier day (the wrapper asks ``due --fresh`` before its standing run); the Interface does not say whether a
miss makes the fresh set due on a day that is not a Monday, so the suite asks only on Mondays.
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

import w2_172_git as G
import w2_187_world as W
from w2_187_world import W172

MON, MON2 = "2026-11-16T12:00:00Z", "2026-11-23T12:00:00Z"


def record(w):
    return {"event": "declared", "set": W.STD, "set_digest": "0" * 64, "n": 80, "n_apart": 1,
            "writer_brief_sha256": W.WRITER_SHA, "checker_brief_sha256": W.CHECKER_SHA, "written_commit": w.l0,
            "wave0": False, "at": "2026-10-01T00:00:00Z"}


def standing_line(w, week, *, passes=True, pct=96.0, **over):
    line = G.plant_history_line(w.l0, passes=passes, **over)
    line.update(kind="standing", set=W.STD, week=week, audit=W.STD, pct=pct, word="pass" if passes else "miss", n=80,
                right=round(pct * 0.8), wrong=0, not_found=0, dropped=0)
    return line


def start(at, kind):
    return {"audit": "memory-audit-20261001", "commit": "0" * 40, "at": at, "force": False, "kind": kind}


def light(tmp_path, now, *, live=True, history=(), starts=(), name="w"):
    w = G.due_repo(tmp_path / name, now=now)
    w.mem.mkdir(parents=True, exist_ok=True)
    if live:
        (w.mem / "STANDING.jsonl").write_text(json.dumps(record(w)) + "\n", encoding="utf-8")
    w.plant_history(*history)
    w.plant_starts(*starts)
    w.plant_audits({"time": "2026-10-27T22:00:00Z", "commit": w.l0, "run": "x", "audit": "memory-audit-20261027"})
    return w


def fresh(w, **kw):
    return w.drive("due", *w.common_flags(), "--store-link", str(w.link), "--fresh", **kw)


STABLE = ("2026-W42", "2026-W43", "2026-W44")


def stable(w):
    return [standing_line(w, week) for week in STABLE]


# -- the standing cadence over the live set's own lines --------------------------------------------------------------------
def w_at(days):
    return W172.iso(W172.parse_iso(W.NOW) - timedelta(days=days))


def test_s8_the_standing_cadence_is_the_computed_rule_over_standing_lines_and_ignores_fresh_starts(tmp_path):
    w = light(tmp_path, W.NOW, starts=[start(w_at(30), "standing"), start(w_at(1), "fresh")])
    w.plant_history(*stable(w))
    run = w.due()
    assert run.code == 0 and run.lines[0] == "MODE monthly" and run.lines[1].startswith("DUE yes ") \
        and run.lines[2] == "REASON stable", "a fresh start yesterday does not postpone the standing run: " + repr(run)


def test_s8_a_standing_miss_sends_the_standing_cadence_back_to_weekly_at_once(tmp_path):
    w = light(tmp_path, W.NOW, starts=[start(w_at(7), "standing")])
    w.plant_history(*stable(w)[:2], standing_line(w, "2026-W44", passes=False, pct=90.0))
    run = w.due()
    assert run.code == 0 and run.lines[0] == "MODE weekly" and run.lines[2] == "REASON verdict", run


def test_s8_fresh_lines_do_not_make_the_standing_cadence_monthly(tmp_path):
    w = light(tmp_path, W.NOW, starts=[start(w_at(30), "standing")])
    w.plant_history(*[{**x, "kind": "fresh"} for x in G.stable_history(w.l0)])
    live = w.drive("standing", "live", "--sets-root", str(w.sets), "--repo", str(w.repo))
    assert live.code == 0 and live.lines[-1] == f"LIVE {W.STD}", live
    run = w.due()
    assert run.lines[0] == "MODE weekly" and run.lines[2] == "REASON start", "no standing figure yet: " + repr(run)


# -- due --fresh --------------------------------------------------------------------------------------------------------------
def test_s8_the_fresh_set_is_due_the_first_time(tmp_path):
    w = light(tmp_path, MON)
    run = fresh(w)
    assert run.code == 0 and run.lines[0] == "MODE fresh" and run.lines[1].startswith("DUE yes next ") \
        and run.lines[2] == "REASON first", run


def test_s8_the_fresh_set_28_days_after_the_last_fresh_run_is_due_on_the_monday(tmp_path):
    w = light(tmp_path, MON, starts=[start("2026-10-19T21:00:00Z", "fresh")])
    run = fresh(w)
    assert run.code == 0 and run.lines[0] == "MODE fresh" and run.lines[1].startswith("DUE yes") \
        and run.lines[2] == "REASON 28d", run


def test_s8_the_fresh_set_27_days_after_is_not_due_and_names_the_next_monday(tmp_path):
    w = light(tmp_path, MON, starts=[start("2026-10-20T21:00:00Z", "fresh")])
    run = fresh(w)
    assert run.code == 1 and run.lines == ["MODE fresh", "DUE no next 2026-11-23", "REASON wait"], run


def test_s8_the_fresh_set_is_due_on_a_monday_only_not_on_the_day_the_28_days_end(tmp_path):
    w = light(tmp_path, "2026-11-13T12:00:00Z", starts=[start("2026-10-14T21:00:00Z", "fresh")])
    run = fresh(w)
    assert run.code == 1 and run.lines == ["MODE fresh", "DUE no next 2026-11-16", "REASON wait"], run


def test_s8_a_standing_miss_makes_the_fresh_set_due_on_the_next_monday(tmp_path):
    w = light(tmp_path, MON, starts=[start("2026-11-06T21:00:00Z", "fresh")])
    w.plant_history(*stable(w)[:2], standing_line(w, "2026-W46", passes=False, pct=90.0))
    run = fresh(w)
    assert run.code == 0 and run.lines[0] == "MODE fresh" and run.lines[1].startswith("DUE yes") \
        and run.lines[2] == "REASON miss", run


def test_s8_a_fresh_start_in_the_current_iso_week_answers_the_miss(tmp_path):
    w = light(tmp_path, MON, starts=[start("2026-11-16T09:00:00Z", "fresh")])
    w.plant_history(*stable(w)[:2], standing_line(w, "2026-W46", passes=False, pct=90.0))
    run = fresh(w)
    assert run.code == 1 and run.lines[1].startswith("DUE no") and run.lines[2] == "REASON wait", run


def test_s8_the_fresh_set_stays_due_every_monday_until_a_standing_run_passes_then_every_28_days(tmp_path):
    w = light(tmp_path, MON2, name="a", starts=[start("2026-11-16T09:00:00Z", "fresh")])
    w.plant_history(*stable(w)[:2], standing_line(w, "2026-W46", passes=False, pct=90.0))
    again = fresh(w)
    assert again.code == 0 and again.lines[2] == "REASON miss", "the next Monday: still due while the miss stands: " + repr(again)
    p = light(tmp_path, MON2, name="b", starts=[start("2026-11-16T09:00:00Z", "fresh")])
    p.plant_history(*stable(p)[:2], standing_line(p, "2026-W46", passes=False, pct=90.0), standing_line(p, "2026-W47"))
    passed = fresh(p)
    assert passed.code == 1 and passed.lines == ["MODE fresh", "DUE no next 2026-12-14", "REASON wait"], passed


def test_s8_with_no_live_set_due_fresh_answers_as_due(tmp_path):
    w = light(tmp_path, W.NOW, live=False, history=G.stable_history("0" * 40))
    w.plant_starts(w.start_line(w_at(30), commit=w.l0))
    plain, other = w.due(), fresh(w)
    assert (other.code, other.lines) == (plain.code, plain.lines), (plain, other)


# -- a real standing miss -----------------------------------------------------------------------------------------------------
def test_s8_a_standing_miss_is_a_history_line_with_its_counts_and_a_p1_line_in_the_digest(ran_std):
    world, run = ran_std("five")
    assert run.code == 0, run
    (line,) = [x for x in world.history_kind("standing") if x["week"] == world.week]
    assert (line["word"], line["passes"], line["measured"], line["used"]) == ("miss", False, True, True), line
    assert (line["n"], line["right"], line["wrong"], line["not_found"], line["dropped"]) == (80, 75, 2, 3, 0)
    assert line["pct"] == 93.75 and line["set"] == W.STD and line["audit"] == W.STD and line["commit"] == world.audit_commit
    assert line["gov_pin"] == W.W171.PIN and len(line["retrieval_yaml_sha256"]) == 64 and len(line["path_map_sha256"]) == 64
    block = world.std_digest_lines()
    assert "P1 memory below 95 %: wrong 1 incomplete 1 not_found 3" in block, block
    assert "P1 none" not in block


def test_s8_a_passing_run_has_a_pass_line_and_p1_none(ran_std):
    world, run = ran_std("pass76")
    assert run.code == 0, run
    (line,) = world.history_kind("standing")
    assert (line["word"], line["passes"], line["pct"], line["right"]) == ("pass", True, 95.0, 76), line
    assert "P1 none" in world.std_digest_lines()


def test_s8_after_a_measured_miss_the_fresh_set_is_due_on_the_next_monday(copy_std):
    world = copy_std("five")
    with open(world.mem / "STARTS.log", "a", encoding="utf-8") as f:
        f.write(json.dumps({"audit": "memory-audit-20261101", "commit": world.audit_commit, "at": "2026-11-06T21:00:00Z",
                            "force": False, "kind": "fresh"}) + "\n")
    run = world.due_fresh(now=MON)
    assert run.code == 0 and run.lines[0] == "MODE fresh" and run.lines[2] == "REASON miss", run


# -- the repair ----------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["open_boundary", "open_twice"])
def test_s8_the_repair_opens_on_two_misses_or_on_a_miss_5_points_below_the_last_pass(ran_std, name):
    world, run = ran_std(name)
    assert run.code == 0, run
    opened = [x for x in world.history_kind("repair")]
    assert len(opened) == 1 and opened[0]["word"] == "MEMORY_REPAIR open", opened
    assert (opened[0]["set"], opened[0]["week"]) == (W.STD, world.week)
    assert "REPAIR open" in world.std_digest_lines()
    before = W.tree_state(world.runs_env)
    status = world.status_repair()
    assert status.code == 1 and status.lines == [f"REPAIR open since {world.week}"], status
    assert W.tree_state(world.runs_env) == before, "status --repair writes nothing"


def test_s8_one_miss_less_than_5_points_below_the_last_pass_opens_nothing(ran_std):
    world, run = ran_std("five")
    assert run.code == 0, run
    assert world.history_kind("repair") == [] and "REPAIR none" in world.std_digest_lines()
    status = world.status_repair()
    assert status.code == 0 and status.lines == ["REPAIR none"], status


def test_s8_a_later_standing_pass_closes_the_repair(ran_std):
    world, run = ran_std("closes")
    assert run.code == 0, run
    words = [x["word"] for x in world.history_kind("repair")]
    assert words == ["MEMORY_REPAIR open", "MEMORY_REPAIR closed"], words
    status = world.status_repair()
    assert status.code == 0 and status.lines == ["REPAIR none"], status
    assert "REPAIR none" in world.std_digest_lines()


def repair_world(make_world, *, later_pass=False):
    world = make_world(standing=True)
    lines = [world.std_line("2026-W44", 96.0), world.std_line("2026-W45", 90.0, word="miss"),
             {"kind": "repair", "word": "MEMORY_REPAIR open", "set": W.STD, "week": "2026-W45"}]
    if later_pass:
        lines.append(world.std_line("2026-W46", 96.0))
    world.plant_history(*lines)
    return world


def test_s8_status_repair_exits_1_while_open_and_0_after_a_planted_standing_pass(make_world):
    world = repair_world(make_world)
    open_ = world.status_repair()
    assert open_.code == 1 and open_.lines == ["REPAIR open since 2026-W45"], open_
    closed = repair_world(make_world, later_pass=True).status_repair()
    assert closed.code == 0 and closed.lines == ["REPAIR none"], closed


def test_s8_the_owners_decision_id_closes_it_and_is_recorded(make_world):
    world = repair_world(make_world)
    run = world.status_repair("--residual", "DEC-1")
    assert run.code == 0 and run.lines == ["REPAIR residual DEC-1"], run
    last = world.history()[-1]
    assert last["kind"] == "repair" and last["word"] == "MEMORY_REPAIR residual" and last["decision"] == "DEC-1", last
    after = world.status_repair()
    # I8: a plain `status --repair` has two outputs only; the residual closes the repair, so it is `REPAIR none`, exit 0
    assert after.code == 0 and after.lines == ["REPAIR none"], after


@pytest.mark.parametrize("bad", ["DEC-x", "DEC-", "1", "dec-1", "DEC-1 DEC-2"])
def test_s8_a_malformed_decision_id_is_usage_and_writes_nothing(make_world, bad):
    world = repair_world(make_world)
    assert world.status_repair().code == 1, "the repair is open: the subcommand answers"
    before = world.history()
    run = world.status_repair("--residual", bad)
    assert run.code == 4, run
    assert world.history() == before


def test_s8_status_repair_with_no_history_is_none_and_since_is_required_without_repair(make_world):
    world = make_world(standing=True)
    none = world.status_repair()
    assert none.code == 0 and none.lines == ["REPAIR none"], none
    run = world.drive("status", "--sets-root", str(world.sets), "--repo", str(world.repo))
    assert run.code == 4, "--since is required only without --repair"
