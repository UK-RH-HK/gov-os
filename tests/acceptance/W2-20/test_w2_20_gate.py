"""KPI success 2: the gate opens or shuts with a named reason.

The gate is open only when available memory is at least the configured minimum, the 1-minute load is below the
configured limit, and the weighted count of live sessions (a heavy session counts double) is within the configured
maximum. Each broken condition is a reason with its reading and its threshold. A reading that cannot be taken never
opens the gate. W2-M262 (close's cases fail under concurrent machine load) is the load condition's row.
"""

from __future__ import annotations

import pytest

import w2_20_support as support
from w2_20_support import GIB


def test_the_gate_is_open_when_every_condition_holds(machine, repo):
    machine.open_config()
    machine.set_readings(available_bytes=16 * GIB, load=0.5, nproc=4)
    proc = machine.live_process()
    machine.register(repo, proc.pid, ticket="DAEO-open")

    reading = machine.read(repo)
    gate = support.gate_of(reading)
    assert gate["open"] is True, reading
    assert gate["reasons"] == [], reading


@pytest.mark.parametrize("condition", ["memory", "load", "cpu", "disk", "inodes"],
                         ids=["memory", "load [W2-M262]", "cpu", "disk", "inodes"])
def test_one_broken_condition_shuts_the_gate_and_is_named_with_its_reading_and_threshold(machine, repo, condition):
    """DEC-1097 (8): the current conditions (S2, S4, S5, S6); no sessions condition (DEC-983). Memory: 64 GiB
    against the floor 70 GiB plus the new session's 1 GiB; load: min(9, 9) against nproc 4; CPU: 3.5 busy cores plus
    the servers' p95 0.25 + 0.25 against nproc 4; disk: 50 GiB against 100 GiB; inodes: 5,000,000 against 10,000,000."""
    machine.open_config()
    if condition == "memory":
        machine.open_config(memory_floor_bytes=70 * GIB, working_size_bytes=1 * GIB)
        expected = (64 * GIB, 71 * GIB)
    elif condition == "load":
        machine.set_readings(load=9.0, load_15=9.0)
        expected = (9.0, 4)
    elif condition == "cpu":
        machine.set_readings(busy_cores=3.5, embedding_p95=(0.25, 0.25))
        expected = (4.0, 4)
    elif condition == "disk":
        machine.set_readings(free_bytes=50 * GIB)
        expected = (50 * GIB, 100 * GIB)
    else:
        machine.set_readings(free_inodes=5_000_000)
        expected = (5_000_000, 10_000_000)

    reading = machine.read(repo)
    gate = support.gate_of(reading)
    reasons = support.reasons_by_condition(reading)
    assert gate["open"] is False, reading
    assert set(reasons) == {condition}, f"expected the one reason {condition!r}: {gate['reasons']}"
    assert (reasons[condition]["reading"], reasons[condition]["threshold"]) == expected, reasons[condition]


def test_several_broken_conditions_are_all_named(machine, repo):
    """DEC-1097 (8): every current condition broken at once is named (no sessions condition, DEC-983)."""
    machine.open_config(memory_floor_bytes=1 * GIB, working_size_bytes=1 * GIB)
    machine.set_readings(available_bytes=512 * 1024 * 1024, load=12.0, load_15=12.0, nproc=8, busy_cores=9.0,
                         embedding_p95=(0.5, 0.5), free_bytes=10 * GIB, free_inodes=1_000)

    reading = machine.read(repo)
    reasons = support.reasons_by_condition(reading)
    assert support.gate_of(reading)["open"] is False, reading
    assert set(reasons) == {"memory", "load", "cpu", "disk", "inodes"}, reasons
    assert (reasons["memory"]["reading"], reasons["memory"]["threshold"]) == (512 * 1024 * 1024, 2 * GIB)
    assert (reasons["load"]["reading"], reasons["load"]["threshold"]) == (12.0, 8)
    assert (reasons["cpu"]["reading"], reasons["cpu"]["threshold"]) == (10.0, 8)
    assert (reasons["disk"]["reading"], reasons["disk"]["threshold"]) == (10 * GIB, 100 * GIB)
    assert (reasons["inodes"]["reading"], reasons["inodes"]["threshold"]) == (1_000, 10_000_000)


