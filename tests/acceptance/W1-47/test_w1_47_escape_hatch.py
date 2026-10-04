"""W1-47 -- the guard denies a Bash call that asks to run outside the sandbox.

KPI success 1: "The guard's PreToolUse hook denies any Bash call carrying
dangerouslyDisableSandbox: true, whatever the role [CAP-62.a]".
KPI failure 1: "A Bash call carrying dangerouslyDisableSandbox: true reaches
execution".

The field is part of the Bash tool's input. The hook sees it in ``tool_input``
and answers with a deny decision, whoever calls and whatever the command is.
No command here is run.
"""

from __future__ import annotations

import pytest

import w1_47_support as support

ORCHESTRATOR = support.EVERY_ACTOR[support.ORCHESTRATOR]
ENGINEER = support.EVERY_ACTOR[support.ENGINEER]

# Commands the guard lets through for every actor today: they write nothing and install nothing.
READ_ONLY = {
    "listing": "ls -la",
    "git-status": "git status --porcelain",
    "test-run": "python3 -m pytest tests/unit -q",
}
ESCAPE = {"dangerouslyDisableSandbox": True}


@pytest.mark.parametrize("who", sorted(support.EVERY_ACTOR))
@pytest.mark.parametrize("command", sorted(READ_ONLY))
def test_the_escape_hatch_is_denied_whatever_the_role(project, guard, who, command):
    """KPI success 1, failure 1 [CAP-62.a]: every role, a session with no role, and a subagent."""
    text = READ_ONLY[command]
    result = guard(project, "Bash", support.bash_input(text, **ESCAPE), support.EVERY_ACTOR[who])
    support.assert_denied_by_rule(result, f"Bash `{text}` with dangerouslyDisableSandbox: true by {who}")


@pytest.mark.parametrize("mode", support.PERMISSION_MODES)
def test_the_escape_hatch_is_denied_in_every_permission_mode(project, guard, mode):
    """KPI failure 1: no permission mode lets the call reach execution."""
    result = guard(project, "Bash", support.bash_input("ls -la", **ESCAPE), ORCHESTRATOR, mode=mode)
    support.assert_denied_by_rule(result, f"Bash `ls -la` with dangerouslyDisableSandbox: true in {mode} mode")


def test_the_escape_hatch_is_denied_on_a_write_inside_the_ticket_paths(project, guard):
    """KPI success 1: a write the engineer may make is still denied when it asks to leave the sandbox."""
    command = f"echo changed > {support.check_support.SOURCE_FILE}"
    allowed = guard(project, "Bash", support.bash_input(command), ENGINEER)
    support.assert_allowed(allowed, f"the fixture call `{command}` by the engineer, without the field,")
    result = guard(project, "Bash", support.bash_input(command, **ESCAPE), ENGINEER)
    support.assert_denied_by_rule(result, f"Bash `{command}` with dangerouslyDisableSandbox: true by the engineer")


def test_the_escape_hatch_on_an_install_is_denied_not_asked(project, guard):
    """KPI failure 1: an approval prompt would let the owner send the command out of the sandbox."""
    command = "pip install requests"
    result = guard(project, "Bash", support.bash_input(command, **ESCAPE), ORCHESTRATOR)
    support.assert_denied_by_rule(
        result, f"Bash `{command}` with dangerouslyDisableSandbox: true by the orchestrator")


def test_the_escape_hatch_is_denied_through_the_committed_settings(wired, live):
    """KPI success 1: the rule is live in this repository, through the commands its settings register."""
    result = live(wired, "Bash", support.bash_input("ls -la", **ESCAPE), support.ORCHESTRATOR)
    assert result.ran, f"the Bash call reached no registered PreToolUse command: {result.describe()}"
    assert result.decision == "deny", (
        f"Bash `ls -la` with dangerouslyDisableSandbox: true was not denied by the registered commands: "
        f"{result.describe()}"
    )


@pytest.mark.parametrize("who", sorted(support.EVERY_ACTOR))
@pytest.mark.parametrize("extra", ({}, {"dangerouslyDisableSandbox": False}), ids=("absent", "false"))
def test_a_call_that_stays_in_the_sandbox_is_still_let_through(project, guard, who, extra):
    """The rule is about the field set to true: the same command without it, or with it false, is unchanged."""
    result = guard(project, "Bash", support.bash_input("ls -la", **extra), support.EVERY_ACTOR[who])
    support.assert_allowed(result, f"Bash `ls -la` by {who} with dangerouslyDisableSandbox {extra or 'absent'}")
