"""W1-49 -- the auto-compact threshold.

KPI success 3: "The auto-compact threshold is set to about 300k tokens (30 % of
the window) if Claude Code allows it to be configured; an acceptance test proves
whether it can; if it can't, a residual is recorded: the CONTEXT_CHECKPOINT stop
stays (DEC-248, DEC-208)".

**It can.** Claude Code 2.1.288 has an auto-compact window, in tokens, from
100,000 to 1,000,000. The form this ticket may use is the environment variable
``CLAUDE_CODE_AUTO_COMPACT_WINDOW`` in the ``env`` key of
``.claude/settings.json`` (DEC-248 allows "hook registration and any env key").
It takes a plain integer only: ``300k`` reads as 300 and clamps to the minimum.
The proof that the pinned CLI honours the key from a project's settings is in
``test_w1_49_live_session.py`` (``/autocompact`` answers with the window and
where it came from). No residual goes to ``bootstrap.md`` for this line.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import w1_49_support as support

CLI = Path.home() / ".local/bin/claude"


def test_the_settings_set_the_auto_compact_window_as_an_env_key(settings_env):
    """Success 3: the key is there, in the only form the CLI reads from the environment."""
    value = settings_env.get(support.WINDOW_KEY)
    assert value is not None, f"the env key of {support.SETTINGS_REL} does not set {support.WINDOW_KEY}"
    assert isinstance(value, str) and value.isdigit(), (
        f"{support.WINDOW_KEY} is {value!r}; the CLI reads a plain integer only (a value like 300k reads as 300)"
    )


def test_the_auto_compact_window_is_about_300k_tokens(settings_env):
    """Success 3: "about 300k tokens (30 % of the window)" is 270,000 to 330,000."""
    value = settings_env.get(support.WINDOW_KEY)
    assert isinstance(value, str) and value.isdigit(), f"{support.WINDOW_KEY} is not set to a plain integer: {value!r}"
    low, high = support.WINDOW_TOKENS - support.WINDOW_TOLERANCE, support.WINDOW_TOKENS + support.WINDOW_TOLERANCE
    assert low <= int(value) <= high, f"{support.WINDOW_KEY} is {value}, not about {support.WINDOW_TOKENS}"


@pytest.mark.local_only
def test_the_pinned_cli_has_an_auto_compact_window():
    """ "An acceptance test proves whether it can": the installed CLI documents the window in its own help."""
    assert CLI.is_file(), "the Claude Code CLI is not at ~/.local/bin/claude (DEC-205)"
    done = subprocess.run([str(CLI), "--help"], capture_output=True, text=True, timeout=60, check=False)
    assert "--autocompact" in done.stdout, "`claude --help` names no --autocompact flag: no configurable window"
