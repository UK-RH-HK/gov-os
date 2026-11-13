"""KPI success 1, its other half, and failure 1 ("A lead's or a worker's install in a generated project asked or
allowed").

With the coordination ticket set, every session that is not the CTO's is refused, and the refusal tells it to raise
the install as a P1 escalation to the CTO, who asks the owner, as this repository's own hook does after DEC-957 (rule
4 of ``.claude/hooks/pretooluse.py``): a lead (the orchestrator on another ticket), an orchestrator with no ticket,
every other role, a session with no role, a role subagent of another type in the CTO's session, and an orchestrator
subagent in any session that is not the CTO's (DEC-971 item 4).
"""

from __future__ import annotations

import pytest

import w2_110_support as support
from w2_110_support import (COORDINATION, ENGINEER, ENGINEERING, MISSING_TICKET_ID, ORCHESTRATOR, OTHER_ORCHESTRATION,
                            OTHER_ROLES, OWN_TICKET, RESEARCH, TEST_DESIGNER, THIS_REPOSITORYS_ID, Session)
from w1_04_support import command_id


def assert_refused_and_escalated(answer, command, who):
    assert answer.decision == "deny", (
        f"`{command}` by {who} was {answer.decision}, not refused: only the CTO's session is asked (DEC-957, "
        f"DEC-971 item 4): {answer.describe()}")
    assert support.tells_to_escalate(answer.reason), (
        f"the refusal of `{command}` by {who} does not tell it to raise the install as a P1 escalation to the CTO "
        f"(DEC-957): {answer.reason!r}")


LEADS_AND_OTHER_ORCHESTRATORS = [
    Session("lead-on-an-engineer-s-ticket", ORCHESTRATOR, ENGINEERING.id),
    Session("lead-on-an-engineer-s-ticket-by-wbs-id", ORCHESTRATOR, ENGINEERING.wbs),
    Session("orchestrator-on-another-orchestration-ticket", ORCHESTRATOR, OTHER_ORCHESTRATION.id),
    Session("orchestrator-on-the-product-s-W2-00-ticket", ORCHESTRATOR, THIS_REPOSITORYS_ID.id),
    Session("orchestrator-on-the-product-s-W2-00-ticket-by-wbs-id", ORCHESTRATOR, THIS_REPOSITORYS_ID.wbs),
    Session("orchestrator-without-a-ticket", ORCHESTRATOR, None),
    Session("orchestrator-with-an-empty-ticket", ORCHESTRATOR, ""),
    Session("orchestrator-on-a-ticket-the-product-does-not-have", ORCHESTRATOR, MISSING_TICKET_ID),
]
OTHER_ROLE_SESSIONS = (
    [Session(f"{role}-on-its-own-ticket", role, OWN_TICKET[role].id) for role in OTHER_ROLES]
    + [Session(f"{role}-on-the-coordination-ticket", role, COORDINATION.id) for role in OTHER_ROLES])
NO_ROLE_SESSIONS = [
    Session("no-role-on-the-coordination-ticket", None, COORDINATION.id),
    Session("empty-role-on-the-coordination-ticket", "", COORDINATION.id),
    Session("unknown-role-owner-on-the-coordination-ticket", "owner", COORDINATION.id),
    Session("no-role-and-no-ticket", None, None),
]
SUBAGENTS_IN_THE_CTO_S_SESSION = [
    Session(f"{subagent}-subagent-in-the-cto-s-session", ORCHESTRATOR, COORDINATION.id, subagent)
    for subagent in (*OTHER_ROLES, "general-purpose", "Explore")]
