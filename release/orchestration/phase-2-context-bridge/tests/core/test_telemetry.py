import pytest

from govbridge.core import telemetry


def test_write_row_rejects_unknown_kind(monkeypatch, tmp_path):
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    with pytest.raises(ValueError):
        telemetry.write_row("not-a-real-kind", {"x": 1})


def test_write_and_read_rows_round_trip(monkeypatch, tmp_path):
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    telemetry.write_row("builds", {"trigger": "full", "llm_invocations": 0})
    telemetry.write_row("builds", {"trigger": "noop", "llm_invocations": 0})
    rows = telemetry.read_rows("builds")
    assert len(rows) == 2
    assert rows[0]["trigger"] == "full"
    assert "written_at" in rows[0]


def test_read_rows_for_a_kind_never_written_is_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    assert telemetry.read_rows("packets") == []


def test_build_id_is_deterministic_length_and_varies():
    a = telemetry.build_id("sha1", "full")
    b = telemetry.build_id("sha1", "full")
    assert len(a) == 16 and len(b) == 16
    assert a != b  # time-salted, never collides across calls
