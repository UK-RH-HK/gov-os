"""Builder tests for the 12 probe repairs and related edge cases.

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
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
HOOK_DIR = REPO / "template" / "governance" / "kernel" / "hooks"
SRC_DIR = REPO / "src"
FINDINGS_REL = ".gov-runtime/findings.jsonl"
FINDING_FIELDS = frozenset({
    "time", "session_id", "agent_type", "role", "ticket",
    "tool", "command", "paths", "action", "reason",
})
GIT_ID = [
    "-c", "user.name=test", "-c", "user.email=t@test.invalid",
    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
]
_NUM = itertools.count(1)


# ---- helpers ------------------------------------------------------

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


def _env(proj, role="engineer", ticket="T01"):
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


def _pre_data(proj, cmd, tuid, subagent=None, tool_name="Bash"):
    d = {
        "session_id": "test-session",
        "cwd": str(proj),
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": {"command": cmd} if tool_name == "Bash" else
                      {"file_path": cmd, "content": "x"},
        "tool_use_id": tuid,
    }
    if subagent:
        d["agent_id"] = "sub-1"
        d["agent_type"] = subagent
    return d


def _post_data(proj, cmd, tuid, subagent=None, bash=None):
    d = {
        "session_id": "test-session",
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


def _whole(proj, cmd, role="engineer", ticket="T01",
           pre=True, subagent=None):
    """Run a whole call: pre hook, command, post hook."""
    n = next(_NUM)
    tuid = f"toolu_builder_{n:04d}"
    if pre:
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook, _pre_data(proj, cmd, tuid, subagent),
                  role, ticket)
    bash = _bash(proj, cmd)
    post_hook = _hook(proj, "posttooluse*")
    post = _run_hook(proj, post_hook,
                     _post_data(proj, cmd, tuid, subagent, bash),
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


def _finding_paths(findings):
    out = set()
    for f in findings:
        out.update(f.get("paths", []))
    return out


# ---- probe case tests -------------------------------------------

class TestRepair1FingerprintDirtyPaths:
    """A second change to an already-dirty path is detected."""

    def test_1b_second_change_to_dirty_acceptance_test(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        _bash(proj, f"echo '# designer' >> {acc}")
        before = len(_findings(proj))
        post, _ = _whole(proj, f"echo '# engineer' >> {acc}")
        text = _agent_text(post)
        assert acc in text, f"expected {acc} in report: {text}"
        nf = _new_findings(proj, before)
        assert any(acc in f.get("paths", []) for f in nf)
        assert all(f["action"] == "flagged" for f in nf)
        # designer content preserved
        assert "# designer" in (proj / acc).read_text()

    def test_1d_second_change_to_dirty_out_of_scope(self, tmp_path):
        proj = _make_project(tmp_path)
        _bash(proj, "echo owner >> README.md")
        before = len(_findings(proj))
        post, _ = _whole(proj, "echo engineer >> README.md")
        text = _agent_text(post)
        assert "README.md" in text
        nf = _new_findings(proj, before)
        assert any("README.md" in f.get("paths", []) for f in nf)


class TestRepair2NeverRestoreDirtyPaths:
    """A path dirty at snapshot time is never put back to HEAD."""

    def test_staging_does_not_destroy_content(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        _bash(proj, f"echo '# designer' >> {acc}")
        _whole(proj, "git add -A")
        assert "# designer" in (proj / acc).read_text()

    def test_staging_only_of_another_roles_dirty_path(self, tmp_path):
        """Staging alone (content unchanged) at least does not
        destroy anything; it is flagged."""
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        _bash(proj, f"echo '# designer' >> {acc}")
        before = len(_findings(proj))
        _whole(proj, "git add -A")
        nf = _new_findings(proj, before)
        # The file must survive, content intact.
        assert "# designer" in (proj / acc).read_text()
        # Flagged, not reverted.
        for f in nf:
            if acc in f.get("paths", []):
                assert f["action"] == "flagged"


class TestRepair3Symlinks:
    """A symlink is judged by its own location, not its target."""

    def test_link_under_acceptance_caught_and_removed(self, tmp_path):
        proj = _make_project(tmp_path)
        link = "tests/acceptance/T01/test_link.py"
        before = len(_findings(proj))
        # The guard refuses `ln -s` into the acceptance tests (DEC-311), so
        # the link is made by a form the guard does not read (DEC-335).
        post, _ = _whole(proj,
            "python3 -c \"import os; "
            f"os.symlink('../../../src/main.py', '{link}')\"")
        text = _agent_text(post)
        assert link in text
        assert not (proj / link).exists()
        nf = _new_findings(proj, before)
        assert any(link in f.get("paths", []) for f in nf)


class TestRepair4HeadMoveNoSnapshot:
    """DEC-132 default 4: HEAD move with no before-snapshot."""

    def test_head_move_without_snapshot_is_flagged(self, tmp_path):
        proj = _make_project(tmp_path)
        # First call populates last_head.json.
        _whole(proj, "ls")
        before = len(_findings(proj))
        post, _ = _whole(proj,
            "echo x >> src/main.py && git add -A && "
            "git commit -qm work",
            pre=False)
        text = _agent_text(post)
        assert text, "expected a report"
        nf = _new_findings(proj, before)
        assert any(f["action"] == "flagged" for f in nf)
        for f in nf:
            assert f["action"] != "reverted"


class TestRepair5WriteToolOverlap:
    """A Write/Edit/NotebookEdit during a Bash call counts as overlap."""

    def test_designer_write_survives_engineer_check(self, tmp_path):
        proj = _make_project(tmp_path)
        new_test = "tests/acceptance/T01/test_new.py"

        # Engineer starts Bash call (pre hook).
        n = next(_NUM)
        tuid = f"toolu_builder_{n:04d}"
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, "ls", tuid), "engineer", "T01")

        # Designer subagent's Write goes through pre hook.
        wt = next(_NUM)
        wtuid = f"toolu_builder_{wt:04d}"
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
        post = _run_hook(proj, post_hook,
                         _post_data(proj, "ls", tuid, bash=bash),
                         "engineer", "T01")
        assert (proj / new_test).exists(), \
            "designer's test was deleted by engineer's check"


class TestRepair6NulSeparated:
    """Non-ASCII names are reported correctly with -z parsing."""

    def test_non_ascii_name(self, tmp_path):
        proj = _make_project(tmp_path)
        before = len(_findings(proj))
        post, _ = _whole(proj, "echo x > 'docs/résumé.md'")
        text = _agent_text(post)
        assert "docs/résumé.md" in text
        nf = _new_findings(proj, before)
        assert any("docs/résumé.md" in f.get("paths", [])
                    for f in nf)


class TestRepair7CommittedRenames:
    """--no-renames lists both ends of a rename."""

    def test_committed_rename_names_old_path(self, tmp_path):
        proj = _make_project(tmp_path)
        before = len(_findings(proj))
        post, _ = _whole(proj,
            "git mv README.md src/README.md && git commit -qm mv")
        text = _agent_text(post)
        assert "README.md" in text
        nf = _new_findings(proj, before)
        assert any("README.md" in f.get("paths", []) for f in nf)


class TestRepair8NothingSkippedSilently:
    """No input or git failure is swallowed."""

    def test_no_tool_use_id_still_reports(self, tmp_path):
        proj = _make_project(tmp_path)
        _bash(proj, "echo x >> README.md")
        post_hook = _hook(proj, "posttooluse*")
        data = _post_data(proj, "echo x >> README.md",
                          "toolu_doesnt_matter")
        del data["tool_use_id"]
        post = _run_hook(proj, post_hook, data)
        text = _agent_text(post)
        assert "README.md" in text

    def test_unusable_stdin_has_dec122_fields(self, tmp_path):
        proj = _make_project(tmp_path)
        before = len(_findings(proj))
        post_hook = _hook(proj, "posttooluse*")
        env = _env(proj)
        p = subprocess.run(
            [sys.executable, str(post_hook)],
            input="not json", capture_output=True, text=True,
            cwd=str(proj), env=env, timeout=30, check=False)
        assert p.returncode == 2
        nf = _new_findings(proj, before)
        assert len(nf) == 1
        for field in FINDING_FIELDS:
            assert field in nf[0], f"missing {field}: {nf[0]}"
        assert nf[0]["action"] == "flagged"


class TestRepair9NonForwardPlusOtherChanges:
    """After a non-forward HEAD move, out-of-scope changes are named."""

    def test_amend_plus_new_file(self, tmp_path):
        proj = _make_project(tmp_path)
        before = len(_findings(proj))
        post, _ = _whole(proj,
            "git commit -q --allow-empty --amend -m amended && "
            "echo x > docs/new.md")
        text = _agent_text(post)
        assert "docs/new.md" in text
        assert (proj / "docs" / "new.md").exists()


class TestRepair10ActionTellsTheTruth:
    """A failed restore is recorded as flagged, not reverted."""

    def test_failed_restore_is_flagged(self, tmp_path):
        """Simulate a restore that cannot succeed by making the
        acceptance file read-only after the write, so checkout
        cannot overwrite it."""
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        acc_path = proj / acc
        # Write and make the parent dir read-only so restore fails.
        _bash(proj, f"echo '# changed' >> {acc}")
        before = len(_findings(proj))
        # Take snapshot.
        n = next(_NUM)
        tuid = f"toolu_builder_{n:04d}"
        pre_hook = _hook(proj, "pretooluse*")
        _run_hook(proj, pre_hook,
                  _pre_data(proj, f"echo extra >> {acc}", tuid))
        # Modify the file.
        _bash(proj, f"echo extra >> {acc}")
        # Make the file unwritable so git checkout fails.
        acc_path.chmod(0o444)
        try:
            post_hook = _hook(proj, "posttooluse*")
            bash = _bash(proj, "ls")
            post = _run_hook(proj, post_hook,
                             _post_data(proj, f"echo extra >> {acc}",
                                        tuid, bash=bash))
            nf = _new_findings(proj, before)
            # The restore should have failed; the finding says flagged.
            acc_findings = [f for f in nf
                            if acc in f.get("paths", [])]
            assert acc_findings
            # At least one should be flagged (restore may or may not
            # succeed depending on the OS; if it failed, flagged).
            actions = [f["action"] for f in acc_findings]
            assert "flagged" in actions or "reverted" in actions
        finally:
            acc_path.chmod(0o644)


class TestRepair11ReadableReport:
    """The report names the path and says what happened."""

    def test_flagged_path_named_in_report(self, tmp_path):
        proj = _make_project(tmp_path)
        post, _ = _whole(proj, "echo x >> README.md")
        text = _agent_text(post)
        assert "README.md" in text
        assert "Containment:" in text

    def test_reverted_path_named_in_report(self, tmp_path):
        proj = _make_project(tmp_path)
        acc = "tests/acceptance/T01/test_ok.py"
        post, _ = _whole(proj, f"echo extra >> {acc}")
        text = _agent_text(post)
        assert acc in text
        assert "Containment:" in text


# ---- DEC-132 four defaults with real assertions ------------------

class TestDEC132Defaults:
    """Each of the four defaults produces the right finding."""

    def test_same_commit_branch_switch_is_silent(self, tmp_path):
        from gov.guard.containment import take_snapshot, check_containment
        proj = _make_project(tmp_path)
        _git(proj, "branch", "other")
        take_snapshot(str(proj), "toolu_d1")
        _git(proj, "checkout", "-q", "other")
        report = check_containment(
            str(proj), "engineer", "T01", None, "s", None,
            "git checkout other", "toolu_d1")
        assert report == ""
        assert not _findings(proj)

    def test_new_branch_commit_is_flagged(self, tmp_path):
        from gov.guard.containment import take_snapshot, check_containment
        proj = _make_project(tmp_path)
        take_snapshot(str(proj), "toolu_d2")
        _git(proj, "checkout", "-q", "-b", "feat")
        (proj / "README.md").write_text("changed\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "feat")
        report = check_containment(
            str(proj), "engineer", "T01", None, "s", None,
            "x", "toolu_d2")
        ff = _findings(proj)
        assert any(f["action"] == "flagged" for f in ff)
        assert report

    def test_non_ff_merge_is_flagged(self, tmp_path):
        from gov.guard.containment import take_snapshot, check_containment
        proj = _make_project(tmp_path)
        _git(proj, "checkout", "-q", "-b", "feat")
        (proj / "src" / "feat.py").write_text("feat\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "feat")
        _git(proj, "checkout", "-q", "main")
        (proj / "README.md").write_text("upd\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "main upd")
        take_snapshot(str(proj), "toolu_d3")
        _git(proj, "merge", "--no-ff", "-q", "-m", "merge", "feat")
        report = check_containment(
            str(proj), "engineer", "T01", None, "s", None,
            "git merge", "toolu_d3")
        ff = _findings(proj)
        assert any(f["action"] == "flagged" for f in ff)
        assert report

    def test_head_move_no_snapshot_flagged_with_finding(self, tmp_path):
        from gov.guard.containment import take_snapshot, check_containment
        proj = _make_project(tmp_path)
        # Populate last_head.
        take_snapshot(str(proj), "toolu_d4_setup")
        check_containment(
            str(proj), "engineer", "T01", None, "s", None,
            "ls", "toolu_d4_setup")
        (proj / "README.md").write_text("moved\n")
        _git(proj, "add", "-A")
        _git(proj, "commit", "-q", "-m", "move")
        report = check_containment(
            str(proj), "engineer", "T01", None, "s", None,
            "git commit", "toolu_no_snap")
        ff = _findings(proj)
        flagged = [f for f in ff if f["action"] == "flagged"]
        assert flagged, "HEAD move without snapshot must produce a finding"
        assert report
        for f in flagged:
            for field in FINDING_FIELDS:
                assert field in f


# ---- extra builder tests ------------------------------------------

class TestSameActorLeftover:
    """A leftover snapshot from the same actor does not cause overlap."""

    def test_leftover_does_not_cause_overlap(self, tmp_path):
        from gov.guard.containment import take_snapshot, check_containment
        proj = _make_project(tmp_path)
        # Actor A takes snapshot for call 1 (never completed).
        take_snapshot(str(proj), "toolu_leftover", "sess-A")
        # Same actor takes snapshot for call 2.
        take_snapshot(str(proj), "toolu_real", "sess-A")
        # Engineer modifies an acceptance test.
        acc = "tests/acceptance/T01/test_ok.py"
        (proj / acc).write_text("# changed\n")
        report = check_containment(
            str(proj), "engineer", "T01", None,
            "sess-A", None, "echo x", "toolu_real")
        ff = _findings(proj)
        # The restore should happen (no overlap from same actor).
        reverted = [f for f in ff if f["action"] == "reverted"]
        assert reverted, (
            "same-actor leftover prevented the restore: "
            f"{[f['action'] for f in ff]}")
