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

**Where it is set (DEC-636, DEC-665).** Until the owner's apply block of
2026-10-11 the variable stood in the ``env`` key of ``.claude/settings.json``,
and two cases here read it there. That file is now rulesync's output, and
rulesync writes no env block; the variable is set in the env block of the
owner's user-level settings, so every repository on this machine gets it. No
case reads the user-level settings. The two cases were rewritten to the decided
state through what a case may read:

- the project's settings set no window of their own (the ``env`` key, through
  the suite's loader, which gives the ``hooks`` and ``env`` keys and nothing
  else);
- the environment a Claude Code session on this machine gives its commands
  carries the variable, a plain integer of about 300k. Claude Code exports the
  env block of its settings to every command a session runs, so this is what
  the user-level entry does, seen from outside it. The case is ``local_only``
  (the entry is this machine's) and is skipped, never passed, when the suite is
  not run from a session. It shows the value a session gets and that the
  project does not supply it; it does not show which file supplies it.
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
def test_a_session_on_this_machine_gets_an_auto_compact_window_of_about_300k_tokens(settings_env):
    """Success 3, rewritten after implementation (DEC-665). "About 300k tokens (30 % of the window)" is 270,000 to
    330,000, as a plain integer: the value a session's commands are given, with no project entry behind it.

    Before: ``test_the_auto_compact_window_is_about_300k_tokens``.
    """
    if os.environ.get(SESSION_MARKER) != "1":
        pytest.skip(f"not run from a Claude Code session ({SESSION_MARKER} is not 1): the env block of the "
                    "user-level settings reaches a session's commands only; the window is not measured")
    assert support.WINDOW_KEY not in settings_env, (
        f"the env key of {support.SETTINGS_REL} sets {support.WINDOW_KEY}: the session's value is the project's, "
        "not the user-level one (DEC-636)"
    )
    value = os.environ.get(support.WINDOW_KEY)
    assert value is not None, (
        f"this session's commands are given no {support.WINDOW_KEY}: no auto-compact window is set for a session "
        "on this machine (DEC-636)"
    )
    assert value.isdigit(), (
        f"{support.WINDOW_KEY} is {value!r}; the CLI reads a plain integer only (a value like 300k reads as 300)"
    )
    low, high = support.WINDOW_TOKENS - support.WINDOW_TOLERANCE, support.WINDOW_TOKENS + support.WINDOW_TOLERANCE
    assert low <= int(value) <= high, f"{support.WINDOW_KEY} is {value}, not about {support.WINDOW_TOKENS}"


@pytest.mark.local_only
def test_the_pinned_cli_has_an_auto_compact_window():
    """ "An acceptance test proves whether it can": the installed CLI documents the window in its own help."""
    assert CLI.is_file(), "the Claude Code CLI is not at ~/.local/bin/claude (DEC-205)"
    done = subprocess.run([str(CLI), "--help"], capture_output=True, text=True, timeout=60, check=False)
    assert "--autocompact" in done.stdout, "`claude --help` names no --autocompact flag: no configurable window"
