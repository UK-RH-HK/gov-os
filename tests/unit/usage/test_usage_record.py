"""Unit tests for gov.usage.record (W2-207): dedupe, skipped counting, role order, never fatal."""
import json
from pathlib import Path

from gov.usage import record


def _line(sid, mid, ts, inp=1, usage=True, cwd="/nonexistent/repo-x"):
    msg = {"id": mid, "model": "m", **({"usage": {"input_tokens": inp, "output_tokens": 1,
                                                   "cache_read_input_tokens": 2, "cache_creation_input_tokens": 3}} if usage else {})}
    return json.dumps({"type": "assistant", "sessionId": sid, "cwd": cwd, "timestamp": ts, "message": msg})


def _setup(tmp_path, monkeypatch, files):
    home = tmp_path / "home"
    d = home / ".claude" / "projects" / "p"
    d.mkdir(parents=True)
    for name, lines in files.items():
        (d / name).write_text("\n".join(lines) + "\n")
    monkeypatch.setenv("HOME", str(home))
    return tmp_path / "root"


def test_message_counted_once_across_resumed_files_last_usage_wins(tmp_path, monkeypatch):
    day = "2026-11-24"
    root = _setup(tmp_path, monkeypatch, {
        "a.jsonl": [_line("S", "m1", day + "T10:00:00Z", 1)],
        "b.jsonl": [_line("S", "m1", day + "T10:00:00Z", 9)]})
    rows, skipped = record.collect(root, day)
    assert len(rows) == 1 and rows[0]["input"] == 9 and skipped == 0
    assert rows[0]["context_peak"] == 9 + 2 + 3 and rows[0]["role"] == "unknown"


def test_bad_and_usageless_lines_are_skipped_and_counted_once(tmp_path, monkeypatch):
    day = "2026-11-24"
    bad = ["not json", _line("S", "n", day + "T10:00:00Z", usage=False), '{"type": "user"}']
    root = _setup(tmp_path, monkeypatch, {"a.jsonl": bad, "b.jsonl": bad[1:]})
    rows, skipped = record.collect(root, day)
    assert rows == [] and skipped == 2


def test_only_the_days_messages_by_utc_timestamp(tmp_path, monkeypatch):
    root = _setup(tmp_path, monkeypatch, {"a.jsonl": [_line("S", "m1", "2026-11-24T23:59:59Z"),
                                                       _line("S", "m2", "2026-11-25T00:00:01Z")]})
    assert len(record.collect(root, "2026-11-25")[0]) == 1
    assert record.collect(root, "2026-11-25")[0][0]["input"] == 1


def test_plan_reading_is_unread_without_a_line_for_the_day(tmp_path):
    log = tmp_path / record.LOG
    log.mkdir(parents=True)
    (log / "usage.txt").write_text("2026-11-23 10:00:00 old\n2026-11-24 10:00:00 a\n2026-11-24 11:00:00 b\n")
    assert record.plan_reading(tmp_path, "2026-11-24") == "b"
    assert record.plan_reading(tmp_path, "2026-11-22") == "unread"
