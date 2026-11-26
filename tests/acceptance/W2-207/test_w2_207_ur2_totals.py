"""UR-2: totals equal the sum of their rows; the plan's reading beside them."""

from __future__ import annotations

import pytest
import w2_207_support as s
from test_w2_207_ur1_record import DAY, plant_scenario

LINE_LATE = "week (all models)=19% (resets Nov 29, 9am (Europe/London));week (Fable)=0% (resets Nov 29, 9am (Europe/London)); last 24h: x"


def test_ur2_every_total_equals_the_sum_of_its_rows(env):
    repo, other = plant_scenario(env)
    # a second model and a second repository role, so the four groupings differ
    env.launch(repo, "S4", "qa")
    env.transcript(repo, "S4", [env.msg(repo, "S4", "q1", s.ts(DAY, "13:00:00"), "m-b", 100, 50, 10, 1)])
    assert env.daily(DAY).returncode == 0
    rec = env.record(DAY)
    assert len(rec["rows"]) == 5
    s.assert_totals_match(rec)
    t = rec["totals"]
    assert set(t["by_repository"]) == {str(repo), str(other)}
    assert set(t["by_role"]) == {"engineer", "reviewer", "cto", "unknown", "qa"}
    assert set(t["by_model"]) == {"m-a", "m-b"}
    assert f"{repo}|qa" in t["by_repository_role"]
    # by hand: the engineer's session is $0.366744 and it is the whole of alpha|engineer
    assert t["by_repository_role"][f"{repo}|engineer"]["cost_usd"] == pytest.approx(0.366744, abs=1e-6)
    assert t["by_role"]["engineer"]["output"] == 434


def test_ur2_the_plan_reading_is_the_last_line_of_that_day(env):
    plant_scenario(env)
    env.usage_txt([
        "2026-11-23 23:00:00 week (all models)=10% (old)",
        "2026-11-24 09:00:00 week (all models)=12% (early)",
        f"2026-11-24 18:28:37 {LINE_LATE}",
        "2026-11-25 00:30:00 week (all models)=25% (next day)",
    ])
    assert env.daily(DAY).returncode == 0
    reading = env.record(DAY)["plan_reading"]
    assert "week (all models)=19%" in reading and "last 24h: x" in reading
    assert "early" not in reading and "next day" not in reading and "old" not in reading
    assert not reading.startswith("2026-11-24")  # the text after the timestamp


@pytest.mark.parametrize("planted", ["other-day-only", "no-file"])
def test_ur2_a_day_with_no_usage_line_reads_unread(env, planted):
    plant_scenario(env)
    if planted == "other-day-only":
        env.usage_txt(["2026-11-23 18:00:00 week (all models)=10% (old)"])
    assert env.daily(DAY).returncode == 0
    rec = env.record(DAY)
    assert rec["plan_reading"] == "unread"
    s.assert_totals_match(rec)
