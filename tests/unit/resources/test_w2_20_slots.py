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
SLEEPER = """import os, sys, time
open(sys.argv[1], "w").write(str(os.getpid()))
time.sleep(float(sys.argv[2]))
"""


def far_servers():
    """Embedding servers on CPUs no test process has, so the slots divide the whole CPU set."""
    return {"shared": {"cpus": "4000", "nice": 10}, "query": {"cpus": "4001", "nice": 0}, "date": "2026-11-01",
            "source": "test"}


@pytest.fixture
def job(tmp_path):
    script, log = tmp_path / "job.py", tmp_path / "job.jsonl"
    script.write_text(JOB)
    return [sys.executable, str(script), str(log)], lambda: [json.loads(x) for x in log.read_text().splitlines()]


def wait_for(path, seconds=10.0):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if path.exists() and path.read_text():
            return path.read_text()
        time.sleep(0.02)
    raise AssertionError(f"{path} never written")


# --- CPU sets and budgets -------------------------------------------------------------------------------------------

def test_each_slot_has_its_share_of_the_cpus_outside_the_servers():
    sets = [slots.cpu_set(range(20), 3, slot, exclude=range(12, 20))[0] for slot in (1, 2, 3)]
    assert sets == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
    sets = [slots.cpu_set(range(20), 3, slot)[0] for slot in (1, 2, 3)]
    assert sets == [list(range(0, 6)), list(range(6, 12)), list(range(12, 18))]  # max(1, 20 // 3) = 6 each


def test_servers_covering_every_cpu_are_not_excluded_and_it_is_said():
    share, note = slots.cpu_set(range(4), 2, 1, exclude=range(4))
    assert share == [0, 1] and "cover every CPU" in note


def test_more_slots_than_cpus_still_gives_each_slot_one_cpu():
    assert [slots.cpu_set([3, 5], 3, slot)[0] for slot in (1, 2, 3)] == [[3], [5], [3]]


@pytest.mark.parametrize("share,workers,configured,expected", [(list(range(6)), 6, None, 1), (list(range(7)), 2, None, 3),
                                                               ([1], 4, None, 1), (list(range(8)), 1, 3, 3)])
def test_the_thread_budget_is_the_share_over_the_workers_at_least_one(share, workers, configured, expected):
    assert slots.budget(share, workers, configured) == expected


def test_the_callers_value_never_stands():
    env = slots.job_env({"OMP_NUM_THREADS": "999", "MKL_NUM_THREADS": "1", "GOMAXPROCS": "x"}, [0, 1, 2, 3], 2, 2, 1)
    assert all(env[name] == "2" for name in slots.THREAD_VARIABLES)
    assert (env["GOV_HEAVY_CPUS"], env["GOV_HEAVY_SLOT"], env["PYTEST_XDIST_AUTO_NUM_WORKERS"]) == ("0-3", "1", "2")


# --- the run --------------------------------------------------------------------------------------------------------

