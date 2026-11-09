"""Unit tests for the engineer's round 3 (W2-20, DAEO-r30l): the independent review's F1, F2, F4, F6 and F8 as the CTO
ruled them.

- F1: one machine-wide start lock from the gate's check until the session is registered, so launches that start
  together are counted against each other (a stand-in CLI, real processes, launches forked at once).
- F2: the cpu rule adds only the part of each server's p95 above its current use (``embedding_cpu_now``).
- F4: a missing or malformed ``oom_floor_bytes`` is named, never a silently skipped trip-wire.
- F6: an entry whose live pid is another process (a reused pid) is stale; CPU samples from before a restart are
  dropped at once.
- F8: a plan override is logged only once the gate admits the launch.

Planted machines (the ``planted`` fixture); no real CLI, server, model or GPU; every process a test starts is ended
by it."""
from __future__ import annotations

import datetime
import fcntl
import json
import os
import signal
import subprocess
import sys
import time
import types
from pathlib import Path

import pytest

from gov.cli.errors import GovError
from gov.launch import gate as launch_gate
from gov.launch import launcher, plan_check
from gov.resources import config as configuration
from gov.resources import gate, machine, registry, slots

GIB = 1024 ** 3


def reasons(reading: dict) -> dict:
    return {r["condition"]: r for r in reading["gate"]["reasons"]}


def far_servers():
    return {"shared": {"cpus": "4000", "nice": 10}, "query": {"cpus": "4001", "nice": 0}, "date": "2026-11-01",
            "source": "test"}


def _quiet_launch_checks(planted, monkeypatch) -> Path:
    """The worker and lead paths reach the gate with their other checks passed; the project folder."""
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *a: None)
    monkeypatch.setattr(launcher, "_check_ticket", lambda *a: None)
    monkeypatch.setattr(launcher, "build_settings", lambda root, role, ticket: {
        "env": {"GOV_ROLE": role, "GOV_TICKET": ticket}, "permissions": {"deny": []},
        "sandbox": {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
                    "network": {"strictAllowlist": True, "allowedDomains": []}}})
    monkeypatch.setattr(launcher.runs, "folder", lambda *a: None)
    monkeypatch.setattr(launcher.runs, "own_folder", lambda *a: None)
    monkeypatch.setattr(launcher, "check_lead", lambda root, ticket: plan_check.LeadCheck(True, "admitted"))
    project = planted.root / "project"
    project.mkdir(exist_ok=True)
    return project


# --- F1: launches that start together --------------------------------------------------------------------------------

STAND_IN_CLI = """#!/bin/sh
: > "$MARKS/started-$$"
while [ ! -e "$MARKS/release" ]; do sleep 0.05; done
"""


def _count(folder: Path, prefix: str) -> int:
    return len([p for p in folder.iterdir() if p.name.startswith(prefix)])


def test_f1_launches_started_together_admit_only_those_the_memory_rule_admits(planted, monkeypatch):
    """Six launches at once against room for three (floor 3 GiB, working size 2 GiB, 9 GiB available): only three
    sessions start, and the other three are refused on memory. Each check is slowed after its reading, so without
    the lock all six would read no session and start."""
    monkeypatch.setenv("GOV_RESOURCES_PROC", "/proc")  # real sessions: their pids are alive
    project = _quiet_launch_checks(planted, monkeypatch)
    planted.config(memory_floor_bytes=3 * GIB, working_size_bytes=2 * GIB)
    planted.memory(available=9 * GIB)  # 9 + the stand-ins' few MiB: n=2 needs 9 (opens), n=3 needs 11 (shuts)
    marks = planted.root / "marks"
    marks.mkdir()
    monkeypatch.setenv("MARKS", str(marks))
    cli = planted.home / launcher.CLI_REL
    cli.parent.mkdir(parents=True)
    cli.write_text(STAND_IN_CLI)
    cli.chmod(0o755)
    real_check = launch_gate.check_start

    def slow_check(**kw):
        reading = real_check(**kw)
        time.sleep(0.3)  # the window between the reading and the registration, widened
        return reading

    monkeypatch.setattr(launch_gate, "check_start", slow_check)
    children = []
    try:
        for i in range(6):
            pid = os.fork()
            if pid == 0:  # pragma: no cover - the child
                code = 4
                try:
                    launcher.launch(project, "engineer", f"T-{i}", [])
                    code = 0
                except GovError as error:
                    (marks / f"refused-{i}").write_text(error.message)
                    code = 3
                except BaseException as error:  # noqa: BLE001
                    (marks / f"error-{i}").write_text(repr(error))
                finally:
                    os._exit(code)
            children.append(pid)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            settled = _count(marks, "started-") + _count(marks, "refused-") + _count(marks, "error-")
            entries = len(list((planted.dir / "sessions").glob("*.json"))) if (planted.dir / "sessions").exists() else 0
            if settled == 6 and entries == _count(marks, "started-"):
                break
            time.sleep(0.05)
        assert _count(marks, "error-") == 0, [p.read_text() for p in marks.glob("error-*")]
        assert _count(marks, "started-") == 3 and _count(marks, "refused-") == 3
        for refused in marks.glob("refused-*"):
            assert refused.read_text().startswith("the resource gate is shut: memory: reading ")
        live, _, _ = registry.sessions()
        assert len(live) == 3
    finally:
        (marks / "release").write_text("")
        codes = []
        for pid in children:
            deadline = time.monotonic() + 30
            while True:
                done, status = os.waitpid(pid, os.WNOHANG)
                if done:
                    codes.append(os.waitstatus_to_exitcode(status))
                    break
                if time.monotonic() > deadline:
                    os.kill(pid, signal.SIGKILL)
                    os.waitpid(pid, 0)
                    codes.append(None)
                    break
                time.sleep(0.05)
    assert sorted(codes) == [0, 0, 0, 3, 3, 3]
    assert list((planted.dir / "sessions").glob("*.json")) == []  # every entry removed when its session ended


