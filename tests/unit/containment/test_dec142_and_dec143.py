"""Builder tests for DEC-142/144/145/146 (pending snapshot timeout and
actor-level clearing) and DEC-143 (restore from pre-call HEAD after a
non-forward HEAD move).

Each test makes whole calls (pre hook, command, post hook) through a
small fixture project, exercising the hooks as the harness would.
Does not import from ``tests/acceptance``.
"""

from __future__ import annotations

import itertools
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
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


# ---- helpers -------------------------------------------------------

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
    """Write *cmd* to a shell script and return a ``bash <script>``
    command line.  The pre-hook sees the wrapper, not the raw write
    targets, so the guard allows it and the snapshot is taken."""
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
    """Run a whole call: pre hook, command, post hook.

    The command is wrapped in a script so the pre-hook's write
    analysis sees a benign ``bash <script>`` and allows the call.
    """
    n = next(_NUM)
    tuid = f"toolu_dec142_{n:04d}"
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
    return [json.loads(l) for l in fp.read_text().splitlines()
            if l.strip()]


def _new_findings(proj, before_count):
    return _findings(proj)[before_count:]


def _begin(proj, cmd, session_id="test-session", agent_id=None,
           subagent=None, role="engineer", ticket="T01"):
    """Run just the PreToolUse hook for a Bash call (takes snapshot,
    no post-hook follows -- simulates a call that never ended)."""
    n = next(_NUM)
    tuid = f"toolu_dec142_{n:04d}"
    pre_hook = _hook(proj, "pretooluse*")
    _run_hook(proj, pre_hook,
              _pre_data(proj, cmd, tuid, session_id, agent_id,
                        subagent),
              role, ticket)
    return tuid


def _issue_non_bash_tool(proj, session_id="test-session",
                         agent_id=None, subagent=None,
                         role="engineer", ticket="T01"):
    """Run the PreToolUse hook for a Read call.  The hook runs
    ``_note_tool_call`` which clears this actor's pending snapshots."""
    n = next(_NUM)
    tuid = f"toolu_dec142_{n:04d}"
    pre_hook = _hook(proj, "pretooluse*")
    _run_hook(proj, pre_hook,
              _pre_data(proj, str(proj / "README.md"), tuid,
                        session_id, agent_id, subagent,
                        tool_name="Read"),
              role, ticket)
    return tuid


def _age_snapshots(proj, seconds_ago):
    """Set the mtime of all snapshot JSON files to *seconds_ago* in
    the past.  Only touches ``.json`` files; the seq counter is left
    alone."""
    sdir = proj / SNAPSHOT_DIR_REL
    if not sdir.is_dir():
        return
    target = time.time() - seconds_ago
    for f in sdir.iterdir():
        if f.suffix == ".json":
            os.utime(f, (target, target))


# ---- DEC-142/144/145/146: pending snapshot timeout -----------------

