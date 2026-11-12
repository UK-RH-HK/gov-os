"""W2-115 S8: the nightly rebuilds its worktree's stores with the full secrets scan before its run."""
from __future__ import annotations

import json
import os

from gov.cli.errors import GovError
from gov.close import command as close_command, nightly
from gov.rebuild import command as rebuild_command

from .test_w2_115_support import project


def test_s8_the_stores_are_rebuilt_with_the_full_scan_before_the_run(tmp_path, monkeypatch):
    repo = project(tmp_path)
    monkeypatch.delenv("GOV_SECRETS_FULL_SCAN", raising=False)
    events = []
    monkeypatch.setattr(rebuild_command, "run", lambda root, args, config: events.append(
        ("rebuild", os.environ.get("GOV_SECRETS_FULL_SCAN"), args.no_embeddings, str(root))) or {"digest": "x"})
    real_tests = close_command._run_tests
    monkeypatch.setattr(close_command, "_run_tests", lambda *a, **k: events.append(("tests",)) or real_tests(*a, **k))
    result = nightly.night(repo.root, "main")
    assert [e[0] for e in events] == ["rebuild", "tests"]
    assert events[0][1] == "1" and events[0][2] is True
    assert events[0][3] != str(repo.root)  # the night's own worktree, never the working tree
    assert "GOV_SECRETS_FULL_SCAN" not in os.environ  # the caller's environment as it was
    record = json.loads((repo.root / result["record"]).read_text(encoding="utf-8"))
    assert record["secrets_full_scan"] is True
    assert record["rebuild"]["GOV_SECRETS_FULL_SCAN"] == "1"


def test_s8_a_failed_rebuild_is_said_in_the_record(tmp_path, monkeypatch):
    repo = project(tmp_path)

    def fails(*a, **k):
        raise GovError("REBUILD_FAILED", "no store")
    monkeypatch.setattr(rebuild_command, "run", fails)
    result = nightly.night(repo.root, "main")
    record = json.loads((repo.root / result["record"]).read_text(encoding="utf-8"))
    assert record["secrets_full_scan"] is False and "no store" in record["rebuild"]["error"]


def test_s8_the_caller_cannot_switch_the_full_scan_off(tmp_path, monkeypatch):
    monkeypatch.setenv("GOV_SECRETS_FULL_SCAN", "0")
    seen = []
    monkeypatch.setattr(rebuild_command, "run", lambda *a, **k: seen.append(os.environ["GOV_SECRETS_FULL_SCAN"]))
    assert nightly.rebuild_stores(tmp_path)["ok"] is True
    assert seen == ["1"] and os.environ["GOV_SECRETS_FULL_SCAN"] == "0"