def test_f1_the_check_runs_under_the_machine_wide_start_lock(planted, monkeypatch):
    project = _quiet_launch_checks(planted, monkeypatch)
    planted.config()
    cli = planted.home / launcher.CLI_REL
    cli.parent.mkdir(parents=True)
    cli.write_text("#!/bin/sh\nexit 0\n")
    cli.chmod(0o755)
    real_check, seen = launch_gate.check_start, []

    def probing_check(**kw):
        fd = os.open(planted.dir / launch_gate.START_LOCK, os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            seen.append("free")
        except BlockingIOError:
            seen.append("held")
        finally:
            os.close(fd)
        return real_check(**kw)

    monkeypatch.setattr(launch_gate, "check_start", probing_check)
    for role in ("engineer", "orchestrator"):
        assert launcher.launch(project, role, "T-1", []) == 0
    assert seen == ["held", "held"]
    launch_gate.StartLock(wait_s=0).release()  # given back after each launch


def test_f1_a_launch_that_ends_before_registering_leaves_no_entry_and_frees_the_lock(planted, monkeypatch):
    project = _quiet_launch_checks(planted, monkeypatch)
    planted.config()
    cli = planted.home / launcher.CLI_REL
    cli.parent.mkdir(parents=True)
    cli.write_text("")  # not executable: the session cannot be started
    with pytest.raises(GovError) as refused:
        launcher.launch(project, "engineer", "T-1", [])
    assert "cannot be started" in refused.value.message
    assert list(planted.dir.glob("sessions/*.json")) == []
    launch_gate.StartLock(wait_s=0).release()


def test_f1_a_registration_that_fails_stops_the_session_leaves_no_entry_and_frees_the_lock(planted, monkeypatch):
    project = _quiet_launch_checks(planted, monkeypatch)
    planted.config()
    (planted.home / ".local" / "bin").mkdir(parents=True)
    (planted.home / launcher.CLI_REL).write_text("")
    killed = []

    class Session:
        pid = 777002

        def __init__(self, argv, cwd, env):
            pass

        def poll(self):
            return None if not killed else -9

        def kill(self):
            killed.append(True)

        def wait(self):
            return -9

    monkeypatch.setattr(launcher, "subprocess", types.SimpleNamespace(Popen=Session))
    monkeypatch.setattr(registry, "register", lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")))
    with pytest.raises(GovError) as refused:
        launcher.launch(project, "engineer", "T-1", [])
    assert "machine-wide registry" in refused.value.message and killed
    assert not (planted.dir / "sessions" / "777002.json").exists()
    launch_gate.StartLock(wait_s=0).release()


def test_f1_a_held_start_lock_refuses_after_its_wait_and_is_never_inherited(planted):
    planted.dir.mkdir(parents=True, exist_ok=True)
    held = launch_gate.StartLock(wait_s=0)
    try:
        assert os.get_inheritable(held.fd) is False
        with pytest.raises(GovError) as refused:
            launch_gate.StartLock(wait_s=0.2)
        assert refused.value.code == "LAUNCH_REFUSED" and "start lock" in refused.value.message
    finally:
        held.release()
        held.release()  # a second release does nothing
    launch_gate.StartLock(wait_s=0).release()


# --- F2: the servers are never counted twice -------------------------------------------------------------------------

@pytest.mark.parametrize("busy,p95,now,reading,open_", [
    (12.0, (8.0, 0.0), (7.5, 0.0), 12.5, True),    # a store rebuild: only the 0.5 above its current use is added
    (12.0, (8.0, 0.0), (0.0, 0.0), 20.0, False),   # the same p95 idle now: all of it is headroom; equal shuts
    (19.5, (8.0, 0.5), (9.0, 0.0), 20.0, False),   # busier now than its p95: adds nothing, takes nothing away
    (3.9, (0.25, 0.25), (0.25, 0.25), 3.9, True),
])
def test_f2_only_the_part_of_each_servers_p95_above_its_current_use_is_added(planted, busy, p95, now, reading, open_):
    planted.config()
    planted.busy(busy)
    planted.servers(*p95)
    planted.servers_now(*now)
    result = gate.read(True)
    assert result["embedding_cpu_now"] == {"shared": now[0], "query": now[1]}
    assert result["embedding_cpu_p95"] == {"shared": p95[0], "query": p95[1]}
    assert ("cpu" not in reasons(result)) is open_
    if not open_:
        assert reasons(result)["cpu"]["reading"] == reading and reasons(result)["cpu"]["threshold"] == 20


def test_f2_busy_cores_alone_shut_only_at_nproc(planted):
    planted.config()
    planted.nproc(4)
    planted.busy(4.0)
    planted.servers(0.25, 0.25)
    planted.servers_now(0.25, 0.25)
    assert reasons(gate.read(True))["cpu"]["reading"] == 4.0


@pytest.mark.parametrize("value", ["not json", '{"shared": 1}', '{"shared": -1, "query": 0}',
                                   '{"shared": true, "query": 0}'])
def test_f2_an_unreadable_current_use_shuts_on_cpu_with_a_null_reading(planted, monkeypatch, value):
    planted.config()
    monkeypatch.setenv("GOV_RESOURCES_EMBEDDING_CPU_NOW", value)
    result = gate.read(True)
    assert result["embedding_cpu_now"] is None and reasons(result)["cpu"]["reading"] is None
    assert "GOV_RESOURCES_EMBEDDING_CPU_NOW" in reasons(result)["cpu"]["why"]


def test_f2_the_own_current_use_is_the_servers_cpu_over_the_last_minute(planted, monkeypatch):
    planted.config()
    monkeypatch.delenv("GOV_RESOURCES_EMBEDDING_CPU")
    monkeypatch.delenv("GOV_RESOURCES_EMBEDDING_CPU_NOW")
    planted.process(900, ticks=0, cmdline="ollama serve")
    planted.process(901, ppid=900, ticks=0, cmdline="ollama runner")
    monkeypatch.setattr(machine, "listener", lambda port, table=None: 900 if port == 11434 else None)
    values = configuration.load()["values"]
    (_, _), (first, why) = machine.servers_cpu(planted.dir, values)
    assert why is None and first == {"shared": 0.0, "query": 0.0}  # a new process: a short window
    path = planted.dir / machine.SERVER_HISTORY
    history = json.loads(path.read_text())
    now = time.time()
    # a sample a minute old at 0 ticks, and one ten seconds old at 29 s: the minute-old one is the window's start
    history["shared"]["window"] = [[now - 60.5, 900, 0], [now - 10, 900, machine.TICKS * 29]]
    path.write_text(json.dumps(history))
    planted.process(901, ppid=900, ticks=machine.TICKS * 30, cmdline="ollama runner")  # 30 s of CPU in the minute
    (_, _), (second, _) = machine.servers_cpu(planted.dir, values)
    assert 0.45 <= second["shared"] <= 0.55 and second["query"] == 0.0
    # the server restarted (another pid): its old process's samples never count; a short window, never null
    planted.gone(901)
    planted.gone(900)
    planted.process(950, ticks=machine.TICKS, cmdline="ollama serve")
    monkeypatch.setattr(machine, "listener", lambda port, table=None: 950 if port == 11434 else None)
    (_, _), (third, why) = machine.servers_cpu(planted.dir, values)
    assert why is None and third["shared"] == 0.0


def test_f2_a_kept_history_written_before_round_3_still_reads(planted, monkeypatch):
    """A ``server-cpu.json`` with no window (written by round 2) gives a short window at once, never a null."""
    planted.config()
    monkeypatch.delenv("GOV_RESOURCES_EMBEDDING_CPU_NOW")
    planted.process(900, ticks=0, cmdline="ollama serve")
    monkeypatch.setattr(machine, "listener", lambda port, table=None: 900 if port == 11434 else None)
    planted.dir.mkdir(parents=True, exist_ok=True)
    (planted.dir / machine.SERVER_HISTORY).write_text(json.dumps(
        {"shared": {"rates": [[time.time() - 5, 1.0]], "last": [time.time() - 5, 900, 0]}}))
    reading = gate.read(True)
    assert reading["embedding_cpu_now"] == {"shared": 0.0, "query": 0.0} and "cpu" not in reasons(reading)


# --- F4: the trip-wire's floor named --------------------------------------------------------------------------------

@pytest.mark.parametrize("value", [None, {"value": "lots", "date": "2026-11-09", "source": "t"},
                                   {"value": 2 * GIB, "date": "", "source": "t"}])
def test_f4_a_missing_or_malformed_trip_floor_is_named_when_a_heavy_job_starts(planted, capfd, value):
    planted.config(embedding_servers=far_servers(), oom_floor_bytes=value)  # None: the key left out
    assert slots.run("test", [sys.executable, "-c", "pass"]) == 0
    err = capfd.readouterr().err
    assert "OOM_TRIPWIRE_OFF" in err and "oom_floor_bytes" in err
    assert any(r["key"] == "oom_floor_bytes" for r in configuration.load()["faults"])
    assert reasons(gate.read(True))["config"]["key"] == "oom_floor_bytes"  # and the gate is shut on it, named


def test_f4_a_good_trip_floor_is_not_named(planted, capfd):
    planted.config(embedding_servers=far_servers())
    assert slots.run("test", [sys.executable, "-c", "pass"]) == 0
    assert "OOM_TRIPWIRE_OFF" not in capfd.readouterr().err


def test_f4_a_trip_wire_pass_without_its_floor_stops_nothing_and_names_it(planted):
    result = slots.tripwire({}, available=1)
    assert result["stopped"] is None and "oom_floor_bytes" in result["why"]
    assert "oom_floor_bytes" in slots.tripwire({"oom_floor_bytes": "2G"})["why"]


def test_f4_the_trip_wire_command_names_a_missing_floor(planted):
    from gov.resources import command
    planted.config(oom_floor_bytes=None)
    args = types.SimpleNamespace(slot=None, passthrough=None, tree=None, workers=None, ticket=None,
                                 session_role=None, gpu_need_mib=None, register=None, init_config=False,
                                 sample=False, remeasure=False, trip_wire=True, check=False, gpu_kind="other")
    with pytest.raises(GovError) as refused:
        command.run(planted.root, args, {})
    assert "oom_floor_bytes" in refused.value.message


# --- F6: a reused pid, and CPU history from before a restart -----------------------------------------------------------

@pytest.fixture
def sleeper():
    process = subprocess.Popen(["sleep", "60"])
    time.sleep(0.05)
    yield process
    process.terminate()
    process.wait(timeout=10)


def _iso(seconds_from_now: float) -> str:
    when = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds_from_now)
    return when.isoformat(timespec="seconds")


def _entry(planted, pid: int, **fields) -> Path:
    folder = planted.dir / "sessions"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{pid}.json"
    path.write_text(json.dumps({"pid": pid, "repository": str(planted.root), "ticket": "T", "role": "engineer",
                                **fields}))
    return path


def test_f6_an_entry_whose_live_pid_started_after_it_was_made_is_stale_and_cleared(planted, monkeypatch, sleeper):
    monkeypatch.setenv("GOV_RESOURCES_PROC", "/proc")
    path = _entry(planted, sleeper.pid, started=_iso(-3600))  # made an hour before this process began
    live, cleared, why = registry.sessions()
    assert why is None and live == [] and [e["pid"] for e in cleared] == [sleeper.pid]
    assert not path.exists()


def test_f6_an_entry_made_when_its_process_ran_stays(planted, monkeypatch, sleeper):
    monkeypatch.setenv("GOV_RESOURCES_PROC", "/proc")
    _entry(planted, sleeper.pid, started=_iso(0))
    _entry(planted, os.getpid(), started=_iso(0))  # registered after it began (gov resources --register): its own
    live, cleared, _ = registry.sessions()
    assert sorted(e["pid"] for e in live) == sorted([sleeper.pid, os.getpid()]) and cleared == []


def test_f6_register_records_the_process_start_and_another_start_is_stale(planted, monkeypatch, sleeper):
    monkeypatch.setenv("GOV_RESOURCES_PROC", "/proc")
    entry = registry.register(sleeper.pid, planted.root, "T", "engineer")
    assert isinstance(entry["start_ticks"], int) and entry["boot"] == machine.boot_id()
    assert [e["pid"] for e in registry.sessions()[0]] == [sleeper.pid]
    path = planted.dir / "sessions" / f"{sleeper.pid}.json"
    path.write_text(json.dumps({**entry, "start_ticks": entry["start_ticks"] - 100}))  # the pid's earlier owner
    live, cleared, _ = registry.sessions()
    assert live == [] and [e["pid"] for e in cleared] == [sleeper.pid] and not path.exists()
    registry.register(sleeper.pid, planted.root, "T", "engineer")
    path.write_text(json.dumps({**json.loads(path.read_text()), "boot": "another-boot"}))  # made before a restart
    assert registry.sessions()[0] == []


def test_f6_on_a_planted_process_table_the_start_is_not_judged(planted):
    planted.process(601)
    _entry(planted, 601, started=_iso(-86400))
    assert [e["pid"] for e in registry.sessions()[0]] == [601]


@pytest.mark.parametrize("kept", [
    {"busy": 900000, "total": 9000000},           # counters above today's: from before a restart
    {"busy": 1000, "total": 8000, "boot": "another-boot"},
])
def test_f6_cpu_samples_from_before_a_restart_are_dropped_at_once(planted, monkeypatch, kept):
    planted.config()
    monkeypatch.delenv("GOV_RESOURCES_BUSY_CORES")
    stat = planted.root / "stat"
    stat.write_text("cpu  7000 0 0 13000 0 0 0 0\n")
    monkeypatch.setenv("GOV_RESOURCES_STAT", str(stat))
    planted.dir.mkdir(parents=True, exist_ok=True)
    (planted.dir / machine.CPU_HISTORY).write_text(json.dumps([{"t": time.time() - 61, **kept}]))
    reading = gate.read(True)
    assert reading["busy_cores_1m"] == 7.0  # a short window of its own: not null, and not judged against the old one
    kept_now = json.loads((planted.dir / machine.CPU_HISTORY).read_text())
    assert all(item["busy"] <= 7000 and item.get("boot", machine.boot_id()) == machine.boot_id() for item in kept_now)


# --- F8: a plan override only once the gate admits ---------------------------------------------------------------------

@pytest.fixture
def lead(planted, monkeypatch, capfd):
    project = _quiet_launch_checks(planted, monkeypatch)
    (planted.home / ".local" / "bin").mkdir(parents=True)
    (planted.home / launcher.CLI_REL).write_text("")
    monkeypatch.setattr(launcher, "check_lead", lambda root, ticket: plan_check.LeadCheck(
        True, f"plan_override DEC-899 admits ticket {ticket} despite: waits for T-1", "DEC-899"))

    class Session:
        pid = 777003

        def __init__(self, argv, cwd, env):
            pass

        def wait(self):
            return 0

        def poll(self):
            return 0

    monkeypatch.setattr(launcher, "subprocess", types.SimpleNamespace(Popen=Session))
    return project


def test_f8_a_plan_override_for_a_lead_the_gate_refuses_is_not_logged(planted, lead, capfd):
    planted.config()
    planted.memory(available=GIB)
    with pytest.raises(GovError) as refused:
        launcher.launch(lead, "orchestrator", "T-3", [])
    assert refused.value.message.startswith("the resource gate is shut: memory")
    assert not (planted.dir / "launch.log").exists()
    assert "OVERRIDE" not in capfd.readouterr().err


def test_f8_a_plan_override_the_gate_admits_is_logged_once(planted, lead, capfd):
    planted.config()
    assert launcher.launch(lead, "orchestrator", "T-3", []) == 0
    [line] = (planted.dir / "launch.log").read_text().splitlines()
    assert "OVERRIDE plan_override: DEC-899: ticket T-3" in line
    assert [x for x in capfd.readouterr().err.splitlines() if "OVERRIDE" in x] == [
        "gov launch: OVERRIDE DEC-899: plan_override DEC-899 admits ticket T-3 despite: waits for T-1 (DEC-899)"]


def test_f8_with_a_gate_override_both_overrides_are_logged_gate_first(planted, lead):
    planted.config()
    planted.memory(available=GIB)
    assert launcher.launch(lead, "orchestrator", "T-3", [], gate_override="DEC-1088") == 0
    lines = (planted.dir / "launch.log").read_text().splitlines()
    assert len(lines) == 2 and "gate_override: DEC-1088" in lines[0] and "plan_override: DEC-899" in lines[1]
