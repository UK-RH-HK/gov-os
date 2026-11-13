"""Premise guards: the planting does what the other tests say it does. These are GREEN today by design; they cover no KPI
line. If one goes red, the planted project (not the dispatcher) is wrong, and every red below it means nothing."""

from __future__ import annotations

import json

import pytest

import w2_121_support as support
from w2_121_support import GIB


def test_premise_planted_machine_has_the_gate_open(project):
    reading = project.gate_reading()
    assert reading["open"] is True, reading


@pytest.mark.parametrize("change, word", [({"mem_gib": 1.5}, "memory"), ({"disk_free_gib": 1}, "disk"),
                                          ({"load": (30.0, 30.0, 30.0)}, "load")])
def test_premise_planted_machine_can_shut_the_gate(project, change, word):
    project.set_machine(**change)
    reading = project.gate_reading()
    assert reading["open"] is False and any(word in r for r in reading["reasons"]), reading


def test_premise_planted_lead_carries_the_launchers_marker(project):
    from gov.launch.launcher import build_lead_settings

    settings = build_lead_settings(project.root, "DAEO-a1")
    pid = project.plant_lead("DAEO-a1")
    cmdline = (project.proc / str(pid) / "cmdline").read_bytes().split(b"\0")
    carried = json.loads(cmdline[cmdline.index(b"--settings") + 1])
    assert carried["env"]["GOV_ROLE"] == settings["env"]["GOV_ROLE"] == "orchestrator"
    assert carried["env"]["GOV_TICKET"] == settings["env"]["GOV_TICKET"] == "DAEO-a1"


def test_premise_planted_processes_are_read_by_the_gates_own_reader(project):
    from gov.resources import machine

    pid = project.plant_lead("DAEO-a2", rss_bytes=GIB)
    project.plant_process(["tail", "-f", "DAEO-a2"])
    import os
    old = os.environ.get("GOV_RESOURCES_PROC")
    os.environ["GOV_RESOURCES_PROC"] = str(project.proc)
    try:
        table = machine.processes()
    finally:
        if old is None:
            del os.environ["GOV_RESOURCES_PROC"]
        else:
            os.environ["GOV_RESOURCES_PROC"] = old
    assert pid in table and table[pid]["rss"] == GIB and "DAEO-a2" in table[pid]["cmdline"]


def test_premise_claim_layouts_in_git(project):
    both = project.add_ticket(1, claim="both")
    integ_only = project.add_ticket(2, claim="integration_only")
    wt_only = project.add_ticket(3, claim="worktree_only")

    def at(ref, entry):
        return support.git(project.root, "show", f"{ref}:.tickets/{entry.ticket}.md")

    assert "status: in_progress" in at("integ", both) and "status: in_progress" in at("work/" + both.w2, both)
    assert "status: in_progress" in at("integ", integ_only) and "status: open" in at("work/" + integ_only.w2, integ_only)
    assert "status: open" in at("integ", wt_only) and "status: in_progress" in at("work/" + wt_only.w2, wt_only)
    assert support.git(project.wt(both), "status", "--porcelain") == ""
    dirty = project.add_ticket(4, dirty=True)
    assert support.git(project.wt(dirty), "status", "--porcelain").endswith("M README.md")
    untracked = project.add_ticket(5, untracked=True)
    assert support.git(project.wt(untracked), "status", "--porcelain", "--untracked-files=no") == ""
