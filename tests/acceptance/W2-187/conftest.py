"""W2-187's fixtures.

* ``template`` (session): the planted world, built once (``w2_187_world.build_template``).
* ``make_world`` (test): a copy of the template for one test, with its store link; ``make_world(now=..., link=...)``.
* ``ran_std`` (session): ``ran_std("pass" | "five" | ...)`` runs one standing run once per session and returns
  ``(world, run)``; tests only read it (a test that must write copies it with ``copy_std``). The fixtures never assert:
  each test starts with ``assert run.code == 0`` so a missing ``standing run`` fails the test instead of erroring here.
* ``ran_fresh`` (session): a whole fresh audit (``python3 -m gov.memaudit run``) beside a planted live standing set.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

import pytest

import w2_187_world as W
from w2_187_world import S171, W171


@pytest.fixture(scope="session", autouse=True)
def _children_import_this_tree_s_gov(tmp_path_factory):
    """Every child imports ``gov`` from this tree's ``src/``; a run that would test other code fails here."""
    home = tmp_path_factory.mktemp("w2-187-home")
    env = {k: v for k, v in __import__("os").environ.items() if not k.startswith(("GOV_", "GIT_"))}
    env.update(HOME=str(home), PYTHONPATH=str(W.SRC), PYTHONDONTWRITEBYTECODE="1")
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=env, capture_output=True,
                          text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().startswith(str(W.SRC) + "/"), (done.stdout, str(W.SRC))


@pytest.fixture(scope="session")
def template(tmp_path_factory):
    base = tmp_path_factory.mktemp("w2-187-template") / "w"
    W.build_template(base)
    return base


def clean_paths(world: W.SW) -> None:
    """The precondition of the substring greps: no path the world builds, and that can appear on a printed line, holds a
    folder word of the sets root, ``hidden`` or one of the planted unique words."""
    for path in (world.sets, world.repo, world.link, world.stub, world.gov, world.claude, world.gate_stub, world.shim,
                 world.runs_env, world.state, world.home):
        text = str(path) + "/"
        bad = [w for w in (*W172.FORBIDDEN, *W.UNIQUE) if w in text]
        assert not bad, f"{path} holds {bad}: rename the test or its folder (path hygiene)"


W172 = W.W172


def build(template, dest, *, now=W.NOW, link=True, std=True) -> W.SW:
    shutil.copytree(template, dest, symlinks=True)
    world = W.SW(dest, now or W.NOW)
    world.set_now(now)
    if link:
        world.make_link()
    if std:
        world.write_x_plan(store_commit=world.audit_commit)
    clean_paths(world)
    return world


@pytest.fixture
def make_world(template, tmp_path):
    count = [0]

    def make(*, now=W.NOW, link=True, scenario=None, std=None, standing=False) -> W.SW:
        """``scenario`` a fresh scenario name (W2-171's), ``std`` a standing scenario name, ``standing`` plants the live
        standing set's record."""
        count[0] += 1
        world = build(template, tmp_path / f"w{count[0]}", now=now, link=link)
        if scenario:
            S171.SCENARIOS[scenario].install(world)
        if std:
            W.scenario(std).install(world)
        if standing or std:
            world.plant_standing()
        return world

    return make


# -- the standing runs, once each ---------------------------------------------------------------------------------------
# name -> how the world is made: the scenario, the standing history planted before the run, the broken anchors, flags
STD_RUNS = {
    "pass": dict(scenario="pass", gate=True, other={"q10"}, spy=True),
    "pass76": dict(scenario="pass76"),
    "five": dict(scenario="five", history=[("2026-W45", 96.0, "pass")], maintain=True),
    "drop3": dict(scenario="pass", broken=["q05", "q17", "q42"]),
    "thin69": dict(scenario="pass", broken=[f"q{k:02d}" for k in range(1, 12)]),
    "live70": dict(scenario="pass", broken=[f"q{k:02d}" for k in range(1, 11)]),
    "open_boundary": dict(scenario="five", history=[("2026-W44", 98.75, "pass")]),
    "open_twice": dict(scenario="five", history=[("2026-W43", 96.0, "pass"), ("2026-W44", 90.0, "miss")]),
    "closes": dict(scenario="pass", history=[("2026-W44", 96.0, "pass"), ("2026-W45", 90.0, "miss")],
                   repair_open="2026-W45"),
}


