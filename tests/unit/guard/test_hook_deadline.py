"""Builder tests for the PreToolUse hook's own deadline (W1-02, DEC-580).

The hook is run as a process, in a temporary project, with a throwaway
package in front of ``src`` on its import path whose decision is the
stand-in each case needs.  Nothing of this repository is opened but the
hook program and the package under ``src``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "template" / "governance" / "kernel" / "hooks" / "pretooluse.py"

DEADLINE_S = 20.0

_DECIDE_HEAD = (
    "import os, re, signal, subprocess, sys\n"
    "FREEZE_FLAG = '.gov-runtime/freeze'\n"
    "def freeze_state(project_root):\n"
    "    return 'absent'\n"
    "def decide(project_root, **kwargs):\n"
)

# Busy in one step for well over the deadline: the regular expression
# backtracks inside the interpreter's own code.  Before that, half an
# answer on stdout and a started program, both of which must be gone.
BUSY = (
    "    child = subprocess.Popen(['sleep', '60'])\n"
    "    with open(os.path.join(project_root, 'pids'), 'w') as f:\n"
    "        f.write(f'{os.getpid()} {child.pid}')\n"
    "    sys.stdout.write('{\"half\": \"an answer\"')\n"
    "    sys.stdout.flush()\n"
    "    re.match(r'(a+)+$', 'a' * 64 + 'b')\n"
    "    return 'allow', ''\n"
)
KILLED = (
    "    sys.stdout.write('half an answer')\n"
    "    sys.stdout.flush()\n"
    "    os.kill(os.getpid(), signal.SIGKILL)\n"
)
LONG_REASON = "a very long reason. " * 10000
LONG_DENY = f"    return 'deny', {LONG_REASON!r}\n"
ALLOW = "    return 'allow', ''\n"


def _run_hook(tmp_path, decide_body, timeout=60):
    """Run the hook on a Read call; return (returncode, stdout, stderr, seconds)."""
    project = tmp_path / "project"
    project.mkdir()
    package = tmp_path / "stand-in" / "gov" / "guard"
    package.mkdir(parents=True)
    (package.parent / "__init__.py").write_text("", encoding="utf-8")
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "decide.py").write_text(_DECIDE_HEAD + decide_body,
                                       encoding="utf-8")
    env = {
        "PATH": os.environ["PATH"],
        "PYTHONPATH": os.pathsep.join(
            [str(tmp_path / "stand-in"), str(REPO / "src")]),
        "CLAUDE_PROJECT_DIR": str(project),
        "HOME": str(tmp_path / "home"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    data = {
        "session_id": "s",
        "cwd": str(project),
        "hook_event_name": "PreToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": str(project / "a-file-of-the-call")},
    }
    started = time.monotonic()
    p = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(data).encode("utf-8"),
        capture_output=True,
        env=env,
        cwd=str(project),
        timeout=timeout,
    )
    return p.returncode, p.stdout, p.stderr, time.monotonic() - started


def _findings(tmp_path):
    path = tmp_path / "project" / ".gov-runtime" / "findings.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines()]


def _running(pid):
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as f:
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return False


def test_a_decision_busy_in_one_step_is_denied_at_the_deadline(tmp_path):
    rc, stdout, stderr, seconds = _run_hook(tmp_path, BUSY)
    assert rc == 0
    # One JSON object and nothing beside it: nothing of the decision's
    # own half-written output.
    answer = json.loads(stdout)["hookSpecificOutput"]
    assert answer["hookEventName"] == "PreToolUse"
    assert answer["permissionDecision"] == "deny"
    reason = answer["permissionDecisionReason"]
    assert "DEC-580" in reason and "in time" in reason
    assert "a-file-of-the-call" not in reason
    assert str(tmp_path) not in reason
    assert stderr == b""
    assert DEADLINE_S - 1 <= seconds <= DEADLINE_S + 6
    # No finding in this round.
    assert _findings(tmp_path) == []
    # Neither the decision's process nor the program it started is left.
    pids = [int(x) for x in
            (tmp_path / "project" / "pids").read_text().split()]
    assert len(pids) == 2
    until = time.monotonic() + 5
    while any(_running(pid) for pid in pids) and time.monotonic() < until:
        time.sleep(0.1)
    assert [pid for pid in pids if _running(pid)] == []


def test_a_decision_process_ended_by_a_signal_is_an_internal_failure(tmp_path):
    rc, stdout, stderr, seconds = _run_hook(tmp_path, KILLED)
    assert rc == 2
    assert stdout == b""
    assert seconds < DEADLINE_S - 1
    findings = _findings(tmp_path)
    assert len(findings) == 1
    assert findings[0]["source"] == "guard"


def test_a_very_long_refusal_arrives_whole(tmp_path):
    rc, stdout, stderr, seconds = _run_hook(tmp_path, LONG_DENY)
    assert rc == 0
    expected = json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": LONG_REASON,
        }
    })
    assert stdout == expected.encode("utf-8")
    assert stderr == b""
    assert _findings(tmp_path) == []


def test_an_allow_is_exit_code_0_with_empty_stdout(tmp_path):
    rc, stdout, stderr, seconds = _run_hook(tmp_path, ALLOW)
    assert rc == 0
    assert stdout == b""
    assert stderr == b""
    assert seconds < DEADLINE_S - 1
    assert _findings(tmp_path) == []
