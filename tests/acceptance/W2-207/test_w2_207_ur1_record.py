"""UR-1: one daily record, one row per session, at ~/.gov-os/usage/<D>.json."""

from __future__ import annotations

import w2_207_support as s

DAY = "2026-11-24"


def plant_scenario(env):
    repo = env.repo("alpha")
    other = env.repo("beta")
    m = env.msg
    env.launch(repo, "S1", "engineer")
    env.transcript(repo, "S1", [
        m(repo, "S1", "m1", s.ts(DAY, "10:00:00"), "m-a", 2, 334, 155144, 574),
        m(repo, "S1", "m2", s.ts(DAY, "10:05:00"), "m-a", 3, 100, 200000, 0),
    ])
    env.transcript(repo, "S1", [
        m(repo, "S1", "h1", s.ts(DAY, "10:10:00"), "m-a", 1, 10, 100, 10, True),
    ], helper="hx", agent_type="reviewer")
    env.transcript(other, "S2", [m(other, "S2", "c1", s.ts(DAY, "11:00:00"), "m-a", 4, 6, 1000, 0)])
    env.cto("S2")
    env.transcript(other, "S3", [m(other, "S3", "u1", s.ts(DAY, "12:00:00"), "m-a", 7, 8, 0, 100)])
    return repo, other


def rows_by_session(rec):
    return {r["session"]: r for r in rec["rows"]}


def test_ur1_daily_writes_one_row_per_session_with_role_tokens_peak_and_cost(env):
    repo, other = plant_scenario(env)
    r = env.daily(DAY)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = env.record(DAY)
    assert rec["date"] == DAY and rec["timezone"] == "UTC"
    assert rec["price_table"]["date"] == "2026-11-01" and rec["price_table"]["path"]
    rows = rows_by_session(rec)
    assert set(rows) == {"S1", "S1/agent-hx", "S2", "S3"}

    a = rows["S1"]
    assert (a["repository"], a["role"], a["model"]) == (str(repo), "engineer", "m-a")
    assert (a["input"], a["output"], a["cache_read"], a["cache_creation"]) == (5, 434, 355144, 574)
    assert a["context_peak"] == 200003  # max(2+155144+574, 3+200000+0)
    assert a["cost_usd"] == 0.366744
    assert a["role_source"] and "unknown" not in a["role_source"]

    h = rows["S1/agent-hx"]
    assert (h["repository"], h["role"]) == (str(repo), "reviewer")
    assert (h["input"], h["output"], h["cache_read"], h["cache_creation"]) == (1, 10, 100, 10)
    assert h["context_peak"] == 111 and h["cost_usd"] == 0.00036

    c = rows["S2"]
    assert (c["repository"], c["role"], c["context_peak"], c["cost_usd"]) == (str(other), "cto", 1004, 0.00116)

    u = rows["S3"]
    assert u["role"] == "unknown" and "unknown" in u["role_source"]
    assert (u["context_peak"], u["cost_usd"]) == (107, 0.00073)


def test_ur1_the_record_is_machine_state_nothing_is_written_under_the_root_or_repositories(env):
    plant_scenario(env)
    before = env.tree(env.root, env.repos)
    assert env.daily(DAY).returncode == 0
    assert (env.usage_dir / f"{DAY}.json").is_file()
    assert env.tree(env.root, env.repos) == before


def test_ur1_rerunning_a_day_rewrites_the_same_rows(env):
    plant_scenario(env)
    assert env.daily(DAY).returncode == 0
    first = env.record(DAY)
    assert env.daily(DAY).returncode == 0
    second = env.record(DAY)
    assert second["rows"] == first["rows"] and second["totals"] == first["totals"]
    assert sorted(p.name for p in env.usage_dir.iterdir()) == [f"{DAY}.json"]


def test_ur1_a_session_with_two_models_gives_two_rows(env):
    repo = env.repo("alpha")
    env.launch(repo, "S1", "engineer")
    env.transcript(repo, "S1", [
        env.msg(repo, "S1", "m1", s.ts(DAY), "m-a", 1, 1, 1, 1),
        env.msg(repo, "S1", "m2", s.ts(DAY, "10:01:00"), "m-b", 10, 100, 1000, 100),
    ])
    assert env.daily(DAY).returncode == 0
    rows = {r["model"]: r for r in env.record(DAY)["rows"]}
    assert set(rows) == {"m-a", "m-b"}
    assert rows["m-b"]["cost_usd"] == 0.00102 and rows["m-b"]["context_peak"] == 1110
    assert rows["m-a"]["cost_usd"] == 0.000036


def test_ur1_a_bare_root_succeeds_with_the_shipped_table(env):
    # supersedes "a missing price table exits 2" (UR-6: the table ships with the product)
    plant_scenario(env)
    (env.root / "governance" / "project" / "usage-prices.yaml").unlink()
    r = env.daily(DAY)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (env.usage_dir / f"{DAY}.json").is_file()


def test_ur1_a_model_with_no_price_has_cost_null_and_is_named_unpriced(env):
    repo = env.repo("alpha")
    env.launch(repo, "S1", "engineer")
    env.transcript(repo, "S1", [
        env.msg(repo, "S1", "m1", s.ts(DAY), "mystery-model", 5, 5, 5, 5),
        env.msg(repo, "S1", "m2", s.ts(DAY, "10:01:00"), "m-a", 1, 1, 1, 1),
    ])
    r = env.daily(DAY)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = env.record(DAY)
    rows = {x["model"]: x for x in rec["rows"]}
    assert rows["mystery-model"]["cost_usd"] is None
    assert rows["mystery-model"]["input"] == 5
    assert rows["m-a"]["cost_usd"] == 0.000036
    assert "unpriced" in (r.stdout + r.stderr + (env.usage_dir / f"{DAY}.json").read_text()).lower()
