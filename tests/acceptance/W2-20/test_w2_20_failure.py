"""KPI failure: a session in another repository counts against the gate; a start while the gate is shut is refused
with the reading [W2-M244, W2-M188].

The start check is ``gov resources --check``, the gate a session start consults before it starts anything: exit 0
and ``ok: true`` when the gate is open; when it is shut, ``ok: false``, the named error ``RESOURCE_GATE_SHUT``, an exit
code other than 0 and 2, and the reading with its reasons in ``error.details``. ``gov launch`` is not run here: the
launcher is W2-21's, whose KPI is that the launch passes this gate.
"""

from __future__ import annotations

import w2_20_support as support
from w2_20_support import GIB


def test_a_session_entered_from_another_repository_counts_against_this_ones_gate(machine):
    """DEC-1097 (8): the other repository's session counts through the memory rule (S6), not a session weight:
    floor 1 GiB + 10 GiB for the new session fits in 12 GiB; with the other's live session it needs 21 GiB."""
    this = machine.repo("this-repo")
    other = machine.repo("other-repo")
    machine.open_config(memory_floor_bytes=1 * GIB, working_size_bytes=10 * GIB)
    machine.set_readings(available_bytes=12 * GIB)

    code, envelope, out, err = machine.check(this)
    assert code == 0 and envelope is not None and envelope.get("ok") is True, (
        f"the start check refused with an empty registry: exit {code}\n{out}\n{err}")

    proc = machine.live_process()
    machine.register(other, proc.pid, ticket="DAEO-othr", role="engineer")

    reading = machine.read(this)
    assert support.session_pids(reading) == [proc.pid], f"this repository does not see the other's session: {reading}"
    assert support.same_path(reading["sessions"][0]["repository"], other), reading["sessions"][0]
    assert support.gate_of(reading)["open"] is False, reading
    reasons = support.reasons_by_condition(reading)
    assert set(reasons) == {"memory"}, reasons
    assert reasons["memory"]["threshold"] == 21 * GIB, reasons["memory"]

    refused = support.refusal_of(*machine.check(this))
    assert "memory" in support.reasons_by_condition(refused), refused
    assert [int(s["pid"]) for s in refused.get("sessions", [])] == [proc.pid], refused


def test_W2_M244_W2_M188_a_start_while_the_gate_is_shut_is_refused_with_the_reading(machine, repo):
    """DEC-1097 (8): the memory rule of S6 (floor 8 GiB plus the new session's 1 GiB working size, no session
    running) in place of the old minimum."""
    machine.open_config(memory_floor_bytes=8 * GIB, working_size_bytes=1 * GIB)
    machine.set_readings(available_bytes=2 * GIB, load=0.5, nproc=4)

    refused = support.refusal_of(*machine.check(repo))
    assert refused.get("available_memory_bytes") == 2 * GIB, f"the refusal does not carry the reading: {refused}"
    assert refused.get("load_1m") == 0.5, refused
    assert refused.get("nproc") == 4, refused
    assert support.gate_of(refused)["open"] is False, refused
    reasons = support.reasons_by_condition(refused)
    assert set(reasons) == {"memory"}, reasons
    assert (reasons["memory"]["reading"], reasons["memory"]["threshold"]) == (2 * GIB, 9 * GIB)


def test_W2_M244_the_refusal_without_json_has_the_same_exit_code_and_names_the_reason(machine, repo):
    machine.open_config(max_load_1m=2.0)
    machine.set_readings(load=5.0)

    json_code = machine.check(repo)[0]
    code, _, out, err = machine.check(repo, json_output=False)
    assert code not in (0, 2), f"the start check without --json ended with exit {code}\n{out}\n{err}"
    assert code == json_code, (code, json_code)
    assert "load" in (out + err).lower(), f"the refusal does not name the load condition:\n{out}\n{err}"


def test_W2_M188_a_start_while_the_gate_is_open_goes_ahead(machine, repo):
    machine.open_config()
    machine.register(repo, machine.live_process().pid, ticket="DAEO-go")

    code, envelope, out, err = machine.check(repo)
    reading = support.reading_of(code, envelope, out, err)
    gate = support.gate_of(reading)
    assert gate["open"] is True and gate["reasons"] == [], reading
