"""W1-49 -- what only a real session can show (``local_only``, DEC-232).

KPI success 4 [CAP-37.g]: "After a forced compaction (/compact), the session's
next action shows it knows the active tickets, the open owner decisions and the
loop counts, without the owner restating them (DEC-248)".
KPI failure 3: "After a compaction the session needs the owner to restate the
active tickets, the open owner decisions or the loop counts".
KPI success 3: the proof that the pinned CLI takes the auto-compact window from
the ``env`` key of a project's settings.

**One session, four short calls**, once per test run, in a temporary project
that holds this repository's two hooks, their registration and the ``env`` key
(copied by value from the ``hooks`` and ``env`` keys; nothing else of the
settings file), a stand-in prompt and, from step 2 on, a stand-in checkpoint:

1. ``claude -p "<say READY>"`` starts the session. There is no checkpoint yet,
   so nothing this call sees carries the invented state.
2. The test writes the checkpoint: invented tickets, invented open owner
   decisions, invented loop counts, and a modification time three days ago.
   Then ``claude -p "/compact" --resume <id>`` forces the compaction:
   PreCompact, the compaction, SessionStart with the source ``compact``. Under
   DEC-264 the old checkpoint blocks nothing, and the PreCompact hook leaves
   its generated state block at the end of the file (revised after the
   implementation, reason "owner decision, DEC-264": DEC-258 blocked this
   compaction).
3. ``claude -p "<where do you stand, what is next>" --resume <id>``. The prompt
   names no ticket, no decision and no count. ``Read`` is the only tool the
   call has (``--tools Read``), so the session can open the two files it is
   told to read and cannot start the next action instead of stating it.
4. ``claude -p "/autocompact" --resume <id>`` prints the window and its origin.
   It calls no model.

**Cost and needs.** The real CLI at ``~/.local/bin/claude`` (2.1.288) with the
caller's own credentials and the network; the cheapest model (``haiku``), a turn
limit on every call, about 0.10 USD a run when measured on 2026-10-04. Not behind
an opt-in variable (DEC-232). Leave it out with ``-m "not local_only"``. A run in
which the model does not answer the question fails with that reason and is
repeated (DEC-232); it is not a finding against the hooks.

The session runs with ``GOV_ROLE=orchestrator`` (DEC-259) and without the guard
hooks: the temporary project registers the two W1-49 hooks and the test's own
recorder, nothing else. A stand-in ``tk`` with invented tickets in progress is
first on the session's ``PATH``.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

import w1_49_support as support

pytestmark = pytest.mark.local_only

CLI = Path.home() / ".local/bin/claude"
CALL_TIMEOUT_S = 300.0
NOT_INHERITED = ("GOV_ROLE", "GOV_TICKET", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_PROJECT_DIR",
                 "CLAUDE_CODE_SSE_PORT", support.WINDOW_KEY)

TICKETS = ("ZQ-71", "ZQ-88")
DECISIONS = ("OD-913", "OD-927")
LOOP_COUNTS = ("17", "23")
CHECKPOINT = (
    "# Orchestrator checkpoint (stand-in, every name and number invented)\n\n"
    "## RESUME HERE\n\n"
    "- Active tickets: ZQ-71 (engineer implementing), ZQ-88 (waiting for its audit)\n"
    "- Open owner decisions: OD-913 (rename the ledger module?), OD-927 (keep the slow parser?)\n"
    "- Loop counts: ZQ-71 review-repair loop 17, ZQ-88 test-fix loop 23\n"
    "- Next action: start the audit of ZQ-88, then read the review of ZQ-71.\n\n"
    "## History\n\n- ZQ-09 closed.\n"
)
START_PROMPT = "Reply with the single word READY. Use no tools."
NEXT_PROMPT = ("Continue. Say where you stand (active tickets, open owner decisions, loop counts) and state your "
               "next action in one short text answer. Do not start that action yet. Ask me nothing.")
RECORDER = (
    "import json, sys\n"
    "data = json.load(sys.stdin)\n"
    "with open(@LOG@, 'a', encoding='utf-8') as handle:\n"
    "    handle.write(json.dumps({'event': data.get('hook_event_name'), 'source': data.get('source'),\n"
    "                             'trigger': data.get('trigger')}) + '\\n')\n"
)


@dataclass(frozen=True)
class Live:
    compact: dict        # the JSON result of the /compact call
    events: list         # what the test's recorder saw, in order
    reply: str           # the answer to NEXT_PROMPT
    how: str             # how that call ended (subtype, turns), for the failure message
    window: str          # the answer to /autocompact
    checkpoint: str      # the checkpoint file after the compaction
    head: str            # the temporary project's HEAD commit


def _call(project, env, *args):
    try:
        done = subprocess.run([str(CLI), "-p", *args, "--model", "haiku", "--output-format", "json"],
                              cwd=str(project), env=env, capture_output=True, text=True, timeout=CALL_TIMEOUT_S,
                              stdin=subprocess.DEVNULL, check=False)
    except subprocess.TimeoutExpired:
        pytest.fail(f"`claude -p {args[0]!r}` did not end within {CALL_TIMEOUT_S:.0f} s", pytrace=False)
    try:
        data = json.loads(done.stdout)
    except ValueError:
        data = None
    if not isinstance(data, dict) or not data.get("session_id"):
        pytest.fail(f"`claude -p {args[0]!r}` gave no result (exit {done.returncode}): "
                    f"{(done.stdout + done.stderr)[-600:]}", pytrace=False)
    return data


@pytest.fixture(scope="module")
def live(hooks, settings_env, precompact_commands, sessionstart_commands, base, tmp_path_factory):
    """The four calls. The two ``*_commands`` fixtures are the red reason until the hooks are registered."""
    if not CLI.is_file():
        pytest.fail("the Claude Code CLI is not at ~/.local/bin/claude (DEC-205)", pytrace=False)
    tmp = tmp_path_factory.mktemp("w1-49-live")
    project = support.make_project(tmp / "repo")
    log = tmp / "events.jsonl"
    recorder = support.write(tmp, "recorder.py", RECORDER.replace("@LOG@", repr(str(log))))
    record = {"hooks": [{"type": "command", "command": f'python3 "{recorder}"'}]}
    settings = {
        "hooks": {
            "PreCompact": support.hook_entries(hooks, "PreCompact", "precompact.py") + [record],
            "SessionStart": support.hook_entries(hooks, "SessionStart", "sessionstart.py") + [record],
            "PostCompact": [record],
        },
        "env": {key: value for key, value in settings_env.items() if key == support.WINDOW_KEY},
    }
    support.write(project, support.SETTINGS_REL, json.dumps(settings, indent=2) + "\n")
    env = {key: value for key, value in os.environ.items() if key not in NOT_INHERITED}
    env["GOV_ROLE"] = support.ORCHESTRATOR
    env["PATH"] = support.make_sandbox(tmp / "sandbox").path

    started = _call(project, env, START_PROMPT, "--max-turns", "3")
    session = started["session_id"]
    checkpoint = support.write_checkpoint(project, support.ORCHESTRATOR_CHECKPOINT_REL, CHECKPOINT,
                                          age_s=support.STALE_AGE_S)
    compact = _call(project, env, "/compact", "--resume", session, "--max-turns", "3")
    after_compaction = checkpoint.read_text(encoding="utf-8")
    answered = _call(project, env, NEXT_PROMPT, "--resume", session, "--max-turns", "8", "--tools", "Read",
                     "--allowedTools", "Read")
    window = _call(project, env, "/autocompact", "--resume", session, "--max-turns", "1")
    events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.is_file() else []
    how = f"subtype={answered.get('subtype')} turns={answered.get('num_turns')} is_error={answered.get('is_error')}"
    return Live(compact, events, str(answered.get("result") or ""), how, str(window.get("result") or ""),
                after_compaction, support.git(project, "rev-parse", "HEAD").strip())


def test_the_forced_compaction_over_an_old_checkpoint_is_not_blocked(live):
    """Success 4 and 5, failure 1: the compaction is real (PostCompact was reached); SessionStart followed with ``compact``."""
    names = [(event["event"], event.get("trigger") or event.get("source")) for event in live.events]
    assert ("PostCompact", "manual") in names, (
        f"the forced compaction did not complete: {str(live.compact.get('result'))[:300]!r}; hook events {names}"
    )
    assert names.index(("PreCompact", "manual")) < names.index(("SessionStart", "compact")), (
        f"PreCompact and SessionStart(compact) did not fire in this order: {names}"
    )


def test_the_forced_compaction_left_the_state_block_in_the_checkpoint(live):
    """Success 5 [CAP-37.g]: the written part first and unchanged, then the block with the git head and tk's tickets."""
    assert live.checkpoint.startswith(CHECKPOINT), "the compaction changed the written part of the checkpoint"
    written, block = support.split_checkpoint(live.checkpoint)
    assert block is not None and written == CHECKPOINT[:len(written)], (
        f"the real session's PreCompact hook appended no state block: the file ends {live.checkpoint[-200:]!r}"
    )
    assert live.head in block and support.TK_LINES[0] in block, (
        f"the state block does not hold the git head and the tickets in progress: {block[:500]!r}"
    )