def test_a_job_runs_in_its_slot_confined_with_its_budget_and_every_child_inherits_both(planted, job, monkeypatch):
    command, runs = job
    planted.config(embedding_servers=far_servers())
    monkeypatch.setenv("OMP_NUM_THREADS", "999")
    code = slots.run("test", command, workers=2)
    assert code == 7
    share, _ = slots.cpu_set(os.sched_getaffinity(0), 3, 1)
    threads = max(1, len(share) // 2)
    for record in runs():
        assert record["cpus"] == share, record
        for name in slots.THREAD_VARIABLES:
            assert record["env"][name] == str(threads), (name, record)
    assert [r["who"] for r in runs()] == ["job", "grandchild"]
    assert list((planted.dir / "slots").glob("slot-*.json")) == []  # the holder record goes with the job


def test_the_configured_thread_budget_replaces_the_derived_one(planted, job):
    command, runs = job
    planted.config(embedding_servers=far_servers(), thread_budget=1)
    slots.run("rebuild", command, workers=1)
    assert {r["env"]["OMP_NUM_THREADS"] for r in runs()} == {"1"}


def test_a_job_waits_while_every_slot_is_taken(planted, job):
    command, runs = job
    planted.config(heavy_slots=1, embedding_servers=far_servers())
    (planted.dir / "slots").mkdir(parents=True)
    fd = os.open(planted.dir / "slots" / "slot-1.lock", os.O_RDWR | os.O_CREAT)
    fcntl.flock(fd, fcntl.LOCK_EX)
    timer = threading.Timer(0.5, os.close, (fd,))
    began = time.monotonic()
    timer.start()
    try:
        assert slots.run("test", command) == 7
    finally:
        timer.join()
    assert time.monotonic() - began >= 0.45 and runs()


def test_a_job_runs_whatever_the_memory_reading_says(planted, job):
    command, runs = job
    planted.config(embedding_servers=far_servers())
    planted.memory(available=1)
    assert slots.run("test", command) == 7 and runs()


def test_two_held_slots_have_disjoint_cpu_sets_and_are_in_the_reading(planted, tmp_path):
    from gov.resources.gate import read
    planted.config(embedding_servers=far_servers())
    script = tmp_path / "sleeper.py"
    script.write_text(SLEEPER)
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)}
    runners, marks = [], [tmp_path / "a.pid", tmp_path / "b.pid"]
    try:
        for mark in marks:
            runners.append(subprocess.Popen([sys.executable, "-c", "import sys; from gov.resources.slots import run; "
                                             "sys.exit(run('test', sys.argv[1:]))", sys.executable, str(script),
                                             str(mark), "30"], env=env))
        for mark in marks:
            wait_for(mark)
        held = read(False)["slots"]
        assert held["total"] == 3 and len(held["held"]) == 2
        sets = [set(configuration.parse_cpus(h["cpus"])) for h in held["held"]]
        assert not sets[0] & sets[1] or len(os.sched_getaffinity(0)) < 2
        assert {h["kind"] for h in held["held"]} == {"test"}
    finally:
        for runner in runners:
            runner.terminate()
            runner.wait(timeout=20)


def test_a_rebuild_excludes_only_another_rebuild_of_the_same_tree(planted, tmp_path):
    planted.config(embedding_servers=far_servers())
    script = tmp_path / "sleeper.py"
    script.write_text(SLEEPER)
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)}
    trees = {"a1": tmp_path / "tree-a", "a2": tmp_path / "tree-a", "b": tmp_path / "tree-b"}
    for tree in trees.values():
        tree.mkdir(exist_ok=True)
    runners = {}
    try:
        for name in ("a1", "b", "a2"):
            runners[name] = subprocess.Popen(
                [sys.executable, "-c", "import sys; from gov.resources.slots import run; "
                 "sys.exit(run('rebuild', sys.argv[2:], tree=sys.argv[1]))", str(trees[name]), sys.executable,
                 str(script), str(tmp_path / f"{name}.pid"), "2" if name == "a1" else "0.1"], env=env)
            if name == "a1":
                wait_for(tmp_path / "a1.pid")
        wait_for(tmp_path / "b.pid")  # another tree's rebuild runs at once
        assert not (tmp_path / "a2.pid").exists()  # the same tree's waits
        wait_for(tmp_path / "a2.pid", 20)
        assert runners["a1"].wait(timeout=20) == 0
    finally:
        for runner in runners.values():
            runner.terminate()
            runner.wait(timeout=20)


def test_a_missing_slot_count_refuses_the_job_naming_it(planted, job):
    planted.config(heavy_slots=None)
    with pytest.raises(GovError) as refused:
        slots.run("test", job[0])
    assert "heavy_slots" in refused.value.message


def test_only_a_test_run_or_a_rebuild_takes_a_slot(planted, job):
    planted.config()
    with pytest.raises(GovError):
        slots.run("session", job[0])


# --- the trip-wire --------------------------------------------------------------------------------------------------

