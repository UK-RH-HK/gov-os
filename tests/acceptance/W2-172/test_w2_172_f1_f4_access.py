"""F1 and F4 (and S1's ``figures`` step, S7's reading by child only): what the driver opens and what it writes.

F1: the driver never builds, opens, lists or stats a path under the sets root, and never names a folder under it on a
command line. A file-access spy (``spy/sitecustomize.py``: a ``sys.addaudithook`` on every Python child) logs, with the
process's full command line, each ``subprocess.Popen`` and each ``open``, ``os.listdir``, ``os.scandir`` and ``os.walk`` of a
path under the sets root; the cases keep the lines of the driver's own process (``python -m gov.memaudit run``). The spy is
shown to see: the planted launch script's process, which does write the set into the sets root, has such lines. (``os.stat``
is not an audited event: the spy cannot show a stat; the Popen lines and the printed lines are the other witnesses.)

F4: the crontab, the path map, the guard, ``.claude/`` and the walls' template of the repository are not written: ``git
status`` of the planted repository after a whole run is empty, their bytes are the committed ones, and the planted
``crontab`` first on every child's PATH is never called.

``figures`` (item 6): one JSON line of numbers and fixed words from ``FIGURES.json`` and ``DROPS.json``, a missing file a
``null``, exit 0, nothing written. Its keys are not fixed by the Interface: the cases do not name them.
"""

from __future__ import annotations

import json
import subprocess

import pytest

import w2_172_checks as C
import w2_172_world as W
from w2_172_world import W171


def test_f1_the_driver_opens_lists_and_names_nothing_under_the_sets_root(ran):
    world, run = ran("words")
    C.assert_ok(run)
    mine = C.driver_events(world)
    assert any(e["kind"] == "hello" for e in mine), "the spy was loaded in the driver's process"
    popens = [e for e in mine if e["kind"] == "popen"]
    assert len(popens) >= len(W.STEPS), "the driver's own children, as the spy saw them"
    touched = [e for e in mine if e["kind"] in ("open", "os.listdir", "os.scandir", "os.walk")]
    assert touched == [], f"the driver itself touched the sets root: {touched[:3]}"
    root = str(world.sets)
    for e in popens:
        for arg in e["arg"]:
            assert root + "/" not in arg, e["arg"]  # no path under the sets root on any command it starts
        if C.classify(e["arg"]):  # the launch and subcommand lines (a `git show` names the repository's own walls' template)
            # Rewrite-Reason: the merge queue's clone path (21:19 ejection): the argv's first element is `sys.executable`
            # (the interpreter's own path may hold a word); `W.forbidden_in_argv` skips that exact element and no other.
            assert W.forbidden_in_argv(e["arg"]) == [], e["arg"]


def test_f1_the_spy_does_see_what_the_launch_script_writes_into_the_sets_root(ran):
    """The control of the case above: the planted launch script's own process opens files under the sets root."""
    world, run = ran("words")
    C.assert_ok(run)
    stub = [e for e in world.spy() if len(e["argv"]) > 1 and e["argv"][1].endswith("launch_stub.py")]
    assert any(e["kind"] in ("open", "os.listdir", "os.scandir") for e in stub), \
        "a spy that sees nothing proves nothing"
    other = [e for e in world.spy() if e["argv"][1:3] == ["-m", "gov.memaudit"] and e["argv"][3] == "preflight"
             and e["kind"] in ("open", "os.listdir", "os.scandir")]
    assert other, "W2-170's code, run as a child, reads the set: the sets root is reached through the children only"


def test_f1_the_driver_runs_nothing_but_the_launch_script_and_the_subcommands_and_git(ran):
    world, run = ran("clean")
    C.assert_ok(run)
    for e in C.driver_events(world):
        if e["kind"] != "popen":
            continue
        args = e["arg"]
        known = C.classify(args) is not None or args[0].endswith("git") or args[0] == "git" \
            or args[0] == str(world.gate_stub) or args[0].endswith("gate_stub.py")
        assert known, f"an unexpected command: {args[:4]}"


