"""S6 and F6: the memory rule.

S6: the gate opens on memory while MemAvailable plus the running sessions' live memory is at least the floor plus a
working size for each running session and for the new one; nothing is reserved for a run that has not started
[DEC-961, DEC-983, DEC-982]. F6 (failure): a worker's memory charged twice (in its lead's tree and as its own
session).

The memory reason's ``reading`` is MemAvailable plus the sessions' live memory; its ``threshold`` the floor plus
(running sessions + 1) working sizes (README, "The gate"). Live memory is each session's process tree, each process
counted once (``sessions_live_memory_bytes`` in the reading).
"""

from __future__ import annotations

import pytest

import w2_20_support as support
from w2_20_support import GIB, MIB


def test_s6_the_running_sessions_live_memory_is_added_to_memavailable(machine, repo):
    """Floor 3 GiB + 2 working sizes of 1 GiB (one session running, and the new one) = 5 GiB. MemAvailable is
    128 MiB short of it; the session holds 256 MiB, which is its own, so the gate opens."""
    machine.open_config(memory_floor_bytes=3 * GIB, working_size_bytes=1 * GIB)
    machine.set_readings(available_bytes=5 * GIB - 128 * MIB)
    session = machine.live_process(memory_mib=256)
    machine.register(repo, session.pid, ticket="DAEO-mem1")

    reading = machine.read(repo)
    live = reading.get("sessions_live_memory_bytes")
    assert isinstance(live, int) and live >= 256 * MIB, f"the session's live memory is not read: {reading}"
    support.opened_of(*machine.check(repo))


@pytest.mark.parametrize("running, opens", [(2, True), (3, False)], ids=["2 running opens", "3 running shuts"])
def test_s6_each_running_session_and_the_new_one_need_a_working_size(machine, repo, running, opens):
    """Floor 3 GiB, working size 1 GiB, MemAvailable 6.5 GiB: with 2 sessions running the need is 3 + 3 = 6 GiB
    (open); with 3 it is 3 + 4 = 7 GiB (shut, threshold 7 GiB)."""
    machine.open_config(memory_floor_bytes=3 * GIB, working_size_bytes=1 * GIB)
    machine.set_readings(available_bytes=6 * GIB + 512 * MIB)
    for n in range(running):
        machine.register(repo, machine.live_process(light=True).pid, ticket=f"DAEO-ws{n}")

    code, envelope, out, err = machine.check(repo)
    if opens:
        support.opened_of(code, envelope, out, err)
    else:
        refused = support.refusal_of(code, envelope, out, err)
        reasons = support.reasons_by_condition(refused)
        assert set(reasons) == {"memory"}, reasons
        assert reasons["memory"]["threshold"] == 7 * GIB, reasons["memory"]
        assert 6 * GIB + 512 * MIB <= reasons["memory"]["reading"] < 7 * GIB, reasons["memory"]


def test_s6_nothing_is_reserved_for_a_run_that_has_not_started(machine, repo):
    """A verification peak of 100 GiB in the file, no verification running: the need is the floor plus one working
    size (4 GiB), and 4 GiB available opens."""
    machine.open_config(memory_floor_bytes=3 * GIB, working_size_bytes=1 * GIB, verification_peak_bytes=100 * GIB)
    machine.set_readings(available_bytes=4 * GIB)

    support.opened_of(*machine.check(repo))
    machine.set_readings(available_bytes=4 * GIB - 1 * MIB)
    reasons = support.reasons_by_condition(support.refusal_of(*machine.check(repo)))
    assert reasons["memory"]["threshold"] == 4 * GIB, f"something beyond the floor and one working size: {reasons}"


def test_f6_a_workers_memory_is_charged_once_not_in_its_leads_tree_and_again_as_its_own_session(machine, repo):
    """A lead whose child, a worker, holds 192 MiB; both are sessions. Counted once, the two sessions' live memory
    is about 192 MiB plus two interpreters; counted twice it would be about 400 MiB. With MemAvailable 300 MiB
    short of the need (3 GiB + 3 x 1 GiB), counted once the gate shuts; counted twice it would open."""
    machine.open_config(memory_floor_bytes=3 * GIB, working_size_bytes=1 * GIB)
    machine.set_readings(available_bytes=6 * GIB - 300 * MIB)
    lead, worker = machine.lead_with_worker(192)
    machine.register(repo, lead.pid, ticket="DAEO-lead", role="orchestrator")
    machine.register(repo, worker, ticket="DAEO-wrkr", role="engineer")

    reading = machine.read(repo)
    assert support.session_pids(reading) == sorted([lead.pid, worker]), reading
    live = reading.get("sessions_live_memory_bytes")
    assert isinstance(live, int) and 192 * MIB <= live < 288 * MIB, (
        f"the two sessions' live memory is {live}: the worker's 192 MiB is not counted exactly once")
    reasons = support.reasons_by_condition(reading)
    assert support.gate_of(reading)["open"] is False and "memory" in reasons, (
        f"the worker's memory was counted twice and opened the gate: {reading}")
    assert reasons["memory"]["threshold"] == 6 * GIB, reasons["memory"]
