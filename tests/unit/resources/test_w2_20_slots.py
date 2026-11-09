"""Unit tests for the heavy-job slots, their CPU sets and thread budgets, the trip-wire and the re-measure (W2-20 S7,
S9, S11, S15, S17; P-5, P-7). Planted machines; the jobs are stand-in programs that record their CPUs and
environment (and a grandchild's); every process a test starts is stopped by it."""
from __future__ import annotations

import datetime
import fcntl
import json
import os
import subprocess
import sys
import threading
import time

import pytest

from gov.cli.errors import GovError
from gov.resources import config as configuration
from gov.resources import measure, slots

GIB = 1024 ** 3
JOB = """import json, os, subprocess, sys
def seen(who):
    with open(sys.argv[1], "a") as out:
        out.write(json.dumps({"who": who, "cpus": sorted(os.sched_getaffinity(0)),
                              "env": {k: v for k, v in os.environ.items() if k.endswith(("THREADS", "PROCS"))
                                      or k.startswith(("GOV_HEAVY", "PYTEST_XDIST"))}}) + "\\n")
if sys.argv[2:] == ["child"]:
    seen("grandchild")
    sys.exit(0)
seen("job")
subprocess.run([sys.executable, __file__, sys.argv[1], "child"], check=True)
sys.exit(7)
"""


def far_servers():
    """Embedding servers on CPUs no test process has, so the slots divide the whole CPU set."""
    return {"shared": {"host": "127.0.0.1:1", "cpus": "4000", "nice": 10, "date": "2026-11-01", "source": "test"},
            "query": {"host": "127.0.0.1:2", "cpus": "4001", "nice": 0, "date": "2026-11-01", "source": "test"}}


@pytest.fixture
def job(tmp_path):
    script, log = tmp_path / "job.py", tmp_path / "job.jsonl"
    script.write_text(JOB)
    return [sys.executable, str(script), str(log)], lambda: [json.loads(x) for x in log.read_text().splitlines()]


# --- CPU sets and budgets -------------------------------------------------------------------------------------------

def test_the_shares_divide_the_cpus_outside_the_servers_evenly_and_contiguously():
    sets, note = slots.shares(range(20), 3, exclude=range(12, 20))
    assert sets == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]] and note is None
    sets, _ = slots.shares(range(20), 3)
    assert sets == [list(range(0, 6)), list(range(6, 13)), list(range(13, 20))]


def test_servers_covering_every_cpu_are_not_excluded_and_it_is_said():
    sets, note = slots.shares(range(4), 2, exclude=range(4))
    assert sets == [[0, 1], [2, 3]] and "not excluded" in note


def test_more_slots_than_cpus_still_gives_each_slot_one_cpu():
    sets, _ = slots.shares([3], 3)
    assert sets == [[3], [3], [3]]


@pytest.mark.parametrize("share,workers,configured,expected", [(list(range(6)), 6, None, 1), (list(range(7)), 2, None, 3),
                                                               ([1], 4, None, 1), (list(range(8)), 1, 3, 3)])
def test_the_thread_budget_is_the_share_over_the_workers_at_least_one(share, workers, configured, expected):
    assert slots.budget(share, workers, configured) == expected


def test_an_inherited_value_never_raises_the_budget():
    env = slots.job_env({"OMP_NUM_THREADS": "64", "MKL_NUM_THREADS": "1", "GOMAXPROCS": "x"}, [0, 1, 2, 3], 2, 2, 1)
    assert env["OMP_NUM_THREADS"] == "2" and env["MKL_NUM_THREADS"] == "1" and env["GOMAXPROCS"] == "2"
    assert all(env[name] for name in slots.THREAD_VARIABLES)
    assert (env["GOV_HEAVY_CPUS"], env["GOV_HEAVY_SLOT"], env["PYTEST_XDIST_AUTO_NUM_WORKERS"]) == ("0-3", "1", "2")


# --- the run --------------------------------------------------------------------------------------------------------

