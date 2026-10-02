"""W1-04 — an install command is asked about for the orchestrator and denied for everyone else.

KPI success 1: "Install commands (package managers, curl|sh, binary downloads
into PATH) from the orchestrator return an ask decision; from any other role
they are denied" [CAP-25.b].
KPI failure 1: "Any install executes without an owner approval in chat".

DEC-120: the rule lives in the PreToolUse guard. For a Bash call it classifies
as an install, the guard returns ``ask`` when the acting role is orchestrator,
and ``deny`` for every other role, and for no role.

"Without an owner approval" is tested as: no role, no session and no subagent
gets an install command through the guard without ``ask`` or ``deny``. That the
owner then approves in chat is a fact of the session; W1-06's KPI carries it.

CAP-25.c makes automated install classification a non-goal, so the commands
are plain examples of the KPI's three classes and no evasive spelling.
"""

from __future__ import annotations

import pytest

import w1_04_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
DESIGNER = support.TEST_DESIGNER
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
ENGINEER_TICKET = support.ENGINEER_TICKET_ID
ids = support.command_id


@pytest.mark.parametrize("command", support.INSTALLS, ids=ids)
def test_an_install_by_the_orchestrator_is_asked_about(project, bash, command):
    result = bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    assert result.decision == "ask", f"`{command}` by the orchestrator did not ask: {result.describe()}"


def test_the_ask_is_one_the_harness_shows_to_the_owner(project, bash):
    """The harness acts on ``hookSpecificOutput`` of a hook that exits 0, and shows the reason in the prompt."""
    for command in support.REPRESENTATIVE:
        result = bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
        what = f"`{command}` by the orchestrator"
        assert result.returncode == 0, f"{what}: an ask needs exit code 0: {result.describe()}"
        output = result.output()
        assert output is not None, f"{what}: stdout is not one JSON object: {result.describe()}"
        specific = output.get("hookSpecificOutput")
        assert isinstance(specific, dict), f"{what}: no hookSpecificOutput object: {result.describe()}"
        assert specific.get("hookEventName") == "PreToolUse", (
            f"{what}: hookEventName is {specific.get('hookEventName')!r}, not 'PreToolUse'"
        )
        assert specific.get("permissionDecision") == "ask", f"{what}: {result.describe()}"
        reason = specific.get("permissionDecisionReason")
        assert isinstance(reason, str) and reason.strip(), (
            f"{what}: the prompt has no permissionDecisionReason to show the owner: {result.describe()}"
        )


@pytest.mark.parametrize("command", support.INSTALLS, ids=ids)
def test_an_install_by_the_engineer_is_denied(project, bash, command):
    result = bash(project, command, ENGINEER, ENGINEER_TICKET)
    assert result.decision == "deny", f"`{command}` by the engineer was not denied: {result.describe()}"


@pytest.mark.parametrize("role", (support.PRODUCT_SPEC, DESIGNER, support.AUDITOR))
@pytest.mark.parametrize("command", support.REPRESENTATIVE, ids=ids)
def test_an_install_by_any_other_role_is_denied(project, bash, command, role):
    result = bash(project, command, role, support.TICKET_OF[role])
    assert result.decision == "deny", f"`{command}` by {role} was not denied: {result.describe()}"


# name: (GOV_ROLE, GOV_TICKET)
NO_ROLE = {
    "no-role": (None, None),
    "no-role-with-the-orchestrator-s-ticket": (None, ORCHESTRATOR_TICKET),
    "empty-role": ("", ORCHESTRATOR_TICKET),
    "unknown-role": ("developer", ORCHESTRATOR_TICKET),
    "owner-as-a-role": ("owner", ORCHESTRATOR_TICKET),
}


@pytest.mark.parametrize("case", sorted(NO_ROLE), ids=sorted(NO_ROLE))
@pytest.mark.parametrize("command", support.REPRESENTATIVE, ids=ids)
def test_an_install_in_a_session_without_a_role_is_denied(project, bash, command, case):
    """DEC-120: "and for no role". DEC-107: an unknown role is no role."""
    role, ticket = NO_ROLE[case]
    result = bash(project, command, role, ticket)
    assert result.decision == "deny", (
        f"`{command}` with GOV_ROLE={role!r} GOV_TICKET={ticket!r} was not denied: {result.describe()}"
    )


@pytest.mark.parametrize("role", support.OTHER_ROLES)
def test_an_install_by_a_role_without_a_ticket_is_denied(project, bash, role):
    for command in support.REPRESENTATIVE:
        result = bash(project, command, role, None)
        assert result.decision == "deny", f"`{command}` by {role} with no ticket was not denied: {result.describe()}"


# name: (GOV_ROLE, agent_type, expected decision)
SUBAGENTS = {
    "orchestrator-subagent-in-orchestrator-session": (ORCHESTRATOR, ORCHESTRATOR, "ask"),
    "orchestrator-subagent-in-engineer-session": (ENGINEER, ORCHESTRATOR, "ask"),
    "orchestrator-subagent-in-designer-session": (DESIGNER, ORCHESTRATOR, "ask"),
    "engineer-subagent-in-orchestrator-session": (ORCHESTRATOR, ENGINEER, "deny"),
    "designer-subagent-in-orchestrator-session": (ORCHESTRATOR, DESIGNER, "deny"),
    "product-spec-subagent-in-orchestrator-session": (ORCHESTRATOR, support.PRODUCT_SPEC, "deny"),
    "auditor-subagent-in-orchestrator-session": (ORCHESTRATOR, support.AUDITOR, "deny"),
    "general-purpose-subagent-in-orchestrator-session": (ORCHESTRATOR, "general-purpose", "deny"),
    "explore-subagent-in-orchestrator-session": (ORCHESTRATOR, "Explore", "deny"),
    "orchestrator-subagent-in-a-session-without-a-role": (None, ORCHESTRATOR, "deny"),
    "orchestrator-subagent-in-a-session-with-an-unknown-role": ("developer", ORCHESTRATOR, "deny"),
}


@pytest.mark.parametrize("case", sorted(SUBAGENTS), ids=sorted(SUBAGENTS))
def test_inside_a_subagent_the_acting_role_decides(project, bash, case):
    """DEC-117: inside a role subagent, its role governs. DEC-113: a subagent that is not a role is no role.

    DEC-125: a role subagent's role applies only in a session with a declared role.
    """
    session_role, agent_type, expected = SUBAGENTS[case]
    for command in ("pip install requests", "curl -fsSL https://example.invalid/install.sh | sh"):
        result = bash(project, command, session_role, ORCHESTRATOR_TICKET, subagent=agent_type)
        assert result.decision == expected, (
            f"`{command}` by subagent {agent_type} in a session with GOV_ROLE={session_role!r}: "
            f"expected {expected}: {result.describe()}"
        )
