"""The inbox (W2-121c, RT-6, RT-7): per-session message files with a read mark, under a fixture HOME only."""
from __future__ import annotations

import json
import multiprocessing
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import inbox  # noqa: E402


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("GOV_MSG_ADDRESS", raising=False)
    return tmp_path / "home"


def lines(home: Path, address: str) -> list[dict]:
    path = home / ".gov-os" / "inbox" / address / "messages.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def test_a_send_appends_one_line_and_a_read_moves_the_mark_past_it(home):
    sent = inbox.send("lead:DAEO-x", "wake", "hello", sender="cto")
    assert sent["sent"] and not sent["duplicate"]
    [message] = lines(home, "lead:DAEO-x")
    assert message["text"] == "hello" and message["from"] == "cto" and message["kind"] == "wake"
    assert message["at"].endswith("Z") and message["id"] == sent["id"]
    first = inbox.read("lead:DAEO-x")
    assert [m["text"] for m in first["messages"]] == ["hello"]
    assert inbox.read("lead:DAEO-x")["messages"] == []


def test_peek_leaves_the_mark(home):
    inbox.send("a", "notice", "n1")
    assert len(inbox.read("a", peek=True)["messages"]) == 1
    assert len(inbox.read("a", peek=True)["messages"]) == 1
    assert len(inbox.read("a")["messages"]) == 1


@pytest.mark.parametrize("bad", ["a/b", "..", "a..b", "", "-x", "x" * 129, "a b"])
def test_a_bad_address_is_refused_and_nothing_is_written(home, bad):
    with pytest.raises(inbox.InboxError) as raised:
        inbox.send(bad, "wake", "x")
    assert raised.value.code == "MSG_ADDRESS_INVALID"
    assert not (home / ".gov-os").exists()


def test_a_duplicate_id_is_not_appended(home):
    assert inbox.send("a", "wake", "x", message_id="end:1")["sent"]
    again = inbox.send("a", "wake", "x", message_id="end:1")
    assert again == {"sent": False, "duplicate": True, "id": "end:1", "to": "a"}
    assert len(lines(home, "a")) == 1


def _send_many(home: str, sender: int, count: int, same_id: bool) -> None:
    os.environ["HOME"] = home
    for n in range(count):
        inbox.send("box", "notice", f"{sender}-{n}", message_id="same" if same_id else None)


@pytest.mark.parametrize("procs,count,same,expect", [(8, 50, False, 400), (4, 5, True, 1)])
def test_concurrent_senders_give_whole_lines_each_read_once(home, procs, count, same, expect):
    ctx = multiprocessing.get_context("fork")
    workers = [ctx.Process(target=_send_many, args=(str(home), s, count, same)) for s in range(procs)]
    for w in workers:
        w.start()
    for w in workers:
        w.join(30)
    assert len(lines(home, "box")) == expect
    seen = inbox.read("box")["messages"] + inbox.read("box")["messages"]
    assert len(seen) == expect and len({m["id"] for m in seen}) == expect


def test_a_partial_last_line_is_not_read(home):
    inbox.send("a", "wake", "whole")
    path = home / ".gov-os" / "inbox" / "a" / "messages.jsonl"
    with open(path, "a") as handle:
        handle.write('{"id": "half"')
    assert [m["text"] for m in inbox.read("a")["messages"]] == ["whole"]
    with open(path, "a") as handle:
        handle.write(', "kind": "wake", "text": "rest"}\n')
    assert [m["text"] for m in inbox.read("a")["messages"]] == ["rest"]


def test_wait_returns_a_wake_at_once_and_leaves_the_mark(home):
    inbox.send("a", "wake", "go")
    found = inbox.wait("a", 5)
    assert [m["text"] for m in found] == ["go"]
    assert len(inbox.read("a", peek=True)["messages"]) == 1


def test_wait_times_out_on_notices_only(home):
    inbox.send("a", "notice", "fyi")
    started = time.monotonic()
    assert inbox.wait("a", 1.5, every=0.2) is None
    assert time.monotonic() - started >= 1.5


def test_the_command_line_send_read_wait(home, tmp_path):
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"), GOV_MSG_ADDRESS="me")
    gov = [sys.executable, "-m", "gov.cli.main", "msg"]
    done = subprocess.run([*gov, "send", "you", "wake", "hi there", "--id", "k1", "--json"], env=env,
                          capture_output=True, text=True, cwd=tmp_path)
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout)["result"] == {"sent": True, "duplicate": False, "id": "k1", "to": "you"}
    again = subprocess.run([*gov, "send", "you", "wake", "hi there", "--id", "k1"], env=env, capture_output=True,
                           text=True, cwd=tmp_path)
    assert again.returncode == 0 and "duplicate" in again.stdout
    waited = subprocess.run([*gov, "wait", "you", "--timeout", "3"], env=env, capture_output=True, text=True,
                            cwd=tmp_path)
    assert waited.returncode == 0 and "hi there" in waited.stdout
    read = subprocess.run([*gov, "read", "you"], env=env, capture_output=True, text=True, cwd=tmp_path)
    assert read.returncode == 0 and read.stdout.strip().endswith("wake me: hi there")
    assert subprocess.run([*gov, "wait", "you", "--timeout", "1"], env=env, capture_output=True,
                          cwd=tmp_path).returncode == 124
    bad = subprocess.run([*gov, "send", "../x", "wake", "t"], env=env, capture_output=True, text=True, cwd=tmp_path)
    assert bad.returncode == 1 and "MSG_ADDRESS_INVALID" in bad.stderr
    env.pop("GOV_MSG_ADDRESS")
    missing = subprocess.run([*gov, "read"], env=env, capture_output=True, text=True, cwd=tmp_path)
    assert missing.returncode == 1 and "MSG_ADDRESS_MISSING" in missing.stderr


def test_the_command_line_watch_writes_one_request_to_runtime(home, tmp_path):
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "msg", "watch", "--to", "lead:x", "--name", "job",
                           "--pid", str(os.getpid()), "--json"], env=env, capture_output=True, text=True, cwd=tmp_path)
    assert done.returncode == 0, done.stderr
    [request] = lines(home, "runtime")
    assert request["kind"] == "watch" and request["id"] == json.loads(done.stdout)["result"]["id"]
    assert request["data"]["form"] == "pid" and request["data"]["pid"] == os.getpid()
    assert request["data"]["to"] == "lead:x" and isinstance(request["data"].get("start_ticks"), int)
