"""W1-04 — the approval prompt appears in every permission mode, Auto mode included.

KPI success 2: "The approval prompt appears even when the harness runs in Auto
mode (DEC-083 KPI)" [CAP-25.b].

DEC-120: the Auto-mode KPI is verified by driving the hook, and by one live
headless attempt. These tests are the first half: the guard is given the
harness's ``permission_mode`` and must answer ``ask`` whatever it says. A
PreToolUse ``ask`` is what makes the harness show the prompt in a mode that
would otherwise let the call through. The live attempt is the switch-over's
(W1-05) and is not a pytest case.
"""

from __future__ import annotations

import pytest

import w1_04_support as support

ORCHESTRATOR = support.ORCHESTRATOR
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
ids = support.command_id


@pytest.mark.parametrize("mode", support.PERMISSION_MODES)
@pytest.mark.parametrize("command", support.REPRESENTATIVE, ids=ids)
def test_an_install_by_the_orchestrator_is_asked_about_in_every_permission_mode(project, bash, command, mode):
    result = bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET, mode=mode)
    assert result.decision == "ask", (
        f"`{command}` by the orchestrator in {mode} mode did not ask: {result.describe()}"
    )


@pytest.mark.parametrize("mode", ("auto", "bypassPermissions", "acceptEdits", "dontAsk"))
def test_an_install_by_another_role_is_denied_in_the_modes_that_skip_prompts(project, bash, mode):
    for role in support.OTHER_ROLES:
        for command in support.REPRESENTATIVE:
            result = bash(project, command, role, support.TICKET_OF[role], mode=mode)
            assert result.decision == "deny", (
                f"`{command}` by {role} in {mode} mode was not denied: {result.describe()}"
            )


@pytest.mark.parametrize("mode", ("auto", "bypassPermissions"))
def test_an_orchestrator_subagent_is_asked_about_in_auto_mode_too(project, bash, mode):
    command = "npm install -g ccusage"
    result = bash(project, command, support.ENGINEER, ORCHESTRATOR_TICKET, subagent=ORCHESTRATOR, mode=mode)
    assert result.decision == "ask", (
        f"`{command}` by an orchestrator subagent in {mode} mode did not ask: {result.describe()}"
    )
