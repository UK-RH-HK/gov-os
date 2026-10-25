"""W2-65 KPI success 4: the SubagentStop hook gives its block reason as Claude Code reads it (DEC-889 item 8, P-H-7).

Claude Code (code.claude.com/docs/en/hooks) blocks a helper's stop on exit 2, giving it the hook's standard error, or
on exit 0 with ``{"decision": "block", "reason": ...}`` on standard output, giving it that reason. Standard output with
exit 2 is not delivered. The case holds for either documented form, and fails for a reason that reaches only standard
output under ``hookSpecificOutput`` with exit 2 and an empty standard error.

The hook program is the template's copy (what adopted projects receive), run as a process from this worktree;
``src/gov/hooks/subagentstop.py`` is held byte-identical to it by W1-29's ``TestHookCopiesIdentical``.
"""

from __future__ import annotations

import json
import os
import subprocess

import w2_65_support as support


def test_a_helper_missing_fields_is_told_which_ones(tmp_path):
    """A final message with six of the twelve fields (as labelled lines) is blocked, and the reason Claude Code
    delivers names each of the six missing fields."""
    present = support.TWELVE_FIELDS[:6]
    missing = support.TWELVE_FIELDS[6:]
    message = "\n".join(f"{field}: w265 value" for field in present)
    hook = support.WORKTREE / support.SUBAGENTSTOP_REL
    payload = {"session_id": "w265-session", "transcript_path": str(tmp_path / "transcript.jsonl"),
               "cwd": str(tmp_path), "hook_event_name": "SubagentStop", "stop_hook_active": False,
               "agent_id": "w265-agent", "agent_type": "engineer", "last_assistant_message": message}
    env = {"PATH": support.SYSTEM_PATH, "HOME": str(tmp_path), "LANG": "C.UTF-8",
           "TMPDIR": os.environ.get("TMPDIR", "/tmp"), "PYTHONPATH": str(support.SRC),
           "PYTHONDONTWRITEBYTECODE": "1", "CLAUDE_PROJECT_DIR": str(tmp_path)}
    done = subprocess.run([support.REAL_PYTHON, str(hook)], input=json.dumps(payload), cwd=str(tmp_path), env=env,
                          capture_output=True, text=True, timeout=30)
    described = f"exit: {done.returncode}\nstdout:\n{done.stdout}\nstderr:\n{done.stderr}"
    reason = support.delivered_block_reason(done.returncode, done.stdout, done.stderr)
    assert reason is not None, (
        f"the helper's stop is not blocked as Claude Code reads it (exit 2, or exit 0 with a block decision)\n"
        f"{described}")
    assert reason.strip(), (
        "the stop is blocked but Claude Code delivers no reason: with exit 2 the reason must be on standard error "
        "(standard output is not read), or exit 0 with {\"decision\": \"block\", \"reason\": ...} on standard "
        f"output\n{described}")
    unnamed = [field for field in missing if field not in reason]
    assert not unnamed, (
        f"the delivered reason does not name the missing fields {unnamed}: {reason!r}\n{described}")
