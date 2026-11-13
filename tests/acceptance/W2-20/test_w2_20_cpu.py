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
    """Round 7 (review F2): the servers idle now (0.0 cores each), so all of each p95 is headroom above their current
    use and counts. 2.5 busy cores of 4: with 0.5 + 0.5 cores of p95 the sum is 3.5 (open); with 1.5 from either
    server it is 4.0 (shut, "below nproc"). The reading shows each server's current use beside its p95."""
    machine.set_readings(nproc=4, busy_cores=2.5, embedding_p95=p95, embedding_now=(0.0, 0.0))

    reading = machine.read(repo)
    shown = reading.get("embedding_cpu_p95")
    assert isinstance(shown, dict) and support.close_to(shown.get("shared"), p95[0]) and support.close_to(
        shown.get("query"), p95[1]), f"the reading does not show both servers' p95: {reading}"
    now = reading.get("embedding_cpu_now")
    assert isinstance(now, dict) and support.close_to(now.get("shared"), 0.0) and support.close_to(
        now.get("query"), 0.0), f"the reading does not show both servers' current use: {reading}"
    code, envelope, out, err = machine.check(repo)
    if opens:
        support.opened_of(code, envelope, out, err)
    else:
        refused = support.refusal_of(code, envelope, out, err)
        reasons = support.reasons_by_condition(refused)
        assert set(reasons) == {"cpu"}, reasons
        assert support.close_to(reasons["cpu"]["reading"], 4.0) and reasons["cpu"]["threshold"] == 4, reasons["cpu"]


# Round 7 (the CTO's ruling under DEC-1097 (8) on review F2, a false refusal): the busy cores already hold the servers'
# current use, so only the part of each server's p95 above its current use is added:
# busy + max(0, p95(shared) - now(shared)) + max(0, p95(query) - now(query)) < nproc. A machine of 20 CPUs, as the
# review's: (busy, p95 (shared, query), now (shared, query), the cpu reading when shut or None when open).
SERVERS_NOW = {
    "a store rebuild: the shared server busy now near its p95 opens": (12.0, (8.0, 0.5), (7.5, 0.5), None),
    "the same p95 with both servers idle now counts its headroom: equal shuts": (11.5, (8.0, 0.5), (0.0, 0.0), 20.0),
    "a server busier now than its p95 subtracts nothing: equal shuts": (19.5, (1.0, 0.5), (3.0, 0.0), 20.0),
}


@pytest.mark.parametrize("case", list(SERVERS_NOW))
def test_s12_only_the_part_of_each_servers_p95_above_its_current_use_is_added(machine, repo, case):
    """A store rebuild: 12 busy cores of 20, 8.0 of them the shared server's now, its p95 8.0: the sum is
    12 + 0.5 + 0 = 12.5, open (counted twice it would be 20.5 and shut). The same p95 with the servers idle now: all
    of it is headroom, 11.5 + 8.0 + 0.5 = 20.0, shut. A server using 3.0 now against a p95 of 1.0 adds nothing and
    takes nothing away: 19.5 + 0 + 0.5 = 20.0, shut (with the difference subtracted it would be 18.0 and open)."""
    busy, p95, now, shut_at = SERVERS_NOW[case]
    machine.set_readings(nproc=20, busy_cores=busy, embedding_p95=p95, embedding_now=now)

    reading = machine.read(repo)
    shown_p95, shown_now = reading.get("embedding_cpu_p95"), reading.get("embedding_cpu_now")
    assert isinstance(shown_p95, dict) and isinstance(shown_now, dict), (
        f"the reading does not show the servers' p95 and current use side by side: {reading}")
    for name, i in (("shared", 0), ("query", 1)):
        assert support.close_to(shown_p95.get(name), p95[i]) and support.close_to(shown_now.get(name), now[i]), (
            f"the {name} server's p95 or current use is not the planted one: {shown_p95}, {shown_now}")
    code, envelope, out, err = machine.check(repo)
    if shut_at is None:
        support.opened_of(code, envelope, out, err)
        assert support.gate_of(reading)["open"] is True, f"the servers' current use was counted twice: {reading}"
    else:
        refused = support.refusal_of(code, envelope, out, err)
        reasons = support.reasons_by_condition(refused)
        assert set(reasons) == {"cpu"}, reasons
        assert support.close_to(reasons["cpu"]["reading"], shut_at) and reasons["cpu"]["threshold"] == 20, (
            reasons["cpu"])


def test_s12_f5_the_servers_current_use_unreadable_shuts_on_cpu(machine, repo):
    """F5: the servers' current use is a reading like their p95; when it cannot be taken it is ``null`` and shuts the
    gate on ``cpu`` with ``reading`` ``null`` (never taken as 0.0 or as their p95), every other reading within."""
    env_extra = {"GOV_RESOURCES_EMBEDDING_CPU_NOW": str(machine.base / "no-such-embedding-cpu-now.json")}

    code, envelope, out, err = machine.gov(repo, env_extra=env_extra)
    reading = support.reading_of(code, envelope, out, err)
    reasons = support.reasons_by_condition(reading)
    assert reading.get("embedding_cpu_now") is None, f"an unreadable current use is shown as {reading}"
    assert support.gate_of(reading)["open"] is False, f"an unreadable current use opened the gate: {reading}"
    assert set(reasons) == {"cpu"} and reasons["cpu"]["reading"] is None, reasons

    refused = support.refusal_of(*machine.check(repo, env_extra=env_extra))
    assert "cpu" in support.reasons_by_condition(refused), refused
