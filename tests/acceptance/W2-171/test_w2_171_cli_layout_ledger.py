"""Interface 1 to 3: the five subcommands' usage and flags, the layout under ``runs/<audit>/`` and the ledger's events.

Commands, exit codes (0 ok, 1 refused with a printed code, 2 stopped, 3 used, 4 usage) and flags are tested as the
callers use them; the layout and the ledger's events are read back from a whole run (``judged:five``).
"""

from __future__ import annotations

import os
import re
import stat

import pytest

import w2_171_scenario as S
import w2_171_world as W

SUBCOMMANDS = {"measure": ("--kept", "--gov", "--store", "--commit", "--repo", "--decision"),
               "judge": ("--claude", "--projection", "--resume", "--repo", "--gov"),
               "classes": ("--sets-root", "--audit"),
               "pool": ("--seed", "--repo", "--gov"),
               "pool-import": ("--sets-root",)}
ISO = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}Z$")


def test_help_prints_usage_for_the_command_and_each_new_subcommand(world):
    top = world.run("--help")
    assert top.code == 0 and top.lines, top
    for name in SUBCOMMANDS:
        assert name in top.out, f"{name} is not among the subcommands the usage lists"
        run = world.run(name, "--help")
        assert run.code == 0 and run.lines, (name, run)
        for flag in SUBCOMMANDS[name]:
            assert flag in run.out, (name, flag)


@pytest.mark.parametrize("args", [
    ("measure",), ("judge", "--sets-root", "{sets}"), ("pool", "--sets-root", "{sets}", "--audit", W.AUDIT, "--seed", "abc"),
    ("measure", "--sets-root", "{sets}", "--audit", W.AUDIT, "--kept", "x"),
    ("judge", "--sets-root", "{sets}", "--audit", W.AUDIT, "--projection", "lots"),
    ("judge", "--sets-root", "{sets}", "--audit", W.AUDIT, "--resume", "now"),
    ("classes", "--sets-root", "{sets}", "--audit", "memory-audit-1"),
    ("pool-import", "--audit", W.AUDIT), ("pool", "--sets-root", "{sets}", "--audit", W.AUDIT, "--nope"),
])
def test_a_usage_fault_is_exit_4(world, args):
    assert world.run(args[0], "--help").code == 0, "the subcommand exists (a missing one is exit 4 as well)"
    before = len(world.ledger())
    run = world.run(*[a.format(sets=world.sets) for a in args])
    assert run.code == 4, run
    assert len(world.ledger()) == before


@pytest.mark.parametrize("sub,flag", [("measure", "--repo"), ("measure", "--gov"), ("measure", "--store"),
                                      ("judge", "--claude"), ("judge", "--gov"), ("pool", "--gov"), ("pool", "--repo")])
def test_a_flag_naming_a_folder_under_the_sets_root_is_exit_4_and_nothing_runs(world, sub, flag):
    base = {"measure": world.measure_flags(), "judge": world.judge_flags(), "pool": world.pool_flags()}[sub]
    args = list(base)
    args[args.index(flag) + 1] = str(world.sets / "fixtures" / "evaluation" / "x" / "thing")
    S.SCENARIOS["five"].install(world)
    assert world.run(sub, "--help").code == 0, "the subcommand exists (a missing one is exit 4 as well)"
    run = world.run(sub, *args)
    assert run.code == 4, run
    assert world.gov_calls() == [] and world.claude_calls() == []
    assert not (world.run_dir / "USED").exists() and not (world.run_dir / "attempt-1").exists()


