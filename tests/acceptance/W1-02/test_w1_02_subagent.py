"""W1-02 — inside a role subagent, the subagent's own role governs.

DEC-117 (owner correction, amends DEC-107): "Inside a subagent with a defined
role, that subagent's role governs its tool calls. The session's role governs
the main thread only. There is no 'stricter of the two'. A subagent whose type
isn't a defined role stays read-only (DEC-113)."

Inside a subagent the PreToolUse stdin object holds ``agent_id`` and
``agent_type``; ``agent_type`` is the name of the subagent definition. Role
subagents are named after their role (DEC-119).

What the tests hold the guard to:

- a write by a role subagent is judged as that role would be judged on the
  active ticket (``GOV_TICKET``), whatever ``GOV_ROLE`` says;
- nothing of the session's role carries into the subagent: an engineer subagent
  in a test-designer session cannot write acceptance tests, and a test-designer
  subagent in an engineer session cannot write source;
- a subagent whose type is not one of the five roles cannot write at all,
  scratch included, and can still read.

Not tested: a role subagent in a session that declares no role or an unknown
role. DEC-117 and KPI success 4 point different ways there; the question is
with the owner (W1-02 KD-9).
"""

from __future__ import annotations

import pytest

import w1_02_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
PRODUCT_SPEC = support.PRODUCT_SPEC
DESIGNER = support.TEST_DESIGNER
AUDITOR = support.AUDITOR

ENGINEER_TICKET = support.TICKET_ID
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
PRODUCT_SPEC_TICKET = support.PRODUCT_SPEC_TICKET_ID

SOURCE = "src/gov/guard/decide.py"
ACCEPTANCE = f"tests/acceptance/{support.TICKET_WBS_ID}/test_fixture.py"
SETTINGS = ".claude/settings.json"
SPEC = "docs/spec/feature.md"
SCRATCH = f"{support.SCRATCH_REL}/note.txt"

# name: (GOV_ROLE, agent_type, GOV_TICKET, repository-relative path)

# The subagent's role allows the write. Under "the stricter of the two" every
# case but the two same-role ones was denied.
ROLE_ALLOWS = {
    "engineer-in-orchestrator-session-source": (ORCHESTRATOR, ENGINEER, ENGINEER_TICKET, SOURCE),
    "engineer-in-designer-session-source": (DESIGNER, ENGINEER, ENGINEER_TICKET, SOURCE),
    "engineer-in-auditor-session-source": (AUDITOR, ENGINEER, ENGINEER_TICKET, SOURCE),
    "engineer-in-engineer-session-source": (ENGINEER, ENGINEER, ENGINEER_TICKET, SOURCE),
    "designer-in-orchestrator-session-acceptance-test": (ORCHESTRATOR, DESIGNER, ENGINEER_TICKET, ACCEPTANCE),
    "designer-in-engineer-session-acceptance-test": (ENGINEER, DESIGNER, ENGINEER_TICKET, ACCEPTANCE),
    "designer-in-designer-session-acceptance-test": (DESIGNER, DESIGNER, ENGINEER_TICKET, ACCEPTANCE),
    "orchestrator-in-engineer-session-own-ticket": (ENGINEER, ORCHESTRATOR, ORCHESTRATOR_TICKET, SETTINGS),
    "product-spec-in-orchestrator-session-own-ticket": (ORCHESTRATOR, PRODUCT_SPEC, PRODUCT_SPEC_TICKET, SPEC),
    "auditor-in-engineer-session-scratch": (ENGINEER, AUDITOR, ENGINEER_TICKET, SCRATCH),
    # DEC-156 (W1-45): moved from ROLE_DENIES; the orchestrator may write SOURCE
    # regardless of the active ticket.  Rewrite: owner correction, DEC-156.
    "orchestrator-in-engineer-session-on-the-engineer-s-ticket": (ENGINEER, ORCHESTRATOR, ENGINEER_TICKET, SOURCE),
}

# The subagent's role does not allow the write, whatever the session's role allows.
ROLE_DENIES = {
    "engineer-in-engineer-session-outside-the-ticket": (ENGINEER, ENGINEER, ENGINEER_TICKET, "README.md"),
    "engineer-in-engineer-session-acceptance-test": (ENGINEER, ENGINEER, ENGINEER_TICKET, ACCEPTANCE),
    "engineer-in-designer-session-acceptance-test": (DESIGNER, ENGINEER, ENGINEER_TICKET, ACCEPTANCE),
    "engineer-in-orchestrator-session-on-the-orchestrator-s-ticket":
        (ORCHESTRATOR, ENGINEER, ORCHESTRATOR_TICKET, SETTINGS),
    "designer-in-engineer-session-source": (ENGINEER, DESIGNER, ENGINEER_TICKET, SOURCE),
    "designer-in-designer-session-source": (DESIGNER, DESIGNER, ENGINEER_TICKET, SOURCE),
    "auditor-in-engineer-session-source": (ENGINEER, AUDITOR, ENGINEER_TICKET, SOURCE),
    # DEC-156 (W1-45): the orchestrator-in-engineer-session case is moved to ROLE_ALLOWS.
    # Rewrite: owner correction, DEC-156.
    "product-spec-in-engineer-session-source": (ENGINEER, PRODUCT_SPEC, ENGINEER_TICKET, SOURCE),
}

# Subagent types that are not one of the five roles: built-in types, and names
# that only look like a role.
NON_ROLE_TYPES = ("general-purpose", "Explore", "Plan", "claude", "Engineer", "engineer-helper", "test-designer")

