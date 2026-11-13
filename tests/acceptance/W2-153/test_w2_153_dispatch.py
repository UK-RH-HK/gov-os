"""S2, F1 and F2 for the dispatcher's lead line (``governance/project/orchestration/tools/dispatch/launch_now.sh``).

The script names its paths absolutely (the CLI, the orchestrator folder, the worktrees folder), so each case runs a
copy with those paths pointed into a temporary folder (``w2_153_support.DispatchBed``); the CLI there is the stand-in
that records its arguments and its working folder. The baseline for F2 is integrate's script at the baseline commit,
run on the same bed.
"""

from __future__ import annotations

import os

import pytest

import w2_153_support as support
from w2_153_support import FLAG, DispatchBed


@pytest.fixture
def bed(tmp_path):
    return DispatchBed(tmp_path / "bed")


def _started(run: dict) -> dict:
    assert run["exit"] == 0, f"the lead line ended with exit {run['exit']}\nstderr: {run['stderr']}"
    assert len(run["calls"]) == 1, f"the stand-in CLI was called {len(run['calls'])} times, not once"
    return run["calls"][0]


def _resolved(call: dict, value: str) -> str:
    return os.path.realpath(os.path.join(call["cwd"], value))


def test_s2_the_lead_line_passes_the_flag_with_role_lead_md(bed):
    call = _started(bed.run(support.current_dispatch_script()))
    values = support.flag_values(call["argv"])
    assert len(values) == 1, f"{FLAG} must be passed once: {support.shown(call['argv'])}"
    assert _resolved(call, values[0]) == os.path.realpath(bed.expected_path()), (
        f"{FLAG} names {values[0]} (from {call['cwd']}), not the lead tree's .claude/templates/role-lead.md")


def test_f1_the_lead_line_refuses_when_role_lead_md_is_missing(bed):
    """The other seven copies are there; only role-lead.md is missing."""
    os.unlink(bed.expected_path())
    run = bed.run(support.current_dispatch_script())
    assert run["exit"] != 0, f"the lead line did not refuse (exit 0); the stand-in CLI was called {len(run['calls'])} time(s)"
    assert run["calls"] == [], f"a lead session was started ({len(run['calls'])} call(s))"


def _without_add_dirs(argv: list[str]) -> list[str]:
    """``argv`` with each ``--add-dir <value>`` pair taken out: the lead's own tests worktree and the runs root, added
    to the lead line after W2-153 by ACT-LEADS-ADD-DIR-1 (DEC-1161 (2)); W2-153's comparison is of everything else."""
    out, skip = [], False
    for arg in argv:
        if skip:
            skip = False
            continue
        if arg == "--add-dir":
            skip = True
            continue
        out.append(arg)
    return out


def test_f2_the_lead_line_is_integrate_s_but_for_the_one_flag(bed):
    ours = _started(bed.run(support.current_dispatch_script()))
    theirs = _started(bed.run(support.baseline_dispatch_script()))
    assert ours["cwd"] == theirs["cwd"], f"the lead starts in {ours['cwd']}, integrate's in {theirs['cwd']}"
    mine = support.without_flag(_without_add_dirs(ours["argv"]))
    assert mine == theirs["argv"], f"the lead line changed beyond the one flag\nthis tree: {mine}\nintegrate: {theirs['argv']}"


def test_f2_guard_integrate_s_lead_line_starts_on_the_same_bed_without_the_flag(bed):
    """The baseline is what F2 compares against: integrate's script starts the stand-in in the lead's tree, with
    the lead's settings and no template flag."""
    call = _started(bed.run(support.baseline_dispatch_script()))
    assert os.path.realpath(call["cwd"]) == os.path.realpath(bed.tree)
    assert support.flag_values(call["argv"]) == []
    assert any(support.DISPATCH_TICKET in arg and "orchestrator" in arg for arg in call["argv"]), call["argv"]
