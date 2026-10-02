"""Builder tests for the three review fixes.

Fix 1: pending snapshot of another actor means overlap (flag, never
       revert); same-actor leftover is cleaned up and does not cause
       overlap.
Fix 2: the sequence counter uses atomic O_APPEND increments.
Fix 3: ``_fp_changed_batch`` replaces per-path git calls.

Each test makes whole calls (pre hook, command, post hook) through a
small fixture project where needed, or exercises the function directly
for unit-level checks.  Does not import from ``tests/acceptance``.
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


def _env(proj, role="engineer", ticket="T01",
         session_id="test-session", agent_id=None):
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
    return env


def _hook(proj, pattern):
    hd = proj / "governance" / "kernel" / "hooks"
    hits = sorted(hd.glob(pattern))
    assert hits, f"no hook matches {pattern}"
    return hits[0]


def _run_hook(proj, hook_path, data, role="engineer", ticket="T01"):
    env = _env(proj, role, ticket)
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
        "tool_input": {"command": cmd} if tool_name == "Bash" else
                      {"file_path": cmd, "content": "x"},
        "tool_use_id": tuid,
    }
    if agent_id is not None:
        d["agent_id"] = agent_id
    if subagent:
        if "agent_id" not in d:
            d["agent_id"] = "sub-1"
        d["agent_type"] = subagent
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
    if agent_id is not None:
        d["agent_id"] = agent_id
    if subagent:
        if "agent_id" not in d:
            d["agent_id"] = "sub-1"
        d["agent_type"] = subagent
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


def _script_cmd(proj, cmd):
    """Save *cmd* as a script outside the project and return the
    ``bash <script>`` command string.  The guard cannot classify a
    script call, so it lets it through and the before-snapshot exists.
    """
    scripts = proj.parent / "scripts"
    scripts.mkdir(exist_ok=True)
    n = next(_NUM)
    sc = scripts / f"cmd_{n:04d}.sh"
    sc.write_text(cmd + "\n")
    return f"bash {sc}"


def _whole(proj, cmd, role="engineer", ticket="T01",
           pre=True, subagent=None, session_id="test-session",
           agent_id=None):
    """Run a whole call: pre hook, command, post hook.

    The command is saved as a script so the guard cannot classify it;
    this matches the acceptance-test convention.
    """
    hook_cmd = _script_cmd(proj, cmd)
    n = next(_NUM)
    tuid = f"toolu_review_{n:04d}"
    if pre:
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, hook_cmd, tuid, session_id=session_id,
                            agent_id=agent_id, subagent=subagent),
                  role, ticket)
    bash = _bash(proj, cmd)
    post_hook = _hook(proj, "posttooluse*")
    post = _run_hook(proj, post_hook,
                     _post_data(proj, hook_cmd, tuid,
                                session_id=session_id,
                                agent_id=agent_id, subagent=subagent,
                                bash=bash),
                     role, ticket)
    return post, tuid


def _agent_text(proc):
    if proc.returncode == 2:
        return proc.stderr.strip()
    if proc.returncode != 0:
        return ""
    try:
        d = json.loads(proc.stdout.strip() or "null")
    except ValueError:
        return ""
    if not isinstance(d, dict):
        return ""
    sp = d.get("hookSpecificOutput")
    if isinstance(sp, dict):
        return sp.get("additionalContext", "")
    return ""


def _findings(proj):
    fp = proj / FINDINGS_REL
    if not fp.is_file():
        return []
    return [json.loads(l) for l in fp.read_text().splitlines() if l.strip()]


def _new_findings(proj, before_count):
    return _findings(proj)[before_count:]


# ====================================================================
# Fix 1 — pending snapshot of another actor means overlap
# ====================================================================

class TestPendingSnapshotOverlap:
    """Probe case 5b: a designer subagent's call started earlier and
    still runs; the new acceptance test survives the engineer's check
    and the finding says flagged."""

    def test_5b_other_actors_earlier_call_still_running(self, tmp_path):
        proj = _make_project(tmp_path)
        new_test = "tests/acceptance/T01/test_new_by_designer.py"
        cmd_designer = f"echo 'def test_x(): pass' > {new_test}"

        # Designer subagent starts FIRST (pre hook).
        n1 = next(_NUM)
        tuid_designer = f"toolu_review_{n1:04d}"
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, cmd_designer, tuid_designer,
                            session_id="sess-orch",
                            agent_id="designer-sub-1",
                            subagent="independent-test-designer"),
                  "orchestrator", "T01")

        # Engineer starts SECOND (pre hook).
        n2 = next(_NUM)
        tuid_eng = f"toolu_review_{n2:04d}"
        _run_hook(proj, pre_hook,
                  _pre_data(proj, "ls", tuid_eng,
                            session_id="sess-eng"),
                  "engineer", "T01")

        # Designer's command writes the file.
        _bash(proj, cmd_designer)

        # Engineer's call ends and post hook runs.
        bash_eng = _bash(proj, "ls")
        post_hook = _hook(proj, "posttooluse*")
        before = len(_findings(proj))
        post = _run_hook(proj, post_hook,
                         _post_data(proj, "ls", tuid_eng,
                                    session_id="sess-eng",
                                    bash=bash_eng),
                         "engineer", "T01")

        # The designer's new test must survive.
        assert (proj / new_test).exists(), \
            "designer's new test was deleted by engineer's check"

        # Any finding for it must say flagged, not reverted.
        nf = _new_findings(proj, before)
        for f in nf:
            if new_test in f.get("paths", []):
                assert f["action"] == "flagged", \
                    f"expected flagged, got {f['action']}"


class TestSameActorLeftoverCleanup:
    """Probe case 5c: same-actor leftover is cleaned up and does not
    prevent the restore."""

    def test_5c_leftover_removed_and_restore_happens(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"

        # Same actor takes a snapshot that never completes (leftover).
        n1 = next(_NUM)
        tuid_leftover = f"toolu_review_{n1:04d}"
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, "ls", tuid_leftover,
                            session_id="sess-eng"),
                  "engineer", "T01")

        # Same actor makes a real call: pre hook, change, post hook.
        before = len(_findings(proj))
        post, tuid_real = _whole(proj, f"echo '# engineer' >> {acc}",
                                 session_id="sess-eng")

        # The engineer's change to the test must be restored.
        assert "# engineer" not in (proj / acc).read_text()
        nf = _new_findings(proj, before)
        reverted = [f for f in nf if f["action"] == "reverted"]
        assert reverted, \
            f"same-actor leftover prevented restore: {[f['action'] for f in nf]}"

        # The leftover snapshot file must be gone.
        snap_file = proj / SNAPSHOT_DIR_REL / f"{tuid_leftover}.json"
        assert not snap_file.exists(), "leftover snapshot was not removed"


class TestDifferentSessionPendingOverlap:
    """A different session (other session_id, no agent_id) with a
    pending snapshot means overlap."""

    def test_different_session_pending_causes_overlap(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"

        # Session B starts a call (pre hook) but never finishes.
        n1 = next(_NUM)
        tuid_b = f"toolu_review_{n1:04d}"
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, "ls", tuid_b,
                            session_id="sess-other"),
                  "engineer", "T01")

        # Session A runs a full call that modifies an acceptance test.
        before = len(_findings(proj))
        post, _ = _whole(proj, f"echo '# engineer' >> {acc}",
                         session_id="sess-eng")

        # Attribution is uncertain; change must be flagged, not reverted.
        nf = _new_findings(proj, before)
        acc_findings = [f for f in nf if acc in f.get("paths", [])]
        assert acc_findings, "no finding for the acceptance test"
        for f in acc_findings:
            assert f["action"] == "flagged", \
                f"expected flagged, got {f['action']}"
        # The engineer's change survives (not restored).
        assert "# engineer" in (proj / acc).read_text()


class TestOldPendingSnapshotIgnored:
    """A pending snapshot older than the clean-up age is not treated
    as overlap."""

    def test_old_snapshot_does_not_cause_overlap(self, tmp_path):
        from gov.guard.containment import (
            take_snapshot, check_containment, _CLEANUP_AGE_S,
            SNAPSHOT_DIR_REL,
        )
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"

        # Another session takes a snapshot (different actor).
        take_snapshot(str(proj), "toolu_old", "sess-other", "")

        # Age the snapshot beyond cleanup age.
        old_snap = proj / SNAPSHOT_DIR_REL / "toolu_old.json"
        old_time = time.time() - _CLEANUP_AGE_S - 10
        os.utime(str(old_snap), (old_time, old_time))

        # Our actor takes its snapshot and modifies an acceptance test.
        take_snapshot(str(proj), "toolu_ours", "sess-eng", "")
        (proj / acc).write_text("# changed\n")
        report = check_containment(
            str(proj), "engineer", "T01", None,
            "sess-eng", None, "echo changed", "toolu_ours")

        ff = _findings(proj)
        # The old snapshot must not cause overlap, so the restore happens.
        reverted = [f for f in ff if f["action"] == "reverted"]
        assert reverted, \
            f"old snapshot incorrectly caused overlap: {[f['action'] for f in ff]}"


# ====================================================================
# Fix 2 — atomic sequence counter
# ====================================================================

class TestAtomicCounter:
    """The counter uses an append-only file; N increments give N."""

    def test_n_increments_give_n(self, tmp_path):
        from gov.guard.containment import _increment_seq, _read_seq
        root = str(tmp_path)
        assert _read_seq(root) == 0
        for i in range(1, 51):
            val = _increment_seq(root)
            assert val == i, f"after {i} increments, got {val}"
        assert _read_seq(root) == 50

    def test_write_tool_marker_causes_overlap(self, tmp_path):
        """A Write/Edit during a running Bash call increments the
        counter, so the Bash call's check sees overlap."""
        proj = _make_project(tmp_path)
        new_test = "tests/acceptance/T01/test_new.py"

        # Engineer starts Bash call (pre hook).
        n = next(_NUM)
        tuid = f"toolu_review_{n:04d}"
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, "ls", tuid),
                  "engineer", "T01")

        # Designer subagent's Write goes through pre hook (increments seq).
        wn = next(_NUM)
        wtuid = f"toolu_review_{wn:04d}"
        wp = _pre_data(proj, str(proj / new_test), wtuid,
                       subagent="independent-test-designer",
                       tool_name="Write")
        wp["tool_name"] = "Write"
        wp["tool_input"] = {"file_path": str(proj / new_test),
                            "content": "x"}
        _run_hook(proj, pre_hook, wp, "engineer", "T01")
        (proj / new_test).parent.mkdir(parents=True, exist_ok=True)
        (proj / new_test).write_text("def test_x(): pass\n")

        # Engineer's Bash finishes.
        bash = _bash(proj, "ls")
        post_hook = _hook(proj, "posttooluse*")
        before = len(_findings(proj))
        post = _run_hook(proj, post_hook,
                         _post_data(proj, "ls", tuid, bash=bash),
                         "engineer", "T01")

        # The test must survive (overlap prevents restore).
        assert (proj / new_test).exists(), \
            "write-tool overlap did not protect the designer's test"


