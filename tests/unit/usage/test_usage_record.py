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


# --- UR-5 to UR-7: split cache-write prices, the table's resolution order, temporary folders -------------------------

def _row_line(sid, mid, model, ts, cwd, usage):
    return json.dumps({"type": "assistant", "sessionId": sid, "cwd": cwd, "timestamp": ts,
                       "message": {"id": mid, "model": model, "usage": usage}})


def test_cache_creation_splits_into_five_minute_and_one_hour(tmp_path, monkeypatch):
    day = "2026-11-24"
    use = {"input_tokens": 1, "cache_creation_input_tokens": 30,
           "cache_creation": {"ephemeral_5m_input_tokens": 10, "ephemeral_1h_input_tokens": 20}}
    root = _setup(tmp_path, monkeypatch, {"a.jsonl": [_row_line("S", "m1", "m", day + "T10:00:00Z", "/nonexistent/x", use)]})
    (row,), _ = record.collect(root, day)
    assert (row["cache_creation"], row["cache_creation_5m"], row["cache_creation_1h"]) == (30, 10, 20)


def test_an_absent_or_inconsistent_split_makes_all_cache_creation_five_minute(tmp_path, monkeypatch):
    day = "2026-11-24"
    absent = {"input_tokens": 1, "cache_creation_input_tokens": 30}
    bad = {"input_tokens": 1, "cache_creation_input_tokens": 30,
           "cache_creation": {"ephemeral_5m_input_tokens": 1, "ephemeral_1h_input_tokens": 2}}
    root = _setup(tmp_path, monkeypatch, {"a.jsonl": [_row_line("A", "m1", "m", day + "T10:00:00Z", "/nonexistent/x", absent),
                                                      _row_line("B", "m1", "m", day + "T10:00:00Z", "/nonexistent/x", bad)]})
    rows, _ = record.collect(root, day)
    assert [(r["cache_creation"], r["cache_creation_5m"], r["cache_creation_1h"]) for r in rows] == [(30, 30, 0)] * 2


def _table(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_split_prices_price_each_write_kind_and_the_legacy_key_prices_both(tmp_path):
    _table(tmp_path / "governance/project/usage-prices.yaml",
           "models:\n  a: {input: 0, output: 0, cache_read: 0, cache_write_5m: 2, cache_write_1h: 4}\n"
           "  b: {input: 0, output: 0, cache_read: 0, cache_creation: 3}\n")
    prices = record.load_prices(tmp_path)
    row = {"input": 0, "output": 0, "cache_read": 0, "cache_creation_5m": 1_000_000, "cache_creation_1h": 1_000_000}
    assert record._cost(dict(row, model="a"), prices) == 6.0
    assert record._cost(dict(row, model="b"), prices) == 6.0


def test_a_repository_table_overrides_and_the_shipped_one_serves_a_bare_root(tmp_path):
    shipped = record.load_prices(tmp_path)
    assert "claude-opus-5-5" in shipped["models"]
    _table(tmp_path / "governance/project/usage-prices.yaml",
           "date: x\nmodels:\n  only: {input: 1, output: 1, cache_read: 1, cache_creation: 1}\n")
    own = record.load_prices(tmp_path)
    assert list(own["models"]) == ["only"]


def test_the_error_names_both_places_when_neither_table_is_readable(tmp_path, monkeypatch):
    monkeypatch.setattr(record, "SHIPPED", tmp_path / "nowhere.yaml")
    try:
        record.load_prices(tmp_path)
    except record.UsageError as exc:
        assert str(tmp_path / "governance/project/usage-prices.yaml") in str(exc) and "nowhere.yaml" in str(exc)
    else:
        raise AssertionError("no error")


def test_temporary_is_under_tmp_and_not_a_real_git_folder(tmp_path):
    import subprocess
    assert record.is_temporary("/tmp/gone-for-sure-xyz")
    assert record.is_temporary("/var/tmp/gone-for-sure-xyz")
    assert not record.is_temporary("/nonexistent/repo-x")
    plain = Path("/tmp") / f"usage-unit-{tmp_path.name}"
    plain.mkdir()
    try:
        assert record.is_temporary(str(plain))
        subprocess.run(["git", "init", "-q", str(plain)], check=True)
        assert not record.is_temporary(str(plain))
    finally:
        import shutil
        shutil.rmtree(plain, ignore_errors=True)


def test_temporary_rows_are_left_out_of_rows_and_totals_and_counted(tmp_path, monkeypatch):
    day = "2026-11-24"
    use = {"input_tokens": 1000000}
    root = _setup(tmp_path, monkeypatch, {"a.jsonl": [
        _row_line("T", "m1", "claude-opus-5-5", day + "T10:00:00Z", "/tmp/gone-for-sure-xyz", use),
        _row_line("R", "m1", "claude-opus-5-5", day + "T10:00:00Z", "/nonexistent/real", use)]})
    rec = record.build(root, day)
    assert [r["repository"] for r in rec["rows"]] == ["/nonexistent/real"]
    assert list(rec["totals"]["by_repository"]) == ["/nonexistent/real"] and rec["totals"]["all"]["sessions"] == 1
    assert rec["temporary"]["sessions"] == 1 and rec["temporary"]["cost_usd"] == 4.0
