"""S5: the rule that tells active from stable is computed, never chosen (Interface items 1 and 9).

``python3 -m gov.memaudit due --sets-root <root>`` prints three lines, ``MODE weekly|monthly``, ``DUE yes|no next
<yyyy-mm-dd>`` and ``REASON <code>``, and exits 0 when due, 1 when not due, 4 on usage. Planted: git histories with
committer dates (``w2_172_git.DueRepo``: 100 non-excluded tracked paths, 10 excluded ones), ``HISTORY.jsonl``,
``STARTS.log`` and ``AUDITS.log`` (agreeing on the last audit's commit), and ``GOV_MEMAUDIT_NOW``.

* Weekly while fewer than 3 measured lines; monthly when the last 3 measured lines each have churn under 5 %, no
  retrieval path changed in the 28 days before, a verdict that passed and no pool regression, and no trigger holds.
* The triggers, computed at the store link's head ``H``: churn(H) of 10 % or more; a retrieval-glob path in
  ``git diff --name-only <last audit commit> H``; the last measured line's verdict below the bar; its pool regression.
* Due after 6 days (weekly) or 28 (monthly) since the last start; no start at all is due.

Readings: the reason ``start`` is the reason of a repository with no measured line at all; for one or two measured lines
the cases accept ``start`` or ``active`` (the Interface does not say which); ``active`` is the reason of three measured
lines of which one fails a condition while no trigger holds.
"""

from __future__ import annotations

import re

import pytest

import w2_172_git as G
from w2_172_world import NOW

DUE_LINE = re.compile(r"DUE (yes|no) next \d{4}-\d{2}-\d{2}")


def due(w, **kw):
    return w.due(**kw)


def lines_of(run):
    assert run.code in (0, 1), run
    lines = run.out.splitlines()
    assert len(lines) == 3, run.out
    assert lines[0] in ("MODE weekly", "MODE monthly"), lines
    assert DUE_LINE.fullmatch(lines[1]), lines
    assert re.fullmatch(r"REASON (start|stable|churn|retrieval|verdict|pool|active)", lines[2]), lines
    return lines


def expect(run, mode, reason, due_now):
    lines = lines_of(run)
    assert lines[0] == f"MODE {mode}", run
    assert lines[2] == f"REASON {reason}", run
    assert lines[1].startswith("DUE yes" if due_now else "DUE no"), run
    assert run.code == (0 if due_now else 1), run
    assert run.err == "" or "ERROR" not in run.err


def world(tmp_path, *, history=None, days=7.0, **repo):
    w = G.due_repo(tmp_path / "w", **repo)
    G.plant_state(w, history if history is not None else G.stable_history(w.l0), last_start_days=days)
    return w


# -- the start and the mode --------------------------------------------------------------------------------------------
def test_s5_with_no_audit_yet_it_is_weekly_and_due_for_the_start(tmp_path):
    w = G.due_repo(tmp_path / "w")
    G.plant_state(w, [], last_start_days=None)
    expect(w.due(), "weekly", "start", True)


@pytest.mark.parametrize("measured", [1, 2])
def test_s5_fewer_than_three_measured_lines_is_weekly(tmp_path, measured):
    w = G.due_repo(tmp_path / "w")
    G.plant_state(w, G.stable_history(w.l0)[:measured], last_start_days=7)
    run = w.due()
    lines = lines_of(run)
    assert lines[0] == "MODE weekly" and lines[2] in ("REASON start", "REASON active"), run.out


def test_s5_three_audits_each_stable_with_the_rest_met_is_monthly(tmp_path):
    w = world(tmp_path, days=10)
    expect(w.due(), "monthly", "stable", False)


def test_s5_only_measured_lines_count_and_only_the_last_three(tmp_path):
    w = G.due_repo(tmp_path / "w")
    bad = G.plant_history_line(w.l0, churn=0.30, passes=False, pool_regression=True, retrieval_28d=True)
    unmeasured = G.plant_history_line(w.l0, churn=0.0, measured=False, used=True)
    G.plant_state(w, [bad, *G.stable_history(w.l0), unmeasured], last_start_days=10)
    expect(w.due(), "monthly", "stable", False)


def test_s5_a_store_link_named_by_rebuild_yaml_on_the_main_line_is_the_default(tmp_path):
    w = world(tmp_path, days=10)
    w.commit({"governance/project/rebuild.yaml": f"integration_store: {w.link}\n"}, "2026-11-10T01:00:00+00:00",
             "the store's place")
    run = w.due(link=False)
    expect(run, "monthly", "stable", False)


# -- the four triggers, each alone ----------------------------------------------------------------------------------------
def test_s5_a_churn_of_40_percent_is_weekly_at_once(tmp_path):
    w = world(tmp_path, plain=40, days=7)
    expect(w.due(), "weekly", "churn", True)


