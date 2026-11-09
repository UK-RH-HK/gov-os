"""KPI success 3: a stale entry (dead PID) is cleared [W2-M244, W2-M188, W2-M262].

An entry whose process is no longer alive does not count against the gate, and is removed from the registry when the
registry is read (the read reports it once under ``cleared``; a later read does not see it again). A live entry is
kept.
"""

from __future__ import annotations

import w2_20_support as support
from w2_20_support import GIB


def test_W2_M244_W2_M188_W2_M262_a_dead_pid_is_cleared_and_a_live_one_is_kept(machine, repo):
    machine.open_config()
    live = machine.live_process()
    doomed = machine.live_process()
    machine.register(repo, live.pid, ticket="DAEO-live")
    machine.register(repo, doomed.pid, ticket="DAEO-dead")
    assert support.session_pids(machine.read(repo)) == sorted([live.pid, doomed.pid])

    machine.stop(doomed)

    first = machine.read(repo)
    assert support.session_pids(first) == [live.pid], f"a dead PID is still read as a live session: {first}"
    cleared = first.get("cleared")
    assert isinstance(cleared, list), f"the reading does not report the entries it cleared: {first}"
    assert [int(e["pid"]) for e in cleared] == [doomed.pid], cleared
    assert cleared[0].get("ticket") == "DAEO-dead", cleared

    second = machine.read(repo)
    assert support.session_pids(second) == [live.pid], f"the live entry was not kept: {second}"
    assert second.get("cleared") == [], f"the stale entry was not removed from the registry by the first read: {second}"


def test_W2_M244_W2_M188_W2_M262_a_stale_entry_does_not_count_against_the_gate(machine, repo):
    """DEC-1097 (8), the memory rule of S6 in place of the session weights: a live entry would need a second working
    size (1 + 10 x 2 = 21 GiB > 12 GiB) and shut the gate; once its process has died it does not (1 + 10 = 11)."""
    machine.open_config(memory_floor_bytes=1 * GIB, working_size_bytes=10 * GIB)
    machine.set_readings(available_bytes=12 * GIB)
    gone = machine.live_process()
    machine.register(repo, gone.pid, ticket="DAEO-gone")
    live_reading = machine.read(repo)
    assert support.gate_of(live_reading)["open"] is False, f"the premise: one live session shuts it: {live_reading}"
    machine.stop(gone)

    reading = machine.read(repo)
    assert reading.get("sessions") == [], reading
    assert support.gate_of(reading)["open"] is True, f"a dead session counted against the gate: {reading}"

    code, envelope, out, err = machine.check(repo)
    assert code == 0 and envelope is not None and envelope.get("ok") is True, (
        f"the start check refused because of a dead session: exit {code}\n{out}\n{err}")
