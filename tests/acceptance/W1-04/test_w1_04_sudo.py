"""W1-04 — ``sudo`` is denied to every agent role, the orchestrator included.

KPI failure 2: "sudo is ever allowed to an agent role".
CAP-25.b: "sudo with the owner". DEC-083: "sudo stays with the owner".

For the orchestrator the answer is ``deny`` and not ``ask``: an ``ask`` that the
owner approves would still be ``sudo`` run by an agent.
"""

from __future__ import annotations

import pytest

import w1_04_support as support

ORCHESTRATOR = support.ORCHESTRATOR
ids = support.command_id


@pytest.mark.parametrize("role", support.KNOWN_ROLES)
@pytest.mark.parametrize("command", support.SUDO, ids=ids)
def test_sudo_is_denied_to_every_role(project, bash, command, role):
    result = bash(project, command, role, support.TICKET_OF[role])
    assert result.decision == "deny", f"`{command}` by {role} was not denied: {result.describe()}"


@pytest.mark.parametrize("command", support.SUDO, ids=ids)
def test_sudo_is_denied_in_a_session_without_a_role(project, bash, command):
    for role in (None, "developer"):
        result = bash(project, command, role, None)
        assert result.decision == "deny", f"`{command}` with GOV_ROLE={role!r} was not denied: {result.describe()}"


@pytest.mark.parametrize("mode", support.PERMISSION_MODES)
def test_sudo_by_the_orchestrator_is_denied_in_every_permission_mode(project, bash, mode):
    for command in ("sudo apt-get install -y jq", "sudo ls /root"):
        result = bash(project, command, ORCHESTRATOR, support.ORCHESTRATOR_TICKET_ID, mode=mode)
        assert result.decision == "deny", (
            f"`{command}` by the orchestrator in {mode} mode was not denied: {result.describe()}"
        )


def test_sudo_by_an_orchestrator_subagent_is_denied(project, bash):
    command = "sudo apt-get install -y jq"
    result = bash(project, command, support.ENGINEER, support.ORCHESTRATOR_TICKET_ID, subagent=ORCHESTRATOR)
    assert result.decision == "deny", f"`{command}` by an orchestrator subagent was not denied: {result.describe()}"