def test_f4_a_whole_run_leaves_the_repositorys_guard_path_map_claude_and_template_as_committed(ran):
    world, run = ran("words")
    C.assert_ok(run)
    assert world.git_status() == "", world.git_status()
    for rel, digest in world.guarded_files().items():
        committed = subprocess.run(["git", "-C", str(world.repo), "show", f"HEAD:{rel}"], capture_output=True,
                                   check=True).stdout
        assert digest == W.sha(committed), rel
    done = subprocess.run(["git", "-C", str(world.link), "status", "--porcelain", "--untracked-files=no"],
                          capture_output=True, text=True, env=W171.git_env(world.home))
    assert done.returncode == 0 and done.stdout == "", "the store link's checkout is as it was"
    assert (world.repo / ".claude" / "settings.json").read_text() == '{"planted": true}\n'


def test_f4_neither_the_driver_nor_the_wrapper_calls_the_crontab(ran, make_world):
    world, run = ran("clean")
    C.assert_ok(run)
    assert world.crontab_calls() == ""
    shimmed = make_world(link=False)
    shimmed.plant_plan("shim_plan.json", {"due_lines": ["MODE weekly", "DUE yes next 2026-11-16", "REASON start"],
                                          "due_exit": 0, "run_exit": 0})
    shimmed.wrapper(env={"GOV_MEMAUDIT_PYTHON": str(shimmed.shim), "GOV_MEMAUDIT_SETS_ROOT": str(shimmed.sets)})
    assert shimmed.crontab_calls() == ""


def test_f4_the_driver_writes_only_under_its_own_folder_and_the_children_write_theirs(ran, make_world):
    """Nothing outside ``<R>`` is the driver's: a run that stops at its first launch changes, outside the state logs of the
    planted programs (and git's own folders), only ``<R>``."""
    world = make_world()
    world.plan_launch({"writer-1": [{"exit": 10}]})
    before = W171.snapshot(world.base)
    run = world.go()
    assert run.code == 2, run
    after = W171.snapshot(world.base)
    state = str(world.state)
    mem = str(world.mem)
    new = {p for p in after if p not in before or before[p] != after[p]}
    stray = sorted(p for p in new if not p.startswith(state) and not p.startswith(mem) and "/.git" not in p)
    assert stray == [], stray


# -- `figures` ----------------------------------------------------------------------------------------------------------
def test_s1_figures_prints_one_json_line_of_numbers_and_writes_nothing(ran):
    world, run = ran("words")
    C.assert_ok(run)
    before = W171.snapshot(world.sets, world.mem)
    out = world.drive("figures", "--sets-root", str(world.sets), "--audit", world.audit, spy=False)
    assert out.code == 0, out
    assert len(out.out.splitlines()) == 1, out.out
    doc = json.loads(out.out)
    assert isinstance(doc, dict) and doc
    for word in W171.UNIQUE:
        assert word not in out.out + out.err
    assert W171.snapshot(world.sets, world.mem) == before, "figures reads and writes nothing"


def test_s1_figures_of_an_audit_with_no_files_is_a_json_line_and_exit_0(make_world):
    world = make_world()
    out = world.drive("figures", "--sets-root", str(world.sets), "--audit", "memory-audit-20260101", spy=False)
    assert out.code == 0, out
    assert len(out.out.splitlines()) == 1 and isinstance(json.loads(out.out), dict), out.out


# -- the command line ----------------------------------------------------------------------------------------------------
def test_s1_the_runs_folder_is_never_a_flag_and_the_sets_root_is_required(make_world):
    world = make_world()
    assert world.drive("run", "--help").code == 0, "the subcommand exists"
    assert world.drive("run", "--repo", str(world.repo)).code == 4, "--sets-root is required"
    run = world.drive(*world.run_args(), "--runs-dir", str(world.runs))
    assert run.code == 4, "the runs folder is $GOV_INDEP_RUNS_DIR, never a flag"
    assert world.stub_calls() == [] and world.starts() == []


def test_s1_run_prints_through_say_only_never_a_path_under_the_sets_root(make_world):
    """A refusal names the sets root nowhere in the folder form; every printed line is one of the forms of the Interface.

    Rewrite-Reason: the merge queue's clone path (21:19 ejection). The word grep goes through ``W.forbidden_in_text``: a
    whitespace-delimited token equal to ``sys.executable`` alone is skipped, a word anywhere else still fails."""
    world = make_world()
    world.audits_log.unlink()
    run = world.go()
    assert run.code == 1, run
    for line in (run.out + run.err).splitlines():
        assert str(world.sets) + "/" not in line and W.forbidden_in_text(line) == [], line
