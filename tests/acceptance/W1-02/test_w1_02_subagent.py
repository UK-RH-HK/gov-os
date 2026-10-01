"""W1-02 — a subagent named in the hook input: the stricter of the two roles applies.

Owner answer to KD-1: "If the hook input also identifies a subagent, the guard
applies the stricter of the two."

The harness does carry such a field. Inside a subagent, the PreToolUse stdin
object holds ``agent_id`` and ``agent_type``; ``agent_type`` is the name of the
subagent definition (checked in the hook input schema of the installed harness,
version 2.1.286). Role subagents are named after their role (ADR-0002 L1).

"Stricter" is tested as: a write passes only if the session's role (``GOV_ROLE``)
and the subagent's role would each allow it. A subagent type that is not one of
the five roles, such as ``general-purpose``, is open (KD-7) and is not tested.
"""

from __future__ import annotations

import pytest

import w1_02_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
DESIGNER = support.TEST_DESIGNER
AUDITOR = support.AUDITOR
TICKET = support.TICKET_ID

SOURCE = "src/gov/guard/decide.py"
ACCEPTANCE = f"tests/acceptance/{support.TICKET_WBS_ID}/test_fixture.py"

# name: (GOV_ROLE, agent_type, repository-relative path, allowed)
CASES = {
    "engineer-in-engineer-session-inside-the-ticket": (ENGINEER, ENGINEER, SOURCE, True),
    "engineer-in-engineer-session-outside-the-ticket": (ENGINEER, ENGINEER, "README.md", False),
    "engineer-in-engineer-session-acceptance-test": (ENGINEER, ENGINEER, ACCEPTANCE, False),
    "designer-in-designer-session-acceptance-test": (DESIGNER, DESIGNER, ACCEPTANCE, True),
    "designer-in-designer-session-source": (DESIGNER, DESIGNER, SOURCE, False),
    "auditor-in-engineer-session-source": (ENGINEER, AUDITOR, SOURCE, False),
    "orchestrator-in-engineer-session-source": (ENGINEER, ORCHESTRATOR, SOURCE, False),
    "designer-in-engineer-session-source": (ENGINEER, DESIGNER, SOURCE, False),
    "designer-in-engineer-session-acceptance-test": (ENGINEER, DESIGNER, ACCEPTANCE, False),
    "engineer-in-designer-session-acceptance-test": (DESIGNER, ENGINEER, ACCEPTANCE, False),
    "engineer-in-designer-session-source": (DESIGNER, ENGINEER, SOURCE, False),
    "engineer-in-auditor-session-source": (AUDITOR, ENGINEER, SOURCE, False),
    "engineer-in-role-less-session-source": (None, ENGINEER, SOURCE, False),
    "engineer-in-unknown-role-session-source": ("developer", ENGINEER, SOURCE, False),
    "designer-in-role-less-session-acceptance-test": (None, DESIGNER, ACCEPTANCE, False),
}


@pytest.mark.parametrize("case", sorted(CASES), ids=sorted(CASES))
def test_the_stricter_of_session_role_and_subagent_role_applies(project, write, case):
    session_role, subagent_role, relpath, allowed = CASES[case]
    for tool_name in ("Edit", "Write"):
        result = write(project, relpath, session_role, TICKET, tool_name, subagent=subagent_role)
        what = f"{tool_name} on {relpath} by subagent {subagent_role} in a session with GOV_ROLE={session_role!r}"
        if allowed:
            support.assert_allowed(result, what)
        else:
            support.assert_denied(result, what)


def test_a_subagent_cannot_widen_the_session_s_bash_writes(project, bash):
    command = f"echo changed > {ACCEPTANCE}"
    result = bash(project, command, ENGINEER, TICKET, subagent=DESIGNER)
    support.assert_denied(result, f"Bash `{command}` by a test-designer subagent in an engineer session")
    command = f"echo changed > {SOURCE}"
    result = bash(project, command, ENGINEER, TICKET, subagent=AUDITOR)
    support.assert_denied(result, f"Bash `{command}` by an auditor subagent in an engineer session")
    result = bash(project, command, ENGINEER, TICKET, subagent=ENGINEER)
    support.assert_allowed(result, f"Bash `{command}` by an engineer subagent in an engineer session")


def test_a_subagent_can_still_read(project, call):
    result = call(project, "Read", {"file_path": str(project / SOURCE)},
                  role=ENGINEER, ticket=TICKET, subagent=AUDITOR)
    support.assert_allowed(result, "Read by an auditor subagent in an engineer session")