def test_a_job_runs_in_its_slot_confined_with_its_budget_and_every_child_inherits_both(planted, job, monkeypatch):
    command, runs = job
    planted.config(embedding_servers=far_servers())
    monkeypatch.setenv("OMP_NUM_THREADS", "99")
    code = slots.run("test", command, workers=2, env=dict(os.environ))
    assert code == 7
    expected, _ = slots.shares(os.sched_getaffinity(0), 3)
    share = expected[0]
    threads = max(1, len(share) // 2)
    for record in runs():
        assert record["cpus"] == share, record
        for name in slots.THREAD_VARIABLES:
            assert record["env"][name] == str(threads), (name, record)
        assert record["env"]["GOV_HEAVY_SLOT"] == "1"
    assert [r["who"] for r in runs()] == ["job", "grandchild"]
    assert list((planted.dir / "slots").glob("slot-*.json")) == []  # the holder record goes with the job


def test_the_configured_thread_budget_replaces_the_derived_one(planted, job):
    command, runs = job
    data = planted.config(embedding_servers=far_servers())
    data["thread_budget"] = {"value": 1, "date": "2026-11-09", "source": "test"}
    (planted.dir / "gate.json").write_text(json.dumps(data))
    slots.run("rebuild", command, workers=1, env=dict(os.environ))
    assert {r["env"]["OMP_NUM_THREADS"] for r in runs()} == {"1"}


def test_a_job_waits_while_every_slot_is_taken(planted, job, monkeypatch):
    command, runs = job
    planted.config(heavy_slots=1, embedding_servers=far_servers())
    monkeypatch.setattr(slots, "WAIT_EVERY_S", 0.05)
    (planted.dir / "slots").mkdir(parents=True)
    fd = os.open(planted.dir / "slots" / "slot-1.lock", os.O_RDWR | os.O_CREAT)
    fcntl.flock(fd, fcntl.LOCK_EX)
    timer = threading.Timer(0.4, os.close, (fd,))
    began = time.monotonic()
    timer.start()
    try:
        assert slots.run("test", command, env=dict(os.environ)) == 7
    finally:
        timer.join()
    assert time.monotonic() - began >= 0.35 and runs()


def test_a_job_waits_for_memory_room_for_its_own_peak(planted, job, monkeypatch):
    command, runs = job
    planted.config(floor_bytes=GIB, trip_floor_bytes=GIB // 2, working_size_bytes=GIB, verification_peak_bytes=8 * GIB,
                   embedding_servers=far_servers())
    planted.memory(available=4 * GIB)
    monkeypatch.setattr(slots, "WAIT_EVERY_S", 0.05)
    timer = threading.Timer(0.3, planted.memory, kwargs={"available": 10 * GIB})
    timer.start()
    try:
        assert slots.run("test", command, env=dict(os.environ)) == 7
    finally:
        timer.join()


def test_a_configuration_fault_refuses_the_job_naming_it(planted, job):
    planted.config(heavy_slots=None)
    with pytest.raises(GovError) as refused:
        slots.run("test", job[0], env=dict(os.environ))
    assert "heavy_slots" in refused.value.message


def test_only_a_test_run_or_a_rebuild_takes_a_slot(planted, job):
    planted.config()
    with pytest.raises(GovError):
        slots.run("session", job[0])


# --- the trip-wire --------------------------------------------------------------------------------------------------

def _hold(planted, slot, pid, kind="test"):
    folder = planted.dir / "slots"
    folder.mkdir(parents=True, exist_ok=True)
    fd = os.open(folder / f"slot-{slot}.lock", os.O_RDWR | os.O_CREAT)
    fcntl.flock(fd, fcntl.LOCK_EX)
    (folder / f"slot-{slot}.json").write_text(json.dumps({"slot": slot, "pid": pid, "kind": kind, "tree": "/t",
                                                          "command": "x"}))
    return fd


def test_below_the_trip_floor_the_largest_heavy_job_is_stopped_and_the_stop_is_a_finding(planted, monkeypatch):
    monkeypatch.setenv("GOV_RESOURCES_PROC", "/proc")  # real processes, real memory
    values = planted.config(floor_bytes=4 * GIB, trip_floor_bytes=2 * GIB)
    values = configuration.load()["values"]
    big = subprocess.Popen([sys.executable, "-c", "b = bytearray(80 * 1024 * 1024); import time; time.sleep(60)"],
                           start_new_session=True)
    small = subprocess.Popen(["sleep", "60"], start_new_session=True)
    session = subprocess.Popen(["sleep", "60"], start_new_session=True)
    planted.session(session.pid)
    fds = []
    try:
        time.sleep(0.5)
        fds = [_hold(planted, 1, big.pid), _hold(planted, 2, small.pid, "rebuild")]
        assert slots.tripwire(values, available=3 * GIB) is None  # above the trip floor: nothing
        finding = slots.tripwire(values, available=GIB)
        assert finding["finding"] == "OOM_TRIPWIRE" and finding["stopped"]["pid"] == big.pid
        assert big.wait(timeout=10) is not None
        assert small.poll() is None and session.poll() is None  # nothing else is stopped
        [line] = (planted.dir / slots.FINDINGS).read_text().splitlines()
        assert json.loads(line)["stopped"]["pid"] == big.pid
    finally:
        for fd in fds:
            os.close(fd)
        for process in (big, small, session):
            process.kill()
            process.wait()


def test_no_heavy_job_means_nothing_is_stopped(planted):
    planted.config()
    assert slots.tripwire(configuration.load()["values"], available=1) is None


# --- the re-measure (S9, P-5, P-7) ----------------------------------------------------------------------------------

def test_the_remeasure_writes_the_three_figures_dated_with_old_and_new_side_by_side(planted, tmp_path):
    lock = tmp_path / "verify.lock"
    planted.config(verification_lock=str(lock))
    planted.process(70, rss=3 * GIB)
    planted.session(70)
    held = os.open(lock, os.O_RDWR | os.O_CREAT)
    fcntl.flock(held, fcntl.LOCK_EX)
    try:
        first = measure.sample()
    finally:
        os.close(held)
    assert first["verification"] is True and first["sessions"][0]["bytes"] == 3 * GIB
    planted.process(70, rss=GIB)
    planted.process(71, ppid=1, rss=2 * GIB, cmdline="gov rebuild")
    fd = _hold(planted, 1, 71, "rebuild")
    try:
        second = measure.sample()
    finally:
        os.close(fd)
    assert second["verification"] is False and second["jobs"] == [{"pid": 71, "kind": "rebuild", "tree": "/t",
                                                                   "bytes": 2 * GIB}]
    old = configuration.load()["values"]
    result = measure.remeasure(today=datetime.date(2026, 11, 9))
    figures = result["figures"]
    assert figures["verification_peak_bytes"]["new"]["value"] == 3 * GIB
    assert figures["working_size_bytes"]["new"]["value"] == GIB
    assert figures["rebuild_peak_bytes"]["new"]["value"] == 2 * GIB
    for key in configuration.MEASURED:
        assert figures[key]["old"]["value"] == old[key]
        assert figures[key]["new"]["date"] == "2026-11-09" and "sample" in figures[key]["new"]["source"]
    stored = json.loads((planted.dir / "gate.json").read_text())
    assert stored["rebuild_peak_bytes"]["value"] == 2 * GIB and stored["floor_bytes"]["value"] == 3 * GIB


def test_a_figure_with_no_sample_is_kept_and_said_so(planted):
    planted.config()
    result = measure.remeasure()
    assert all(change["new"] is None and change["kept"] for change in result["figures"].values())


def test_the_sample_names_an_unknown_lock_state(planted, tmp_path):
    folder = tmp_path / "locked"
    folder.mkdir()
    lock = folder / "verify.lock"
    lock.write_text("")
    lock.chmod(0)
    planted.config(verification_lock=str(lock))
    try:
        state = measure.sample()["verification"]
    finally:
        lock.chmod(0o600)
    assert state in (None, False)  # root may open it anyway; otherwise the state is named unknown
