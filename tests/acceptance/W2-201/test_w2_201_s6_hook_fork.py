"""W2-201 S6: no fork for helper work, by the hook.

A spawn whose ``subagent_type`` is ``fork`` (tool ``Agent`` or ``Task``, with or without a model) is refused, exit 2,
with a message naming "a fresh helper from a written brief" and DEC-1212 (4); only an exceptions entry for
``subagent_type: fork`` lifts it; every other subagent type is judged as before. The project is S5's (a C3 ticket named
in the prompt, the four roles' C3 entries), so no other rule refuses these spawns.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

FORK_WORDS = ("a fresh helper from a written brief", "DEC-1212 (4)")
FORKS = [("Agent", k.NO_MODEL), ("Agent", "opus"), ("Task", k.NO_MODEL), ("Task", k.SONNET)]


@pytest.mark.parametrize("tool, model", FORKS, ids=["agent-no-model", "agent-opus", "task-no-model", "task-sonnet"])
def test_s6_a_fork_spawn_is_refused_naming_a_fresh_helper_from_a_written_brief(hook_base, tool, model):
    project = k.hook_project(hook_base)
    k.refused(k.run_hook(project, k.spawn(kind="fork", model=model, tool=tool)), *FORK_WORDS)


def test_s6_an_exceptions_entry_for_fork_lifts_the_refusal(hook_base):
    """Guard on the base (the base lets a Sonnet fork through)."""
    entries = k.C3_ENTRIES + [{"subagent_type": "fork", "model": "sonnet", "decided": "the owner (W2-201 fixture)"}]
    project = k.hook_project(hook_base, exceptions={"exceptions": entries})
    k.let_through(k.run_hook(project, k.spawn(kind="fork", model="sonnet")))


def test_s6_an_entry_for_every_type_does_not_lift_the_fork_refusal(hook_base):
    """Only an entry for ``subagent_type: fork`` lifts it, not one written for every type (``*``)."""
    entries = k.C3_ENTRIES + [{"subagent_type": "*", "model": "sonnet", "decided": "the owner (W2-201 fixture)"}]
    project = k.hook_project(hook_base, exceptions={"exceptions": entries})
    k.refused(k.run_hook(project, k.spawn(kind="fork", model="sonnet")), *FORK_WORDS)


@pytest.mark.parametrize("model", [k.NO_MODEL, "sonnet"], ids=["no-model", "sonnet"])
def test_s6_a_general_purpose_spawn_is_judged_as_before(hook_base, model):
    """Guard on the base: a general-purpose helper on Sonnet or with no model is let through."""
    project = k.hook_project(hook_base)
    k.let_through(k.run_hook(project, k.spawn(kind="general-purpose", model=model)))
