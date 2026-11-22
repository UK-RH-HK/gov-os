"""Unit tests of G3's rehearsal (W2-209 S5): the refusals before any clone, and the steps with stand-ins."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from gov.release import proving


def kept_run(folder: Path, names=proving.NAMES, queue=None) -> Path:
    (folder / "run.json").parent.mkdir(parents=True, exist_ok=True)
    (folder / "run.json").write_text("{}", encoding="utf-8")
    for name in names:
        (folder / "repos" / name).mkdir(parents=True)
        (folder / "repos" / name / "file.txt").write_text(name, encoding="utf-8")
    (folder / "report.json").write_text(json.dumps({"repositories": {
        name: {"queue": {"ticket": queue.get(name)} if queue and queue.get(name) else {"run": False}}
        for name in proving.NAMES}}), encoding="utf-8")
    return folder


def test_no_kept_run_a_missing_folder_and_five_repositories_are_not_ready(tmp_path):
    for kept in (None, tmp_path / "absent"):
        report = proving.rehearse(tmp_path, "0" * 40, "0.1.2", kept)
        assert report["verdict"] == "NOT_READY" and report["reasons"]
    five = kept_run(tmp_path / "five", names=proving.NAMES[:5])
    report = proving.rehearse(tmp_path, "0" * 40, "0.1.2", five)
    assert report["verdict"] == "NOT_READY" and proving.NAMES[5] in report["reasons"][0]


def stand_in_source(monkeypatch):
    def source(root, commit, version, folder):
        (folder / "source").mkdir()
        return folder / "source"
    monkeypatch.setattr(proving, "_scratch_source", source)


def test_all_steps_passing_is_ready_and_a_failing_step_names_the_repository_and_the_step(tmp_path, monkeypatch):
    stand_in_source(monkeypatch)
    kept = kept_run(tmp_path / "kept", queue={"python-app": "T-1"})
    calls, failing = [], {}

    def run(step, repository, argv, cwd):
        calls.append((step, repository, Path(cwd).name))
        assert Path(cwd) != kept / "repos" / repository  # a throwaway copy, never the kept repository
        if failing.get("step") == step and failing.get("repository") == repository:
            return 1, "{}"
        return 0, json.dumps({"result": {"files": {"conflicts": []}}})

    judge = lambda repository, root, outputs: {"verdict": "READY"}  # noqa: E731
    report = proving.rehearse(tmp_path, "0" * 40, "0.1.2", kept, run=run, judge=judge)
    assert report["verdict"] == "READY" and report["reasons"] == []
    assert report["repositories"]["python-app"]["steps"]["close"]["skipped"] is False
    assert report["repositories"]["legacy-docs"]["steps"]["close"]["skipped"] is True
    assert [c for c in calls if c[1] == "python-app"][-1][0] == "close"
    failing.update(step="update", repository="legacy-docs")
    report = proving.rehearse(tmp_path, "0" * 40, "0.1.2", kept, run=run, judge=judge)
    assert report["verdict"] == "NOT_READY" and report["reasons"][0].startswith("legacy-docs: update")
    assert report["repositories"]["legacy-docs"]["failed"] == "update"
    again = proving.rehearse(tmp_path, "0" * 40, "0.1.2", kept, run=run,
                             judge=lambda repository, root, outputs: {"verdict": "NOT_READY" if repository == "rust-workspace"
                                                                       and Path(root).parts[-3] != "repos" else "READY"})
    assert "rust-workspace: judge" in " ".join(again["reasons"])


def test_a_conflict_listed_by_the_check_is_not_ready(tmp_path, monkeypatch):
    stand_in_source(monkeypatch)
    kept = kept_run(tmp_path / "kept")

    def run(step, repository, argv, cwd):
        conflicts = ["a.md"] if step == "check" and repository == "secret-history" else []
        return 0, json.dumps({"result": {"files": {"conflicts": conflicts}}})

    report = proving.rehearse(tmp_path, "0" * 40, "0.1.2", kept, run=run, judge=lambda *a: {"verdict": "READY"})
    assert report["verdict"] == "NOT_READY" and report["reasons"][0].startswith("secret-history: check")