ORCHESTRATOR_SUBAGENTS_ELSEWHERE = [
    Session("orchestrator-subagent-in-a-lead-s-session", ORCHESTRATOR, ENGINEERING.id, ORCHESTRATOR),
    Session("orchestrator-subagent-in-an-orchestrator-session-without-a-ticket", ORCHESTRATOR, None, ORCHESTRATOR),
    Session("orchestrator-subagent-in-an-engineer-s-session", ENGINEER, ENGINEERING.id, ORCHESTRATOR),
    Session("orchestrator-subagent-in-an-engineer-s-session-on-the-coordination-ticket", ENGINEER,
            COORDINATION.id, ORCHESTRATOR),
    Session("orchestrator-subagent-in-a-test-designer-s-session-on-the-coordination-ticket", TEST_DESIGNER,
            COORDINATION.id, ORCHESTRATOR),
    Session("orchestrator-subagent-in-a-session-without-a-role-on-the-coordination-ticket", None,
            COORDINATION.id, ORCHESTRATOR),
]
EVERY_OTHER_SESSION = (LEADS_AND_OTHER_ORCHESTRATORS + OTHER_ROLE_SESSIONS + NO_ROLE_SESSIONS
                       + SUBAGENTS_IN_THE_CTO_S_SESSION + ORCHESTRATOR_SUBAGENTS_ELSEWHERE)


@pytest.mark.parametrize("session", EVERY_OTHER_SESSION, ids=str)
def test_every_session_but_the_cto_s_is_refused_and_told_to_escalate(ask, session):
    assert_refused_and_escalated(ask("key-by-id", session), support.INSTALL, session.name)


LEAD = LEADS_AND_OTHER_ORCHESTRATORS[0]
WORKER = OTHER_ROLE_SESSIONS[0]   # the engineer on its own ticket


@pytest.mark.parametrize("command", support.INSTALLS, ids=[command_id(c) for c in support.INSTALLS])
@pytest.mark.parametrize("session", [LEAD, WORKER], ids=str)
def test_every_install_of_a_lead_and_of_a_worker_is_refused(ask, session, command):
    assert_refused_and_escalated(ask("key-by-id", session, command), command, session.name)


@pytest.mark.parametrize("mode", support.PROMPT_SKIPPING_MODES)
def test_a_lead_is_refused_in_the_modes_that_skip_prompts(ask, mode):
    assert_refused_and_escalated(ask("key-by-id", LEAD, support.INSTALL, mode), support.INSTALL,
                                 f"{LEAD.name} in mode {mode}")


@pytest.mark.parametrize("session", [LEAD, LEADS_AND_OTHER_ORCHESTRATORS[3], LEADS_AND_OTHER_ORCHESTRATORS[5],
                                     ORCHESTRATOR_SUBAGENTS_ELSEWHERE[2]], ids=str)
def test_with_the_key_by_wbs_id_the_others_are_refused_too(ask, session):
    assert_refused_and_escalated(ask("key-by-wbs", session), support.INSTALL, session.name)


@pytest.mark.parametrize("session", [
    Session("orchestrator-on-the-first-coordination-ticket", ORCHESTRATOR, COORDINATION.id),
    Session("orchestrator-on-the-first-coordination-ticket-by-wbs-id", ORCHESTRATOR, COORDINATION.wbs),
    Session("orchestrator-on-the-product-s-W2-00-ticket", ORCHESTRATOR, THIS_REPOSITORYS_ID.id),
], ids=str)
def test_when_the_key_names_another_ticket_the_others_are_refused(ask, session):
    """The key, not the code, names the CTO: with it naming ``DAEO-1ead``, the orchestrator on ``DAEO-c0rd`` is a
    lead like any other (its asked counterpart is in ``test_w2_110_cto_asked.py``)."""
    assert_refused_and_escalated(ask("key-names-another-ticket", session), support.INSTALL, session.name)


def test_a_research_session_outside_its_experiment_folder_is_refused_and_told_to_escalate(ask):
    """The research role's exception is only inside its experiment folder (DEC-163); from the project's root its
    install is refused like any worker's (inside the folder: ``test_w2_110_unchanged.py``)."""
    session = Session("research-outside-its-experiment-folder", RESEARCH, OWN_TICKET[RESEARCH].id, cwd_rel="src/app")
    assert_refused_and_escalated(ask("key-by-id", session), support.INSTALL, session.name)
