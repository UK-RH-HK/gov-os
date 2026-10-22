"""W2-62 -- a live resumed session reads the whole section (``local_only``, DEC-232).

KPI success 2, second half: "... the hook delivers the section by a route that arrives whole
(for example the section's first part with the exact file, line range and size to read
before anything else), and a live resumed session shows the whole section read".
KPI failure: "A RESUME HERE section of 50,000 characters reaches the resumed session with no
character lost".

**One session, two calls**, in a temporary project built from scratch with no project
settings of its own. ``--settings`` (a file outside the project) carries exactly one
SessionStart hook: ``python3 <this worktree>/template/governance/kernel/hooks/sessionstart.py``.
``GOV_ROLE=orchestrator`` is in the session's environment; ``GOV_TICKET`` is not.

1. ``claude -p "<reply READY>"`` starts the session. There is no checkpoint yet, so nothing
   this call sees carries the token.
2. The test writes the orchestrator checkpoint: a RESUME HERE section of about 50,000
   characters whose last line ends with a random token made for this run, then a later
   section whose last line is a decoy. Then ``claude -p "<follow your session-start
   instructions, quote the section's last line>" --resume <id>``: the hook fires with the
   source ``resume``. ``Read`` is the only tool (``--tools Read --allowedTools Read``).

The case passes when the answer quotes the token exactly. Model and effort (DEC-839):
``claude-opus-5-5`` with ``--effort low``, since the session must read and quote. Not runnable
inside a sandbox without network: the lead runs it (see the README).
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

import w2_62_support as support

pytestmark = pytest.mark.local_only

CLI = Path.home() / ".local/bin/claude"
MODEL = "claude-opus-5-5"
CALL_TIMEOUT_S = 600.0
NOT_INHERITED = ("GOV_ROLE", "GOV_TICKET", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_PROJECT_DIR",
                 "CLAUDE_CODE_SSE_PORT", "PYTHONPATH")
START_PROMPT = "Reply with the single word READY. Use no tools."
QUOTE_PROMPT = ("Follow your session-start instructions now. Then quote, exactly and on one line, the last line of "
                "the RESUME HERE section of your checkpoint. Reply with that line only. Ask me nothing.")


def _call(project, env, settings, prompt, *args):
    command = [str(CLI), "-p", prompt, "--model", MODEL, "--effort", "low", "--settings", str(settings),
               "--output-format", "json", *args]
    try:
        done = subprocess.run(command, cwd=str(project), env=env, capture_output=True, text=True,
                              timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL, check=False)
    except subprocess.TimeoutExpired:
        pytest.fail(f"`claude -p` did not end within {CALL_TIMEOUT_S:.0f} s", pytrace=False)
    try:
        data = json.loads(done.stdout)
    except ValueError:
        data = None
    if not isinstance(data, dict) or not data.get("session_id"):
        pytest.fail(f"`claude -p` gave no result (exit {done.returncode}): {(done.stdout + done.stderr)[-600:]}",
                    pytrace=False)
    return data


def test_a_resumed_session_quotes_the_last_line_of_a_50000_character_section(tmp_path, code_under_test):
    """Success 2 (second half), failure line: the token at the end of the section is quoted exactly."""
    if not CLI.is_file():
        pytest.skip("the Claude Code CLI is not at ~/.local/bin/claude")
    project = support.make_project(tmp_path / "repo", support.roster(support.DEFAULT_PROMPT))
    sandbox = support.make_sandbox(tmp_path / "sandbox")
    hook = {"type": "command", "command": f'python3 "{support.SESSIONSTART}"', "timeout": 30}
    settings = support.write(tmp_path, "settings.json", json.dumps({"hooks": {"SessionStart": [{"hooks": [hook]}]}}))
    env = {key: value for key, value in os.environ.items() if key not in NOT_INHERITED}
    env["GOV_ROLE"] = support.ORCHESTRATOR
    env["PATH"] = sandbox.path

    started = _call(project, env, settings, START_PROMPT, "--tools", "")
    token = f"W262-{os.urandom(8).hex()}"
    section = support.section_text(50_000, token)
    decoy = "\n## History\n\n- HISTORY-MARKER the last line of the file is not the section's: W262-decoy\n"
    cp = support.checkpoint(section, after=decoy)
    support.write_checkpoint(project, support.ORCH, cp)
    answered = _call(project, env, settings, QUOTE_PROMPT, "--resume", started["session_id"],
                     "--tools", "Read", "--allowedTools", "Read")
    reply = str(answered.get("result") or "")
    how = f"subtype={answered.get('subtype')} turns={answered.get('num_turns')} is_error={answered.get('is_error')}"
    if not reply.strip():
        pytest.fail(f"the resumed session gave no answer ({how}); repeat the run (DEC-232)", pytrace=False)
    assert token in reply, (
        f"the resumed session did not quote the token {token} that ends the {len(section):,}-character section "
        f"(lines {cp.first}-{cp.last}) ({how}): {reply[-600:]!r}")
