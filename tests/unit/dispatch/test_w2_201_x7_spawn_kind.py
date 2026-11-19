"""Builder tests for W2-201 fix X7 (DEC-1219 (5)): the relaunch starts the same kind of launch.

Regression evidence only; ``subprocess.Popen`` is replaced, nothing is started.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import relaunch  # noqa: E402

SESSION = "11111111-2222-3333-4444-555555555555"


@pytest.fixture
def spawned(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    seen = {}

    class Child:
        pid = 77

    def popen(command, **kwargs):
        seen.update(command=command, **kwargs)
        return Child()
    monkeypatch.setattr(relaunch.subprocess, "Popen", popen)

    def run(**keys):
        entry = {"role": "engineer", "ticket": "DAEO-x", "repository": str(tmp_path), "session_id": SESSION, **keys}
        assert relaunch.spawn(tmp_path / "runtime", entry) == 77
        command = seen["command"]
        cut = command.index("--")
        return command[3:cut], command[cut + 1:]
    return run


def test_a_fix_entry_is_launched_with_fix_and_its_ticket(spawned, monkeypatch):
    monkeypatch.setattr(relaunch, "next_step", lambda entry: "S")
    before, after = spawned(kind="fix", kind_line="the line")
    assert before == ["launch", "engineer", "DAEO-x", "--fix", "the line", "--root", before[-1]]
    assert after == ["--resume", SESSION, "Resume at the recorded next step (DAEO-x): S"]


def test_a_chore_entry_is_launched_with_chore_and_no_ticket(spawned, monkeypatch):
    def no_checkpoint(entry):
        raise AssertionError("a chore has no checkpoint to read")
    monkeypatch.setattr(relaunch, "next_step", no_checkpoint)
    before, after = spawned(role="orchestrator", ticket="chore-0a1b2c3d", kind="chore", kind_line="tidy")
    assert before == ["launch", "orchestrator", "--chore", "tidy", "--root", before[-1]]
    assert "chore-0a1b2c3d" not in before
    assert after[:2] == ["--resume", SESSION]
    assert after[2].startswith("Resume at the recorded next step") and relaunch.FALLBACK_STEP in after[2]


@pytest.mark.parametrize("keys", ({}, {"kind": "feature", "kind_line": None}))
def test_a_feature_or_an_old_entry_is_launched_as_before(spawned, monkeypatch, keys):
    monkeypatch.setattr(relaunch, "next_step", lambda entry: "S")
    before, _ = spawned(**keys)
    assert before == ["launch", "engineer", "DAEO-x", "--root", before[-1]]
