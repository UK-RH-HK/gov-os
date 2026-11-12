"""W2-172's fixtures.

* ``template`` (session): the planted world built once (``w2_172_world.build_template``).
* ``make_world`` (test): a copy of the template for one test, with its store link; ``make_world(now=..., link=...)``.
* ``ran`` (session): ``ran("words" | "clean" | "five37")`` runs one whole audit through ``python3 -m gov.memaudit run``
  once per session and returns ``(world, run)``; tests only read it (a test that must write copies it with
  ``copy_ran``). The fixture never asserts: each test starts with ``assert run.code == 0`` so a missing ``run`` fails the
  test instead of erroring in a fixture.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

import pytest

import w2_172_world as W
from w2_172_world import S171, W171


@pytest.fixture(scope="session", autouse=True)
def _children_import_this_tree_s_gov(tmp_path_factory):
    """Every child imports ``gov`` from this tree's ``src/``; a run that would test other code fails here."""
    home = tmp_path_factory.mktemp("w2-172-home")
    env = {k: v for k, v in __import__("os").environ.items() if not k.startswith(("GOV_", "GIT_"))}
    env.update(HOME=str(home), PYTHONPATH=str(W.SRC), PYTHONDONTWRITEBYTECODE="1")
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=env, capture_output=True,
                          text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().startswith(str(W.SRC) + "/"), (done.stdout, str(W.SRC))


@pytest.fixture(scope="session")
def template(tmp_path_factory):
    base = tmp_path_factory.mktemp("w2-172-template") / "w"
    W.build_template(base)
    return base


def clean_paths(world: W.World) -> None:
    """The precondition of S1/F1's substring grep: no path that can appear on a printed command line holds a folder
    word of the sets root (nor ``hidden``, ``say``'s own refusal word)."""
    for path in (world.sets, world.repo, world.link, world.stub, world.gov, world.claude, world.gate_stub, world.shim,
                 W.SRC, sys.executable):
        text = str(path) + "/"
        bad = [w for w in W.FORBIDDEN if w in text]
        assert not bad, f"{path} holds {bad}: rename the test or its folder (path hygiene)"


@pytest.fixture
def make_world(template, tmp_path):
    count = [0]

    def make(*, now=W.NOW, link=True, scenario=None, link_commit=None) -> W.World:
        count[0] += 1
        dest = tmp_path / f"w{count[0]}"
        shutil.copytree(template, dest, symlinks=True)
        world = W.World(dest, now or W.NOW)
        world.set_now(now)
        if link:
            world.make_link(link_commit)
        if scenario:
            S171.SCENARIOS[scenario].install(world)
        clean_paths(world)
        return world

    return make


# -- the whole audits, run once ----------------------------------------------------------------------------------------
# the plan of the planted launch script for each, and the earlier pool figure (the last audit's, planted)
RUNS = {
    # the five misses and the words: a first checker pass with a revision (so the two second-round steps run), a pool
    # that fell from the last audit's (a regression)
    "words": dict(scenario="words", plan={"checker-1": [{"revise": ["q05"]}]},
                  earlier_pool={"n": 2, "hit5": 2, "full": 2}),
    # no miss; a clean first pass; the pool as it was
    "clean": dict(scenario="clean", plan={}, earlier_pool={"n": 2, "hit5": 0, "full": 0}),
    # a set of 37 after the second checker pass rejected three; no earlier audit's pool figure
    "five37": dict(scenario="five37", plan={"checker-1": [{"revise": ["q27", "q33", "q34"]}],
                                            "checker-2": [{"reject": ["q27", "q33", "q34"]}]}, earlier_pool=None),
}


@pytest.fixture(scope="session")
def ran(template, tmp_path_factory):
    cache = {}

    def get(name: str):
        if name not in cache:
            spec = RUNS[name]
            dest = tmp_path_factory.mktemp(f"w2-172-ran-{name}") / "w"
            shutil.copytree(template, dest, symlinks=True)
            world = W.World(dest)
            world.make_link()
            clean_paths(world)
            S171.SCENARIOS[spec["scenario"]].install(world)
            world.plan_launch(spec["plan"])
            if spec["earlier_pool"] is not None:
                world.plant_earlier(W171.EARLIER, pool=spec["earlier_pool"])
            run = world.go(gate=world.gate_stub)
            cache[name] = (world, run)
        return cache[name]

    return get


@pytest.fixture
def copy_ran(ran, tmp_path):
    """A writable copy of a whole run (its store link made again in the copy)."""
    def make(name: str) -> W.World:
        source, _ = ran(name)
        dest = tmp_path / f"copy-{name}"
        shutil.copytree(source.base, dest, symlinks=True)
        world = W.World(dest, source.now)
        world.make_link()
        for name in ("launch_calls.jsonl", "gate_calls.jsonl", "spy.jsonl", "gov_calls.jsonl", "claude_calls.jsonl"):
            (world.state / name).unlink(missing_ok=True)
        return world

    return make
