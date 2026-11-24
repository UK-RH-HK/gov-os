"""UR-5: prices that match the plan's own counting (5-minute and 1-hour cache writes priced apart)."""

from __future__ import annotations

import w2_207_support as s

DAY = "2026-11-24"
OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"


def session_cost(rec, session):
    return sum(r["cost_usd"] for r in rec["rows"] if r["session"] == session or r["session"].startswith(session + "/"))


def plant_lead(env):
    repo = env.git_repo("lead-repo")
    env.launch(repo, "L1", "lead")
    env.transcript(repo, "L1", [
        env.msg_split(repo, "L1", "a1", s.ts(DAY, "10:00:00"), OPUS, 1000, 2000, 500000, 100000, 300000),
        env.msg_split(repo, "L1", "a2", s.ts(DAY, "10:05:00"), SONNET, 10000, 5000, 1000000, 0, 200000),
    ])
    # by hand per million tokens: opus 4/5/8/0.2/20 -> 3.044; sonnet 2/2.5/4/0.1/10 -> 0.97; sum 4.014
    env.lead_record("L1-lead", 4.014, {
        OPUS: {"inputTokens": 1000, "outputTokens": 2000, "cacheReadInputTokens": 500000,
               "cacheCreationInputTokens": 400000, "costUSD": 3.044},
        SONNET: {"inputTokens": 10000, "outputTokens": 5000, "cacheReadInputTokens": 1000000,
                 "cacheCreationInputTokens": 200000, "costUSD": 0.97},
    })
    return repo


def test_ur5_a_lead_session_costs_what_its_record_says_within_one_percent(env):
    env.bare_root()
    plant_lead(env)
    r = env.daily(DAY)
    assert r.returncode == 0, r.stdout + r.stderr
    got = session_cost(env.record(DAY), "L1")
    assert abs(got - 4.014) <= 0.01 * 4.014, got


def test_ur5_one_hour_writes_are_not_priced_as_five_minute_writes(env):
    env.bare_root()
    repo = env.git_repo("lead-repo")
    env.launch(repo, "L2", "lead")
    # 5m 100000 -> 0.5, 1h 300000 -> 2.4; a single 5m rate for all 400000 would give 2.0 for the writes
    env.transcript(repo, "L2", [env.msg_split(repo, "L2", "a1", s.ts(DAY), OPUS, 0, 0, 0, 100000, 300000)])
    assert env.daily(DAY).returncode == 0
    rows = [x for x in env.record(DAY)["rows"] if x["session"] == "L2"]
    assert len(rows) == 1
    row = rows[0]
    assert (row["cache_creation"], row["cache_creation_5m"], row["cache_creation_1h"]) == (400000, 100000, 300000)
    assert abs(row["cost_usd"] - 2.9) < 1e-6, row["cost_usd"]


def test_ur5_without_the_split_all_cache_creation_is_five_minute(env):
    env.bare_root()
    repo = env.git_repo("lead-repo")
    env.launch(repo, "L3", "lead")
    env.transcript(repo, "L3", [env.msg(repo, "L3", "a1", s.ts(DAY), OPUS, 0, 0, 0, 50000)])
    assert env.daily(DAY).returncode == 0
    row = [x for x in env.record(DAY)["rows"] if x["session"] == "L3"][0]
    assert (row["cache_creation"], row["cache_creation_5m"], row["cache_creation_1h"]) == (50000, 50000, 0)
    assert abs(row["cost_usd"] - 0.25) < 1e-6, row["cost_usd"]


def test_ur5_a_table_with_separate_write_prices_prices_each_kind(env):
    env.prices("date: 2026-11-24\nmodels:\n  m-a: {input: 0, output: 0, cache_read: 0, cache_write_5m: 5, cache_write_1h: 8}\n")
    repo = env.git_repo("alpha")
    env.transcript(repo, "S1", [env.msg_split(repo, "S1", "a1", s.ts(DAY), "m-a", 0, 0, 0, 1000000, 1000000)])
    assert env.daily(DAY).returncode == 0
    row = env.record(DAY)["rows"][0]
    assert abs(row["cost_usd"] - 13.0) < 1e-6, row["cost_usd"]


def test_ur5_the_old_single_cache_creation_key_prices_both_write_kinds(env):
    # the planted table of the older tests: m-a cache_creation 5 per million
    repo = env.git_repo("alpha")
    env.transcript(repo, "S1", [env.msg_split(repo, "S1", "a1", s.ts(DAY), "m-a", 0, 0, 0, 1000000, 1000000)])
    assert env.daily(DAY).returncode == 0
    row = env.record(DAY)["rows"][0]
    assert abs(row["cost_usd"] - 10.0) < 1e-6, row["cost_usd"]
