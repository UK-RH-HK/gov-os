"""The relaunch of a session that died (W2-205, RT-5, F1): off by default, once per ticket and boot, claimed in a file
before the launch, never for a session that returned. The launch itself is replaced by a recorder."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import inbox, relaunch, runtime  # noqa: E402
from gov.resources import machine  # noqa: E402

SESSION = "11111111-2222-3333-4444-555555555555"


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


@pytest.fixture
def launches(monkeypatch):
    found = []
    monkeypatch.setattr(relaunch, "spawn", lambda place, entry: found.append(dict(entry)) or 4242)
    monkeypatch.setattr(relaunch, "next_step", lambda entry: "S")
    return found


def config(home: Path, text: str) -> None:
    folder = home / ".gov-os" / "runtime"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "config.json").write_text(text)


def dead(home: Path, **extra) -> dict:
    child = subprocess.Popen(["sleep", "0.2"])
    found = machine.identity(child.pid)
    child.wait()
    entry = {"pid": child.pid, "repository": "/r", "ticket": "DAEO-x", "role": "engineer", "notify": "lead:DAEO-x",
             "address": "engineer:DAEO-x", "started": "2026-11-17T00:00:00+00:00", "session_id": SESSION,
             "boot": found["boot"], "start_ticks": found["start_ticks"], **extra}
    entry = {k: v for k, v in entry.items() if v is not None}
    (home / ".gov-os" / "machine" / "sessions" / f"{child.pid}.json").write_text(json.dumps(entry))
    return entry


def log(home: Path) -> list[dict]:
    path = home / ".gov-os" / "runtime" / "log.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()]


def messages(address="lead:DAEO-x") -> list[dict]:
    return inbox.read(address, peek=True)["messages"]


def test_the_key_absent_false_unreadable_or_empty_is_off_and_gives_slice_1s_message(home, launches):
    entry = dead(home)
    for text in (None, '{"relaunch": false}', "not json", "{}", '{"relaunch": "yes"}'):
        if text is not None:
            config(home, text)
        runtime.watch_pass()
        assert launches == [] and not (home / ".gov-os" / "runtime" / "relaunch").exists()
    assert [m["id"] for m in messages()] == [runtime.end_id(entry)]
    assert not [e for e in log(home) if e["event"] == "relaunched"]


def test_an_unreadable_config_is_named_as_a_problem(home, launches):
    dead(home)
    config(home, "not json")
    code, state = runtime.watch_pass()
    assert any("config.json" in p for p in state["problems"])


def test_a_death_is_claimed_then_relaunched_once_and_logged(home, launches):
    config(home, '{"relaunch": true}')
    entry = dead(home)
    runtime.watch_pass()
    runtime.watch_pass()
    assert len(launches) == 1 and launches[0]["session_id"] == SESSION
    assert [e["id"] for e in log(home) if e["event"] == "relaunched"] == [relaunch.claim_id(entry)]
    assert (home / ".gov-os" / "runtime" / "relaunch" / relaunch.claim_id(entry)).is_file()
    assert messages() == []  # a relaunch is no end to tell: the next end is the relaunched session's own


def test_a_claim_left_by_a_pass_killed_before_its_log_line_stops_a_second_launch(home, launches):
    config(home, '{"relaunch": true}')
    entry = dead(home)
    assert relaunch.claim(home / ".gov-os" / "runtime", entry)
    runtime.watch_pass()
    assert launches == [] and messages() == []


def test_a_second_death_in_the_boot_is_one_died_twice_message_and_no_launch(home, launches):
    config(home, '{"relaunch": true}')
    dead(home)
    runtime.watch_pass()
    second = dead(home)
    for _ in range(3):
        runtime.watch_pass()
    assert len(launches) == 1
    [message] = messages()
    assert message["id"] == f"died-twice:DAEO-x:{second['boot']}" and "died twice" in message["text"]


def test_an_entry_with_no_session_id_is_one_message_saying_it_cannot_resume(home, launches):
    config(home, '{"relaunch": true}')
    dead(home, session_id=None)
    runtime.watch_pass()
    runtime.watch_pass()
    [message] = messages()
    assert "cannot resume" in message["text"] and launches == []


def test_a_return_is_no_death(home, launches):
    config(home, '{"relaunch": true}')
    entry = dead(home)
    inbox.send("lead:DAEO-x", "wake", "ended with exit code 0", sender=entry["address"],
               message_id=runtime.end_id(entry))
    runtime.watch_pass()
    assert launches == []


def test_an_exit_file_holding_0_is_a_return_and_one_holding_another_code_is_not(home, launches, tmp_path):
    config(home, '{"relaunch": true}')
    done = tmp_path / "exit-0"
    done.write_text("0\n")
    dead(home, exit_file=str(done))
    runtime.watch_pass()
    assert launches == []
    failed = tmp_path / "exit-1"
    failed.write_text("1\n")
    dead(home, exit_file=str(failed), ticket="DAEO-y")
    runtime.watch_pass()
    assert [e["ticket"] for e in launches] == ["DAEO-y"]


def test_a_session_whose_launcher_still_runs_is_ending_not_dead(home, launches):
    config(home, '{"relaunch": true}')
    keeper = subprocess.Popen(["sleep", "30"])
    try:
        dead(home, launcher_pid=keeper.pid)
        runtime.watch_pass()
        assert launches == [] and messages() == []
    finally:
        keeper.kill()
        keeper.wait()


def test_a_launch_that_cannot_start_keeps_the_claim_and_tells_the_launcher(home, monkeypatch):
    config(home, '{"relaunch": true}')

    def broken(place, entry):
        raise OSError("no such file")
    monkeypatch.setattr(relaunch, "spawn", broken)
    entry = dead(home)
    runtime.watch_pass()
    runtime.watch_pass()
    assert (home / ".gov-os" / "runtime" / "relaunch" / relaunch.claim_id(entry)).is_file()
    [message] = messages()
    assert "could not be relaunched" in message["text"]


def test_the_relaunch_text_names_the_checkpoints_next_step(monkeypatch):
    monkeypatch.setattr(relaunch, "next_step", lambda entry: "write the digest")
    assert relaunch.text({"ticket": "DAEO-x"}) == "Resume at the recorded next step (DAEO-x): write the digest"


def test_a_ticket_with_no_checkpoint_still_gets_a_text(tmp_path):
    found = relaunch.next_step({"repository": str(tmp_path), "ticket": "DAEO-x"})
    assert found == relaunch.FALLBACK_STEP


def test_the_spawned_launch_is_gov_launch_with_resume_and_the_text_last(home, tmp_path, monkeypatch):
    seen = {}

    class Child:
        pid = 77

    def popen(command, **kwargs):
        seen.update(command=command, **kwargs)
        return Child()
    monkeypatch.setattr(relaunch.subprocess, "Popen", popen)
    monkeypatch.setattr(relaunch, "next_step", lambda entry: "S")
    entry = {"role": "engineer", "ticket": "DAEO-x", "repository": str(tmp_path), "session_id": SESSION,
             "notify": "lead:DAEO-x"}
    assert relaunch.spawn(home / ".gov-os" / "runtime", entry) == 77
    command = seen["command"]
    assert command[1:3] == ["-m", "gov.cli.main"] and command[3:6] == ["launch", "engineer", "DAEO-x"]
    assert command[command.index("--") + 1:] == ["--resume", SESSION, "Resume at the recorded next step (DAEO-x): S"]
    assert seen["cwd"] == str(tmp_path) and seen["start_new_session"] is True
    assert seen["env"]["GOV_MSG_ADDRESS"] == "lead:DAEO-x"