def test_below_the_trip_floor_the_largest_heavy_job_is_stopped_and_the_stop_is_a_finding(planted, tmp_path, monkeypatch):
    monkeypatch.setenv("GOV_RESOURCES_PROC", "/proc")  # real processes, real memory
    planted.config(embedding_servers=far_servers(), memory_floor_bytes=4 * GIB, oom_floor_bytes=2 * GIB)
    values = configuration.load()["values"]
    big_job = tmp_path / "big.py"
    big_job.write_text("import os, sys, time\nb = bytearray(120 * 1024 * 1024)\nb[::4096] = b'x' * len(b[::4096])\n"
                       "open(sys.argv[1], 'w').write(str(os.getpid()))\ntime.sleep(60)\n")
    small_job = tmp_path / "small.py"
    small_job.write_text(SLEEPER)
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)}
    starter = "import sys; from gov.resources.slots import run; sys.exit(run(sys.argv[1], sys.argv[2:]))"
    big = subprocess.Popen([sys.executable, "-c", starter, "test", sys.executable, str(big_job),
                            str(tmp_path / "big.pid")], env=env)
    small = subprocess.Popen([sys.executable, "-c", starter, "rebuild", sys.executable, str(small_job),
                              str(tmp_path / "small.pid"), "60"], env=env)
    session = subprocess.Popen(["sleep", "60"])
    planted.session(session.pid)
    try:
        big_pid, small_pid = int(wait_for(tmp_path / "big.pid")), int(wait_for(tmp_path / "small.pid"))
        assert slots.tripwire(values, available=3 * GIB)["stopped"] is None  # at or above the floor: nothing
        assert slots.tripwire(values, available=2 * GIB)["stopped"] is None
        result = slots.tripwire(values, available=GIB)
        stopped = result["stopped"]
        assert stopped["pid"] == big.pid and stopped["command_pid"] == big_pid and "big.py" in stopped["command"]
        assert big.wait(timeout=20) is not None
        with pytest.raises(ProcessLookupError):
            os.kill(big_pid, 0)
        os.kill(small_pid, 0)  # nothing else is stopped
        assert small.poll() is None and session.poll() is None
        [line] = (planted.dir / slots.FINDINGS).read_text().splitlines()
        assert json.loads(line)["stopped"]["pid"] == big.pid
    finally:
        for process in (big, small, session):
            process.terminate()
            process.wait(timeout=20)


def test_no_heavy_job_means_nothing_is_stopped(planted):
    planted.config()
    assert slots.tripwire(configuration.load()["values"], available=1)["stopped"] is None


# --- the re-measure (S9, P-5, P-7) ----------------------------------------------------------------------------------

def _hold(planted, slot, pid, kind="test"):
    folder = planted.dir / "slots"
    folder.mkdir(parents=True, exist_ok=True)
    fd = os.open(folder / f"slot-{slot}.lock", os.O_RDWR | os.O_CREAT)
    fcntl.flock(fd, fcntl.LOCK_EX)
    (folder / f"slot-{slot}.json").write_text(json.dumps({"slot": slot, "pid": pid, "kind": kind, "tree": "/t",
                                                          "command": "x"}))
    return fd


def test_the_remeasure_writes_the_three_figures_dated_with_old_and_new_side_by_side(planted, tmp_path):
    lock = tmp_path / "verify.lock"
    planted.config(verification_lock=str(lock))
    planted.process(70, rss=3 * GIB)
    planted.session(70)
    held = os.open(lock, os.O_RDWR | os.O_CREAT)
    fcntl.flock(held, fcntl.LOCK_EX)
    try:
        first = measure.sample()["samples"]
    finally:
        os.close(held)
    assert first == [{"pid": 70, "tree_memory_bytes": 3 * GIB, "verification": True, "ticket": "DAEO-x",
                      "role": "engineer"}]
    planted.process(70, rss=GIB)
    planted.process(71, ppid=1, rss=2 * GIB, cmdline="gov rebuild")
    fd = _hold(planted, 1, 71, "rebuild")
    try:
        second = measure.sample()["samples"]
    finally:
        os.close(fd)
    assert {(s["pid"], s["tree_memory_bytes"], s["verification"], s.get("kind")) for s in second} == {
        (70, GIB, False, None), (71, 2 * GIB, False, "rebuild")}
    old = json.loads((planted.dir / "gate.json").read_text())
    result = measure.remeasure(today=datetime.date(2026, 11, 9))
    assert result["new"]["verification_peak_bytes"]["value"] == 3 * GIB
    assert result["new"]["working_size_bytes"]["value"] == GIB  # the slot holder's 2 GiB is no working size
    assert result["new"]["rebuild_peak_bytes"]["value"] == 2 * GIB
    for key in configuration.MEASURED:
        assert result["old"][key] == old[key]
        assert result["new"][key]["date"] == "2026-11-09" and "sample" in result["new"][key]["source"]
    stored = json.loads((planted.dir / "gate.json").read_text())
    assert stored["rebuild_peak_bytes"]["value"] == 2 * GIB and stored["memory_floor_bytes"] == old["memory_floor_bytes"]


def test_a_figure_with_no_sample_is_kept(planted):
    planted.config()
    result = measure.remeasure()
    assert result["new"] == result["old"]
