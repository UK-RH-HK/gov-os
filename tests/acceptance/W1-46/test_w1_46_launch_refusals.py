"""W1-46 -- the tickets ``gov launch`` refuses (DEC-242).

DEC-242: "``gov launch`` refuses to launch for an unknown ticket, a ticket that
isn't ``in_progress``, or a ticket of another role. It refuses a research ticket
whose ``allowed_paths`` isn't exactly one experiment folder."

Every refusal is a non-zero exit with a named reason, and nothing is started
(KPI success 1's words for a refusal). Each test first launches the same role on
its own ticket in the same project, so the ticket is the reason.

"A ticket of another role" is tested where the ticket's ``role`` names a worker
role other than the one launched and that role has no work on such a ticket: a
research session on an engineer's ticket, an engineer on a research ticket, an
engineer on an auditor's ticket. The independent test designer is launched on
the engineer's ticket it writes the tests for (MR-3): that launch is in every
other file of this suite. Which other tickets the two independent roles may be
launched on is not tested; see DP-8 in the README.

No session is started.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

ENGINEER, AUDITOR, RESEARCH = support.ENGINEER, support.AUDITOR, support.RESEARCH
FOLDER = support.EXPERIMENT_REL
NEW_TICKET = "DAEO-zz98"

NOT_ONE_EXPERIMENT_FOLDER = {
    "several-entries": (f"{FOLDER}/**", "experiments/spikes/exp-900/**"),
    "no-entry": (),
    "the-whole-repository": ("**",),
    "a-pattern-over-several-folders": ("experiments/spikes/exp-*/**",),
    "a-file": (f"{FOLDER}/README.md",),
}


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


@pytest.mark.parametrize("role, ticket_role", ((RESEARCH, ENGINEER), (ENGINEER, RESEARCH), (ENGINEER, AUDITOR)),
                         ids=("research-on-an-engineers-ticket", "engineer-on-a-research-ticket",
                              "engineer-on-an-auditors-ticket"))
def test_a_ticket_of_another_role_refuses_the_launch(launch, role, ticket_role):
    launch(role).session()
    support.assert_refused(launch(role, support.TICKET_OF[ticket_role]), "role")


@pytest.mark.parametrize("name", sorted(NOT_ONE_EXPERIMENT_FOLDER))
def test_a_research_ticket_that_is_not_exactly_one_experiment_folder_refuses_the_launch(launch, project, name):
    """Several entries, none, or an entry that is not one experiment folder: no fence can be generated from it."""
    launch(RESEARCH).session()
    ticket = support.write_ticket(project, NEW_TICKET, RESEARCH, allowed_paths=NOT_ONE_EXPERIMENT_FOLDER[name])
    support.assert_refused(launch(RESEARCH, ticket), "allowed_paths", "experiment folder")


def test_a_second_research_ticket_with_one_experiment_folder_is_launched(launch, project, sandbox):
    """The control of the cases above: one folder, another one, and the fence follows the ticket."""
    ticket = support.write_ticket(project, NEW_TICKET, RESEARCH, allowed_paths=("experiments/spikes/exp-900/**",))
    result = launch(RESEARCH, ticket)
    assert result.run.returncode == 0, f"gov launch refused a research ticket with one folder\n{result.describe()}"
    assert not support.edit_denied(result, "experiments/spikes/exp-900/data.txt", project, sandbox)
    assert support.edit_denied(result, f"{FOLDER}/README.md", project, sandbox), (
        "the fence of a research session on another ticket leaves the first ticket's folder open"
    )
