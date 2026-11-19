"""``gov msg digest`` and ``gov msg audit`` (W2-205, RT-6), and the kind ``relay``, through the command module."""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import inbox  # noqa: E402
from gov.msg import command  # noqa: E402


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("GOV_MSG_ADDRESS", raising=False)
    return tmp_path / "home"


def plant(to: str, kind: str, at: str, *, sender="cto", message_id=None, text="t") -> str:
    folder = inbox.folder(to)
    folder.mkdir(parents=True, exist_ok=True)
    ident = message_id or f"{to}-{at}-{kind}-{sender}"
    with open(folder / "messages.jsonl", "a") as handle:
        handle.write(json.dumps({"id": ident, "at": at, "from": sender, "to": to, "kind": kind, "text": text}) + "\n")
    return ident


def days_ago(days: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))


def run(action: str, **fields):
    args = argparse.Namespace(**{"action": action, "json": False, "session": "", "role": None, "address": None,
                                 "day": None, "days": None, **fields})
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = command.run(REPO, args, {})
    return code, out.getvalue(), err.getvalue()


def test_send_accepts_the_kind_relay_and_a_relay_is_never_a_wake(home):
    inbox.send("cto", "relay", "from the owner", sender="owner")
    assert inbox.wakes("cto") == []
    assert [m["kind"] for m in inbox.read("cto")["messages"]] == ["relay"]


def test_the_digest_is_one_line_a_day_for_notices_read_or_unread_and_nothing_else(home):
    plant("cto", "notice", "2026-11-17T09:00:00Z")
    plant("cto", "notice", "2026-11-17T21:00:00Z", message_id="b")
    plant("cto", "notice", "2026-11-18T01:00:00Z")
    plant("cto", "wake", "2026-11-18T02:00:00Z")
    inbox.read("cto")                      # read or unread: the digest counts both
    plant("cto", "notice", "2026-11-19T01:00:00Z")
    code, out, _ = run("digest", address="cto")
    assert code == 0 and out.splitlines() == ["2026-11-17 2 notices", "2026-11-18 1 notices", "2026-11-19 1 notices"]


def test_the_digest_of_one_day_is_that_days_line_alone(home):
    plant("cto", "notice", "2026-11-17T09:00:00Z")
    plant("cto", "notice", "2026-11-18T09:00:00Z")
    code, out, _ = run("digest", address="cto", day="2026-11-18")
    assert out.splitlines() == ["2026-11-18 1 notices"]


def test_the_digest_address_defaults_to_the_environment_and_refuses_none(home, monkeypatch):
    code, _out, err = run("digest")
    assert code == 1 and "MSG_ADDRESS_MISSING" in err
    monkeypatch.setenv("GOV_MSG_ADDRESS", "cto")
    plant("cto", "notice", "2026-11-17T09:00:00Z")
    assert run("digest")[1] == "2026-11-17 1 notices\n"


def test_the_digest_does_not_move_the_mark_and_wakes_no_one(home):
    plant("cto", "notice", "2026-11-17T09:00:00Z")
    run("digest", address="cto")
    assert len(inbox.read("cto", peek=True)["messages"]) == 1 and inbox.wakes("cto") == []


def test_the_audit_exits_0_when_no_message_names_the_owner(home):
    plant("cto", "wake", days_ago(1), sender="lead:T-1")
    code, out, _ = run("audit", days=7)
    assert code == 0 and "relay" not in out.replace("0 relays", "")


def test_the_audit_exits_3_naming_each_relay(home):
    kind = plant("cto", "relay", days_ago(1), sender="lead:T-1", message_id="r-kind")
    sender = plant("lead:T-1", "wake", days_ago(1), sender="owner", message_id="r-from")
    to = plant("owner", "wake", days_ago(1), sender="cto", message_id="r-to")
    plant("cto", "wake", days_ago(1), sender="lead:T-1", message_id="fine")
    code, out, _ = run("audit", days=7)
    assert code == 3
    for ident in (kind, sender, to):
        assert ident in out
    assert "fine" not in out
    assert any("r-from" in line and "owner" in line and "lead:T-1" in line for line in out.splitlines())


def test_the_audit_counts_the_last_n_days_only(home):
    plant("cto", "relay", days_ago(30), sender="owner", message_id="old")
    assert run("audit", days=7)[0] == 0
    assert run("audit", days=60)[0] == 3


def test_the_audit_scans_every_inbox_and_reads_only_files(home):
    plant("worker:T-1:engineer", "relay", days_ago(0.1), sender="x", message_id="r1")
    plant("operator", "wake", days_ago(0.1), sender="owner", message_id="r2")
    code, out, _ = run("audit", days=1)
    assert code == 3 and "r1" in out and "r2" in out


def test_the_audit_counts_a_message_whose_time_cannot_be_read(home):
    plant("cto", "relay", "not a time", sender="x", message_id="odd")
    assert run("audit", days=1)[0] == 3


def test_the_audit_json_is_one_envelope(home):
    plant("cto", "relay", days_ago(1), sender="x", message_id="r1")
    args = argparse.Namespace(action="audit", json=True, session="", role=None, days=7)
    out = io.StringIO()
    with redirect_stdout(out):
        code = command.run(REPO, args, {})
    envelope = json.loads(out.getvalue())
    assert code == 3 and envelope["result"]["relays"][0]["id"] == "r1"
