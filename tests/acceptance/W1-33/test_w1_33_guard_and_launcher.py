"""W1-33 -- what the definitions state is what the launcher decides.

A role definition grants nothing by itself: the launcher decides which roles it starts. This test asks it, in a
temporary copy of the project, for the decision the KPI lines state. No session is started and no call is made.

Rewrite-Reason: EMERGENCY-2 6.1 (the guard / the sandbox retired), DAEO-gr7t. The cases that asked the guard for a
role's write scope and the install rule, and the case that read the launcher's empty network profile (the sandbox's),
are deleted with the guard and the sandbox, with the fixtures only they used (the generated project and its guard
line). The launcher's refusal of a role that is not a worker stays, on the conftest's fixtures.
"""

from __future__ import annotations

import pytest

import w1_33_support as support

launch_support = support.launch_support


def _ready_list_without(project, ticket):
    """Plant an approved ready list whose one batch holds another ticket, never ``ticket`` (W2-136's form)."""
    other = launch_support.TICKET_OF[support.ENGINEER]
    assert other != ticket
    launch_support.write(project, support.READY_REL,
                         "# the approved ready list (planted for the W1-33 launcher case)\n"
                         f"# batch 1\nW1-98 {other} W1-98-A5-plan.md W1-98-A5-plan.json\n")


@pytest.mark.parametrize("ready", ["no ready list", "a ready list without the ticket"])
@pytest.mark.parametrize("role", support.NOT_LAUNCHED)
def test_the_launcher_starts_no_session_for_a_role_that_is_not_a_worker(launch, project, role, ready):
    """Rewritten for DEC-1088 (5)(a) (W2-136 S9). The orchestrator on a ticket is a lead launch, no longer refused as
    "not a worker role". Outside an approved ready list it starts no session, and the refusal names the ticket and
    the ready list. The gate is planted open, so the refusal is the lead check's, not the gate's."""
    ticket = support.w47.TICKET_OF[role]
    if ready != "no ready list":
        _ready_list_without(project, ticket)
    result = launch(role, ticket)
    launch_support.assert_refused(result, *support.LEAD_REFUSAL_WORDS)
    said = result.run.stderr + "\n" + result.run.stdout
    assert ticket in said, f"the refusal does not name the ticket {ticket}\n{result.describe()}"
