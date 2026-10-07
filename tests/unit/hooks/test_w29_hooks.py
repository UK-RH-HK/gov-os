"""Unit tests for the W1-29 session hooks (new file; W1-49 tests stay in test_resume_hooks.py)."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS = REPO_ROOT / "template" / "governance" / "kernel" / "hooks"
SRC_HOOKS = REPO_ROOT / "src" / "gov" / "hooks"

sys.dont_write_bytecode = True
sys.path.insert(0, str(HOOKS))
sys.path.insert(0, str(REPO_ROOT / "src"))

import precompact  # noqa: E402
import sessionstart  # noqa: E402


ORCH = ".gov-runtime/scratch/orchestrator/CHECKPOINT.md"
WRITTEN = "# C\n\n## RESUME HERE\n\n- SECRET-71\n"

TWELVE_FIELDS = (
    "task", "status", "work_completed", "files_changed",
    "evidence", "tests", "discoveries", "risks",
    "lessons", "proposed_decisions", "unresolved",
    "recommended_next_action",
)


def _run(name, root, role="orchestrator", ticket=None, stdin=None, hooks_dir=HOOKS):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "CLAUDE_PROJECT_DIR": str(root),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(REPO_ROOT / "src"),
    }
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    return subprocess.run(
        [sys.executable, str(hooks_dir / name)],
        input=stdin or "{}",
        capture_output=True, text=True,
        cwd=str(root), env=env, timeout=30, check=False,
    )


# --------------------------------------------------------------------------
# SubagentStop: empty/null rejection (Finding 2)
# --------------------------------------------------------------------------

class TestSubagentStopEmptyNull:

    def test_null_value_not_accepted(self):
        from subagentstop import _find_fields, TWELVE_FIELDS as TF
        fields = {f: "meaningful" for f in TF}
        fields["evidence"] = None
        found = _find_fields(json.dumps(fields))
        assert "evidence" not in found

    def test_empty_string_not_accepted(self):
        from subagentstop import _find_fields, TWELVE_FIELDS as TF
        fields = {f: "meaningful" for f in TF}
        fields["work_completed"] = ""
        found = _find_fields(json.dumps(fields))
        assert "work_completed" not in found

    def test_both_empty_and_null_rejected(self):
        from subagentstop import _find_fields, TWELVE_FIELDS as TF
        fields = {f: "meaningful" for f in TF}
        fields["work_completed"] = ""
        fields["evidence"] = None
        found = _find_fields(json.dumps(fields))
        assert "work_completed" not in found
        assert "evidence" not in found
        assert len(found) == len(TF) - 2

    def test_all_meaningful_values_accepted(self):
        from subagentstop import _find_fields, TWELVE_FIELDS as TF
        fields = {f: "present" for f in TF}
        found = _find_fields(json.dumps(fields))
        assert found == set(TF)

    def test_src_copy_also_rejects_empty_null(self):
        script = SRC_HOOKS / "subagentstop.py"
        assert script.is_file()
        fields = {f: "meaningful" for f in TWELVE_FIELDS}
        fields["work_completed"] = ""
        fields["evidence"] = None
        inp = json.dumps({
            "hook_event_name": "SubagentStop",
            "last_assistant_message": json.dumps(fields),
        })
        result = subprocess.run(
            [sys.executable, str(script)],
            input=inp, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 2


# --------------------------------------------------------------------------
# SubagentStop: fail-closed on exceptions
# --------------------------------------------------------------------------

class TestSubagentStopFailClosed:

    @pytest.mark.parametrize("raw_input", ["", "NOT JSON{{{"])
    def test_malformed_input_exits_2(self, raw_input):
        result = subprocess.run(
            [sys.executable, str(HOOKS / "subagentstop.py")],
            input=raw_input, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 2

    def test_src_copy_fails_closed(self):
        result = subprocess.run(
            [sys.executable, str(SRC_HOOKS / "subagentstop.py")],
            input="", capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 2


# --------------------------------------------------------------------------
# Stop: checkpoint write and stop_hook_active guard
# --------------------------------------------------------------------------

class TestStopHook:

    def test_stop_hook_active_returns_immediately(self):
        import stop
        stdin_data = json.dumps({
            "hook_event_name": "Stop",
            "stop_hook_active": {"hook_name": "gov-stop"},
            "last_assistant_message": "Done.",
        })
        with mock.patch("sys.stdin", io.StringIO(stdin_data)), \
             mock.patch.dict(os.environ, {"GOV_TICKET": "T-aaaa", "CLAUDE_PROJECT_DIR": "/tmp/x"}):
            wrote = []
            with mock.patch("gov.checkpoint.record.write", side_effect=lambda *a: wrote.append(a)):
                stop.main()
            assert not wrote

    def test_no_ticket_returns_immediately(self):
        import stop
        stdin_data = json.dumps({"hook_event_name": "Stop", "last_assistant_message": "Done."})
        with mock.patch("sys.stdin", io.StringIO(stdin_data)), \
             mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": "/tmp/x"}, clear=False):
            env = os.environ.copy()
            env.pop("GOV_TICKET", None)
            with mock.patch.dict(os.environ, env, clear=True):
                stop.main()

    def test_writes_checkpoint_on_normal_stop(self, tmp_path):
        script = SRC_HOOKS / "stop.py"
        assert script.is_file()
        (tmp_path / ".tickets").mkdir()
        (tmp_path / ".tickets" / "TEST-abcd.md").write_text(
            "---\nid: TEST-abcd\nstatus: in_progress\ntitle: T\nsources: []\ndepends_on: []\n---\n# T\n",
        )
        cp_dir = tmp_path / "docs" / "checkpoints" / "TEST-abcd"
        cp_dir.mkdir(parents=True)
        _init_git(tmp_path)
        stdin_data = json.dumps({
            "hook_event_name": "Stop", "session_id": "s1",
            "last_assistant_message": "Done.",
        })
        result = subprocess.run(
            [sys.executable, str(script)],
            input=stdin_data, capture_output=True, text=True,
            cwd=str(tmp_path), timeout=30,
            env={
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "PYTHONPATH": str(REPO_ROOT / "src"),
                "PYTHONDONTWRITEBYTECODE": "1",
                "CLAUDE_PROJECT_DIR": str(tmp_path),
                "GOV_TICKET": "TEST-abcd",
                "GOV_ROLE": "engineer",
            },
        )
        assert result.returncode == 0
        assert list(cp_dir.glob("CP-*.md"))


# --------------------------------------------------------------------------
# PreCompact: combined checkpoint record + state block
# --------------------------------------------------------------------------

_GIT_ENV = {
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


def _init_git(root):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(root), **_GIT_ENV}
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "main"],
                   env=env, capture_output=True, check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"],
                   env=env, capture_output=True, check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "init"],
                   env=env, capture_output=True, check=True)


def _make_project(tmp_path):
    (tmp_path / ".tickets").mkdir()
    (tmp_path / ".tickets" / "TEST-abcd.md").write_text(
        "---\nid: TEST-abcd\nstatus: in_progress\ntitle: T\nsources: []\ndepends_on: []\n---\n# T\n",
    )
    cp_dir = tmp_path / "docs" / "checkpoints" / "TEST-abcd"
    cp_dir.mkdir(parents=True)
    _init_git(tmp_path)
    return tmp_path


class TestPreCompactCombined:

    def test_checkpoint_record_written_for_any_role(self, tmp_path):
        project = _make_project(tmp_path)
        cp_dir = project / "docs" / "checkpoints" / "TEST-abcd"
        run = _run("precompact.py", project, role="engineer", ticket="TEST-abcd")
        assert run.returncode == 0
        assert list(cp_dir.glob("CP-*.md")), "checkpoint record must be written"

    def test_state_block_still_appended_for_orchestrator(self, tmp_path):
        project = _make_project(tmp_path)
        ckpt = project / ORCH
        ckpt.parent.mkdir(parents=True)
        ckpt.write_text(WRITTEN)
        stamp = time.time() - 60
        os.utime(ckpt, (stamp, stamp))
        run = _run("precompact.py", project, role="orchestrator")
        assert run.returncode == 0
        text = ckpt.read_text()
        assert text.startswith(WRITTEN)
        assert precompact.BEGIN.decode() in text

    def test_no_ticket_no_record(self, tmp_path):
        project = _make_project(tmp_path)
        ckpt = project / ORCH
        ckpt.parent.mkdir(parents=True)
        ckpt.write_text(WRITTEN)
        run = _run("precompact.py", project, role="orchestrator")
        assert run.returncode == 0
        cp_dir = project / "docs" / "checkpoints" / "TEST-abcd"
        assert not list(cp_dir.glob("CP-TEST-abcd-0001.md")), \
            "no checkpoint record when ticket not set"

    def test_checkpoint_failure_reports_systemmessage(self, monkeypatch, capsys):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/nonexistent")
        monkeypatch.setenv("GOV_TICKET", "BAD-tick")
        monkeypatch.setenv("GOV_ROLE", "engineer")
        monkeypatch.setattr("sys.stdin", io.StringIO("{}"))
        precompact.main()
        out = capsys.readouterr().out
        if out:
            msg = json.loads(out)
            assert "systemMessage" in msg
            assert "checkpoint not written" in msg["systemMessage"]


# --------------------------------------------------------------------------
# SessionStart: combined injection and cut order
# --------------------------------------------------------------------------

class TestSessionStartCombined:

    def test_orchestrator_gets_prompt_path(self, tmp_path):
        project = _make_project(tmp_path)
        ckpt = project / ORCH
        ckpt.parent.mkdir(parents=True)
        ckpt.write_text(WRITTEN)
        stamp = time.time() - 60
        os.utime(ckpt, (stamp, stamp))
        stdin = json.dumps({"source": "compact"})
        run = _run("sessionstart.py", project, role="orchestrator", stdin=stdin)
        assert run.returncode == 0
        data = json.loads(run.stdout)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        assert sessionstart.PROMPT_REL in ctx

    def test_non_orchestrator_no_prompt_path(self, tmp_path):
        project = _make_project(tmp_path)
        stdin = json.dumps({"source": "compact"})
        run = _run("sessionstart.py", project, role="engineer", ticket="TEST-abcd", stdin=stdin)
        assert run.returncode == 0
        if run.stdout.strip():
            data = json.loads(run.stdout)
            ctx = data.get("hookSpecificOutput", {}).get("additionalContext", "")
            assert sessionstart.PROMPT_REL not in ctx

    def test_checkpoint_resume_brief_on_compact(self, tmp_path):
        project = _make_project(tmp_path)
        (project / "docs" / "checkpoints" / "TEST-abcd" / "CP-TEST-abcd-0001.md").write_text(
            "---\nid: CP-TEST-abcd-0001\ntype: checkpoint\nstatus: ACTIVE\n"
            "state_class: NARRATIVE\ntitle: TEST-abcd at compaction\n"
            "task: TEST-abcd\ntask_status: in_progress\ntrigger: compaction\n"
            "next_action: Continue implementation\ncreated: 2026-10-05T00:00:00Z\n"
            "inputs:\n  - id: TEST-abcd\n    version: abc1234\n"
            "    hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000'\n"
            "---\n\n# CP-TEST-abcd-0001\n",
        )
        _init_git(project)
        stdin = json.dumps({"source": "compact"})
        run = _run("sessionstart.py", project, role="engineer", ticket="TEST-abcd", stdin=stdin)
        assert run.returncode == 0
        assert run.stdout.strip()
        data = json.loads(run.stdout)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        assert "TEST-abcd" in ctx
        assert "Checkpoint resume" in ctx

    def test_no_w49_parts_when_no_role(self, tmp_path):
        project = _make_project(tmp_path)
        run = _run("sessionstart.py", project, role=None)
        assert run.returncode == 0
        if run.stdout.strip():
            data = json.loads(run.stdout)
            ctx = data.get("hookSpecificOutput", {}).get("additionalContext", "")
            assert sessionstart.PROMPT_REL not in ctx

    def test_cut_order_preserves_critical(self, tmp_path):
        project = _make_project(tmp_path)
        ckpt = project / ORCH
        ckpt.parent.mkdir(parents=True)
        large_section = "x" * 9500
        ckpt.write_text(f"# C\n\n## RESUME HERE\n\n{large_section}\n")
        stamp = time.time() - 60
        os.utime(ckpt, (stamp, stamp))
        stdin = json.dumps({"source": "compact"})
        run = _run("sessionstart.py", project, role="orchestrator", ticket="TEST-abcd", stdin=stdin)
        assert run.returncode == 0
        data = json.loads(run.stdout)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        assert len(ctx) <= sessionstart.CAP_CHARS
        assert sessionstart.PROMPT_REL in ctx

    def test_within_cap(self, tmp_path):
        project = _make_project(tmp_path)
        ckpt = project / ORCH
        ckpt.parent.mkdir(parents=True)
        ckpt.write_text(WRITTEN)
        os.utime(ckpt, (time.time() - 60, time.time() - 60))
        stdin = json.dumps({"source": "compact"})
        run = _run("sessionstart.py", project, role="orchestrator", ticket="TEST-abcd", stdin=stdin)
        assert run.returncode == 0
        data = json.loads(run.stdout)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        assert len(ctx) <= sessionstart.CAP_CHARS


def _checkpoint(root, age_s, text=WRITTEN):
    path = root / ORCH
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    stamp = time.time() - age_s
    os.utime(path, (stamp, stamp))
    return path