def test_the_layout_under_the_run_folder(make_world):
    world = make_world("judged:five")
    run = world.run_dir
    for name in ("PREFLIGHT.json", "DROPS.json", "DECLARATION.json", "USED", "ledger.jsonl", "COUNTS", "misses.jsonl",
                 "FIGURES.json", "gov"):
        assert (run / name).is_file(), name
    wrapper = run / "gov"
    assert stat.S_IMODE(wrapper.stat().st_mode) == 0o700
    first = wrapper.read_text(encoding="utf-8").splitlines()[0]
    assert first.startswith("#!") and "python" in first, "the wrapper is a Python file"
    for name in ("control-1", "attempt-1"):
        for part in ("kept", "measure.txt", "measure.err", "ms"):
            assert (run / name / part).exists(), (name, part)
    for part in ("ENDED", "DONE"):
        assert (run / "attempt-1" / part).is_file(), part
    assert not (run / "attempt-1" / "FAULT").exists() and not (run / "STOPPED").exists()
    assert not (run / "ready").exists(), "the probe's result is a ledger event, not a file"
    assert (run / "COUNTS").read_text().strip() == "attempt-1"
    assert (run / "reader" / "plan.json").is_file() and len(list((run / "reader").glob("q*.json"))) == 40
    assert len(list((run / "control-1" / "kept").glob("*.json"))) == 40
    assert not [p for p in run.rglob("*") if p.name.endswith(".tmp")], "written whole by temporary name, then renamed"
    assert stat.S_IMODE(run.stat().st_mode) == 0o700


def test_the_ledger_events_have_item_3s_fields(make_world):
    world = make_world("judged:five")
    ledger = world.ledger()
    assert [e["seq"] for e in ledger] == list(range(1, len(ledger) + 1)), "seq consecutive"
    assert all(ISO.match(e["at"]) for e in ledger), "at is ISO UTC to the microsecond"
    by = {}
    for e in ledger:
        by.setdefault(e["event"], []).append(e)
    assert set(by) >= {"preflight", "declaration", "used", "ready", "control", "search", "attempt", "store", "counts",
                       "spend", "figures"}, sorted(by)
    ready = by["ready"]
    assert len(ready) == 1 and ready[0]["ok"] is True and ready[0]["why"] is None
    control = by["control"][0]
    assert {"k", "hit5", "of", "last", "last_audit", "ok"} <= set(control) and control["of"] == 40
    searches = by["search"]
    assert {"phase", "attempt", "call", "qid", "rc", "ms", "ok"} <= set(searches[0])
    phases = {p: [e for e in searches if e["phase"] == p] for p in ("ready", "control", "attempt", "later")}
    assert all(phases.values()) and {e["phase"] for e in searches} == set(phases)
    assert len(phases["ready"]) == 1 and len(phases["control"]) == 40
    kept = len(list((world.attempt_dir(1) / "kept").glob("*.json")))
    assert len(phases["attempt"]) == kept
    assert sorted(e["call"] for e in phases["attempt"]) == list(range(1, kept + 1)), "call is the kept number"
    assert all(e["qid"] is None for e in phases["attempt"]) and all(e["qid"] for e in phases["later"])
    assert all(isinstance(e["ms"], int) and e["ms"] >= 0 for e in searches)
    assert [(e["n"], e["state"], e["cause"]) for e in by["attempt"]] == [(1, "start", None), (1, "done", None)]
    store = by["store"][0]
    assert (store["n"], store["same"], store["sha256"]) == (1, True, W.sha_file(world.store))
    assert by["counts"][0]["attempt"] == "attempt-1"
    figures = by["figures"][0]
    assert {k: figures[k] for k in ("right", "wrong", "n", "passes")} == {"right": 35, "wrong": 2, "n": 40,
                                                                          "passes": True}
    order = [e["event"] for e in ledger]
    assert order.index("counts") < order.index("spend") < order.index("figures")


def test_the_ledger_after_a_whole_measure_ends_with_counts(world):
    S.SCENARIOS["five"].install(world)
    assert world.measure().code == 0
    ledger = world.ledger()
    assert ledger[-1]["event"] == "counts" and ledger[-1]["attempt"] == "attempt-1"
    assert os.path.exists(world.run_dir / "COUNTS")
