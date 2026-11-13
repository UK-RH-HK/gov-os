"""KPI failure 2: any session but the CTO's asked or let through, in the adopted planted repository (Interface I3).

An engineer, an independent-test-designer, an independent-auditor and an orchestrator on another ticket each attempt
an install: each is refused (the hook's decision ``deny``), none is asked, none let through. Their tickets are planted
before adoption and exist in ``.tickets/``; the orchestrator's other ticket is ``DAEO-1ead``.

On the base the refusals already hold (the key is absent, so every session is refused): the cases on the sessions'
own tickets are green there, and guard against an implementation that asks too many. The cases that put a worker on
the new coordination ticket need its id, which the base does not create: they are red there for that reason.
"""

from __future__ import annotations

import pytest

import w2_113_support as support
from w2_113_support import w110

Session = w110.Session
WORKERS = (w110.ENGINEER, w110.TEST_DESIGNER, w110.AUDITOR)
OWN = {w110.ENGINEER: support.ENGINEERING.id, w110.TEST_DESIGNER: support.ENGINEERING.id,
       w110.AUDITOR: support.AUDIT.id}


def assert_refused(answer, who, command=support.INSTALL):
    assert answer.decision == "deny", (
        f"{who}'s `{command}` in the adopted repository must be refused; it was {answer.decision} "
        f"(never asked, never let through): {answer.describe()}")


@pytest.mark.parametrize("role", WORKERS)
@pytest.mark.parametrize("command", support.INSTALLS)
def test_a_worker_on_its_own_ticket_is_refused(adoption, decide, role, command):
    support.assert_succeeded(adoption("standard"))
    assert_refused(decide(Session(f"{role}-on-its-own-ticket", role, OWN[role]), command), role, command)


def test_an_orchestrator_on_another_ticket_is_refused(adoption, decide):
    adopted = adoption("standard")
    support.assert_succeeded(adopted)
    other = support.OTHER
    assert f"{other.id}.md" in support.ticket_files(adopted.project), f"{other.id} does not exist in .tickets/"
    for ticket in (other.id, other.wbs):     # by id, and by WBS id
        assert_refused(decide(w110.cto(ticket, f"orchestrator-on-{ticket}")), f"the orchestrator on {ticket}")


@pytest.mark.parametrize("command", support.INSTALLS)
def test_an_orchestrator_on_another_ticket_is_refused_for_every_install(adoption, decide, command):
    support.assert_succeeded(adoption("standard"))
    assert_refused(decide(w110.cto(support.OTHER.id, "second-orchestrator"), command),
                   f"the orchestrator on {support.OTHER.id}", command)


def test_an_orchestrator_with_no_ticket_is_refused(adoption, decide):
    support.assert_succeeded(adoption("standard"))
    assert_refused(decide(w110.cto(None, "orchestrator-without-a-ticket")), "the orchestrator with no GOV_TICKET")


@pytest.mark.parametrize("role", WORKERS)
def test_a_worker_on_the_coordination_ticket_is_refused(adoption, decide, role):
    """The key names the ticket, but only the orchestrator's session on it is the CTO's."""
    adopted = adoption("standard")
    support.assert_succeeded(adopted)
    ticket = adopted.new_ticket()
    assert_refused(decide(Session(f"{role}-on-the-coordination-ticket", role, ticket)), f"the {role} on {ticket}")


def test_an_orchestrator_subagent_in_a_worker_s_session_is_refused(adoption, decide):
    adopted = adoption("standard")
    support.assert_succeeded(adopted)
    ticket = adopted.new_ticket()
    session = Session("orchestrator-subagent-in-an-engineer-s-session", w110.ENGINEER, ticket, w110.ORCHESTRATOR)
    assert_refused(decide(session), "an orchestrator subagent in an engineer's session on the coordination ticket")