# name: (GOV_ROLE, GOV_TICKET, path the session's own role may write)
SESSION_WRITES = {
    "engineer-session-source": (ENGINEER, ENGINEER_TICKET, SOURCE),
    "designer-session-acceptance-test": (DESIGNER, ENGINEER_TICKET, ACCEPTANCE),
    "orchestrator-session-own-ticket": (ORCHESTRATOR, ORCHESTRATOR_TICKET, SETTINGS),
    "engineer-session-scratch": (ENGINEER, ENGINEER_TICKET, SCRATCH),
}


def _what(tool_name, relpath, subagent, session_role):
    return f"{tool_name} on {relpath} by subagent {subagent} in a session with GOV_ROLE={session_role!r}"


@pytest.mark.parametrize("case", sorted(ROLE_ALLOWS), ids=sorted(ROLE_ALLOWS))
def test_a_role_subagent_writes_what_its_own_role_allows(project, write, case):
    session_role, subagent_role, ticket, relpath = ROLE_ALLOWS[case]
    for tool_name in ("Edit", "Write"):
        result = write(project, relpath, session_role, ticket, tool_name, subagent=subagent_role)
        support.assert_allowed(result, _what(tool_name, relpath, subagent_role, session_role))


@pytest.mark.parametrize("case", sorted(ROLE_DENIES), ids=sorted(ROLE_DENIES))
def test_a_role_subagent_gets_nothing_from_the_session_s_role(project, write, case):
    session_role, subagent_role, ticket, relpath = ROLE_DENIES[case]
    # The pair is the point of the case: the same subagent, in the same session,
    # is allowed the write its own role covers and denied this one.
    own = {ENGINEER: (ENGINEER_TICKET, SOURCE), DESIGNER: (ENGINEER_TICKET, ACCEPTANCE),
           ORCHESTRATOR: (ORCHESTRATOR_TICKET, SETTINGS), PRODUCT_SPEC: (PRODUCT_SPEC_TICKET, SPEC),
           AUDITOR: (ENGINEER_TICKET, SCRATCH)}[subagent_role]
    result = write(project, own[1], session_role, own[0], "Write", subagent=subagent_role)
    support.assert_allowed(result, _what("Write", own[1], subagent_role, session_role))
    for tool_name in ("Edit", "Write"):
        result = write(project, relpath, session_role, ticket, tool_name, subagent=subagent_role)
        support.assert_denied(result, _what(tool_name, relpath, subagent_role, session_role))


def test_a_role_subagent_s_bash_writes_follow_its_own_role(project, bash):
    to_acceptance = f"echo changed > {ACCEPTANCE}"
    to_source = f"echo changed > {SOURCE}"

    result = bash(project, to_acceptance, ENGINEER, ENGINEER_TICKET, subagent=DESIGNER)
    support.assert_allowed(result, f"Bash `{to_acceptance}` by a test-designer subagent in an engineer session")
    result = bash(project, to_source, ENGINEER, ENGINEER_TICKET, subagent=DESIGNER)
    support.assert_denied(result, f"Bash `{to_source}` by a test-designer subagent in an engineer session")

    result = bash(project, to_source, DESIGNER, ENGINEER_TICKET, subagent=ENGINEER)
    support.assert_allowed(result, f"Bash `{to_source}` by an engineer subagent in a test-designer session")
    result = bash(project, to_acceptance, DESIGNER, ENGINEER_TICKET, subagent=ENGINEER)
    support.assert_denied(result, f"Bash `{to_acceptance}` by an engineer subagent in a test-designer session")

    result = bash(project, to_source, ORCHESTRATOR, ENGINEER_TICKET, subagent=ENGINEER)
    support.assert_allowed(result, f"Bash `{to_source}` by an engineer subagent in an orchestrator session")
    result = bash(project, to_source, ENGINEER, ENGINEER_TICKET, subagent=AUDITOR)
    support.assert_denied(result, f"Bash `{to_source}` by an auditor subagent in an engineer session")


@pytest.mark.parametrize("agent_type", NON_ROLE_TYPES)
@pytest.mark.parametrize("case", sorted(SESSION_WRITES), ids=sorted(SESSION_WRITES))
def test_a_subagent_that_is_not_a_role_stays_read_only(project, write, bash, case, agent_type):
    """DEC-113, kept by DEC-117. The implementation at 7d9ab30 already does this."""
    session_role, ticket, relpath = SESSION_WRITES[case]
    result = write(project, relpath, session_role, ticket, "Write")
    support.assert_allowed(result, f"Write on {relpath} by the main thread of a {session_role} session")
    for tool_name in ("Edit", "Write"):
        result = write(project, relpath, session_role, ticket, tool_name, subagent=agent_type)
        support.assert_denied(result, _what(tool_name, relpath, agent_type, session_role))
    command = f"echo changed > {relpath}"
    result = bash(project, command, session_role, ticket, subagent=agent_type)
    support.assert_denied(result, f"Bash `{command}` by subagent {agent_type} in a {session_role} session")


@pytest.mark.parametrize("agent_type", (AUDITOR, ENGINEER, "general-purpose", "Explore"))
def test_a_subagent_can_still_read(project, call, bash, agent_type):
    result = call(project, "Read", {"file_path": str(project / SOURCE)},
                  role=ENGINEER, ticket=ENGINEER_TICKET, subagent=agent_type)
    support.assert_allowed(result, f"Read by subagent {agent_type} in an engineer session")
    result = bash(project, "ls -la", ENGINEER, ENGINEER_TICKET, subagent=agent_type)
    support.assert_allowed(result, f"Bash `ls -la` by subagent {agent_type} in an engineer session")
