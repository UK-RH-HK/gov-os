"""Builder tests for the two probe points:

1. ``_restore_from_head`` with a non-HEAD commit now verifies each
   path against the target commit and returns unrestored paths as
   failed (``flagged``), not ``reverted``.

2. ``_get_pending_timeout()`` rejects values that are not a usable
   duration (zero, negative, nan, inf, non-numeric, empty) and falls
   back to the default 600.
"""

from __future__ import annotations

import itertools
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
HOOK_DIR = REPO / "template" / "governance" / "kernel" / "hooks"
SRC_DIR = REPO / "src"
FINDINGS_REL = ".gov-runtime/findings.jsonl"
SNAPSHOT_DIR_REL = ".gov-runtime/snapshots"
GIT_ID = [
    "-c", "user.name=test", "-c", "user.email=t@test.invalid",
    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
]
_NUM = itertools.count(1)


# ---- helpers (mirrored from test_dec142_and_dec143.py) ----------------

def _git(project, *args):
    p = subprocess.run(
        ["git", "-C", str(project), *GIT_ID, *args],
        capture_output=True, text=True, check=False)
    assert p.returncode == 0, f"git {' '.join(args)}: {p.stderr}"
    return p.stdout


def _make_project(tmp_path):
    proj = tmp_path / "project"
    proj.mkdir()
    (proj / ".gitignore").write_text(".gov-runtime/\n__pycache__/\n")
    (proj / "README.md").write_text("# test\n")
    (proj / "docs").mkdir()
    (proj / "docs" / "notes.md").write_text("notes\n")
    (proj / "src").mkdir()
    (proj / "src" / "main.py").write_text("x = 1\n")
    acc = proj / "tests" / "acceptance" / "T01"
    acc.mkdir(parents=True)
    (acc / "test_ok.py").write_text("def test_pass(): pass\n")
    tk = proj / ".tickets"
    tk.mkdir()
    (tk / "T01.md").write_text(textwrap.dedent("""\
        ---
        id: T01
        status: in_progress
        role: engineer
        allowed_paths:
        - src/**
        ---
    """))
    hd = proj / "governance" / "kernel" / "hooks"
    hd.mkdir(parents=True)
    for pattern in ("pretooluse*", "posttooluse*"):
        for f in sorted(HOOK_DIR.glob(pattern)):
            if f.is_file():
                shutil.copy2(f, hd / f.name)
    _git(proj, "init", "-q", "-b", "main")
    _git(proj, "add", "-A")
    _git(proj, "commit", "-q", "-m", "init")
    return proj


def _env(proj, role="engineer", ticket="T01", extra_env=None):
    base = proj.parent
    for d in ("home", "tmp", "pyc"):
        (base / d).mkdir(exist_ok=True)
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(base / "home"),
        "LANG": "C.UTF-8",
        "TMPDIR": str(base / "tmp"),
        "CLAUDE_PROJECT_DIR": str(proj),
        "PYTHONPATH": str(SRC_DIR),
        "PYTHONPYCACHEPREFIX": str(base / "pyc"),
    }
    if role:
        env["GOV_ROLE"] = role
    if ticket:
        env["GOV_TICKET"] = ticket
    if extra_env:
        env.update(extra_env)
    return env


def _hook(proj, pattern):
    hd = proj / "governance" / "kernel" / "hooks"
    hits = sorted(hd.glob(pattern))
    assert hits, f"no hook matches {pattern}"
    return hits[0]


def _run_hook(proj, hook_path, data, role="engineer", ticket="T01",
              extra_env=None):
    env = _env(proj, role, ticket, extra_env)
    p = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(data), capture_output=True, text=True,
        cwd=str(proj), env=env, timeout=30, check=False)
    return p


def _pre_data(proj, cmd, tuid, session_id="test-session",
              agent_id=None, subagent=None, tool_name="Bash"):
    d = {
        "session_id": session_id,
        "cwd": str(proj),
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": ({"command": cmd} if tool_name == "Bash"
                       else {"file_path": cmd}),
        "tool_use_id": tuid,
    }
    if subagent:
        d["agent_type"] = subagent
    if agent_id is not None:
        d["agent_id"] = agent_id
    return d


def _post_data(proj, cmd, tuid, session_id="test-session",
               agent_id=None, subagent=None, bash=None):
    d = {
        "session_id": session_id,
        "cwd": str(proj),
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": cmd},
        "tool_use_id": tuid,
        "tool_response": {
            "stdout": bash.stdout if bash else "",
            "stderr": bash.stderr if bash else "",
            "interrupted": False,
            "isImage": False,
        },
    }
    if subagent:
        d["agent_type"] = subagent
    if agent_id is not None:
        d["agent_id"] = agent_id
    return d


def _bash(proj, cmd):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(proj.parent / "home"),
        "LANG": "C.UTF-8",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t",
    }
    return subprocess.run(
        ["bash", "-c", cmd], cwd=str(proj),
        capture_output=True, text=True, timeout=30,
        check=False, env=env)


def _script(proj, cmd):
    base = proj.parent
    sdir = base / "scripts"
    sdir.mkdir(exist_ok=True)
    n = next(_NUM)
    script = sdir / f"cmd_{n:04d}.sh"
    script.write_text(f"#!/bin/bash\n{cmd}\n")
    script.chmod(0o755)
    return f"bash {script}"


def _whole(proj, cmd, role="engineer", ticket="T01", pre=True,
           session_id="test-session", agent_id=None, subagent=None,
           extra_env=None):
    n = next(_NUM)
    tuid = f"toolu_rv_{n:04d}"
    hook_cmd = _script(proj, cmd)
    if pre:
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, hook_cmd, tuid, session_id,
                            agent_id, subagent),
                  role, ticket, extra_env)
    bash = _bash(proj, cmd)
    post_hook = _hook(proj, "posttooluse*")
    post = _run_hook(proj, post_hook,
                     _post_data(proj, hook_cmd, tuid, session_id,
                                agent_id, subagent, bash),
                     role, ticket, extra_env)
    return post, tuid


