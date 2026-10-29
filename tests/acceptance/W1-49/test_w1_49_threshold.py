"""W1-49 -- the auto-compact threshold.

KPI success 3: "The auto-compact threshold is set to about 300k tokens (30 % of
the window) if Claude Code allows it to be configured; an acceptance test proves
whether it can; if it can't, a residual is recorded: the CONTEXT_CHECKPOINT stop
stays (DEC-248, DEC-208)".

**It can.** Claude Code 2.1.288 has an auto-compact window, in tokens, from
100,000 to 1,000,000. The form used is the environment variable
``CLAUDE_CODE_AUTO_COMPACT_WINDOW``. It takes a plain integer only: ``300k``
reads as 300 and clamps to the minimum. No residual goes to ``bootstrap.md``
for this line.

**No threshold is set (DEC-838, DEC-865).** The 300k entry of DEC-636 and
DEC-665 (in the owner's user-level settings from 2026-10-11) is retired: since
2026-10-19 every session uses its model's full window, and no launch and no
settings file passes a compaction threshold. The two cases read what a case may
read:

- the project's settings set no window of their own (the ``env`` key, through
  the suite's loader, which gives the ``hooks`` and ``env`` keys and nothing
  else);
- the environment a Claude Code session on this machine gives its commands
  carries no ``CLAUDE_CODE_AUTO_COMPACT_WINDOW``. Claude Code exports the env
  block of its settings to every command a session runs, and a launch's own
  environment reaches them too, so a threshold from either would show here. The
  case is ``local_only`` (the environment is this machine's) and is skipped,
  never passed, when the suite is not run from a session.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import w1_49_support as support

CLI = Path.home() / ".local/bin/claude"
SESSION_MARKER = "CLAUDECODE"   # Claude Code sets it to 1 in the environment of every command a session runs


def test_the_project_settings_set_no_auto_compact_window_of_their_own(settings_env):
    """Success 3, rewritten after implementation (DEC-665). rulesync writes no env block (DEC-636): the generated
    project settings do not set the window, so nothing in the project stands in front of the user-level entry.

    Before: ``test_the_settings_set_the_auto_compact_window_as_an_env_key``.
    """
    assert support.WINDOW_KEY not in settings_env, (
        f"the env key of {support.SETTINGS_REL} sets {support.WINDOW_KEY}: the window is set in the owner's "
        "user-level settings (DEC-636), and a project entry would be read in its place"
    )


@pytest.mark.local_only
def test_a_session_on_this_machine_is_given_no_compaction_threshold(settings_env):
    """Success 3, rewritten after implementation (DEC-838, DEC-865). No launch and no settings file passes a
    compaction threshold: the variable is in neither the project's ``env`` key nor the environment a session gives
    its commands, so the session uses its model's full window.

    Before: ``test_a_session_on_this_machine_gets_an_auto_compact_window_of_about_300k_tokens`` (DEC-636, DEC-665:
    the variable a plain integer of about 300k in a session's environment).
    """
    if os.environ.get(SESSION_MARKER) != "1":
        pytest.skip(f"not run from a Claude Code session ({SESSION_MARKER} is not 1): the env block of a settings "
                    "file reaches a session's commands only; the window is not measured")
    assert support.WINDOW_KEY not in settings_env, (
        f"the env key of {support.SETTINGS_REL} sets {support.WINDOW_KEY}: a settings file passes a compaction "
        "threshold, and no settings file may (DEC-838)"
    )
    given = os.environ.get(support.WINDOW_KEY)   # one value, so that a failure prints nothing else of the environment
    assert given is None, (
        f"this session's commands are given {support.WINDOW_KEY}={given!r}: a launch or a settings file passes a "
        "compaction threshold, and the session does not use its model's full window (DEC-838)"
    )


@pytest.mark.local_only
def test_the_pinned_cli_has_an_auto_compact_window():
    """ "An acceptance test proves whether it can": the installed CLI documents the window in its own help."""
    assert CLI.is_file(), "the Claude Code CLI is not at ~/.local/bin/claude (DEC-205)"
    done = subprocess.run([str(CLI), "--help"], capture_output=True, text=True, timeout=60, check=False)
    assert "--autocompact" in done.stdout, "`claude --help` names no --autocompact flag: no configurable window"
