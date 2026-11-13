"""Builder tests for P-1, the guard's freeze look-up and the hooks comparison (W2-05's resume, regression evidence
only; the acceptance tests are W2-05's own)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from gov.adapters import portability
from gov.check import runner
from gov.guard import decide
from gov.util.gitenv import program_env

CLEAN = {"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
         "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}


@pytest.fixture()
def repo(tmp_path):
    path = tmp_path / "repo"
    path.mkdir()
    subprocess.run(["git", "-C", str(path), "init", "-q", "-b", "main"], check=True, env=CLEAN)
    return path


def test_a_program_that_may_start_git_elsewhere_gets_no_index(repo):
    for value in (str(repo / ".git" / "index"), str(repo / ".git" / "index.lock"), ".git/index"):
        base = {"PATH": "/usr/bin:/bin", "GIT_INDEX_FILE": value, "GIT_DIR": str(repo / ".git"),
                "GIT_WORK_TREE": str(repo), "GIT_COMMON_DIR": str(repo / ".git"), "GIT_AUTHOR_NAME": "a"}
        env = program_env(base=base)
        assert {k for k in env if k.startswith("GIT_")} == {"GIT_NO_LAZY_FETCH", "GIT_AUTHOR_NAME"}
    assert program_env(pinned=True, base={})["GIT_CONFIG_GLOBAL"] == os.devnull


def test_a_declared_check_receives_no_inherited_index(repo, monkeypatch):
    monkeypatch.setenv("GIT_INDEX_FILE", str(repo / ".git" / "index.lock"))
    monkeypatch.setenv("GIT_DIR", str(repo / ".git"))
    code, out, _err = runner._run_command("env", repo)
    assert code == 0
    assert not [line for line in out.splitlines() if line.startswith(("GIT_INDEX_FILE=", "GIT_DIR="))]


def test_the_freeze_look_up_runs_no_git_from_path(repo, tmp_path, monkeypatch):
    planted = tmp_path / "bin"
    planted.mkdir()
    marker = tmp_path / "ran"
    (planted / "git").write_text(f"#!/bin/sh\ntouch {marker}\nexit 1\n")
    (planted / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{planted}:/usr/bin:/bin")
    monkeypatch.setenv("GIT_TRACE", str(tmp_path / "trace"))
    decide._mirror_path(str(repo))
    assert not marker.exists() and not (tmp_path / "trace").exists()


def test_the_freeze_look_up_refuses_when_no_git_is_resolved_or_it_hangs(repo, monkeypatch):
    monkeypatch.setattr(decide, "_git_binary", lambda: None)
    with pytest.raises(decide.FreezeLookupUnavailable):
        decide._mirror_path(str(repo))
    assert decide._mirror_frozen(str(repo)) is True
    verdict, reason = decide.decide("Read", {"file_path": str(repo / "a")}, str(repo), "engineer", None)
    assert verdict == "deny" and "freeze look-up" in reason

    def hang(*_args, **kwargs):
        raise subprocess.TimeoutExpired("git", kwargs.get("timeout"))
    monkeypatch.setattr(decide, "_git_binary", lambda: "/usr/bin/git")
    monkeypatch.setattr(subprocess, "run", hang)
    with pytest.raises(decide.FreezeLookupUnavailable, match="15 s"):
        decide._mirror_path(str(repo))


def _hooks(path: Path, events: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("// a comment\n" + json.dumps({"version": 1, "hooks": events}, indent=1))


def _two(tmp_path, template: dict, ours: dict) -> list[dict]:
    (tmp_path / "template" / "governance" / "kernel").mkdir(parents=True)
    _hooks(tmp_path / "template" / ".rulesync" / "hooks.jsonc", template)
    _hooks(tmp_path / ".rulesync" / "hooks.jsonc", ours)
    return portability._hooks_findings(tmp_path)


def _hook(name: str, matcher: str | None = None, template: bool = False) -> dict:
    prefix = "template/" if template else ""
    command = f"python3 \"$CLAUDE_PROJECT_DIR/{prefix}governance/kernel/hooks/{name}.py\""
    return {"type": "command", "command": command, **({"matcher": matcher} if matcher else {})}


def test_hooks_that_differ_only_in_paths_order_or_wrapper_are_no_drift(tmp_path):
    template = {"stop": [_hook("stop")], "postToolUse": [_hook("post", "Bash"), _hook("other")]}
    ours = {"postToolUse": [_hook("other", template=True), _hook("post", "Bash", template=True)],
            "stop": [{"type": "command", "command": "exec \"$p\" -E template/governance/kernel/hooks/stop.py"}]}
    assert _two(tmp_path, template, ours) == []


def test_each_drifted_event_is_one_finding_naming_it(tmp_path):
    template = {"sessionStart": [_hook("s")], "stop": [_hook("stop")], "postToolUse": [_hook("p", "Bash")]}
    ours = {"sessionStart": [_hook("s", "compact|clear|resume")], "postToolUse": [_hook("p", "Edit")],
            "preCompact": [_hook("c")]}
    findings = _two(tmp_path, template, ours)
    events = sorted(next(e for e in ("sessionStart", "stop", "postToolUse", "preCompact") if e in f["message"])
                    for f in findings)
    assert events == ["postToolUse", "preCompact", "sessionStart", "stop"]
    assert all(f["file"].endswith("hooks.jsonc") for f in findings)


def test_this_repository_s_two_hooks_sources_agree():
    root = Path(__file__).resolve().parents[3]
    assert portability._hooks_findings(root) == []