@pytest.mark.parametrize("plain,mode,reason", [(10, "weekly", "churn"), (9, "monthly", "stable")])
def test_s5_churn_of_10_percent_or_more_is_the_trigger_9_is_not(tmp_path, plain, mode, reason):
    w = world(tmp_path, plain=plain, days=10)
    expect(w.due(), mode, reason, mode == "weekly")  # 10 days since the last start


def test_s5_the_paths_the_exclusion_file_names_never_count_in_the_churn(tmp_path):
    """All ten excluded paths and the exclusion file itself changed in the window: churn 0, not 10 % or more; and with 9
    plain paths changed besides, 9 % (not 19 %)."""
    w = world(tmp_path, excluded=10, days=10)
    expect(w.due(), "monthly", "stable", False)
    w2 = G.due_repo(tmp_path / "w-b", plain=9, excluded=10)
    G.plant_state(w2, G.stable_history(w2.l0), last_start_days=10)
    expect(w2.due(), "monthly", "stable", False)


@pytest.mark.parametrize("path", G.RETR)
def test_s5_a_change_to_a_retrieval_path_since_the_last_audit_is_weekly_at_once(tmp_path, path):
    w = world(tmp_path, retr_after=(path,), days=10)
    expect(w.due(), "weekly", "retrieval", True)


def test_s5_a_retrieval_change_before_the_last_audit_is_not_a_trigger(tmp_path):
    w = world(tmp_path, retr_before=2, days=10)
    expect(w.due(), "monthly", "stable", False)


def test_s5_a_last_verdict_below_the_bar_is_weekly_at_once(tmp_path):
    w = G.due_repo(tmp_path / "w")
    history = G.stable_history(w.l0)
    history[-1] = G.plant_history_line(w.l0, passes=False)
    G.plant_state(w, history, last_start_days=10)
    expect(w.due(), "weekly", "verdict", True)


def test_s5_a_last_pool_regression_is_weekly_at_once(tmp_path):
    w = G.due_repo(tmp_path / "w")
    history = G.stable_history(w.l0)
    history[-1] = G.plant_history_line(w.l0, pool_regression=True)
    G.plant_state(w, history, last_start_days=10)
    expect(w.due(), "weekly", "pool", True)


# -- the three audits' own conditions: a failing one keeps the rule weekly -----------------------------------------------------
@pytest.mark.parametrize("field,value", [("churn", 0.05), ("churn", 0.2), ("retrieval_28d", True),
                                         ("passes", False), ("pool_regression", True)])
def test_s5_one_of_the_last_three_audits_failing_a_condition_keeps_it_weekly(tmp_path, field, value):
    w = G.due_repo(tmp_path / "w")
    history = G.stable_history(w.l0)
    history[0] = G.plant_history_line(w.l0, **{field: value})  # the first of the three: no trigger of the last line
    G.plant_state(w, history, last_start_days=10)
    expect(w.due(), "weekly", "active", True)


def test_s5_churn_just_under_5_percent_in_each_of_the_three_is_stable(tmp_path):
    w = G.due_repo(tmp_path / "w")
    G.plant_state(w, [G.plant_history_line(w.l0, churn=0.0499) for _ in range(3)], last_start_days=10)
    expect(w.due(), "monthly", "stable", False)


# -- due at 5, 6, 27 and 28 days ----------------------------------------------------------------------------------------------
@pytest.mark.parametrize("days,due_now", [(5, False), (6, True)])
def test_s5_weekly_is_due_after_6_days_not_5(tmp_path, days, due_now):
    w = G.due_repo(tmp_path / "w", plain=40)  # weekly by churn
    G.plant_state(w, G.stable_history(w.l0), last_start_days=days)
    run = w.due()
    expect(run, "weekly", "churn", due_now)
    if not due_now:
        assert run.out.splitlines()[1] == "DUE no next 2026-11-11", "the 6th day after the last start"


@pytest.mark.parametrize("days,due_now", [(27, False), (28, True)])
def test_s5_monthly_is_due_after_28_days_not_27(tmp_path, days, due_now):
    w = world(tmp_path, days=days)
    run = w.due()
    expect(run, "monthly", "stable", due_now)
    if not due_now:
        assert run.out.splitlines()[1] == "DUE no next 2026-11-11", "the 28th day after the last start"


def test_s5_the_exit_code_is_4_on_usage(tmp_path):
    w = G.due_repo(tmp_path / "w")
    assert w.drive("due", "--help").code == 0, "the subcommand exists"
    assert w.drive("due").code == 4, "--sets-root is required"
    assert w.drive("due", "--sets-root", str(w.sets), "--no-such-flag").code == 4


@pytest.mark.parametrize("sub", ["run", "due", "baseline", "status"])
def test_s5_each_new_subcommand_has_a_help_that_exits_0(tmp_path, sub):
    w = G.due_repo(tmp_path / "w")
    run = w.drive(sub, "--help")
    assert run.code == 0 and run.out.strip(), run
    assert "--sets-root" in run.out
    assert str(w.sets) + "/" not in run.out
