"""The end events and ``gov dispatch waits --ends`` (W2-205, RT-2): every end is one ``end`` event in the runtime log;
the gap is the message's time less ``ended_at``; a gap over 120 s is a finding; an end with no message is a gap to now."""
from __future__ import annotations

import argparse
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import admission, command, ends, inbox  # noqa: E402

NOW = 1_800_000_000.0


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("GOV_MSG_ADDRESS", raising=False)
    monkeypatch.delenv("GOV_RUNTIME_NOW", raising=False)
    return tmp_path / "home"


def log_events(home: Path) -> list[dict]:
    path = home / ".gov-os" / "runtime" / "log.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def plant_message(to: str, message_id: str, at: str) -> None:
    folder = inbox.folder(to)
    folder.mkdir(parents=True, exist_ok=True)
    line = {"id": message_id, "at": at, "from": "x", "to": to, "kind": "wake", "text": "t"}
    with open(folder / "messages.jsonl", "a") as handle:
        handle.write(json.dumps(line) + "\n")


def waits_ends(*extra: str, as_json: bool = False):
    out = io.StringIO()
    args = argparse.Namespace(action="waits", ends=True, json=as_json, session="", role=None, over=None, gpu_need_mib=None)
    with redirect_stdout(out):
        code = command.run(REPO, args, {})
    return code, out.getvalue()


def test_record_writes_one_end_event_with_its_fields_and_a_duplicate_id_writes_none(home):
    assert ends.record("end:a:1:2", "worker", "cto", "2026-11-19T10:00:00Z", ticket="T-1") is True
    assert ends.record("end:a:1:2", "worker", "cto", "2026-11-19T10:00:05Z", ticket="T-1") is False
    [event] = [e for e in log_events(home) if e["event"] == "end"]
    assert (event["id"], event["kind"], event["to"], event["ended_at"], event["ticket"]) == \
        ("end:a:1:2", "worker", "cto", "2026-11-19T10:00:00Z", "T-1")
    assert event["at"].endswith("Z")


def test_a_job_end_carries_the_job_and_the_estimate_flag(home):
    ends.record("job:j1", "job", "lead:T-1", "2026-11-19T10:00:00Z", job="j1", estimated=True)
    [event] = log_events(home)
    assert event["job"] == "j1" and event["estimated"] is True and "ticket" not in event


def test_wake_of_a_heavy_job_gives_one_end_event_and_its_message(home, monkeypatch):
    monkeypatch.setenv("GOV_MSG_ADDRESS", "lead:T-1")
    admission.wake("j9", "test", 0, 3.0)
    admission.wake("j9", "test", 0, 3.0)
    [event] = [e for e in log_events(home) if e["event"] == "end"]
    assert (event["id"], event["kind"], event["to"], event["job"]) == ("job:j9", "job", "lead:T-1", "j9")
    assert len(inbox.read("lead:T-1", peek=True)["messages"]) == 1


def test_a_gap_is_the_messages_time_less_ended_at_and_over_120_s_is_a_finding(home):
    ends.record("end:ok", "worker", "cto", "2026-11-19T10:00:00Z", ticket="T-1")
    ends.record("end:late", "lead", "cto", "2026-11-19T10:00:00Z", ticket="T-2")
    plant_message("cto", "end:ok", "2026-11-19T10:02:00Z")      # exactly 120 s: no finding
    plant_message("cto", "end:late", "2026-11-19T10:03:20Z")    # 200 s
    rows = ends.analyse(admission.events(), NOW)
    assert {r["id"]: r["gap_s"] for r in rows} == {"end:ok": 120.0, "end:late": 200.0}
    assert [r["id"] for r in ends.findings(rows)] == ["end:late"]


def test_the_first_message_with_the_id_counts(home):
    ends.record("end:a", "worker", "cto", "2026-11-19T10:00:00Z")
    plant_message("cto", "end:a", "2026-11-19T10:01:00Z")
    plant_message("cto", "end:a", "2026-11-19T10:09:00Z")
    [row] = ends.analyse(admission.events(), NOW)
    assert row["gap_s"] == 60.0


def test_an_end_with_no_message_is_a_gap_to_now_and_unsent(home):
    ends.record("end:a", "worker", "cto", ends.stamp(NOW - 30))
    [row] = ends.analyse(admission.events(), NOW)
    assert row["unsent"] is True and row["gap_s"] == 30.0
    assert "unsent" in ends.render([row], [], 120.0)


def test_the_report_prints_a_line_a_end_and_exits_3_naming_a_late_one(home):
    ends.record("end:late", "worker", "cto", "2026-11-19T10:00:00Z")
    plant_message("cto", "end:late", "2026-11-19T10:03:20Z")
    code, text = waits_ends()
    assert code == 3
    assert "end:late worker cto gap 200 s" in text and "finding: end:late" in text


def test_the_report_exits_0_when_every_gap_is_within_the_limit(home):
    ends.record("end:a", "worker", "cto", "2026-11-19T10:00:00Z")
    plant_message("cto", "end:a", "2026-11-19T10:01:00Z")
    code, text = waits_ends()
    assert code == 0 and "finding" not in text and "end:a worker cto gap 60 s" in text


def test_json_is_one_envelope_with_the_rows_and_the_same_exit_code(home):
    ends.record("end:late", "worker", "cto", "2026-11-19T10:00:00Z")
    plant_message("cto", "end:late", "2026-11-19T10:03:20Z")
    code, text = waits_ends(as_json=True)
    envelope = json.loads(text)
    assert code == 3 and envelope["ok"] is True and envelope["result"]["ends"][0]["id"] == "end:late"