@pytest.mark.parametrize("condition", ["memory", "load", "cpu", "disk", "inodes"])
def test_exactly_at_a_threshold(machine, repo, condition):
    """DEC-1097 (8). "At least" opens at the value: memory (MemAvailable equal to the floor plus the new session's
    working size, no session running, S6), disk and inodes (S4 "shuts below a floor"). "Below" shuts at the value:
    load (both loads equal to nproc, S5) and CPU (busy cores plus the servers' p95 equal to nproc, S2)."""
    machine.open_config(memory_floor_bytes=2 * GIB, working_size_bytes=1 * GIB)
    machine.set_readings(nproc=3)
    if condition == "memory":
        machine.set_readings(available_bytes=3 * GIB)
    elif condition == "load":
        machine.set_readings(load=3.0, load_15=3.0)
    elif condition == "cpu":
        machine.set_readings(busy_cores=2.5, embedding_p95=(0.25, 0.25))
    elif condition == "disk":
        machine.set_readings(free_bytes=100 * GIB)
    else:
        machine.set_readings(free_inodes=10_000_000)

    reading = machine.read(repo)
    reasons = support.reasons_by_condition(reading)
    if condition in ("memory", "disk", "inodes"):
        assert support.gate_of(reading)["open"] is True, f"{condition} equal to its floor must open: {reading}"
        assert reasons == {}, reasons
    else:
        assert support.gate_of(reading)["open"] is False, f"{condition} equal to nproc must shut: {reading}"
        assert set(reasons) == {condition}, reasons
        assert (reasons[condition]["reading"], reasons[condition]["threshold"]) == (3.0, 3)


def test_with_no_configuration_file_the_gate_is_shut_and_names_it(machine, repo):
    """DEC-1097 (8), S8 and F5 (DEC-947 item 3, DEC-950 item 2): every value is in the one configuration file, and a
    value missing shuts the gate, named; no default stands in for it (the old defaults of DEC-742 are gone)."""
    machine.config_file.unlink()
    machine.set_readings(available_bytes=64 * GIB, load=0.5, nproc=4)

    reading = machine.read(repo)
    assert support.gate_of(reading)["open"] is False, f"no configuration file, and the gate opened: {reading}"
    config = support.config_reasons(reading)
    assert config, f"the gate is not shut on the configuration: {reading['gate']}"
    named = " ".join(map(str, config))
    assert "gate.json" in named or any(key in named for key in support.GATE_KEYS), (
        f"the reason names neither the file nor a value: {config}")
    refused = support.refusal_of(*machine.check(repo))
    assert support.config_reasons(refused), refused


