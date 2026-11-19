"""W2-201 F1: unreadable means Sonnet and never a crash.

Each fault planted in turn in S5's project (the prompt names a C3 ticket, the exceptions file lists the engineer on Opus
for C3): an exceptions file that does not parse, a criticality file that does not parse or is missing, a ticket whose
front matter cannot be read, a project folder with no ``.tickets``. Under each, the hook refuses a spawn naming Opus
(exit 2, its reason on stderr) and lets a Sonnet spawn and a spawn with no model through (exit 0, nothing on stdout).
An event that is not JSON, or one for another tool, exits 0.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

BAD_TICKET = "---\nid: DAEO-c3c3\nallowed_paths: [src/critical/core/**\nprofile: STANDARD\n---\n# unreadable\n"

FAULTS = {
    "exceptions-file-does-not-parse": dict(exceptions="exceptions: [ {subagent_type: engineer, model: opus\n"),
    "criticality-file-does-not-parse": dict(rubric="version: 1\nrules: [ {class: C3, paths: [src/critical/*]\n"),
    "criticality-file-missing": dict(rubric=None),
    "ticket-front-matter-unreadable": dict(tickets={k.C3_TICKET: BAD_TICKET}),
    "no-tickets-folder": dict(tickets=None),
}


@pytest.mark.parametrize("fault", sorted(FAULTS))
def test_f1_a_fault_refuses_opus_and_lets_sonnet_and_no_model_through(hook_base, fault):
    """Red on the base for the criticality and ticket faults (the base lets a listed Opus spawn through without
    reading either); the exceptions fault is a guard there (the base reads an unparsable file as no exception)."""
    project = k.hook_project(hook_base, **FAULTS[fault])
    k.refused(k.run_hook(project, k.spawn(model="opus")))
    for model in ("sonnet", k.SONNET, k.NO_MODEL):
        k.let_through(k.run_hook(project, k.spawn(model=model)))


@pytest.mark.parametrize("event", [
    "this is not JSON {",
    '{"tool_name": "Bash", "tool_input": {"command": "true", "model": "opus"}}',
    '{"tool_name": "Read", "tool_input": {"file_path": "/x", "subagent_type": "fork"}}',
], ids=["not-json", "bash-tool", "read-tool"])
def test_f1_an_event_that_is_not_json_or_for_another_tool_exits_0(hook_base, event):
    """Guard on the base."""
    project = k.hook_project(hook_base)
    run = k.run_hook(project, event)
    assert run.code == 0, f"the hook did not exit 0\n{run.describe()}"
