"""KPI success 3, first half [CAP-05.b], with the record of KPI success 4 [CAP-05.d].

"gov pause --cancel-agents releases every claim and records the cancelled
sessions" (CANCEL_AGENTS).

A claim is the lock ``.tickets/.claims/<ticket id>`` naming its holder, by
convention ``<role>:<session>`` (DEC-292, ``gov.tasks``). The claims are made
and read through ``gov.tasks``. The command cannot stop a process: what it
leaves is that no lock is held, and a record of who held each.

Decision packages: where the record is written and its shape are DP-6. These
cases follow its recommended option in the weakest form: the holder of a
released claim is named in the command's result and in that ticket's file.
Whether a ticket's ``status`` changes (DP-4) and whether ``--cancel-agents``
also sets the flag (DP-8) are asserted nowhere.
"""

from __future__ import annotations

import w1_28_support as support


def test_cancel_agents_releases_every_claim(project, sandbox, pause, interface, claims):
    assert support.locks(project) == sorted(claims), "the fixture claims were not made"
    support.succeeded(pause("--cancel-agents"), interface)
    for ticket in claims:
        assert support.tasks(project, sandbox, "holder", ticket) is None, f"{ticket} is still claimed"
    assert support.locks(project) == [], f"locks are left in {support.CLAIMS_REL}: {support.locks(project)}"


def test_a_released_ticket_can_be_claimed_again(project, sandbox, pause, interface, claims):
    support.succeeded(pause("--cancel-agents"), interface)
    again = support.tasks(project, sandbox, "claim", support.TICKET, "engineer:w1-28-session-c")
    assert again == {"ticket": support.TICKET, "holder": "engineer:w1-28-session-c"}, again


def test_the_result_names_each_cancelled_session(pause, interface, claims):
    said = support.text_of(support.succeeded(pause("--cancel-agents"), interface))
    for ticket, holder in claims.items():
        assert ticket in said, f"the result does not name the ticket {ticket}: {said}"
        assert holder in said, f"the result does not name the cancelled session {holder}: {said}"


def test_each_cancelled_session_is_recorded_in_its_ticket(project, pause, interface, claims):
    """DP-6, recommended option: the record is in the ticket's file."""
    before = {ticket: support.ticket_file(project, ticket) for ticket in claims}
    support.succeeded(pause("--cancel-agents"), interface)
    for ticket, holder in claims.items():
        text = support.ticket_file(project, ticket)
        assert text != before[ticket], f".tickets/{ticket}.md is unchanged: nothing was recorded in the ticket"
        assert holder in text, f".tickets/{ticket}.md does not name the cancelled session {holder}"
        other = next(name for name in claims.values() if name != holder)
        assert other not in text, f".tickets/{ticket}.md names {other}, which held another ticket"


def test_cancel_agents_with_no_claim_succeeds_and_releases_nothing(project, pause, interface):
    support.succeeded(pause("--cancel-agents"), interface)
    assert support.locks(project) == []


def test_cancel_agents_gives_the_same_result_on_repeat(project, sandbox, pause, interface, claims):
    """KPI success 4, "the same result on repeat" (DP-7: the state after the repeat is the state after the first)."""
    support.succeeded(pause("--cancel-agents"), interface)
    support.succeeded(pause("--cancel-agents"), interface)
    assert support.locks(project) == [], f"claims after the repeat: {support.locks(project)}"
    for ticket in claims:
        assert support.tasks(project, sandbox, "holder", ticket) is None, f"{ticket} is claimed after the repeat"
