"""W1-46 -- the tickets ``gov launch`` refuses (DEC-242).

DEC-242: "``gov launch`` refuses to launch for an unknown ticket, a ticket that
isn't ``in_progress``, or a ticket of another role. It refuses a research ticket
whose ``allowed_paths`` isn't exactly one experiment folder." Emergency 2
(docs/emergency-2/EMERGENCY-2.md 2.2, 6.1; release 0.1.2) removed the research
fence the experiment folder was built for: the launcher no longer checks a research
ticket's folder, and those two cases are retired. The ticket refusals stay.

Every refusal is a non-zero exit with a named reason, and nothing is started
(KPI success 1's words for a refusal). Each test first launches the same role on
its own ticket in the same project, so the ticket is the reason.

"A ticket of another role" is tested where the ticket's ``role`` names a worker
role other than the one launched and that role has no work on such a ticket: a
research session on an engineer's ticket, an engineer on a research ticket, an
engineer on an auditor's ticket. The independent test designer is launched on
the engineer's ticket it writes the tests for (MR-3): that launch is in every
other file of this suite.

DEC-271 (batch 4, on DP-8): "``gov launch`` starts an engineer or a research
session only on a ticket of its own role. An independent test designer and an
independent auditor are launched on any ticket that is ``in_progress``: their
work is always on another role's ticket."

No session is started.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

ENGINEER, AUDITOR, RESEARCH = support.ENGINEER, support.AUDITOR, support.RESEARCH
TEST_DESIGNER = support.TEST_DESIGNER
NEW_TICKET = "DAEO-zz98"


@pytest.mark.parametrize("role", (ENGINEER, RESEARCH))
def test_an_unknown_ticket_refuses_the_launch(launch, role):
    launch(role).session()
    support.assert_refused(launch(role, "DAEO-zz00"), "ticket")


@pytest.mark.parametrize("status", ("open", "closed"))
def test_a_ticket_that_is_not_in_progress_refuses_the_launch(launch, project, status):
    launch(ENGINEER).session()
    ticket = support.write_ticket(project, NEW_TICKET, ENGINEER, status=status)
    support.assert_refused(launch(ENGINEER, ticket), "in_progress", "status", status)


def test_the_same_ticket_in_progress_is_launched(launch, project):
    """The control of the two cases above: the status is the only difference."""
    ticket = support.write_ticket(project, NEW_TICKET, ENGINEER)
    result = launch(ENGINEER, ticket)
    assert result.run.returncode == 0, f"gov launch refused a ticket in progress\n{result.describe()}"
    assert result.variable("GOV_TICKET") == ticket


@pytest.mark.parametrize("role, ticket_role", ((RESEARCH, ENGINEER), (ENGINEER, RESEARCH), (ENGINEER, AUDITOR),
                                               (RESEARCH, AUDITOR)),
                         ids=("research-on-an-engineers-ticket", "engineer-on-a-research-ticket",
                              "engineer-on-an-auditors-ticket", "research-on-an-auditors-ticket"))
def test_a_ticket_of_another_role_refuses_the_launch(launch, role, ticket_role):
    launch(role).session()
    support.assert_refused(launch(role, support.TICKET_OF[ticket_role]), "role")


@pytest.mark.parametrize("role", (TEST_DESIGNER, AUDITOR))
@pytest.mark.parametrize("ticket_role", (ENGINEER, AUDITOR, RESEARCH))
def test_the_two_independent_roles_are_launched_on_a_ticket_of_any_role(launch, role, ticket_role):
    """DEC-271: "on any ticket that is ``in_progress``". The session is that role's, on that ticket."""
    ticket = support.TICKET_OF[ticket_role]
    result = launch(role, ticket)
    assert result.run.returncode == 0, (
        f"gov launch refused a {role} on a ticket of the role {ticket_role}\n{result.describe()}"
    )
    assert (result.variable("GOV_ROLE"), result.variable("GOV_TICKET")) == (role, ticket)


@pytest.mark.parametrize("role", (TEST_DESIGNER, AUDITOR))
@pytest.mark.parametrize("status", ("open", "closed"))
def test_the_two_independent_roles_are_refused_a_ticket_that_is_not_in_progress(launch, project, role, status):
    """DEC-271: "any ticket that is ``in_progress``", and no other."""
    launch(role).session()
    ticket = support.write_ticket(project, NEW_TICKET, ENGINEER, status=status)
    support.assert_refused(launch(role, ticket), "in_progress", "status", status)
