"""W1-05 — minimal subagent definitions for the five Wave 1 roles (DEC-119).

KPI success 3 to 7: "A minimal subagent definition for the <role> role exists
under .claude/agents/, with the subagent type name <role>".

DEC-113: a subagent whose type is not a defined role is read-only. So the guard
needs the five roles as subagent types the moment it goes live, and the type
names must be the role names the guard knows.

A definition is a Markdown file under ``.claude/agents/`` whose YAML frontmatter
holds ``name`` (the subagent type name) and ``description``; the harness needs
both to load it.
"""

from __future__ import annotations

import pytest

import w1_05_support as support

TICKET = support.FIXTURE_TICKET_ID


def _definition(role):
    found = support.agent_definitions().get(role, [])
    assert found, (
        f"no file under {support.AGENTS_REL}/ defines a subagent with the type name {role!r} "
        "(frontmatter `name:`)"
    )
    names = ", ".join(str(path.relative_to(support.REPO_ROOT)) for path in found)
    assert len(found) == 1, f"the subagent type name {role!r} is defined {len(found)} times: {names}"
    return found[0]


@pytest.mark.parametrize("role", support.ROLES)
def test_a_subagent_definition_exists_for_the_role(role):
    path = _definition(role)
    pairs = support.frontmatter(path.read_text(encoding="utf-8"))
    assert pairs.get("description", "").strip(), (
        f"{path.relative_to(support.REPO_ROOT)} has no `description`; the harness does not load it as a subagent"
    )


@pytest.mark.parametrize("role", support.ROLES)
def test_the_live_guard_takes_the_definition_s_type_name_as_the_role(role, live, decide):
    """Inside the subagent, the hook input carries the definition's ``name`` as ``agent_type`` (DEC-117)."""
    type_name = support.frontmatter(_definition(role).read_text(encoding="utf-8"))["name"]
    target = live / support.SCRATCH_REL / "note.txt"
    result = decide(live, "Write", support.write_input("Write", target), support.ORCHESTRATOR, TICKET,
                    subagent=type_name)
    assert result.decision == "allow", (
        f"Write to the scratch set by subagent {type_name!r} in an orchestrator session was not allowed, "
        f"so the guard does not take it as a role: {result.describe()}"
    )
    result = decide(live, "Write", support.write_input("Write", target), support.ORCHESTRATOR, TICKET,
                    subagent="general-purpose")
    assert result.decision == "deny", (
        f"Write to the scratch set by a general-purpose subagent was not denied: {result.describe()}"
    )


def test_the_engineer_subagent_can_work_on_an_engineer_ticket(live, decide):
    """The reason for DEC-113's consequence: delegated work must be able to write once the guard is live."""
    _definition(support.ENGINEER)
    source = live / support.FIXTURE_SOURCE
    result = decide(live, "Write", support.write_input("Write", source), support.ORCHESTRATOR, TICKET,
                    subagent=support.ENGINEER)
    assert result.decision == "allow", (
        f"Write on {support.FIXTURE_SOURCE} by the engineer subagent in an orchestrator session: {result.describe()}"
    )
    acceptance = live / support.ACCEPTANCE_REL / "W1-90" / "test_new.py"
    result = decide(live, "Write", support.write_input("Write", acceptance), support.ORCHESTRATOR, TICKET,
                    subagent=support.ENGINEER)
    assert result.decision == "deny", (
        f"Write on an acceptance test by the engineer subagent was not denied: {result.describe()}"
    )
    _definition(support.TEST_DESIGNER)
    result = decide(live, "Write", support.write_input("Write", acceptance), support.ORCHESTRATOR, TICKET,
                    subagent=support.TEST_DESIGNER)
    assert result.decision == "allow", (
        f"Write on an acceptance test by the test-designer subagent: {result.describe()}"
    )
