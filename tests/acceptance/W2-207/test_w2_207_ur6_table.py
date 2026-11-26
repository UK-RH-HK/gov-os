"""UR-6: the price table is found from anywhere: shipped with the product, a repository's own overrides it."""

from __future__ import annotations

from pathlib import Path

import yaml

import w2_207_support as s

DAY = "2026-11-24"
MODELS = ("claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5-2")
SHIPPED = s.SRC / "gov" / "_shipped" / "governance" / "project" / "usage-prices.yaml"
COMMITTED = Path(__file__).resolve().parents[3] / "governance" / "project" / "usage-prices.yaml"
# input, 5m write, 1h write, cache read, output
WANT = {
    "claude-opus-5-5": (4, 5, 8, 0.2, 20),
    "claude-sonnet-5-5": (2, 2.5, 4, 0.1, 10),
    "claude-haiku-5-5": (0.1, 0.125, 0.2, 0.01, 0.5),
    "claude-fable-5-2": (8, 10, 16, 0.2, 40),
}


def test_ur6_a_bare_root_works_with_the_shipped_table_for_the_real_models(env):
    env.bare_root()
    repo = env.git_repo("alpha")
    for n, model in enumerate(MODELS):
        sid = f"S{n}"
        env.transcript(repo, sid, [env.msg(repo, sid, "m1", s.ts(DAY), model, 1000000, 0, 0, 0)])
    r = env.daily(DAY)
    assert r.returncode == 0, r.stdout + r.stderr
    got = {x["model"]: x["cost_usd"] for x in env.record(DAY)["rows"]}
    for model in MODELS:
        assert abs(got[model] - WANT[model][0]) < 1e-6, (model, got[model])


def test_ur6_the_shipped_file_holds_the_figures_and_equals_the_committed_table(env):
    assert SHIPPED.is_file(), SHIPPED
    assert SHIPPED.read_bytes() == COMMITTED.read_bytes()
    models = yaml.safe_load(SHIPPED.read_text())["models"]
    for model, (i, w5, w1, cr, o) in WANT.items():
        m = models[model]
        assert (m["input"], m["cache_write_5m"], m["cache_write_1h"], m["cache_read"], m["output"]) == (i, w5, w1, cr, o)


def test_ur6_a_repository_table_overrides_the_shipped_one(env):
    env.prices("date: 2026-11-24\nmodels:\n  claude-opus-5-5: {input: 1, output: 1, cache_read: 1, cache_creation: 1}\n")
    repo = env.git_repo("alpha")
    env.transcript(repo, "S1", [env.msg(repo, "S1", "m1", s.ts(DAY), "claude-opus-5-5", 1000000, 0, 0, 0)])
    assert env.daily(DAY).returncode == 0
    assert abs(env.record(DAY)["rows"][0]["cost_usd"] - 1.0) < 1e-6
