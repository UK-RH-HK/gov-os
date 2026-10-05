"""W1-46 -- ``Edit`` deny rules for the acceptance tests, the tickets and ``.claude`` (batch 4, after implementation).

KPI success 11 (DEC-315): "The settings it builds carry Edit deny rules for
tests/acceptance/** (every role but the independent test designer), .tickets/**
and .claude/**: in a launched worker session a write there fails, through a file
tool and through an opaque Bash form".

DEC-315 (owner, on DP-12 option (a)), under MR-3, CAP-58 and CAP-61. Why: an
opaque Bash write (an interpreter one-liner, ``sh -c``) is not parsed by the
guard and the working directory is writable in the sandbox; an ``Edit`` deny
rule binds the file tools and Bash at the OS level (CAP-58.d).

**The built rules** are read by what they cover (README, reading 4): a file that
exists at launch and a new one, in each tree. ``.claude/settings.local.json``
is the file git ignores and the containment check does not see (DP-12).

**The independent test designer** writes ``tests/acceptance/**`` (MR-3): its
settings carry no rule that covers a path there, and do carry the two others.

**A ticket that names a path under one of the three trees.** The package left
such a path out of the rule; the decision as taken does not. The rule stays
(fail closed): no exception is asserted, and none is accepted.

**"Through a file tool"** is the guard's side and the rules' side: the guard,
asked through the registered PreToolUse commands, refuses a Write and an Edit
there for each worker role on its fixture ticket. "Through an opaque Bash form"
needs a session: three assertions in the engineer session of
``test_w1_46_live_sessions.py``.

No session is started.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

w47 = support.w47
ENGINEER, TEST_DESIGNER = support.ENGINEER, support.TEST_DESIGNER
NOT_THE_TEST_DESIGNER = tuple(role for role in support.WORKER_ROLES if role != TEST_DESIGNER)
NEW_TICKET = "DAEO-zz98"

# In each tree: a path that exists in the fixture project at launch, and one that does not.
ACCEPTANCE = ("tests/acceptance/W1-90/test_fixture.py", "tests/acceptance/W1-99/test_new.py")
TICKETS = (f".tickets/{support.TICKET_OF[ENGINEER]}.md", ".tickets/DAEO-zz99.md")
CLAUDE = (support.SETTINGS_REL, support.LOCAL_SETTINGS_REL, support.AGENT_REL, ".claude/commands/new.md")


def _open(result, paths, project, sandbox):
    return [rel for rel in paths if not support.edit_denied(result, rel, project, sandbox)]


@pytest.mark.parametrize("role", NOT_THE_TEST_DESIGNER)
def test_the_built_settings_deny_edits_of_the_acceptance_tests(launch, project, sandbox, role):
    """Every role but the independent test designer."""
    result = launch(role)
    assert _open(result, ACCEPTANCE, project, sandbox) == [], (
        f"no Edit deny rule of a launched {role}'s settings covers {_open(result, ACCEPTANCE, project, sandbox)}; "
        f"rules: {support.deny_rules(result.settings(), 'Edit')}"
    )


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_built_settings_deny_edits_of_the_tickets(launch, project, sandbox, role):
    result = launch(role)
    assert _open(result, TICKETS, project, sandbox) == [], (
        f"no Edit deny rule of a launched {role}'s settings covers {_open(result, TICKETS, project, sandbox)}; "
        f"rules: {support.deny_rules(result.settings(), 'Edit')}"
    )


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_built_settings_deny_edits_under_dot_claude(launch, project, sandbox, role):
    """The settings, the local settings that do not exist yet, a role definition, a new file."""
    result = launch(role)
    assert _open(result, CLAUDE, project, sandbox) == [], (
        f"no Edit deny rule of a launched {role}'s settings covers {_open(result, CLAUDE, project, sandbox)}; "
        f"rules: {support.deny_rules(result.settings(), 'Edit')}"
    )


def test_the_test_designers_settings_carry_no_rule_for_the_acceptance_tests(launch, project, sandbox):
    """MR-3: the acceptance tests are the test designer's to write, in a launched session too."""
    result = launch(TEST_DESIGNER)
    closed = [rel for rel in (*ACCEPTANCE, "tests/acceptance", support.OWN_PATH[TEST_DESIGNER])
              if support.edit_denied(result, rel, project, sandbox)]
    assert closed == [], (
        f"an Edit deny rule of a launched test designer's settings covers {closed}; rules: "
        f"{support.deny_rules(result.settings(), 'Edit')}"
    )


def test_the_test_designer_on_another_roles_ticket_keeps_its_own_rules(launch, project, sandbox):
    """The rules follow the role launched, not the role of the ticket (DEC-271): here the auditor's ticket."""
    result = launch(TEST_DESIGNER, support.TICKET_OF[support.AUDITOR])
    assert result.run.returncode == 0, f"gov launch refused a test designer on an auditor's ticket\n{result.describe()}"
    assert not support.edit_denied(result, ACCEPTANCE[0], project, sandbox)
    assert _open(result, TICKETS + CLAUDE, project, sandbox) == []


def test_a_ticket_that_names_a_path_under_the_three_trees_keeps_the_rules(launch, project, sandbox):
    """Fail closed: the ticket's ``allowed_paths`` open nothing in the built rules."""
    named = (support.AGENT_REL, TICKETS[0], "tests/acceptance/W1-90/**")
    ticket = support.write_ticket(project, NEW_TICKET, ENGINEER, allowed_paths=("src/gov/launch/**",) + named)
    result = launch(ENGINEER, ticket)
    assert result.run.returncode == 0, f"gov launch refused the ticket\n{result.describe()}"
    opened = _open(result, (support.AGENT_REL, TICKETS[0], ACCEPTANCE[0]), project, sandbox)
    assert opened == [], (
        f"a ticket that names {opened} took them out of the Edit deny rules; rules: "
        f"{support.deny_rules(result.settings(), 'Edit')}"
    )


@pytest.mark.parametrize("role", support.WORKER_ROLES)
@pytest.mark.parametrize("tool", ("Write", "Edit"))
def test_a_file_tool_write_to_the_three_trees_is_refused_by_the_guard(guard, project, role, tool):
    """ "Through a file tool": the guard's side, for each worker role on its fixture ticket."""
    paths = TICKETS + CLAUDE + (() if role == TEST_DESIGNER else ACCEPTANCE)
    for rel in paths:
        result = guard(tool, w47.write_input(tool, project / rel), role)
        w47.assert_stopped(result, f"{tool} to {rel} by {role}")
