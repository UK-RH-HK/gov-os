"""The watch pass (W2-121c, RT-2, RT-7, F1, F2): one machine-wide pass over a fixture HOME, one state file."""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import inbox, runtime  # noqa: E402
from gov.resources import machine  # noqa: E402


@pytest.fixture
def home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / ".gov-os" / "machine" / "sessions").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    monkeypatch.setenv("GOV_RESOURCES_NPROC", "8")
    for name in ("GOV_RESOURCES_PROC", "GOV_RUNTIME_NOW", "GOV_MSG_ADDRESS", "GOV_RESOURCES_MEMINFO"):
        monkeypatch.delenv(name, raising=False)
    return home


def messages(address: str) -> list[dict]:
    return inbox.read(address, peek=True)["messages"]


def ended_process() -> tuple[int, dict]:
    child = subprocess.Popen(["sleep", "0.2"])
    found = machine.identity(child.pid)
    child.wait()
    return child.pid, found


def plant_entry(home: Path, pid: int, found: dict | None, **extra) -> dict:
    entry = {"pid": pid, "repository": "/r", "ticket": "DAEO-x", "role": "engineer",
             "started": "2026-11-17T00:00:00+00:00", **extra}
    if found:
        entry.update(boot=found["boot"], start_ticks=found["start_ticks"])
    (home / ".gov-os" / "machine" / "sessions" / f"{pid}.json").write_text(json.dumps(entry))
    return entry


def test_five_passes_leave_state_and_log_only(home):
    for _ in range(5):
        code, state = runtime.watch_pass()
        assert code == 0
    folder = home / ".gov-os" / "runtime"
    assert sorted(p.name for p in folder.iterdir()) == ["log.jsonl", "state.json"]
    data = json.loads((folder / "state.json").read_text())
    assert data["format"] == 1 and data["limits"]["sessions_max"] == 4 and data["machine"]["cpus"] == 8


def test_a_held_lock_exits_4_and_writes_nothing(home):
    runtime.watch_pass()
    folder = home / ".gov-os" / "runtime"
    before = (folder / "state.json").read_bytes()
    fd = os.open(folder, os.O_RDONLY)
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        assert runtime.watch_pass()[0] == 4
    finally:
        os.close(fd)
    assert (folder / "state.json").read_bytes() == before


def test_an_entry_dead_at_the_first_pass_is_one_wake_to_its_notify(home):
    pid, found = ended_process()
    plant_entry(home, pid, found, notify="lead:DAEO-x")
    for _ in range(6):
        runtime.watch_pass()
    [message] = messages("lead:DAEO-x")
    assert message["kind"] == "wake" and message["id"] == f"end:{found['boot']}:{pid}:{found['start_ticks']}"


def test_an_end_between_two_passes_goes_to_cto_without_notify(home):
    child = subprocess.Popen(["sleep", "30"])
    plant_entry(home, child.pid, machine.identity(child.pid))
    runtime.watch_pass()
    assert messages("cto") == []
    child.kill()
    child.wait()
    runtime.watch_pass()
    assert len(messages("cto")) == 1


def test_a_tracked_session_whose_entry_went_is_still_messaged(home):
    child = subprocess.Popen(["sleep", "30"])
    found = machine.identity(child.pid)
    plant_entry(home, child.pid, found)
    runtime.watch_pass()
    (home / ".gov-os" / "machine" / "sessions" / f"{child.pid}.json").unlink()
    child.kill()
    child.wait()
    runtime.watch_pass()
    runtime.watch_pass()
    assert [m["id"] for m in messages("cto")] == [f"end:{found['boot']}:{child.pid}:{found['start_ticks']}"]


def test_an_end_the_launcher_messaged_adds_none(home):
    pid, found = ended_process()
    entry = plant_entry(home, pid, found)
    inbox.send("cto", "wake", "the launcher's", message_id=runtime.end_id(entry))
    runtime.watch_pass()
    assert len(messages("cto")) == 1


def watch(**data) -> str:
    return inbox.send("runtime", "watch", "w", data=data)["id"]


def test_exit_file_and_pid_watches_send_once(home, tmp_path):
    exit_file = tmp_path / "job.exit"
    request = watch(form="exit-file", path=str(exit_file), to="lead:y", name="job")
    pid, found = ended_process()
    watch(form="pid", pid=pid, boot=found["boot"], start_ticks=found["start_ticks"], to="lead:y", name="p")
    runtime.watch_pass()
    assert len(messages("lead:y")) == 1  # the pid watch; the exit file is not there yet
    exit_file.write_text("3\n")
    for _ in range(5):
        runtime.watch_pass()
    found = messages("lead:y")
    assert len(found) == 2
    by_id = {m["id"]: m for m in found}
    assert "3" in by_id[f"watch:{request}"]["text"]
    assert inbox.pending("runtime")[0] == []


def test_a_stall_sends_once_and_pushes_once_per_incident(home, tmp_path, monkeypatch):
    transcript, pushed = tmp_path / "t.jsonl", tmp_path / "pushed.txt"
    transcript.write_text("x\n")
    stub = tmp_path / "push.sh"
    stub.write_text(f"#!/bin/sh\necho \"$1\" >> {pushed}\n")
    stub.chmod(0o755)
    watch(form="transcript", path=str(transcript), to="cto", name="CTO", push=str(stub))
    noon = time.mktime((2026, 11, 17, 12, 0, 0, 0, 0, -1))
    monkeypatch.setenv("GOV_RUNTIME_NOW", time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(noon)))
    os.utime(transcript, (noon - 4000, noon - 4000))
    runtime.watch_pass()
    for _ in range(3):
        runtime.watch_pass()
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not pushed.exists():
        time.sleep(0.05)
    assert len(messages("cto")) == 1 and "66" in messages("cto")[0]["text"]
    os.utime(transcript, (noon - 10, noon - 10))
    runtime.watch_pass()
    os.utime(transcript, (noon - 5000, noon - 5000))
    runtime.watch_pass()
    runtime.watch_pass()
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and len(pushed.read_text().splitlines()) < 2:
        time.sleep(0.05)
    time.sleep(0.2)
    assert len(messages("cto")) == 2 and len(pushed.read_text().splitlines()) == 2


@pytest.mark.parametrize("silent_min,expect", [(90, 0), (130, 1)])
def test_the_night_limit(home, tmp_path, monkeypatch, silent_min, expect):
    transcript = tmp_path / "t.jsonl"
    transcript.write_text("x\n")
    watch(form="transcript", path=str(transcript), to="cto", name="CTO")
    night = time.mktime((2026, 11, 17, 3, 0, 0, 0, 0, -1))
    monkeypatch.setenv("GOV_RUNTIME_NOW", time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(night)))
    os.utime(transcript, (night - silent_min * 60, night - silent_min * 60))
    runtime.watch_pass()
    assert len(messages("cto")) == expect


def test_faults_are_problems_and_the_pass_goes_on(home, tmp_path):
    (home / ".gov-os" / "machine" / "sessions" / "77.json").write_text("{not json")
    watch(form="transcript", path=str(tmp_path / "gone.jsonl"), to="cto", name="CTO")
    exit_file = tmp_path / "e.exit"
    exit_file.write_text("0\n")
    watch(form="exit-file", path=str(exit_file), to="lead:z", name="job")
    code, state = runtime.watch_pass()
    assert code == 0 and len(messages("lead:z")) == 1
    text = " ".join(state["problems"])
    assert "77.json" in text and "gone.jsonl" in text
    log = (home / ".gov-os" / "runtime" / "log.jsonl").read_text()
    assert '"problem"' in log and "77.json" in log
