"""W1-49 -- the two hooks exist and are registered; the guard hooks stay registered.

KPI success 1 [CAP-37.g]: "A PreCompact hook ensures the orchestrator's checkpoint
is current". KPI success 2 [CAP-37.g]: "A SessionStart hook on compact, clear and
resume injects ...". A hook that is not registered runs for nobody.

Only the ``hooks`` key of ``.claude/settings.json`` is read. Plain ``startup`` is
not required to be registered, and no test here asks for it or forbids it.
"""

from __future__ import annotations

import pytest

import w1_49_support as support


@pytest.mark.parametrize("rel", (support.PRECOMPACT_REL, support.SESSIONSTART_REL))
def test_the_hook_file_exists_in_the_kernel_template(rel):
    assert (support.REPO_ROOT / rel).is_file(), f"the hook {rel} does not exist yet"


@pytest.mark.parametrize("trigger", ("manual", "auto"))
def test_the_precompact_hook_is_registered_for_both_triggers(hooks, trigger):
    """Success 1, failure 1: a compaction Claude Code starts itself (``auto``) is the one nobody watches."""
    command = support.command_for(hooks, "PreCompact", trigger, support.PRECOMPACT_REL)
    assert command is not None, (
        f"{support.SETTINGS_REL} registers no PreCompact hook that runs {support.PRECOMPACT_REL} for a "
        f"{trigger} compaction"
    )
    assert "$CLAUDE_PROJECT_DIR" in command, f"the command does not find the hook through $CLAUDE_PROJECT_DIR: {command}"


@pytest.mark.parametrize("source", ("compact", "clear", "resume"))
def test_the_sessionstart_hook_is_registered_for_compact_clear_and_resume(hooks, source):
    """Success 2, failure 2 [CAP-37.g]."""
    command = support.command_for(hooks, "SessionStart", source, support.SESSIONSTART_REL)
    assert command is not None, (
        f"{support.SETTINGS_REL} registers no SessionStart hook that runs {support.SESSIONSTART_REL} for the "
        f"source {source}"
    )
    assert "$CLAUDE_PROJECT_DIR" in command, f"the command does not find the hook through $CLAUDE_PROJECT_DIR: {command}"


@pytest.mark.parametrize("event, tool, rel", (
    ("PreToolUse", "Edit", support.GUARD_REL),
    ("PreToolUse", "Write", support.GUARD_REL),
    ("PreToolUse", "NotebookEdit", support.GUARD_REL),
    ("PreToolUse", "Bash", support.GUARD_REL),
    ("PreToolUse", "Read", support.GUARD_REL),
    ("PostToolUse", "Bash", support.CONTAINMENT_REL),
    ("PostToolUseFailure", "Bash", support.CONTAINMENT_REL),
))
def test_the_guard_hooks_stay_registered(hooks, event, tool, rel):
    """The ticket edits the settings file for the two new hooks only. Green before the implementation; it must stay so."""
    assert support.command_for(hooks, event, tool, rel) is not None, (
        f"{support.SETTINGS_REL} no longer registers {rel} for {event} on {tool}"
    )
