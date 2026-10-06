"""Builder tests for the W1-29 hooks (regression evidence)."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import types
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[3] / "template/governance/kernel/hooks"

sys.dont_write_bytecode = True
sys.path.insert(0, str(HOOKS))
import precompact  # noqa: E402
import sessionstart  # noqa: E402


def _run(name, root, role="orchestrator", ticket=None, stdin_data="{}"):
    env = {
        "PATH": str(root / "no-bin"),
        "CLAUDE_PROJECT_DIR": str(root),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if role is not None:
        env["GOV_ROLE"] = role
    if ticket is not None:
        env["GOV_TICKET"] = ticket
    return subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=stdin_data,
        capture_output=True,
        text=True,
        cwd=str(root),
        env=env,
        timeout=30,
        check=False,
    )


def _injection(run):
    return json.loads(run.stdout)["hookSpecificOutput"]["additionalContext"]


def _mock_gov(monkeypatch, *, write_fn=None, context_fn=None, brief_fn=None):
    gov = types.ModuleType("gov")
    gov_cp = types.ModuleType("gov.checkpoint")
    gov_rec = types.ModuleType("gov.checkpoint.record")
    gov_ctx = types.ModuleType("gov.context")
    if write_fn is not None:
        gov_rec.write = write_fn
    if brief_fn is not None:
        gov_rec.brief = brief_fn
    if context_fn is not None:
        gov_ctx.context = context_fn
    gov.checkpoint = gov_cp
    gov.context = gov_ctx
    gov_cp.record = gov_rec
    for name, mod in [("gov", gov), ("gov.checkpoint", gov_cp),
                      ("gov.checkpoint.record", gov_rec), ("gov.context", gov_ctx)]:
        monkeypatch.setitem(sys.modules, name, mod)


# --- PreCompact ---


def test_precompact_no_ticket_exits_silently(tmp_path):
    run = _run("precompact.py", tmp_path)
    assert (run.returncode, run.stdout, run.stderr) == (0, "", "")


def test_precompact_gov_unavailable_reports_gracefully(tmp_path):
    run = _run("precompact.py", tmp_path, ticket="T-0001")
    assert run.returncode == 0
    msg = json.loads(run.stdout)
    assert "PreCompact" in msg["systemMessage"]
    assert "checkpoint not written" in msg["systemMessage"]


def test_precompact_calls_write_with_correct_args(monkeypatch, capsys):
    calls = []

    def mock_write(root, ticket, trigger, next_action, inputs):
        calls.append((str(root), ticket, trigger, next_action, inputs))
        return {"path": "p", "id": "i"}

    _mock_gov(monkeypatch, write_fn=mock_write)
    monkeypatch.setenv("GOV_TICKET", "W1-29")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/proj")
    monkeypatch.setattr("sys.stdin", io.StringIO("{}"))
    precompact.main()
    assert capsys.readouterr().out == ""
    assert calls == [("/proj", "W1-29", "compaction", "Resume after compaction", [])]


def test_precompact_write_failure_emits_system_message(monkeypatch, capsys):
    def failing(*a):
        raise RuntimeError("disk full")

    _mock_gov(monkeypatch, write_fn=failing)
    monkeypatch.setenv("GOV_TICKET", "W1-29")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/proj")
    monkeypatch.setattr("sys.stdin", io.StringIO("{}"))
    precompact.main()
    msg = json.loads(capsys.readouterr().out)
    assert "disk full" in msg["systemMessage"]
    assert "compaction proceeds" in msg["systemMessage"]


def test_precompact_always_exits_zero(tmp_path):
    run = _run("precompact.py", tmp_path, ticket="T-0001", stdin_data="not json")
    assert run.returncode == 0


# --- SessionStart ---


def test_sessionstart_fork_returns_empty_context(tmp_path):
    run = _run("sessionstart.py", tmp_path, stdin_data='{"source": "fork"}')
    assert run.returncode == 0
    assert _injection(run) == ""


def test_sessionstart_no_ticket_no_gov_content(tmp_path):
    run = _run("sessionstart.py", tmp_path, stdin_data='{"source": "startup"}')
    assert run.returncode == 0
    assert _injection(run) == ""


def test_sessionstart_injects_context_summary(monkeypatch, capsys):
    _mock_gov(monkeypatch,
              context_fn=lambda root, ticket, brief=False: {"summary": "Gov summary here"})
    monkeypatch.setenv("GOV_TICKET", "W1-29")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/proj")
    monkeypatch.setattr("sys.stdin", io.StringIO('{"source": "startup"}'))
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **kw: types.SimpleNamespace(returncode=1, stdout="", stderr=""))
    sessionstart.main()
    result = json.loads(capsys.readouterr().out)
    assert "Gov summary here" in result["hookSpecificOutput"]["additionalContext"]


def test_sessionstart_compact_includes_checkpoint_brief(monkeypatch, capsys):
    _mock_gov(monkeypatch,
              context_fn=lambda root, ticket, brief=False: {"summary": ""},
              brief_fn=lambda root, ticket: {
                  "ticket": ticket, "next_action": "run tests", "path": "docs/cp/001.md",
              })
    monkeypatch.setenv("GOV_TICKET", "W1-29")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/proj")
    monkeypatch.setattr("sys.stdin", io.StringIO('{"source": "compact"}'))
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **kw: types.SimpleNamespace(returncode=1, stdout="", stderr=""))
    sessionstart.main()
    ctx = _injection(types.SimpleNamespace(stdout=capsys.readouterr().out))
    assert "run tests" in ctx and "W1-29" in ctx and "docs/cp/001.md" in ctx


def test_sessionstart_startup_does_not_call_brief(monkeypatch, capsys):
    brief_called = []
    _mock_gov(monkeypatch,
              context_fn=lambda root, ticket, brief=False: {"summary": "ctx"},
              brief_fn=lambda root, ticket: brief_called.append(1) or {})
    monkeypatch.setenv("GOV_TICKET", "W1-29")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/proj")
    monkeypatch.setattr("sys.stdin", io.StringIO('{"source": "startup"}'))
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **kw: types.SimpleNamespace(returncode=1, stdout="", stderr=""))
    sessionstart.main()
    assert brief_called == []


def test_sessionstart_includes_tk_ready_output(monkeypatch, capsys):
    _mock_gov(monkeypatch,
              context_fn=lambda root, ticket, brief=False: {"summary": ""})
    monkeypatch.setenv("GOV_TICKET", "W1-29")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/proj")
    monkeypatch.setattr("sys.stdin", io.StringIO('{"source": "startup"}'))
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **kw: types.SimpleNamespace(returncode=0, stdout="tk is ready\n", stderr=""))
    sessionstart.main()
    result = json.loads(capsys.readouterr().out)
    assert "tk is ready" in result["hookSpecificOutput"]["additionalContext"]


def test_sessionstart_caps_at_10k_chars(monkeypatch, capsys):
    _mock_gov(monkeypatch,
              context_fn=lambda root, ticket, brief=False: {"summary": "x" * 15_000})
    monkeypatch.setenv("GOV_TICKET", "W1-29")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/proj")
    monkeypatch.setattr("sys.stdin", io.StringIO('{"source": "startup"}'))
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **kw: types.SimpleNamespace(returncode=1, stdout="", stderr=""))
    sessionstart.main()
    result = json.loads(capsys.readouterr().out)
    assert len(result["hookSpecificOutput"]["additionalContext"]) == 10_000


def test_sessionstart_always_exits_zero(tmp_path):
    run = _run("sessionstart.py", tmp_path, stdin_data="not json")
    assert run.returncode == 0
