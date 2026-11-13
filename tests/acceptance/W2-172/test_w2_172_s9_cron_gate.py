"""S9 and F4's wrapper half: the cron wrapper ``memaudit_cron.sh`` and the gate (Interface item 8).

The wrapper runs ``due`` and starts the cycle only when an audit is due, with the pinned interpreter
(``GOV_MEMAUDIT_PYTHON``, else ``/usr/bin/python3``) and the sets root (``GOV_MEMAUDIT_SETS_ROOT``, else
``$HOME/gov-os-eval``); not due: no start, exit 0; due: ``run --sets-root <root> --gate-cmd <gate>`` and the exit of ``run``;
one JSON line a run in ``<R>/cron.log``: ``{"at","due","mode","reason","started","exit"}``. It holds no ``crontab``
(the crontab is class (O), an ACT): ``grep -c crontab`` of the wrapper is 0 and a planted ``crontab`` first on PATH is
never called. The planted interpreter (``py_shim.py``) answers ``-m gov.memaudit due|run`` from a plan and logs the calls.

The gate: before steps 7, 8 and 11 (``measure``, ``judge``, ``pool``) ``run`` calls ``--gate-cmd`` with no arguments (exit 0
open, else busy), polling every ``GOV_MEMAUDIT_GATE_POLL_S`` seconds for at most ``GOV_MEMAUDIT_GATE_MAX_S`` (default 3600)
and then stopping ``STOPPED <step> gate busy`` (a stop at that step, exit 2). The busy case runs the real driver without
``GOV_MEMAUDIT_NOW`` (the store's commit is planted at the real time) so that the wait can run out by the seam or the real
clock; the wrapper does not override the 3600 default. Readings: the wrapper's default gate is the product's
``gov resources --check`` (O2). PKG-W2-172-TESTS-1 GATE-1 (a) (DEC-1112 (3)): the driver splits ``--gate-cmd``'s value with
``shlex.split`` and runs the words as given, so that default works as it is; "called with no arguments" reads "run as its
words" (a one-word value, as the planted gate is, gets no arguments). The cases give the wrapper a stub gate through
``GOV_MEMAUDIT_GATE`` and test the default only by the wrapper's text (``resources --check``).
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from datetime import datetime, timedelta, timezone

import pytest

import w2_172_checks as C
import w2_172_world as W
from w2_172_digest import by_word

SCRIPT = W.WRAPPER
DUE_LINES = ["MODE monthly", "DUE yes next 2026-11-16", "REASON start"]
NOT_DUE_LINES = ["MODE monthly", "DUE no next 2026-12-01", "REASON stable"]


def shim_world(make_world, **plan):
    world = make_world(link=False)
    world.plant_plan("shim_plan.json", plan)
    return world


def env_for(world, **extra):
    env = {"GOV_MEMAUDIT_PYTHON": str(world.shim), "GOV_MEMAUDIT_SETS_ROOT": str(world.sets)}
    env.update(extra)
    return env


def cron_lines(world):
    return world.jsonl_file(world.mem / "cron.log")


def test_s9_not_due_it_starts_nothing_exits_0_and_appends_one_line(make_world):
    world = shim_world(make_world, due_lines=NOT_DUE_LINES, due_exit=1)
    done = world.wrapper(env=env_for(world))
    assert done.returncode == 0, (done.stdout, done.stderr)
    calls = world.shim_calls()
    assert [c["sub"] for c in calls] == ["due"], calls
    assert "--sets-root" in calls[0]["argv"] and calls[0]["argv"][calls[0]["argv"].index("--sets-root") + 1] == str(world.sets)
    lines = cron_lines(world)
    assert len(lines) == 1 and set(lines[0]) == {"at", "due", "mode", "reason", "started", "exit"}, lines
    assert (lines[0]["due"], lines[0]["started"], lines[0]["exit"]) == (False, False, 0)
    assert (lines[0]["mode"], lines[0]["reason"]) == ("monthly", "stable")
    assert datetime.fromisoformat(lines[0]["at"].replace("Z", "+00:00"))


def test_s9_due_and_idle_it_starts_the_cycle_with_the_gate_and_exits_with_runs_code(make_world):
    world = shim_world(make_world, due_lines=DUE_LINES, due_exit=0, run_lines=["STARTED"], run_exit=0)
    done = world.wrapper(env=env_for(world, GOV_MEMAUDIT_GATE=str(world.gate_stub)))
    assert done.returncode == 0, (done.stdout, done.stderr)
    calls = world.shim_calls()
    assert [c["sub"] for c in calls] == ["due", "run"], calls
    argv = calls[1]["argv"]
    assert argv[argv.index("--sets-root") + 1] == str(world.sets)
    assert argv[argv.index("--gate-cmd") + 1] == str(world.gate_stub), "GOV_MEMAUDIT_GATE is the gate's command"
    lines = cron_lines(world)
    assert len(lines) == 1 and (lines[0]["due"], lines[0]["started"], lines[0]["exit"]) == (True, True, 0)
    assert (lines[0]["mode"], lines[0]["reason"]) == ("monthly", "start")


def test_s9_the_wrapper_exits_with_the_code_run_exits_with(make_world):
    world = shim_world(make_world, due_lines=DUE_LINES, due_exit=0, run_exit=2)
    done = world.wrapper(env=env_for(world))
    assert done.returncode == 2, (done.stdout, done.stderr)
    lines = cron_lines(world)
    assert (lines[0]["due"], lines[0]["started"], lines[0]["exit"]) == (True, True, 2), lines


def test_s9_one_line_a_run_is_appended(make_world):
    world = shim_world(make_world, due_lines=NOT_DUE_LINES, due_exit=1)
    for _ in range(3):
        assert world.wrapper(env=env_for(world)).returncode == 0
    assert len(cron_lines(world)) == 3


def test_s9_the_wrapper_defaults_to_the_sets_root_under_home(make_world):
    world = shim_world(make_world, due_lines=NOT_DUE_LINES, due_exit=1)
    done = world.wrapper(env={"GOV_MEMAUDIT_PYTHON": str(world.shim)})
    assert done.returncode == 0, (done.stdout, done.stderr)
    argv = world.shim_calls()[0]["argv"]
    assert argv[argv.index("--sets-root") + 1] == str(world.home / "gov-os-eval")


def test_s9_the_wrapper_writes_nothing_but_the_cron_log_and_calls_no_crontab(make_world):
    world = shim_world(make_world, due_lines=DUE_LINES, due_exit=0, run_exit=0)
    before = W.W171.snapshot(world.base)
    done = world.wrapper(env=env_for(world))
    assert done.returncode == 0
    after = W.W171.snapshot(world.base)
    new = {p for p in after if p not in before}
    changed = {p for p in before if p in after and before[p] != after[p]}
    allowed = {str(world.mem) + "/", str(world.mem / "cron.log")}
    state = str(world.state)
    assert {p for p in new | changed if not p.startswith(state)} <= allowed | {str(world.runs / "indep") + "/"}, \
        sorted(new | changed)
    assert world.crontab_calls() == ""


def test_s9_the_wrapper_holds_no_crontab_edit(tmp_path):
    assert SCRIPT.is_file(), "governance/project/orchestration/tools/memaudit_cron.sh"
    counted = subprocess.run(["grep", "-c", "crontab", str(SCRIPT)], capture_output=True, text=True)
    assert counted.stdout.strip() == "0", counted
    assert subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True).returncode == 0


def test_s9_the_wrapper_names_its_interpreter_sets_root_and_gate_by_the_interfaces_variables():
    text = SCRIPT.read_text()
    assert text.startswith("#!") and "bash" in text.splitlines()[0]
    for needle in ("GOV_MEMAUDIT_PYTHON", "/usr/bin/python3", "GOV_MEMAUDIT_SETS_ROOT", "gov-os-eval",
                   "GOV_MEMAUDIT_GATE", "resources --check", "--gate-cmd", "cron.log"):
        assert needle in text, needle
    assert "gate_check.py" not in text, "the product's own check, not the CTO's scratch script (O2)"


# -- the gate, through the real driver -----------------------------------------------------------------------------------
def real_clock_world(make_world):
    """A world on the real clock: the store's commit is an empty commit on main dated an hour ago, the planted set carries
    its sha, and the audit is named by today's UTC date."""
    world = make_world(now=None, link=False)
    when = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(timespec="seconds")
    world.repo_git("commit", "-q", "--allow-empty", "-m", "fresh", date=when)
    fresh = world.repo_git("rev-parse", "HEAD").strip()
    world.make_link(fresh, head=fresh)
    world.set_now(W.iso(datetime.now(timezone.utc)))
    world.fresh = fresh
    return world


