"""A burned release is never offered by the update machinery (W2-209 S9): ``gov.update.pending.pending`` reads ``burned``."""
from __future__ import annotations

from pathlib import Path

from gov.update import core, pending


def _plant(monkeypatch, tmp_path, found, burned):
    home = tmp_path / "home"
    (home / ".local/share/gov-os").mkdir(parents=True)
    if burned is not None:
        (home / ".local/share/gov-os/burned").write_text("".join(f"{v}\n" for v in burned), encoding="utf-8")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setattr(core, "held_release", lambda project: "0.1.1")
    monkeypatch.setattr(pending, "_source", lambda project, source: tmp_path / "src")
    monkeypatch.setattr(pending, "_candidates", lambda src, held: list(found))
    monkeypatch.setattr(pending, "_kind", lambda src, version: "patch")
    monkeypatch.setattr(pending, "_fixes", lambda src, held, newest: 2)
    return pending.pending(tmp_path / "project")


def test_every_newer_release_burned_is_no_pending_update_and_says_why(monkeypatch, tmp_path):
    report = _plant(monkeypatch, tmp_path, ["0.1.2"], ["0.1.2"])
    assert report["pending"] is False and report["burned"] is True
    assert report["held"] == "0.1.1" and report["newest"] == "0.1.2"
    assert "burned" in report["reason"] and "burned" in report["summary"]


def test_a_burned_release_is_skipped_for_an_older_unburned_one(monkeypatch, tmp_path):
    report = _plant(monkeypatch, tmp_path, ["0.1.2", "0.1.3"], ["0.1.3"])
    assert report["pending"] is True and report["newest"] == "0.1.2"


def test_without_a_burned_file_the_newest_is_offered(monkeypatch, tmp_path):
    report = _plant(monkeypatch, tmp_path, ["0.1.2"], None)
    assert report["pending"] is True and report["newest"] == "0.1.2"