def _findings(proj):
    fp = proj / FINDINGS_REL
    if not fp.is_file():
        return []
    return [json.loads(line) for line in fp.read_text().splitlines()
            if line.strip()]


def _new_findings(proj, before_count):
    return _findings(proj)[before_count:]


# ---- Point 1: restore verification after non-HEAD restore ------------

class TestRestoreFromPreCallHeadVerification:
    """After a non-forward HEAD move, ``_restore_from_head`` with a
    specific commit now verifies each path against that commit.  Paths
    that could not be restored are returned as failed and recorded as
    ``flagged``, not ``reverted``."""

    def test_normal_case_restored_and_reverted(self, tmp_path):
        """When the restore succeeds, the finding says ``reverted``
        and the pre-call content is back."""
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        original = (proj / acc).read_text()
        # A second commit so amend produces a non-forward move.
        (proj / "src" / "main.py").write_text("x = 2\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "second")
        before = len(_findings(proj))
        cmd = (f"git commit -q --amend --no-edit && "
               f"echo changed >> {acc}")
        post, _ = _whole(proj, cmd)
        nf = _new_findings(proj, before)
        # The acceptance test holds the pre-call HEAD content.
        assert (proj / acc).read_text() == original, (
            "acceptance test not restored to pre-call HEAD content")
        # Finding for the test says reverted.
        reverted = [f for f in nf if f["action"] == "reverted"
                    and acc in f.get("paths", [])]
        assert reverted, f"no reverted finding for {acc}: {nf}"

    def test_blocked_restore_says_flagged_not_reverted(self, tmp_path):
        """When the restore cannot bring a path back (the parent
        directory is read-only so ``git checkout`` cannot write the
        file), the finding says ``flagged`` and the report says the
        restore failed."""
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        acc_dir = proj / "tests" / "acceptance" / "T01"
        # A second commit so amend produces a non-forward move.
        (proj / "src" / "main.py").write_text("x = 2\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "second")

        # Run the three phases manually so we can lock the directory
        # between the command and the post-hook.
        n = next(_NUM)
        tuid = f"toolu_rv_{n:04d}"
        cmd = (f"git commit -q --amend --no-edit && "
               f"echo changed >> {acc}")
        hook_cmd = _script(proj, cmd)

        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, hook_cmd, tuid))
        bash = _bash(proj, cmd)

        # Make the parent directory read-only so that git checkout
        # cannot write the file back.  No special privileges needed.
        before = len(_findings(proj))
        acc_dir.chmod(0o555)
        try:
            post_hook = _hook(proj, "posttooluse*")
            post = _run_hook(proj, post_hook,
                             _post_data(proj, hook_cmd, tuid, bash=bash))
        finally:
            # Restore permissions so pytest can clean up tmp_path.
            acc_dir.chmod(0o755)

        nf = _new_findings(proj, before)
        # The acceptance test is NOT restored -- the file still has the
        # changed content because git checkout could not write.
        assert "changed" in (proj / acc).read_text(), (
            "expected the changed content to remain (restore should "
            "have failed)")
        # Finding for the test says flagged, not reverted.
        flagged = [f for f in nf if f["action"] == "flagged"
                   and acc in f.get("paths", [])]
        assert flagged, (
            f"expected a flagged finding for {acc} when restore "
            f"fails: {nf}")
        reverted = [f for f in nf if f["action"] == "reverted"
                    and acc in f.get("paths", [])]
        assert not reverted, (
            f"the path should NOT be recorded as reverted when "
            f"the restore failed: {nf}")
        # The report (post-hook stdout) should mention the failure.
        report = ""
        if post.returncode == 0 and post.stdout.strip():
            try:
                out = json.loads(post.stdout)
                report = (out.get("hookSpecificOutput", {})
                          .get("additionalContext", ""))
            except (json.JSONDecodeError, ValueError):
                report = post.stdout
        assert "not restored" in report.lower() or "failed" in report.lower(), (
            f"the report should mention the restore failure: "
            f"{report!r}")


# ---- Point 2: _get_pending_timeout validation ------------------------

class TestGetPendingTimeoutValidation:
    """``_get_pending_timeout()`` rejects values that are not a usable
    duration and falls back to the default 600."""

    @pytest.fixture(autouse=True)
    def _patch_env(self, monkeypatch):
        # Ensure there is no leftover env var.
        monkeypatch.delenv("GOV_PENDING_SNAPSHOT_TIMEOUT_S", raising=False)

    @pytest.mark.parametrize("value,expected", [
        ("", 600),
        ("abc", 600),
        ("0", 600),
        ("-5", 600),
        ("nan", 600),
        ("inf", 600),
        ("120", 120),
        ("0.5", 0.5),
    ])
    def test_get_pending_timeout(self, value, expected, monkeypatch):
        from gov.guard.containment import _get_pending_timeout
        monkeypatch.setenv("GOV_PENDING_SNAPSHOT_TIMEOUT_S", value)
        result = _get_pending_timeout()
        assert result == expected, (
            f"GOV_PENDING_SNAPSHOT_TIMEOUT_S={value!r}: "
            f"expected {expected}, got {result}")

    def test_unset_returns_default(self, monkeypatch):
        """When the env var is not set, the default 600 is returned."""
        from gov.guard.containment import _get_pending_timeout
        monkeypatch.delenv("GOV_PENDING_SNAPSHOT_TIMEOUT_S", raising=False)
        assert _get_pending_timeout() == 600
