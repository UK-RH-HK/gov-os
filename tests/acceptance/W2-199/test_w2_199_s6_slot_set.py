"""W2-199, success line 6 (RT-3, one slot set replaces heavy_slot.sh's).

The kinds are ``test``, ``rebuild``, ``measure``, ``embedder``, ``reranker`` (the last two are success line 9's);
``--held <slot,slot>`` runs the command with the union of those slots' CPU sets and ``workers x (number held)`` workers
and takes no lock; a caller with ``GOV_HEAVY_PRIORITY=1`` is served before an ordinary waiter (an ordinary run does not
take a free slot while a live priority waiter exists), holds at most ``GOV_HEAVY_PRIO_CAP`` (default 2) slots at once and
while capped is not a waiter; a waiter's registration is a file in the slots folder named for its pid (``prio-<pid>``,
the name the ticket's F1 gives), ignored once the pid is dead.

The slots' CPU sets are read from the jobs themselves (``GOV_HEAVY_CPUS`` of a run in slot 1, 2, 3), never computed
here: the machine's own affinity decides them.
"""

from __future__ import annotations

import os
import signal

import pytest

import w2_199_support as s

PRIORITY = {"GOV_HEAVY_PRIORITY": "1"}
ONE_SLOT = {"GOV_HEAVY_SLOTS": "1"}


@pytest.mark.parametrize("kind", ["test", "rebuild", "measure"])
def test_s6_each_kind_runs_its_command_and_exits_with_the_commands_code(box, kind):
    done = box.run(kind, "--", "sh", "-c", "exit 6")
    assert done.returncode == 6, f"--slot {kind}: exit {done.returncode}, not the command's 6\n{s.said(done)}"
    done = box.run(kind, "--", "true")
    assert done.returncode == 0, f"--slot {kind} -- true: exit {done.returncode}\n{s.said(done)}"
    assert len(box.events("started")) == 2, f"--slot {kind}: two `started` events expected: {box.log()}"


def test_s6_held_1_2_gives_twice_the_workers_the_union_of_the_two_cpu_sets_and_takes_no_lock(make_box):
    if len(os.sched_getaffinity(0)) < 3:
        pytest.skip("fewer than 3 CPUs usable here: three slots cannot have different CPU sets")
    box = make_box(s.PROFILE_32, heavy_slots=None)  # three derived slots
    probes = [box.start(name) for name in "abc"]
    for job in probes:
        job.must_start(8.0)
    per = {job.env()["GOV_HEAVY_SLOT"]: (s.cpu_set(job.env()["GOV_HEAVY_CPUS"]),
                                         int(job.env()["PYTEST_XDIST_AUTO_NUM_WORKERS"])) for job in probes}
    assert set(per) == {"1", "2", "3"}, f"three runs got the slots {sorted(per)}"
    for job in probes:
        assert job.release_and_finish()[0] == 0
    held = box.start("held", opts=("--held", "1,2"))
    held.must_start(8.0)
    env = held.env()
    assert env.get("PYTEST_XDIST_AUTO_NUM_WORKERS") == str(2 * per["1"][1]), (
        f"--held 1,2 gives {env.get('PYTEST_XDIST_AUTO_NUM_WORKERS')} workers, not twice a slot's {per['1'][1]}")
    assert s.cpu_set(env.get("GOV_HEAVY_CPUS", "")) == per["1"][0] | per["2"][0], (
        f"--held 1,2 gives CPUs {env.get('GOV_HEAVY_CPUS')}, not the union of {per['1'][0]} and {per['2'][0]}")
    taken = [box.start(name) for name in "xyz"]  # all three slots are free while the held run goes on: it took no lock
    for job in taken:
        job.must_start(8.0)
    assert box.locks_held(), "the three ordinary runs hold no slot lock"
    for job in taken + [held]:
        job.release()
    assert all(job.finish()[0] == 0 for job in taken + [held])


@pytest.mark.parametrize("first", ["priority", "ordinary"])
def test_s6_a_priority_waiter_is_served_before_an_ordinary_one_whichever_came_first(box, first):
    holder = box.start("holder", extra_env=ONE_SLOT)
    holder.must_start(5.0)
    envs = {"priority": {**ONE_SLOT, **PRIORITY}, "ordinary": ONE_SLOT}
    waiters = {}
    for name in ([first] + [other for other in ("priority", "ordinary") if other != first]):
        waiters[name] = box.start(name, extra_env=envs[name])
        assert waiters[name].held_for(0.8)
    registered = s.poll(lambda: [p for p in box.prio_files() if str(waiters["priority"].pid) in p.name], 3.0)
    assert registered, f"no registration file named for the priority waiter's pid {waiters['priority'].pid} in " \
                       f"{box.slots_dir}: {[p.name for p in box.prio_files()]}"
    holder.release_and_finish()
    assert s.poll(lambda: waiters["priority"].mark.exists() or waiters["ordinary"].mark.exists(), 6.0), (
        "neither waiter started when the slot freed")
    assert waiters["priority"].mark.exists() and not waiters["ordinary"].mark.exists(), (
        f"the slot went to the ordinary waiter, order {box.order()}")
    waiters["priority"].release_and_finish()
    waiters["ordinary"].must_start(5.0)
    assert box.order() == ["holder", "priority", "ordinary"], f"start order {box.order()}"
    assert waiters["ordinary"].release_and_finish()[0] == 0


def test_s6_a_priority_waiter_killed_is_ignored_and_its_file_removed_so_the_ordinary_waiter_starts(box):
    holder = box.start("holder", extra_env=ONE_SLOT)
    holder.must_start(5.0)
    ordinary = box.start("ordinary", extra_env=ONE_SLOT)
    assert ordinary.held_for(0.8)
    priority = box.start("priority", extra_env={**ONE_SLOT, **PRIORITY})
    assert s.poll(lambda: [p for p in box.prio_files() if str(priority.pid) in p.name], 3.0), "no registration file"
    priority.proc.send_signal(signal.SIGKILL)
    priority.proc.wait(timeout=5)
    holder.release_and_finish()
    ordinary.must_start(6.0)
    assert not [p for p in box.prio_files() if str(priority.pid) in p.name] or s.poll(
        lambda: not [p for p in box.prio_files() if str(priority.pid) in p.name], 3.0), (
        "the dead priority waiter's registration file is still there")
    assert ordinary.release_and_finish()[0] == 0


def test_s6_two_priority_runs_holding_two_of_three_slots_cap_a_third_and_an_ordinary_run_takes_the_free_slot(make_box):
    box = make_box(s.PROFILE_32, heavy_slots=None)  # three derived slots
    held = [box.start(name, extra_env=PRIORITY) for name in ("p1", "p2")]
    for job in held:
        job.must_start(6.0)
    third = box.start("p3", extra_env=PRIORITY)
    assert third.held_for(1.5), "a third priority run took a slot: the cap of 2 is not held"
    assert not [p for p in box.prio_files() if str(third.pid) in p.name], (
        "a capped priority run is registered as a waiter")
    ordinary = box.start("ordinary")
    ordinary.must_start(5.0)
    assert third.held_for(0.5), "the capped priority run started in the slot the ordinary run took"
    for job in held + [ordinary]:
        job.release()
    third.must_start(5.0)
    third.release()
    assert all(job.finish()[0] == 0 for job in held + [ordinary, third])
