"""W2-171's fixtures: stages of the planted world, built once per session and copied whole for each test.

Stages (each a folder copied with ``shutil.copytree``; no test sees another's writes):

* ``prepared``: W2-170's world with the set of 40 pre-flighted and voided (``DROPS.json`` written): ``measure`` starts here;
  ``prepared37``: the same with three questions rejected by the checker (a set of 37), for the scaled bar.
* ``measured:<scenario>``: ``prepared`` with the scenario's plans, after ``measure`` (exit 0, ``COUNTS`` written).
* ``judged:<scenario>``: ``measured:<scenario>`` after ``judge`` (exit 0, ``FIGURES.json`` written).

A stage records each tool run's exit code and output in ``stage.json`` beside the world, read back as
``world.staged["measure"]`` / ``["judge"]`` (``code``, ``out``, ``err``). The fakes find their plans and logs through
``W171_STATE`` (the world's ``state/``), so a copied world never reads another world's plan.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

import pytest

import w2_171_scenario as S
import w2_171_world as W


@pytest.fixture(scope="session", autouse=True)
def _children_import_this_tree_s_gov(tmp_path_factory):
    """Every child process imports ``gov`` from this tree's ``src/``; a run that would test other code fails here,
    before any case."""
    home = tmp_path_factory.mktemp("w2-171-home")
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=W.child_env(home),
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().startswith(str(W.SRC) + "/"), (done.stdout, str(W.SRC))


def _record(world: W.World, key: str, run: W.Run) -> None:
    path = world.base / "stage.json"
    data = json.loads(path.read_text()) if path.exists() else {}
    data[key] = {"code": run.code, "out": run.out, "err": run.err}
    path.write_text(json.dumps(data))


@pytest.fixture(scope="session")
def stages(tmp_path_factory):
    cache = {}

    def get(key: str):
        if key in cache:
            return cache[key]
        if key in ("prepared", "prepared37"):
            base = tmp_path_factory.mktemp(f"w2-171-{key}") / "w"
            W.build(base)
            W.World(base).prepare(drops=("q27", "q33", "q34") if key == "prepared37" else ())
        else:
            kind, name = key.split(":")
            own = "prepared37" if S.SCENARIOS[name].dropped else "prepared"
            source = get(own if kind == "measured" else f"measured:{name}")
            base = tmp_path_factory.mktemp(f"w2-171-{kind}-{name}") / "w"
            shutil.copytree(source, base, symlinks=True)
            world = W.World(base)
            if kind == "measured":
                S.SCENARIOS[name].install(world)
                run = world.measure()
                assert run.code == 0, (key, run)
                _record(world, "measure", run)
            else:
                run = world.judge()
                assert run.code == 0, (key, run)
                _record(world, "judge", run)
        cache[key] = base
        return base

    return get


@pytest.fixture
def make_world(stages, tmp_path):
    count = [0]

    def make(stage: str = "prepared") -> W.World:
        count[0] += 1
        dest = tmp_path / f"world{count[0]}"
        shutil.copytree(stages(stage), dest, symlinks=True)
        world = W.World(dest)
        stage_file = dest / "stage.json"
        world.staged = json.loads(stage_file.read_text()) if stage_file.exists() else {}
        return world

    return make


@pytest.fixture
def world(make_world) -> W.World:
    return make_world("prepared")