def test_s9_a_busy_gate_stops_the_measure_with_gate_busy_after_the_wait_runs_out(make_world):
    world = real_clock_world(make_world)
    world.plan_launch({"writer-1": [{"rewrite_commit": world.fresh}]})
    world.plan_gate(1)  # busy, always
    started = time.monotonic()
    run = world.go(gate=world.gate_stub, now=None, env={"GOV_MEMAUDIT_GATE_MAX_S": "2", "GOV_MEMAUDIT_GATE_POLL_S": "1"})
    waited = time.monotonic() - started
    assert run.code == 2, run
    assert "STOPPED measure gate busy" in run.lines, run.out
    assert not (world.run_dir / "DECLARATION.json").exists() and not (world.run_dir / "USED").exists(), \
        "no measure step was started while the gate was busy"
    assert not (world.audit_dir / "measure.out").exists() or (world.audit_dir / "measure.out").read_text() == ""
    calls = world.gate_calls()
    assert 2 <= len(calls) <= 8 and all(c["argv"] == [] for c in calls), calls
    assert waited < 120, "the wait is bounded"
    counts = world.counts()
    assert counts["stop"]["step"] == "measure" and counts["stop"]["used"] is False, counts
    words = by_word(world.digest(), strict=False)
    assert words["STOP"].group(0).startswith("STOP measure ") and words["OWNER"]["word"] == "OWNER none"
    assert run.lines[-12:] == world.digest()
    assert world.history() == []
    assert world.gov_calls() == []


