"""W1-04 — the rule only ever escalates: to ``ask`` or to ``deny``, never to an allowance.

KPI failure 3: "A matcher result ever allows a command that the harness would
otherwise ask about (matching only escalates to ask or deny)".
DEC-120: "The classifier only ever escalates: a match never allows something
the harness would otherwise ask about (DEC-083)."

Three things follow, and each is tested:

- the hook never tells the harness to skip its own prompt (an explicit allow);
- a call the guard denies stays denied when the rule would only have asked;
- what the rule does not match keeps the guard's own answer.
"""

from __future__ import annotations

import pytest

import w1_04_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
ENGINEER_TICKET = support.ENGINEER_TICKET_ID
ids = support.command_id


def test_the_hook_never_gives_an_explicit_allow(project, bash):
    """Whatever the command, role and mode: no ``permissionDecision: "allow"`` and no ``decision: "approve"``."""
    commands = support.REPRESENTATIVE + support.ORDINARY + ("sudo apt-get install -y jq",)
    sessions = [(role, support.TICKET_OF[role]) for role in support.KNOWN_ROLES] + [(None, None)]
    for role, ticket in sessions:
        for mode in ("default", "auto", "bypassPermissions"):
            for command in commands:
                result = bash(project, command, role, ticket, mode=mode)
                assert not result.explicit_allow(), (
                    f"`{command}` with GOV_ROLE={role!r} in {mode} mode: the hook told the harness to allow "
                    f"the call without its own prompt: {result.describe()}"
                )


@pytest.mark.parametrize("command", support.ORDINARY, ids=ids)
def test_a_command_that_installs_nothing_gets_no_decision_from_the_rule(project, bash, command):
    """The hook stays silent, so the harness's own permission rules decide as before."""
    for role, ticket in ((ORCHESTRATOR, ORCHESTRATOR_TICKET), (ENGINEER, ENGINEER_TICKET)):
        for mode in ("default", "auto"):
            result = bash(project, command, role, ticket, mode=mode)
            what = f"`{command}` by {role} in {mode} mode"
            assert result.decision == "allow", f"{what} was escalated: {result.describe()}"
            assert not result.explicit_allow(), f"{what}: explicit allow: {result.describe()}"


# name: command. Each is an install and also a write the guard denies the orchestrator.
# Under DEC-156 the orchestrator writes anywhere except tests/acceptance/** and (DEC-176)
# .gov-runtime/ other than scratch/**. Each command combines an install with a write
# to one of those denied paths.
DENIED_BY_THE_GUARD = {
    "write-into-gov-runtime": "pip install requests && touch .gov-runtime/findings.jsonl",
    "redirect-into-gov-runtime": "npm install -g ccusage > .gov-runtime/records.jsonl",
    "write-into-the-acceptance-tests": "pip install requests && touch tests/acceptance/W1-90/test_new.py",
}


@pytest.mark.parametrize("case", sorted(DENIED_BY_THE_GUARD), ids=sorted(DENIED_BY_THE_GUARD))
def test_a_call_the_guard_denies_stays_denied_for_the_orchestrator(project, bash, case):
    """The rule's ``ask`` must not replace the guard's ``deny``."""
    command = DENIED_BY_THE_GUARD[case]
    result = bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    assert result.decision == "deny", (
        f"`{command}` by the orchestrator: the guard's denial of the write was lowered: {result.describe()}"
    )


def test_a_frozen_repository_stays_closed_to_an_install_that_writes(project, bash):
    """The write is inside the orchestrator's ticket paths. The freeze flag denies it; the rule must not ask instead."""
    command = "pip install requests | tee governance/project/install.log"
    result = bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    assert result.decision == "ask", f"`{command}` by the orchestrator before the freeze: {result.describe()}"
    support.set_freeze(project)
    result = bash(project, command, ORCHESTRATOR, ORCHESTRATOR_TICKET)
    assert result.decision == "deny", f"`{command}` by the orchestrator while frozen: {result.describe()}"


def test_the_guard_s_answers_on_file_writes_are_unchanged(project, write):
    """The rule shares the guard's hook (DEC-120). It must leave the guard's own decisions as they were."""
    result = write(project, "src/gov/guard/decide.py", ENGINEER, ENGINEER_TICKET)
    assert result.decision == "allow", f"Write inside the engineer's ticket paths: {result.describe()}"
    assert not result.explicit_allow(), f"Write inside the ticket paths: explicit allow: {result.describe()}"
    result = write(project, "README.md", ENGINEER, ENGINEER_TICKET)
    assert result.decision == "deny", f"Write outside the engineer's ticket paths: {result.describe()}"
    result = write(project, "governance/project/tool-registry.yaml", ORCHESTRATOR, ORCHESTRATOR_TICKET)
    assert result.decision == "allow", f"Write inside the orchestrator's ticket paths: {result.describe()}"
    result = write(project, "tests/acceptance/W1-90/test_fixture.py", ORCHESTRATOR, ORCHESTRATOR_TICKET)
    assert result.decision == "deny", f"Write into tests/acceptance by the orchestrator: {result.describe()}"