@pytest.mark.parametrize("missing", ["memory", "load", "busy cores", "embedding p95", "disk"])
def test_a_reading_that_cannot_be_taken_never_opens_the_gate(machine, repo, missing):
    """Fail closed (F5): with every other reading far within its limit, an unreadable reading is ``null`` and shuts
    the gate, named with its condition. DEC-1097 (8): the current readings (S2, S4, S5, S6, S12)."""
    machine.open_config(memory_floor_bytes=1 * GIB, working_size_bytes=1 * GIB, disk_floor_bytes=1,
                        inode_floor=1)
    env_extra: dict = {}
    if missing == "memory":
        env_extra = {"GOV_RESOURCES_MEMINFO": str(machine.base / "no-such-meminfo")}
        field, condition = "available_memory_bytes", "memory"
    elif missing == "load":
        machine.loadavg.write_text("not a load average\n")
        field, condition = "load_1m", "load"
    elif missing == "busy cores":
        machine.busy.write_text("many\n")
        field, condition = "busy_cores_1m", "cpu"
    elif missing == "embedding p95":
        env_extra = {"GOV_RESOURCES_EMBEDDING_CPU": str(machine.base / "no-such-embedding-cpu.json")}
        field, condition = "embedding_cpu_p95", "cpu"
    else:
        env_extra = {"GOV_RESOURCES_DISK": str(machine.base / "no-such-disk.json")}
        field, condition = "disk", "disk"

    code, envelope, out, err = machine.gov(repo, env_extra=env_extra)
    reading = support.reading_of(code, envelope, out, err)
    reasons = support.reasons_by_condition(reading)
    assert reading.get(field) is None, f"an unreadable {missing} reading is reported as {reading.get(field)!r}"
    assert support.gate_of(reading)["open"] is False, f"an unreadable {missing} reading opened the gate: {reading}"
    assert condition in reasons, reasons
    assert set(reasons) <= {condition, "inodes"}, reasons  # an unreadable disk leaves the inodes unread too
    assert reasons[condition]["reading"] is None, reasons[condition]

    refused = support.refusal_of(*machine.check(repo, env_extra=env_extra))
    assert condition in support.reasons_by_condition(refused), refused


@pytest.mark.parametrize("weighted, start", [(7, "light"), (7, "heavy"), (8, "light")],
                         ids=["7, a light start opens", "7, a heavy start is refused",
                              "8, the reading shuts and a light start is refused"])
def test_DEC_747_at_most_8_holds_after_the_start(machine, repo, weighted, start):
    """DEC-747 (delegated, staged), a reading of DEC-742: the start check opens on sessions only when the live
    weighted count plus the new session's weight (1 light, 2 heavy) is at most the maximum; the reading shows the
    gate shut on sessions once the count is at the maximum. DEC-742's default maximum, 8; the other conditions hold.
    """
    assert not machine.config_file.exists()
    for n in range(3):
        machine.register(repo, machine.live_process().pid, ticket=f"DAEO-bh{n}", heavy=True)
    for n in range(weighted - 6):
        machine.register(repo, machine.live_process().pid, ticket=f"DAEO-bl{n}")

    reading = machine.read(repo)
    assert reading.get("weighted_sessions") == weighted, f"three heavy and {weighted - 6} light sessions: {reading}"
    assert reading["thresholds"]["max_weighted_sessions"] == 8, reading
    reasons = support.reasons_by_condition(reading)
    if weighted < 8:
        assert support.gate_of(reading)["open"] is True and reasons == {}, f"{weighted} of 8 must read open: {reading}"
    else:
        assert support.gate_of(reading)["open"] is False, f"8 of 8 leaves no room and must read shut: {reading}"
        assert set(reasons) == {"sessions"}, reasons
        assert (reasons["sessions"]["reading"], reasons["sessions"]["threshold"]) == (8, 8), reasons["sessions"]

    heavy = start == "heavy"
    after = weighted + (2 if heavy else 1)
    code, envelope, out, err = machine.check(repo, heavy=heavy)
    if after <= 8:
        opened = support.reading_of(code, envelope, out, err)
        gate = support.gate_of(opened)
        assert gate["open"] is True and gate["reasons"] == [], f"{weighted} + 1 = {after} must open: {opened}"
    else:
        refused = support.refusal_of(code, envelope, out, err)
        assert refused.get("weighted_sessions") == weighted, f"the refusal does not carry the reading: {refused}"
        assert support.gate_of(refused)["open"] is False, refused
        reasons = support.reasons_by_condition(refused)
        assert set(reasons) == {"sessions"}, f"a {start} start at {weighted} of 8 is refused on sessions: {reasons}"
        assert (reasons["sessions"]["reading"], reasons["sessions"]["threshold"]) == (after, 8), (
            f"the reason carries the count after the start ({weighted} + {after - weighted}) and the maximum: "
            f"{reasons['sessions']}")
