"""S11: the schedule's code (Interface I11).

``memaudit_cron.sh --repo <dir>`` first asks ``standing live``. With a live set (exit 0) it runs ``due`` and ``due --fresh``,
then ``maintain`` when either is due, ``standing run --gate-cmd`` when ``due``, ``maintain`` once more when that run's last line
ends ``misses``, and ``run --gate-cmd`` when ``due --fresh``, in that order; any other answer is today's path (``due``, then
``run``, W2-172's S9 cases). The interpreter is a planted shim (``py_shim187.py``) that answers each call from a plan and logs
its key, argv and cwd. ``cron.log`` is ``<key folder>/cron.log`` (the ``KEY`` line ``standing live`` prints), else
``$RUNS/indep/memaudit/cron.log``; its line keeps the six keys; the wrapper's exit is the last started step's. A9's
``memory_sets.walls_act`` writes ACT.md's step 6, the repository's cron line (Mondays 21:00), as text for the operator: no
crontab is called.

Readings: ``--repo`` is given to ``standing live`` (Interface: ``standing live --repo``); every call runs with the repository as
its working directory.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

import w2_187_world as W

KEY = "repo-0123abcd"
DUE_YES, DUE_NO = ["MODE weekly", "DUE yes next 2026-11-16", "REASON start"], ["MODE monthly", "DUE no next 2026-12-01", "REASON stable"]
FRESH_YES, FRESH_NO = ["MODE fresh", "DUE yes next 2026-11-16", "REASON 28d"], ["MODE fresh", "DUE no next 2026-12-14", "REASON wait"]


def plan(*, standing=True, fresh=True, misses=False, live=True, key=True, standing_exit=0, run_exit=0):
    head = [f"KEY {KEY}"] if key else []
    return {
        "standing live": {"lines": head + [f"LIVE {W.STD}" if live else "LIVE none"], "exit": 0 if live else 1},
        "due": {"lines": DUE_YES if standing else DUE_NO, "exit": 0 if standing else 1},
        "due --fresh": {"lines": FRESH_YES if fresh else FRESH_NO, "exit": 0 if fresh else 1},
        "maintain": {"lines": ["MAINTAIN 1 store x 2 layout x 3 links 0 4 unindexed 0 5 not_found 0 second 0 6 reanchor 0"], "exit": 0},
        "standing run": {"lines": [f"STANDING 2026-W47 right {75 if misses else 80} of 80: {'misses' if misses else 'passes'}"],
                         "exit": standing_exit},
        "run": {"lines": ["STARTED"], "exit": run_exit},
    }


def go(make_world, spec, *, args=(), env=None, cwd=None, gate=False):
    world = make_world(link=False)
    world.plant_plan("shim187_plan.json", spec)
    shim = world.base / "bin" / "py_shim187"
    extra = {"GOV_MEMAUDIT_GATE": str(world.gate_stub)} if gate else {}
    e = world.child_env(spy=False, extra={"GOV_MEMAUDIT_PYTHON": str(shim), "GOV_MEMAUDIT_SETS_ROOT": str(world.sets),
                                          **extra, **(env or {})})
    done = subprocess.run(["bash", str(W.WRAPPER), *args], cwd=str(cwd or world.repo), env=e, capture_output=True, text=True,
                          timeout=300)
    return world, done


def keys(world):
    return [c["key"] for c in world.jsonl("shim187_calls.jsonl")]


def cron_lines(world, folder=None):
    return world.jsonl_file((folder or world.runs_env / "indep" / "memaudit" / KEY) / "cron.log")


@pytest.mark.parametrize("standing,fresh,misses,expected", [
    (True, True, True, ["standing live", "due", "due --fresh", "maintain", "standing run", "maintain", "run"]),
    (True, True, False, ["standing live", "due", "due --fresh", "maintain", "standing run", "run"]),
    (True, False, True, ["standing live", "due", "due --fresh", "maintain", "standing run", "maintain"]),
    (True, False, False, ["standing live", "due", "due --fresh", "maintain", "standing run"]),
    (False, True, False, ["standing live", "due", "due --fresh", "maintain", "run"]),
    (False, False, False, ["standing live", "due", "due --fresh"]),
])
def test_s11_the_wrapper_runs_the_pass_the_standing_run_and_the_fresh_cycle_in_that_order_when_due(make_world, standing, fresh,
                                                                                                   misses, expected):
    world, done = go(make_world, plan(standing=standing, fresh=fresh, misses=misses))
    assert done.returncode == 0, (done.stdout, done.stderr)
    assert keys(world) == expected


def test_s11_nothing_runs_when_neither_is_due_and_one_line_is_logged_under_the_key_folder(make_world):
    world, done = go(make_world, plan(standing=False, fresh=False))
    assert done.returncode == 0, (done.stdout, done.stderr)
    assert keys(world) == ["standing live", "due", "due --fresh"]
    (line,) = cron_lines(world)
    assert set(line) == {"at", "due", "mode", "reason", "started", "exit"}, line
    assert (line["due"], line["started"], line["exit"]) == (False, False, 0)


def test_s11_a_run_is_logged_with_its_exit_and_the_wrapper_exits_with_the_last_started_steps(make_world):
    world, done = go(make_world, plan(standing=True, fresh=True, run_exit=2))
    assert done.returncode == 2, (done.stdout, done.stderr)
    (line,) = cron_lines(world)
    assert (line["due"], line["started"], line["exit"]) == (True, True, 2), line
    world, done = go(make_world, plan(standing=True, fresh=False, standing_exit=3))
    assert done.returncode == 3 and keys(world)[-1] == "standing run", (done.stdout, done.stderr)


def test_s11_the_gate_is_the_gate_command_of_both_runs_and_every_call_runs_in_the_repository(make_world):
    world, done = go(make_world, plan(standing=True, fresh=True), gate=True)
    assert done.returncode == 0, (done.stdout, done.stderr)
    calls = world.jsonl("shim187_calls.jsonl")
    assert {c["key"] for c in calls} >= {"standing run", "run"}, keys(world)
    for call in calls:
        assert call["cwd"] == os.path.realpath(world.repo), call
        if call["key"] in ("standing run", "run"):
            argv = call["argv"]
            assert argv[argv.index("--gate-cmd") + 1] == str(world.gate_stub), call
            assert argv[argv.index("--sets-root") + 1] == str(world.sets)


def test_s11_repo_names_the_repository_the_wrapper_enters_and_standing_live_is_asked_for_it(make_world, tmp_path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    world = make_world(link=False)
    world.plant_plan("shim187_plan.json", plan(standing=False, fresh=False))
    e = world.child_env(spy=False, extra={"GOV_MEMAUDIT_PYTHON": str(world.base / "bin" / "py_shim187"),
                                          "GOV_MEMAUDIT_SETS_ROOT": str(world.sets)})
    done = subprocess.run(["bash", str(W.WRAPPER), "--repo", str(world.repo)], cwd=str(elsewhere), env=e, capture_output=True,
                          text=True, timeout=300)
    assert done.returncode == 0, (done.stdout, done.stderr)
    calls = world.jsonl("shim187_calls.jsonl")
    assert calls and all(c["cwd"] == os.path.realpath(world.repo) for c in calls), calls
    live = calls[0]
    assert live["key"] == "standing live" and live["argv"][live["argv"].index("--repo") + 1] in (
        str(world.repo), os.path.realpath(world.repo)), live


def test_s11_with_no_live_set_it_is_todays_path_due_then_run(make_world):
    world, done = go(make_world, plan(live=False, standing=True), args=())
    assert done.returncode == 0 and keys(world) == ["standing live", "due", "run"], (keys(world), done.stderr)
    world, done = go(make_world, plan(live=False, standing=False))
    assert done.returncode == 0 and keys(world) == ["standing live", "due"], keys(world)


def test_s11_cron_log_falls_back_to_the_runs_folders_when_no_key_line_is_printed(make_world):
    world, done = go(make_world, plan(standing=False, fresh=False, key=False))
    assert done.returncode == 0, (done.stdout, done.stderr)
    assert keys(world) == ["standing live", "due", "due --fresh"]
    (line,) = cron_lines(world, world.runs_env / "indep" / "memaudit")
    assert set(line) == {"at", "due", "mode", "reason", "started", "exit"}


def test_s11_the_wrapper_names_no_crontab_and_calls_none(make_world):
    assert subprocess.run(["grep", "-c", "crontab", str(W.WRAPPER)], capture_output=True, text=True).stdout.strip() == "0"
    world, done = go(make_world, plan())
    assert done.returncode == 0 and world.crontab_calls() == ""


# -- A9's ACT package ----------------------------------------------------------------------------------------------------------
def act(world, *extra, out=None):
    out = out or world.base / "adoption-out"
    sets_root = str(world.base / "never-made-sets")
    env = world.child_env(spy=False, extra={"PYTHONPATH": str(W.SRC)})
    done = subprocess.run([sys.executable, str(W.HERE / "call_walls_act.py"), str(out), sets_root, "memory-audit-20261113", *extra],
                          cwd=str(world.work), env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stderr[-800:]
    return (out / "memory-audit" / "ACT-WALLS" / "ACT.md").read_text(encoding="utf-8"), sets_root


def step6(text: str) -> str:
    """Step 6 as text: its line and the lines after it up to the next numbered step."""
    lines = text.splitlines()
    starts = [i for i, x in enumerate(lines) if x.startswith("6.")]
    assert len(starts) == 1, f"ACT.md has one step 6: {text}"
    rest = []
    for x in lines[starts[0] + 1:]:
        if x[:1].isdigit():
            break
        rest.append(x)
    return " ".join([lines[starts[0]], *rest])


def test_s11_acts_step_6_is_the_repositorys_cron_line_for_mondays_at_21_and_is_never_installed(make_world):
    world = make_world(link=False)
    text, sets_root = act(world, str(world.repo))
    row = step6(text)
    assert "0 21 * * 1" in row and "Mondays 21:00" in row, row
    assert f"GOV_MEMAUDIT_SETS_ROOT={sets_root}" in row, row
    assert f"governance/project/orchestration/tools/memaudit_cron.sh --repo {world.repo}" in row, row
    for n in "12345":
        assert any(x.startswith(f"{n}. ") for x in text.splitlines()), f"step {n} is still there"
    assert world.crontab_calls() == "" and not os.path.exists(sets_root), "text only: no crontab read, no folder made"


def test_s11_without_a_repo_the_cron_line_names_the_git_top_level_of_the_adoption_folder(make_world):
    world = make_world(link=False)
    text, _ = act(world, out=world.repo / "adoption-out")
    row = step6(text)
    assert f"memaudit_cron.sh --repo {world.repo}" in row or f"memaudit_cron.sh --repo {os.path.realpath(world.repo)}" in row, row
    assert world.crontab_calls() == ""
