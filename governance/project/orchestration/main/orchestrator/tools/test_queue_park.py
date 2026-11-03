import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import land  # noqa: E402
import queue_park  # noqa: E402


def entry(q, d, w2):
    (q / d).mkdir(parents=True, exist_ok=True)
    (q / d / f"{w2}.json").write_text(json.dumps({"ticket": w2}))


def names(q, d):
    return sorted(p.stem for p in (q / d).glob("*.json"))


def test_strays_are_the_approvals_not_named(tmp_path):
    for w in ("W2-11", "W2-122", "W2-123"):
        entry(tmp_path, "approved", w)
    assert land.strays(tmp_path, ["W2-122", "W2-123"]) == ["W2-11"]
    assert land.strays(tmp_path, ["W2-11", "W2-122", "W2-123"]) == []
    assert land.strays(tmp_path / "none", ["W2-1"]) == []


def test_land_refuses_before_anything_is_queued(tmp_path, monkeypatch, capsys):
    entry(tmp_path, "approved", "W2-11")
    monkeypatch.setattr(land, "QUEUE", tmp_path)
    monkeypatch.setattr(land, "sh", lambda cmd, **kw: type("R", (), {"returncode": 0})())
    monkeypatch.setattr(land, "git", lambda *a: "c" * 40)
    monkeypatch.setattr(land, "ticket_of", lambda w2: ("DAEO-x", "STANDARD"))
    monkeypatch.setattr(land, "precheck", lambda *a: ([], None))
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-122=abc1234", "--base", "abc1234"])
    try:
        land.main()
    except SystemExit as e:
        assert e.code == 2
    else:
        raise AssertionError("land.main did not refuse")
    out = capsys.readouterr().out
    assert "REFUSED before anything was queued" in out and "W2-11" in out


def test_park_keeps_the_named_and_unpark_restores(tmp_path):
    for w in ("W2-11", "W2-105", "W2-122"):
        entry(tmp_path, "approved", w)
    assert queue_park.main(["park", "--keep", "W2-122", "--queue", str(tmp_path)]) == 0
    assert names(tmp_path, "approved") == ["W2-122"]
    assert names(tmp_path, queue_park.PARKED) == ["W2-105", "W2-11"]
    assert queue_park.main(["unpark", "--queue", str(tmp_path)]) == 0
    assert names(tmp_path, "approved") == ["W2-105", "W2-11", "W2-122"]
    assert names(tmp_path, queue_park.PARKED) == []


def test_a_clash_is_never_overwritten(tmp_path):
    entry(tmp_path, "approved", "W2-11")
    entry(tmp_path, queue_park.PARKED, "W2-11")
    (tmp_path / queue_park.PARKED / "W2-11.json").write_text("older")
    assert queue_park.main(["park", "--queue", str(tmp_path)]) == 1
    assert (tmp_path / queue_park.PARKED / "W2-11.json").read_text() == "older"
    assert names(tmp_path, "approved") == ["W2-11"]