def test_s9_a_gate_that_opens_lets_the_measure_start_once(make_world):
    """Busy twice, then open: the driver polled three times, then ran ``measure`` (which here refuses at once: the store's
    head is not the audit commit, so nothing is searched)."""
    world = real_clock_world(make_world)
    world.make_link(world.fresh, head="0" * 40)
    world.plan_launch({"writer-1": [{"rewrite_commit": world.fresh}]})
    world.plan_gate(1, 1, 0)
    run = world.go(gate=world.gate_stub, now=None, env={"GOV_MEMAUDIT_GATE_MAX_S": "30", "GOV_MEMAUDIT_GATE_POLL_S": "1"})
    assert run.code == 2 and "STOPPED measure 1" in run.lines, run
    assert len(world.gate_calls()) == 3, world.gate_calls()


def test_s9_the_gate_is_asked_before_measure_judge_and_pool_and_before_nothing_else(ran):
    world, run = ran("clean")
    C.assert_ok(run)
    calls = world.gate_calls()
    assert len(calls) == 3 and all(c["argv"] == [] for c in calls), calls
    # what stood in the audit's folder of the sets root at each call: before measure, before judge, before pool
    assert [bool(c["seen"].get("DECLARATION.json")) for c in calls] == [False, True, True]
    assert [bool(c["seen"].get("FIGURES.json")) for c in calls] == [False, False, True]
    assert [bool(c["seen"].get("POOL.json")) for c in calls] == [False, False, False]


def test_s9_without_a_gate_command_no_gate_is_asked(make_world):
    world = make_world()
    world.make_link(head="0" * 40)
    world.plan_launch({})
    run = world.go()  # no --gate-cmd: run by hand, no gate
    assert run.code == 2 and "STOPPED measure 1" in run.lines, run
    assert world.gate_calls() == []