class TestSameActorLaterNonBashClears:
    """DEC-142: a later tool call of the same actor (any tool, any
    guard decision) proves its earlier call is over and clears the
    leftover snapshot."""

    def test_later_read_clears_leftover(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        # Actor A starts a Bash call (pre-hook only, no post).
        _begin(proj, "ls", session_id="sess-A")
        # Actor A issues a Read call -- clears its leftover.
        _issue_non_bash_tool(proj, session_id="sess-A")
        # Engineer changes an acceptance test in a full call.
        before = len(_findings(proj))
        post, _ = _whole(proj, f"echo changed >> {acc}",
                         session_id="sess-eng")
        nf = _new_findings(proj, before)
        reverted = [f for f in nf if f["action"] == "reverted"
                    and acc in f.get("paths", [])]
        assert reverted, (
            "the same actor's later Read should clear the leftover "
            f"and allow the restore; findings: {nf}")
        assert (proj / acc).read_text() == "def test_pass(): pass\n"


class TestAnotherActorDoesNotClear:
    """DEC-142: another actor's later call does not clear the first
    actor's pending snapshot."""

    def test_different_session_does_not_clear(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        # Actor A starts a Bash call (pre-hook only, no post).
        _begin(proj, "ls", session_id="sess-A")
        # Actor B (different session) issues a Read call -- does NOT
        # clear Actor A's snapshot.
        _issue_non_bash_tool(proj, session_id="sess-B")
        # Engineer changes an acceptance test in a full call.
        before = len(_findings(proj))
        post, _ = _whole(proj, f"echo changed >> {acc}",
                         session_id="sess-eng")
        nf = _new_findings(proj, before)
        flagged = [f for f in nf if f["action"] == "flagged"
                   and acc in f.get("paths", [])]
        assert flagged, (
            "another actor's call should NOT clear the first actor's "
            f"snapshot; the test should be flagged: {nf}")
        assert "changed" in (proj / acc).read_text()

    def test_different_agent_id_does_not_clear(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        # Actor A: session + agent_id "agent-A".
        _begin(proj, "ls", session_id="sess-X",
               agent_id="agent-A")
        # Same session but different agent_id issues a Read call.
        _issue_non_bash_tool(proj, session_id="sess-X",
                             agent_id="agent-B")
        # Engineer changes an acceptance test in a full call.
        before = len(_findings(proj))
        post, _ = _whole(proj, f"echo changed >> {acc}",
                         session_id="sess-eng")
        nf = _new_findings(proj, before)
        flagged = [f for f in nf if f["action"] == "flagged"
                   and acc in f.get("paths", [])]
        assert flagged, (
            "a different agent_id should NOT clear another agent's "
            f"snapshot; the test should be flagged: {nf}")


class TestPendingSnapshotTimeout:
    """DEC-142/144: a pending snapshot of another actor stops blocking
    after the timeout (600 s) and still blocks just before it."""

    def test_stops_blocking_after_timeout(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        # Actor A starts a Bash call.
        _begin(proj, "ls", session_id="sess-A")
        # Age Actor A's snapshot past the timeout (660 > 600).
        _age_snapshots(proj, 660)
        # Engineer's full call changes acceptance test -- restored.
        before = len(_findings(proj))
        post, _ = _whole(proj, f"echo changed >> {acc}",
                         session_id="sess-eng")
        nf = _new_findings(proj, before)
        reverted = [f for f in nf if f["action"] == "reverted"
                    and acc in f.get("paths", [])]
        assert reverted, (
            f"after 660 s the leftover should no longer block: {nf}")
        assert (proj / acc).read_text() == "def test_pass(): pass\n"

    def test_still_blocks_just_before_timeout(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        # Actor A starts a Bash call.
        _begin(proj, "ls", session_id="sess-A")
        # Age to just before the timeout (540 < 600).
        _age_snapshots(proj, 540)
        # Engineer's full call changes acceptance test -- flagged.
        before = len(_findings(proj))
        post, _ = _whole(proj, f"echo changed >> {acc}",
                         session_id="sess-eng")
        nf = _new_findings(proj, before)
        flagged = [f for f in nf if f["action"] == "flagged"
                   and acc in f.get("paths", [])]
        assert flagged, (
            f"at 540 s the leftover should still block: {nf}")
        assert "changed" in (proj / acc).read_text()


class TestPendingSnapshotTimeoutEnvVar:
    """DEC-145: ``GOV_PENDING_SNAPSHOT_TIMEOUT_S`` overrides the
    default; a non-number value falls back to 600."""

    def test_custom_timeout_shortens_the_wait(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        _begin(proj, "ls", session_id="sess-A")
        # Age to 130 s (past the custom timeout of 120).
        _age_snapshots(proj, 130)
        before = len(_findings(proj))
        post, _ = _whole(
            proj, f"echo changed >> {acc}",
            session_id="sess-eng",
            extra_env={"GOV_PENDING_SNAPSHOT_TIMEOUT_S": "120"})
        nf = _new_findings(proj, before)
        reverted = [f for f in nf if f["action"] == "reverted"
                    and acc in f.get("paths", [])]
        assert reverted, (
            "with GOV_PENDING_SNAPSHOT_TIMEOUT_S=120 and age=130 s "
            f"the leftover should no longer block: {nf}")

    def test_non_number_falls_back_to_default(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        _begin(proj, "ls", session_id="sess-A")
        # Age to 590 s (still under the default 600).
        _age_snapshots(proj, 590)
        before = len(_findings(proj))
        post, _ = _whole(
            proj, f"echo changed >> {acc}",
            session_id="sess-eng",
            extra_env={"GOV_PENDING_SNAPSHOT_TIMEOUT_S": "abc"})
        nf = _new_findings(proj, before)
        flagged = [f for f in nf if f["action"] == "flagged"
                   and acc in f.get("paths", [])]
        assert flagged, (
            "with GOV_PENDING_SNAPSHOT_TIMEOUT_S=abc and age=590 s "
            f"the default (600) should apply, still blocking: {nf}")


# ---- DEC-143: restore from pre-call HEAD ---------------------------

class TestDEC143RestoreFromPreCallHead:
    """DEC-143: after a non-forward HEAD move, a non-designer's
    changed acceptance test is restored from the pre-call HEAD.
    The HEAD move itself is flagged and never reverted."""

    def test_amend_plus_changed_test_is_restored(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        original = (proj / acc).read_text()
        # A second commit so amend produces a non-forward move.
        (proj / "src" / "main.py").write_text("x = 2\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "second")
        pre_head = _git(proj, "rev-parse", "HEAD").strip()
        # Engineer amends HEAD and changes the acceptance test.
        before = len(_findings(proj))
        cmd = (f"git commit -q --amend --no-edit && "
               f"echo changed >> {acc}")
        post, _ = _whole(proj, cmd)
        post_head = _git(proj, "rev-parse", "HEAD").strip()
        nf = _new_findings(proj, before)
        # The acceptance test holds the pre-call HEAD content.
        assert (proj / acc).read_text() == original, (
            "acceptance test not restored to pre-call HEAD content")
        # HEAD stays where the call left it (not reverted).
        assert post_head != pre_head, "HEAD should have moved"
        # Finding for the test says reverted.
        reverted = [f for f in nf if f["action"] == "reverted"
                    and acc in f.get("paths", [])]
        assert reverted, f"no reverted finding for {acc}: {nf}"
        # Finding for the HEAD move says flagged.
        head_flagged = [f for f in nf if f["action"] == "flagged"
                        and "HEAD" in f.get("reason", "")]
        assert head_flagged, f"no flagged finding for HEAD move: {nf}"

    def test_reset_hard_plus_new_test_is_restored(self, tmp_path):
        proj = _make_project(tmp_path)
        new_test = "tests/acceptance/T01/test_new.py"
        # A second commit.
        (proj / "src" / "main.py").write_text("x = 2\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "second")
        before = len(_findings(proj))
        cmd = (f"git reset -q --hard HEAD~1 && "
               f"echo new > {new_test}")
        post, _ = _whole(proj, cmd)
        nf = _new_findings(proj, before)
        # The new test is gone (pre-call HEAD did not have it).
        assert not (proj / new_test).exists(), (
            f"{new_test} should have been removed by restore")
        reverted = [f for f in nf if f["action"] == "reverted"
                    and new_test in f.get("paths", [])]
        assert reverted, f"no reverted finding for {new_test}: {nf}"


class TestDEC143UncertainAttribution:
    """Without a before-snapshot, attribution is uncertain: the
    acceptance test is flagged and nothing is restored."""

    def test_no_snapshot_means_flagged(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        # A second commit.
        (proj / "src" / "main.py").write_text("x = 2\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "second")
        # First call to populate last_head.
        _whole(proj, "ls")
        before = len(_findings(proj))
        # Engineer amends and changes test WITHOUT a snapshot.
        cmd = (f"git commit -q --amend --no-edit && "
               f"echo changed >> {acc}")
        post, _ = _whole(proj, cmd, pre=False)
        nf = _new_findings(proj, before)
        flagged = [f for f in nf if f["action"] == "flagged"
                   and acc in f.get("paths", [])]
        assert flagged, (
            f"without a snapshot the test should be flagged: {nf}")
        assert "changed" in (proj / acc).read_text()
        assert not any(f["action"] == "reverted" for f in nf), (
            f"nothing should be reverted without a snapshot: {nf}")


class TestDEC143DirtyBeforeCall:
    """A path dirty before the call is never restored, even next to
    a non-forward HEAD move."""

    def test_dirty_acceptance_test_stays(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        # Designer changes the acceptance test before the call.
        _bash(proj, f"echo '# designer' >> {acc}")
        # A second commit (only src, not the acceptance test).
        (proj / "src" / "main.py").write_text("x = 2\n")
        _git(proj, "add", "src/main.py")
        _git(proj, "commit", "-q", "-m", "second")
        # Engineer's call: amend + change the already-dirty test.
        before = len(_findings(proj))
        cmd = (f"git commit -q --amend --no-edit && "
               f"echo '# engineer' >> {acc}")
        post, _ = _whole(proj, cmd)
        nf = _new_findings(proj, before)
        # Dirty at snapshot time -- not restored, only flagged.
        flagged = [f for f in nf if f["action"] == "flagged"
                   and acc in f.get("paths", [])]
        assert flagged, (
            f"dirty-at-snapshot test should be flagged: {nf}")
        reverted = [f for f in nf if f["action"] == "reverted"
                    and acc in f.get("paths", [])]
        assert not reverted, (
            f"dirty-at-snapshot test should NOT be reverted: {nf}")
        # Both the designer's and engineer's content survive.
        text = (proj / acc).read_text()
        assert "# designer" in text and "# engineer" in text


class TestDEC143DesignerKeepsChanges:
    """The test designer's own change next to its own HEAD move
    stays: the changes are in scope for the designer, so they never
    enter the breach list."""

    def test_designer_changes_stay(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        new_test = "tests/acceptance/T01/test_new.py"
        # A second commit.
        (proj / "src" / "main.py").write_text("x = 2\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "second")
        before = len(_findings(proj))
        cmd = (f"git reset -q --hard HEAD~1 && "
               f"echo changed >> {acc} && echo new > {new_test}")
        # Designer role: acceptance tests are in scope.
        post, _ = _whole(proj, cmd,
                         role="independent-test-designer")
        nf = _new_findings(proj, before)
        # The designer's changes STAY.
        assert "changed" in (proj / acc).read_text(), (
            "the designer's acceptance test change was removed")
        assert (proj / new_test).exists(), (
            "the designer's new test was removed")
        # No reverted findings at all.
        reverted = [f for f in nf if f["action"] == "reverted"]
        assert not reverted, (
            f"nothing should be reverted for the designer: {nf}")
        # HEAD move is still flagged.
        head_flagged = [f for f in nf if f["action"] == "flagged"
                        and "HEAD" in f.get("reason", "")]
        assert head_flagged, (
            f"HEAD move should still be flagged: {nf}")