def _reply(live):
    if not live.reply.strip():
        pytest.fail(f"the session gave no answer to the question after the compaction ({live.how}); repeat the run "
                    "(DEC-232)", pytrace=False)
    return live.reply


@pytest.mark.parametrize("ticket", TICKETS)
def test_after_the_compaction_the_session_names_the_active_tickets(live, ticket):
    """Success 4, failure 3 [CAP-37.g]."""
    assert ticket in _reply(live), f"the session's next action does not name the active ticket {ticket}: {live.reply[:600]!r}"


@pytest.mark.parametrize("decision", DECISIONS)
def test_after_the_compaction_the_session_names_the_open_owner_decisions(live, decision):
    """Success 4, failure 3 [CAP-37.g]."""
    assert decision in _reply(live), f"the session does not name the open owner decision {decision}: {live.reply[:600]!r}"


@pytest.mark.parametrize("count", LOOP_COUNTS)
def test_after_the_compaction_the_session_names_the_loop_counts(live, count):
    """Success 4, failure 3 [CAP-37.g]."""
    assert count in _reply(live), f"the session does not name the loop count {count}: {live.reply[:600]!r}"


def test_the_session_takes_the_auto_compact_window_from_the_settings_env_key(live):
    """Success 3: ``/autocompact`` reports "300k tokens (from CLAUDE_CODE_AUTO_COMPACT_WINDOW)"."""
    assert support.WINDOW_KEY in live.window and "300k" in live.window, (
        f"the session does not report a 300k window from {support.WINDOW_KEY}: {live.window[:300]!r}"
    )
