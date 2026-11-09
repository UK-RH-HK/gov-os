"""S2 (its CPU half) and S12 (the servers' p95 at admission).

S2: the gate judges real CPU use (busy cores over the last minute) as well as the load, and shows both
[DEC-1010 item 7, SMART-WORK-3]. S12: the gate counts both embedding servers' CPU p95 when it admits a session
[ACT-OLLAMA-CAP-1, ACT-OLLAMA-CAP-2, DEC-1010 item 7, DEC-1017].

The CPU condition (README, "The gate"): open while busy cores over the last minute plus the shared and the query
server's CPU p95 (in cores) is below nproc; the reason's ``reading`` is that sum, its ``threshold`` nproc.
"""

from __future__ import annotations

import pytest

import w2_20_support as support


@pytest.mark.parametrize("busy, load, shut", [(4.0, 0.1, "cpu"), (0.5, 9.0, "load")],
                         ids=["busy cores high, load low", "load high, busy cores low"])
def test_s2_the_gate_judges_busy_cores_and_load_each_on_its_own_and_shows_both(machine, repo, busy, load, shut):
    """Busy cores high: all 4 of 4 busy, the two servers each using 0.25 cores now (inside the busy cores) with a p95
    of 0.25, so nothing above their current use is added: the cpu reading is the busy cores alone, 4.0, not below
    nproc (the README's cpu rule, round 7: equal shuts), while the load (0.1) is far below it. Load high: 9.0 of 4,
    busy cores 0.5."""
    machine.set_readings(nproc=4, busy_cores=busy, load=load, load_15=load, embedding_p95=(0.25, 0.25),
                         embedding_now=(0.25, 0.25))

    reading = machine.read(repo)
    assert reading.get("busy_cores_1m") == busy, f"the reading does not show the busy cores: {reading}"
    assert reading.get("load_1m") == load and reading.get("load_15m") == load, reading
    reasons = support.reasons_by_condition(reading)
    assert support.gate_of(reading)["open"] is False, reading
    assert set(reasons) == {shut}, f"only {shut} is broken: {reasons}"
    if shut == "cpu":
        assert support.close_to(reasons["cpu"]["reading"], busy) and reasons["cpu"]["threshold"] == 4, (
            f"the servers' use is counted twice: {reasons['cpu']}")

    refused = support.refusal_of(*machine.check(repo))
    assert set(support.reasons_by_condition(refused)) == {shut}, refused


def test_s2_busy_cores_and_load_within_open_the_gate(machine, repo):
    machine.set_readings(nproc=4, busy_cores=2.0, load=2.0, load_15=2.0, embedding_p95=(0.5, 0.5))
    reading = support.opened_of(*machine.check(repo))
    assert reading.get("busy_cores_1m") == 2.0 and reading.get("load_1m") == 2.0, reading


@pytest.mark.parametrize("p95, opens", [((0.5, 0.5), True), ((1.5, 0.0), False), ((0.0, 1.5), False)],
                         ids=["both within", "the shared server's p95 tips it", "the query server's p95 tips it"])
def test_s12_both_servers_cpu_p95_count_when_a_session_is_admitted(machine, repo, p95, opens):
    """2.5 busy cores of 4: with 0.5 + 0.5 cores of p95 the sum is 3.5 (open); with 1.5 from either server it is
    4.0 (shut, "below nproc")."""
    machine.set_readings(nproc=4, busy_cores=2.5, embedding_p95=p95)

    reading = machine.read(repo)
    shown = reading.get("embedding_cpu_p95")
    assert isinstance(shown, dict) and support.close_to(shown.get("shared"), p95[0]) and support.close_to(
        shown.get("query"), p95[1]), f"the reading does not show both servers' p95: {reading}"
    code, envelope, out, err = machine.check(repo)
    if opens:
        support.opened_of(code, envelope, out, err)
    else:
        refused = support.refusal_of(code, envelope, out, err)
        reasons = support.reasons_by_condition(refused)
        assert set(reasons) == {"cpu"}, reasons
        assert support.close_to(reasons["cpu"]["reading"], 4.0) and reasons["cpu"]["threshold"] == 4, reasons["cpu"]
