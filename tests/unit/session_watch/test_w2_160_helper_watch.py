"""`gov session-watch helper-watch` unit cases beyond the acceptance suite: the `x`-open name collision, the window edge,
the empty exit file, a text canary, a configuration error."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from gov.cli.main import main

NOW = 1_800_000_000.0
CANARY = "CANARY-7f3a-never-copied"


def stamp(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat().replace("+00:00", "Z")


class Plant:
    def __init__(self, tmp_path, monkeypatch):
        self.root = tmp_path / "project"
        self.agents = tmp_path / "agents"
        folder = self.root / ".gov-runtime" / "session-watch"
        folder.mkdir(parents=True)
        (folder / "session.txt").write_text("sess-1\n")
        self.agents.mkdir()
        monkeypatch.setenv("GOV_SESSION_WATCH_NOW", str(NOW))
        monkeypatch.setenv("GOV_SESSION_WATCH_SUBAGENTS", str(self.agents))
        monkeypatch.setenv("HOME", str(tmp_path / "home"))
        self.inbox = self.root / ".gov-runtime" / "dispatch" / "inbox"

    def helper(self, ident: str, age_s: float, error: bool = False, finished: bool = False) -> None:
        entry = {"type": "assistant", "timestamp": stamp(NOW - age_s),
                 "message": {"model": "other", "content": [{"type": "text", "text": CANARY}]}}
        if error:
            entry["isApiErrorMessage"] = True
            entry["apiError"] = {"message": CANARY}
        (self.agents / f"agent-{ident}.jsonl").write_text(json.dumps(entry) + "\n")
        (self.agents / f"agent-{ident}.meta.json").write_text(json.dumps({"finished": finished, "description": "d"}))

    def watch(self, capsys, *extra) -> tuple[int, str, str]:
        code = main(["session-watch", "helper-watch", "--once", "--root", str(self.root), *extra])
        out = capsys.readouterr()
        return code, out.out, out.err

    def items(self) -> list:
        return sorted(self.inbox.glob("*-helper-watch*.txt")) if self.inbox.is_dir() else []


def test_two_conditions_in_one_second_get_distinct_items(tmp_path, monkeypatch, capsys):
    plant = Plant(tmp_path, monkeypatch)
    plant.helper("a", 60, error=True)
    plant.helper("b", 60, error=True)
    code, out, err = plant.watch(capsys)
    names = [p.name for p in plant.items()]
    assert code == 0 and len(names) == 2 and any(n.endswith("-helper-watch-2.txt") for n in names)
    assert any(n.endswith("-helper-watch.txt") for n in names)
    assert out.count("HELPER_WATCH item ") == 2


def test_the_window_edge_and_the_stale_edge(tmp_path, monkeypatch, capsys):
    plant = Plant(tmp_path, monkeypatch)
    plant.helper("inside", 24 * 3600, error=True)          # exactly at the window: looked at
    plant.helper("outside", 24 * 3600 + 1, error=True)     # one second past it: skipped
    plant.helper("fresh", 30 * 60 - 1)                     # not yet 30 minutes silent
    plant.helper("silent", 30 * 60)                        # 30 minutes: stalled
    plant.helper("done", 3 * 3600, finished=True)          # finished: never stalled
    plant.watch(capsys)
    text = "".join(p.read_text() for p in plant.items())
    assert "helper inside" in text and "helper silent" in text
    assert "helper outside" not in text and "helper fresh" not in text and "helper done" not in text


def test_a_message_text_is_never_copied(tmp_path, monkeypatch, capsys):
    plant = Plant(tmp_path, monkeypatch)
    plant.helper("a", 60, error=True)
    code, out, err = plant.watch(capsys)
    everything = out + err + "".join(p.read_text() for p in plant.root.rglob("*") if p.is_file()
                                     and "session.txt" not in p.name and ".jsonl" not in p.name)
    assert CANARY not in everything and "api-error" in everything


def test_a_second_pass_adds_nothing_and_the_state_keeps_its_keys(tmp_path, monkeypatch, capsys):
    plant = Plant(tmp_path, monkeypatch)
    plant.helper("a", 60, error=True)
    plant.watch(capsys)
    state_file = plant.root / ".gov-runtime" / "session-watch" / "helper-watch-state.json"
    before = json.loads(state_file.read_text())
    (plant.agents / "agent-a.jsonl").unlink()  # the condition drops out of the next look
    code, out, err = plant.watch(capsys)
    assert len(plant.items()) == 1 and "HELPER_WATCH item" not in out
    assert json.loads(state_file.read_text()) == before


def test_an_empty_exit_file_is_not_an_ending_but_a_gone_pid_is_named(tmp_path, monkeypatch, capsys):
    plant = Plant(tmp_path, monkeypatch)
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    base = plant.root / ".gov-runtime" / "scratch" / "job"
    base.parent.mkdir(parents=True)
    (base.parent / "job.pid").write_text(f"{child.pid}\n")
    (base.parent / "job.exit").write_text("")
    for name in ("job.pid", "job.exit"):
        os.utime(base.parent / name, (NOW, NOW))
    plant.watch(capsys)
    assert len(plant.items()) == 1 and "gone without its exit file" in plant.items()[0].read_text()


def test_a_configuration_error_is_exit_1_and_named(tmp_path, monkeypatch, capsys):
    plant = Plant(tmp_path, monkeypatch)
    config = plant.root / "governance" / "project"
    config.mkdir(parents=True)
    (config / "session-watch.yaml").write_text("session_watch:\n  pid_globs: 5\n")
    code, out, err = plant.watch(capsys)
    assert code == 1 and "pid_globs" in err and plant.items() == []
