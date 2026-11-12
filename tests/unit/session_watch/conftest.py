"""A planted project for `gov session-watch stop-check`: session file, configuration, process list, status, pid files,
transcript and plan stub, all under tmp_path. Never /proc, never a live session, never a registered hook."""

from __future__ import annotations

import io
import json
import os
import stat
from pathlib import Path

import pytest

NOW = 1_800_000_000.0
HOUR = 3600


class Hook:
    def __init__(self, tmp_path: Path, monkeypatch, capsys):
        self.tmp, self.monkeypatch, self.capsys = tmp_path, monkeypatch, capsys
        self.root = tmp_path / "project"
        self.folder = self.root / ".gov-runtime" / "session-watch"
        self.folder.mkdir(parents=True)
        self.sid = "sess-1"
        self.turn_n = 0
        self.transcript_file = tmp_path / "transcript.jsonl"
        self.entries: list[dict] = []
        self.new_turn()
        monkeypatch.setenv("GOV_SESSION_WATCH_NOW", str(NOW))
        monkeypatch.setenv("GOV_SESSION_WATCH_PS", "[]")
        monkeypatch.setenv("GOV_SESSION_WATCH_SUBAGENTS", str(tmp_path / "no-agents"))
        monkeypatch.setenv("GOV_SESSION_WATCH_TASKS", str(tmp_path / "no-tasks"))
        self.session(self.sid)
        self.plan("# batch 1\n")

    # -- planting -----------------------------------------------------------------------------------------------
    def session(self, text: str | None) -> None:
        if text is not None:
            (self.folder / "session.txt").write_text(text + "\n")

    def config(self, text: str) -> None:
        file = self.root / "governance" / "project" / "session-watch.yaml"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text)

    def touch(self, path: Path, age_s: float, text: str = "x") -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        os.utime(path, (NOW - age_s, NOW - age_s))
        return path

    def standby(self, age_s: float) -> None:
        self.touch(self.folder / "standby.txt", age_s)

    def procs(self, *entries: dict) -> None:
        self.monkeypatch.setenv("GOV_SESSION_WATCH_PS", json.dumps(list(entries)))

    def status(self, data: dict, age_s: float = 10) -> None:
        self.touch(self.root / ".gov-runtime" / "dispatch" / "status.json", age_s, json.dumps(data))

    def pidfile(self, name: str, pid: int, exit_file: bool = False) -> Path:
        path = self.touch(self.root / ".gov-runtime" / "jobs" / f"{name}.pid", 60, f"{pid}\n")
        if exit_file:
            self.touch(path.with_suffix(".exit"), 30, "0")
        return path

    def plan(self, ready: str, code: int = 0, sleep: float = 0) -> None:
        ready_file = self.tmp / "ready.txt"
        ready_file.write_text(ready)
        stub = self.tmp / "gov-stub"
        stub.write_text(f"#!/bin/sh\nsleep {sleep}\ncp {ready_file} \"$5\"\nexit {code}\n")
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        self.monkeypatch.setenv("GOV_SESSION_WATCH_GOV", str(stub))

    def ready_of(self, *tickets: str) -> str:
        return "# batch 1\n" + "".join(f"{t}-name {t} brief.md log.json\n" for t in tickets) + "# batch 2\nlater L brief log\n"

    # -- the transcript -----------------------------------------------------------------------------------------
    def new_turn(self, **extra) -> str:
        self.turn_n += 1
        key = f"turn-{self.turn_n}"
        self.entries.append({"type": "user", "uuid": key, "message": {"role": "user", "content": "go"}, **extra})
        self.write_transcript()
        return key

    def say(self, text: str) -> None:
        self.entries.append({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}})
        self.write_transcript()

    def write_transcript(self) -> None:
        self.transcript_file.write_text("".join(json.dumps(e) + "\n" for e in self.entries))

    # -- running the check --------------------------------------------------------------------------------------
    def run(self, check: str, *, active: bool = False, session: str | None = None, extra: dict | None = None,
            stdin: str | None = None) -> dict | None:
        from gov.cli.main import main

        data = {"session_id": session or self.sid, "transcript_path": str(self.transcript_file),
                "stop_hook_active": active, **(extra or {})}
        self.monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(data) if stdin is None else stdin))
        code = main(["session-watch", "stop-check", check, "--root", str(self.root)])
        out = self.capsys.readouterr().out
        assert code == 0 and len(out.strip().splitlines()) <= 1, (code, out)
        return json.loads(out) if out.strip() else None

    def log(self) -> str:
        file = self.folder / "stop-check.log"
        return file.read_text() if file.exists() else ""


@pytest.fixture
def hook(tmp_path, monkeypatch, capsys) -> Hook:
    return Hook(tmp_path, monkeypatch, capsys)


WAITER_CONFIG = "session_watch:\n  waiter_commands: ['inbox-wait', 'other-wait']\n"
