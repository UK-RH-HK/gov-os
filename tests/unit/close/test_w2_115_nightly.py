"""W2-115 S8: the nightly rebuilds its worktree's stores with the full secrets scan before its run."""
from __future__ import annotations

import json
import subprocess

from gov.close import command as close_command, nightly

from .test_w2_115_support import project


def test_s8_the_stores_are_rebuilt_with_the_full_scan_before_the_run(tmp_path, monkeypatch):
    repo = project(tmp_path)
    monkeypatch.delenv("GOV_SECRETS_FULL_SCAN", raising=False)
    events = []
    real_run = subprocess.run

    def spy(cmd, *a, **k):
        if "rebuild" in cmd:
            events.append(("rebuild", (k.get("env") or {}).get("GOV_SECRETS_FULL_SCAN"), cmd))
            return subprocess.CompletedProcess(cmd, 0, "{}", "")
        return real_run(cmd, *a, **k)

    monkeypatch.setattr(nightly.subprocess, "run", spy)
    real_tests = close_command._run_tests
    monkeypatch.setattr(close_command, "_run_tests", lambda *a, **k: events.append(("tests", None, None)) or
                        real_tests(*a, **k))
    result = nightly.night(repo.root, "main")
    assert [e[0] for e in events] == ["rebuild", "tests"]
    assert events[0][1] == "1"
    assert "--no-embeddings" in events[0][2]
    record = json.loads((repo.root / result["record"]).read_text(encoding="utf-8"))
    assert record["secrets_full_scan"] is True
    assert record["rebuild"]["GOV_SECRETS_FULL_SCAN"] == "1"


def test_s8_a_failed_rebuild_is_said_in_the_record(tmp_path, monkeypatch):
    repo = project(tmp_path)
    real_run = subprocess.run
    monkeypatch.setattr(nightly.subprocess, "run", lambda cmd, *a, **k: subprocess.CompletedProcess(
        cmd, 1, "", "no store") if "rebuild" in cmd else real_run(cmd, *a, **k))
    result = nightly.night(repo.root, "main")
    record = json.loads((repo.root / result["record"]).read_text(encoding="utf-8"))
    assert record["secrets_full_scan"] is False and "no store" in record["rebuild"]["error"]


def test_s8_the_caller_cannot_switch_the_full_scan_off(tmp_path, monkeypatch):
    monkeypatch.setenv("GOV_SECRETS_FULL_SCAN", "0")
    seen = {}
    monkeypatch.setattr(nightly.subprocess, "run", lambda cmd, *a, **k: seen.update(k.get("env") or {}) or
                        subprocess.CompletedProcess(cmd, 0, "", ""))
    assert nightly.rebuild_stores(tmp_path)["ok"] is True
    assert seen["GOV_SECRETS_FULL_SCAN"] == "1"
