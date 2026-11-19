"""S11: the steps are on the CLI. One planted world (W2-171's, Gov OS's shape, Gov OS's file by the trial form) is
driven twice, by ``python3 -m gov.memaudit`` and by ``gov memaudit``: the same lines and the same exit codes."""

from __future__ import annotations

import json
import re
import subprocess

import pytest

import w2_204_stages as ST
import w2_204_support as K

NAMES = ("preflight", "void", "declare", "measure", "judge", "figures", "brief", "deliver", "check", "fresh", "scan")
EXPECTED = {"preflight": 0, "void": 0, "measure": 0, "declare": 3, "judge": 0, "figures": 0, "usage": 4}


@pytest.mark.parametrize("step", ST.GOV_OS_STEPS)
def test_s11_both_entries_end_a_step_with_the_same_exit_code_and_lines(stage, step):
    run = stage("govos")
    module, cli = run[f"module:{step}"], run[f"cli:{step}"]
    assert module.code == cli.code == EXPECTED[step], (step, module, cli)
    assert module.lines and module.lines == cli.lines, (step, module, cli)


def test_s11_the_lines_are_the_steps_own(stage):
    """The lines both entries print are the product's, not a shared usage error."""
    run = stage("govos")
    assert run["cli:preflight"].last == "PRE-FLIGHT: every check as expected", run["cli:preflight"]
    assert run["cli:void"].last == "DROPS: kept 40 dropped 0", run["cli:void"]
    assert run["cli:declare"].lines == ["USED"], run["cli:declare"]
    assert any(x.startswith("VERDICT right end to end 40 of 40") for x in run["cli:judge"].lines), run["cli:judge"]
    assert json.loads(run["cli:figures"].last)["verdict"]["right"] == 40, run["cli:figures"]
    assert run["cli:usage"].lines == ["ERROR: UsageError"], run["cli:usage"]


def _help(entry: str, tmp_path) -> K.Call:
    home = tmp_path / "home"
    home.mkdir()
    argv = [*K.ENTRIES[entry], "--help"]
    done = subprocess.run(argv, cwd=tmp_path, capture_output=True, text=True, timeout=120, env=K.W171.child_env(home))
    return K.Call(done.returncode, done.stdout, done.stderr, argv)


@pytest.mark.parametrize("entry", ["cli", "module"])
def test_s11_help_lists_the_steps(entry, tmp_path):
    run = _help(entry, tmp_path)
    wanted = NAMES if entry == "cli" else [n for n in NAMES if n != "scan"]
    missing = [n for n in wanted if not re.search(rf"(?<![\w-]){n}(?![\w-])", run.out)]
    assert run.code == 0 and not missing, (missing, run)


def test_s11_the_exit_words_gain_waiting_5_and_keep_the_others():
    from gov.memaudit import EXIT
    assert EXIT == {"ok": 0, "refused": 1, "void": 2, "stopped": 2, "used": 3, "usage": 4, "waiting": 5}
