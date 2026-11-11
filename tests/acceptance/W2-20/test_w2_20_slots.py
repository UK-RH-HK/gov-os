"""S7 and F4: the heavy-job slots, and no other ceiling.

S7: heavy jobs take a slot: a test run and a rebuild each wait for one of a configured number of machine-wide slots
(the number in the gate's configuration file); sessions, reviews and single-process runs take no slot and are gated
only by load, memory and disk; no other fixed ceiling on leads or sessions [DEC-979 item 1 D1, DEC-983, DEC-982]; a
rebuild excludes only another rebuild of the same tree (each tree its own lock), never every rebuild on the machine
[DEC-1001 (d), DEC-1003, SMART-WORK-2]. F4 (failure): any fixed ceiling on leads or sessions other than the
heavy-job slots (DEC-983).

A heavy job runs as ``gov resources --slot test|rebuild [--tree T] [--workers N] -- <command>`` (README, "Heavy
jobs"): it waits for a slot (and, for a rebuild, the tree's lock), runs the command, and gives the slot back; the
reading's ``slots`` is ``{"total", "held": [...]}``.
"""

from __future__ import annotations

import time

import pytest

import w2_20_support as support

STILL_WAITING_S = 3.0  # how long a waiting job is watched to show it has not started


def _assert_waits(machine, tag):
    time.sleep(STILL_WAITING_S)
    assert not machine.started(tag).exists(), f"{tag} started although no slot (or tree lock) was free"


@pytest.mark.parametrize("holder, waiter", [("test", "test"), ("test", "rebuild"), ("rebuild", "test")],
                         ids=["a test run waits for a test run", "a rebuild waits for a test run",
                              "a test run waits for a rebuild"])
def test_s7_a_heavy_job_waits_for_a_machine_wide_slot(machine, holder, waiter):
    """One slot; the holder runs in one repository and the waiter is asked from another (machine-wide)."""
    this, other = machine.repo("this-repo"), machine.repo("other-repo")
    machine.open_config(heavy_slots=1)
    machine.slot_job(this, holder, "first")
    machine.wait_started("first")

    slots = machine.read(this).get("slots")
    assert isinstance(slots, dict) and slots.get("total") == 1 and len(slots.get("held", [])) == 1, (
        f"the reading does not show the one slot held: {slots}")

    machine.slot_job(other, waiter, "second")
    _assert_waits(machine, "second")
    machine.release("first")
    machine.wait_started("second")
    machine.release("second")


def test_s7_the_number_of_slots_is_the_configuration_files(machine, repo):
    machine.open_config(heavy_slots=2)
    for tag in ("one", "two"):
        machine.slot_job(repo, "test", tag)
    machine.wait_started("one")
    machine.wait_started("two")
    machine.slot_job(repo, "test", "three")
    _assert_waits(machine, "three")
    slots = machine.read(repo).get("slots")
    assert slots.get("total") == 2 and len(slots.get("held", [])) == 2, slots
    machine.release("one")
    machine.wait_started("three")
    for tag in ("two", "three"):
        machine.release(tag)


def test_s7_a_rebuild_excludes_only_another_rebuild_of_the_same_tree(machine, repo):
    """Three slots: a rebuild of tree X holds X's lock; a rebuild of tree Y starts at once; a second rebuild of X
    waits although slots are free, and starts when the first ends."""
    machine.open_config(heavy_slots=3)
    tree_x, tree_y = machine.repo("tree-x"), machine.repo("tree-y")
    machine.slot_job(repo, "rebuild", "x1", tree=tree_x)
    machine.wait_started("x1")
    machine.slot_job(repo, "rebuild", "y1", tree=tree_y)
    machine.wait_started("y1")
    machine.slot_job(repo, "rebuild", "x2", tree=tree_x)
    _assert_waits(machine, "x2")
    machine.release("x1")
    machine.wait_started("x2")
    for tag in ("y1", "x2"):
        machine.release(tag)


def test_s7_a_session_takes_no_slot(machine, repo):
    """Every slot held by a test run: a session's start check still opens, and the gate reads open."""
    machine.open_config(heavy_slots=1)
    machine.slot_job(repo, "test", "holder")
    machine.wait_started("holder")

    support.opened_of(*machine.check(repo))
    assert support.gate_of(machine.read(repo))["open"] is True
    machine.release("holder")


def test_f4_no_fixed_ceiling_on_leads_or_sessions(machine, repo):
    """Forty live sessions, twenty of them leads, with memory for all (3 GiB + 41 x 1 GiB = 44 GiB of 64 GiB):
    the gate reads open and a further start opens."""
    machine.open_config()
    for n in range(40):
        machine.register(repo, machine.live_process(light=True).pid, ticket=f"DAEO-c{n:02d}",
                         role="orchestrator" if n % 2 else "engineer")

    reading = machine.read(repo)
    assert len(reading.get("sessions", [])) == 40, reading
    assert support.gate_of(reading)["open"] is True, f"a ceiling on sessions shut the gate: {reading['gate']}"
    support.opened_of(*machine.check(repo))