# ====================================================================
# Fix 3 — batched fingerprint comparison (twenty dirty paths)
# ====================================================================

class TestBatchedFingerprintComparison:
    """Twenty already-dirty paths, one of them changed again by the
    call.  Exactly that one is flagged."""

    def test_twenty_dirty_one_changed(self, tmp_path):
        proj = _make_project(tmp_path)

        # Create 20 dirty out-of-scope files before the call.
        for i in range(20):
            (proj / "docs" / f"dirty_{i:02d}.md").write_text(
                f"dirty content {i}\n")

        # Take a snapshot (pre hook for a whole call).
        n = next(_NUM)
        tuid = f"toolu_review_{n:04d}"
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, "ls", tuid),
                  "engineer", "T01")

        # Change exactly one of the dirty files.
        target = "docs/dirty_07.md"
        (proj / target).write_text("changed again\n")

        # Run post hook.
        bash = _bash(proj, "ls")
        post_hook = _hook(proj, "posttooluse*")
        before = len(_findings(proj))
        post = _run_hook(proj, post_hook,
                         _post_data(proj, "ls", tuid, bash=bash),
                         "engineer", "T01")

        text = _agent_text(post)
        nf = _new_findings(proj, before)

        # Exactly the changed file is named.
        flagged_paths = set()
        for f in nf:
            flagged_paths.update(f.get("paths", []))

        assert target in flagged_paths, \
            f"changed file not flagged: {flagged_paths}"

        # None of the other 19 dirty files are named.
        for i in range(20):
            if i == 7:
                continue
            other = f"docs/dirty_{i:02d}.md"
            assert other not in flagged_paths, \
                f"unchanged dirty file {other} was incorrectly flagged"