def make_std_world(template, dest, spec: dict) -> W.SW:
    world = build(template, dest)
    sc = W.scenario(spec["scenario"])
    if spec.get("broken"):
        world.break_anchors(spec["broken"])
        sc.live = W.live_without(spec["broken"])
    world.plant_standing()
    lines = [world.std_line(week, pct, word=word) for week, pct, word in spec.get("history", [])]
    if spec.get("repair_open"):
        lines.append({"kind": "repair", "word": "MEMORY_REPAIR open", "set": W.STD, "week": spec["repair_open"]})
    if lines:
        world.plant_history(*lines)
    sc.install(world, other_commit={S171.search_words("q10"): "f" * 40} if spec.get("other") else None)
    world.sc = sc
    return world


@pytest.fixture(scope="session")
def ran_std(template, tmp_path_factory):
    cache = {}

    def get(name: str):
        if name not in cache:
            spec = STD_RUNS[name]
            world = make_std_world(template, tmp_path_factory.mktemp(f"w2-187-std-{name}") / "w", spec)
            if spec.get("maintain"):
                world.maintain_run = world.maintain()
            env = {"W187_FNSPY": str(world.state / "fn_spy.jsonl")} if spec.get("spy") else None
            run = world.standing_run(gate=world.gate_stub if spec.get("gate") else None, env=env)
            cache[name] = (world, run)
        return cache[name]

    return get


@pytest.fixture
def copy_std(ran_std, tmp_path):
    """A writable copy of a standing run (its store link made again in the copy)."""
    def make(name: str) -> W.SW:
        source, _ = ran_std(name)
        dest = tmp_path / f"copy-{name}"
        shutil.copytree(source.base, dest, symlinks=True)
        world = W.SW(dest, source.now)
        world.make_link()
        world.sc = source.sc
        for log in ("launch_calls.jsonl", "gate_calls.jsonl", "spy.jsonl", "gov_calls.jsonl", "claude_calls.jsonl",
                    "gov_x_calls.jsonl"):
            (world.state / log).unlink(missing_ok=True)
        return world

    return make


# -- the fresh audits beside a live standing set -----------------------------------------------------------------------
FRESH_RUNS = {
    # name -> (fresh scenario, the planted standing history: pcts, oldest first)
    "fitted": ("w187_miss4", [96.0, 96.0, 96.0, 96.0]),                # S 96.0, F 90.0
    "fitted_edge": ("w187_miss4", [95.0, 95.0, 95.0, 95.0]),           # S - F = 5.0 exactly
    "near_fitted": ("w187_miss4", [94.5, 95.0, 95.0, 95.0]),           # S 94.875, F 90.0: 4.875, no flag
    "stale": ("clean", [90.0, 90.0, 90.0, 90.0]),                      # F - S = 10
    "stale_edge": ("w187_miss1", [92.5, 92.5, 92.5, 92.5]),            # F 97.5, S 92.5: exactly 5
    "none": ("w187_miss3", [95.0, 95.0, 95.0, 95.0]),                  # S 95.0, F 92.5
    "not_yet": ("clean", [96.0, 96.0]),                                # two weekly figures
}


@pytest.fixture(scope="session")
def ran_fresh(template, tmp_path_factory):
    cache = {}

    def get(name: str):
        if name not in cache:
            scenario, pcts = FRESH_RUNS[name]
            world = build(template, tmp_path_factory.mktemp(f"w2-187-fresh-{name}") / "w")
            world.plant_standing()
            weeks = [f"2026-W{w}" for w in (41, 42, 43, 44, 45)][-len(pcts):]
            world.plant_history(*[world.std_line(w, p) for w, p in zip(weeks, pcts)])
            S171.SCENARIOS[scenario].install(world)
            world.plan_launch({})
            world.plant_earlier(W171.EARLIER, pool={"n": 2, "hit5": 0, "full": 0})
            run = world.go(gate=world.gate_stub, env={"W187_FNSPY": str(world.state / "fn_spy.jsonl")})
            cache[name] = (world, run)
        return cache[name]

    return get


@pytest.fixture
def copy_fresh(ran_fresh, tmp_path):
    """A writable copy of a fresh audit beside its standing set (its store link made again in the copy)."""
    def make(name: str) -> W.SW:
        source, _ = ran_fresh(name)
        dest = tmp_path / f"copy-{name}"
        shutil.copytree(source.base, dest, symlinks=True)
        world = W.SW(dest, source.now)
        world.make_link()
        for log in ("launch_calls.jsonl", "gate_calls.jsonl", "spy.jsonl", "gov_calls.jsonl", "claude_calls.jsonl",
                    "gov_x_calls.jsonl"):
            (world.state / log).unlink(missing_ok=True)
        return world

    return make
