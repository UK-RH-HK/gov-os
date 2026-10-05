"""KPI success 2, first half [CAP-05.b], with the record and the repeat of KPI success 3 [CAP-05.d].

"gov pause --cancel-agents releases every claim and records the cancelled
sessions" (CANCEL_AGENTS).

A claim is the lock ``.tickets/.claims/<ticket id>`` naming its holder, by
convention ``<role>:<session>`` (DEC-292, ``gov.tasks``). The claims are made
and read through ``gov.tasks``.

- **DEC-357.** The command releases the locks and nothing else: no ticket's
  ``status`` changes. It cannot stop a process.
- **DEC-368.** It also sets the freeze flag.
- **DEC-367.** The record is a commit to the ticket file, with the trailers
  ``Task: <ticket>`` and ``Reverts-Task: <ticket>``.
- **DEC-375.** One record commit per released ticket: it changes that
  ticket's file alone and carries that ticket's two trailers and no other
  ticket's; the file then names the session that held the claim. A cancel
  that releases nothing makes no commit (confirmed by DEC-378).
- **The result** lists what was released as ``cancelled``, each entry with the
  ``ticket`` and its ``holder`` (the shape ``gov.tasks.release`` returns).
- **On repeat** (DEC-357) nothing is held any more: the repeat succeeds and
  leaves the project as the first run did, so it makes no commit. A first run
  that finds no claim is in the same position.
"""

from __future__ import annotations

import w1_28_support as support


def _cancel(pause, interface):
    return support.succeeded(pause("--cancel-agents"), interface)


def test_cancel_agents_releases_every_claim(project, sandbox, pause, interface, claims):
    assert support.locks(project) == sorted(claims), "the fixture claims were not made"
    _cancel(pause, interface)
    for ticket in claims:
        assert support.tasks(project, sandbox, "holder", ticket) is None, f"{ticket} is still claimed"
    assert support.locks(project) == [], f"locks are left in {support.CLAIMS_REL}: {support.locks(project)}"


def test_a_released_ticket_can_be_claimed_again(project, sandbox, pause, interface, claims):
    _cancel(pause, interface)
    again = support.tasks(project, sandbox, "claim", support.TICKET, "engineer:w1-28-session-c")
    assert again == {"ticket": support.TICKET, "holder": "engineer:w1-28-session-c"}, again


def test_the_result_names_each_cancelled_session(pause, interface, claims):
    result = _cancel(pause, interface)
    cancelled = support.listed(result, "cancelled")
    found = sorted((entry.get("ticket"), entry.get("holder")) for entry in cancelled if isinstance(entry, dict))
    assert found == sorted(claims.items()), f"`cancelled` is not the released claims, each once: {cancelled}"


def test_cancel_agents_sets_the_freeze_flag(project, sandbox, pause, interface, claims):
    """DEC-368. A session whose claim was released keeps running: the guard now denies its writes."""
    assert not support.is_paused(project)
    _cancel(pause, interface)
    assert support.flag(project).is_file(), f"gov pause --cancel-agents did not set {support.FREEZE_FLAG_REL}"
    support.assert_denied(support.guard_write(project, sandbox, support.ENGINEER), "after --cancel-agents, the write")


def test_the_cancel_is_recorded_by_one_commit_per_released_ticket(project, pause, interface, claims):
    """DEC-367, DEC-375. The commits are made while the freeze the same call set is in force (DEC-368)."""
    before = support.head(project)
    _cancel(pause, interface)
    made = support.new_commits(project, before)
    assert len(made) == len(claims), \
        f"{len(claims)} claims were released and the cancel made {len(made)} commits, not one per released ticket"
    recorded = {}
    for commit in made:
        changed = support.changed_paths(project, commit)
        tickets = [ticket for ticket in claims if changed == [support.ticket_rel(ticket)]]
        assert len(tickets) == 1, \
            f"the commit {commit[:support.SHORT]} of the cancel changes {changed}, not one released ticket's file alone"
        ticket = tickets[0]
        assert ticket not in recorded, f"two commits of the cancel record {ticket}"
        recorded[ticket] = commit
        for key in ("Task", "Reverts-Task"):
            assert support.trailers(project, commit, key) == [ticket], \
                f"the commit {commit[:support.SHORT]} to {support.ticket_rel(ticket)} has not the one trailer " \
                f"`{key}: {ticket}`:\n{support.message(project, commit)}"
    assert sorted(recorded) == sorted(claims)
    assert support.porcelain(project) == "", f"the cancel left uncommitted changes:\n{support.porcelain(project)}"
    assert support.is_paused(project)


def test_a_cancel_that_releases_one_claim_makes_one_commit(project, sandbox, pause, interface):
    """DEC-375, the smallest case: one claim, one record commit, and no other ticket's file is touched."""
    support.tasks(project, sandbox, "claim", support.OTHER_TICKET, support.OTHER_HOLDER)
    before, untouched = support.head(project), support.ticket_file(project, support.TICKET)
    result = _cancel(pause, interface)
    assert len(support.listed(result, "cancelled")) == 1, result
    made = support.new_commits(project, before)
    assert len(made) == 1, f"one claim was released and the cancel made {len(made)} commits"
    assert support.changed_paths(project, made[0]) == [support.ticket_rel(support.OTHER_TICKET)]
    assert support.trailers(project, made[0], "Task") == [support.OTHER_TICKET]
    assert support.trailers(project, made[0], "Reverts-Task") == [support.OTHER_TICKET]
    assert support.ticket_file(project, support.TICKET) == untouched, "the file of a ticket nobody held changed"


def test_each_cancelled_session_is_recorded_in_its_ticket(project, pause, interface, claims):
    """KPI: "records the cancelled sessions". DEC-357: the ticket's status is not changed."""
    before = {ticket: support.ticket_file(project, ticket) for ticket in claims}
    _cancel(pause, interface)
    for ticket, holder in claims.items():
        text = support.committed(project, support.ticket_rel(ticket))
        assert text != before[ticket], f"{support.ticket_rel(ticket)} is unchanged in HEAD: nothing was recorded"
        assert holder in text, f"{support.ticket_rel(ticket)} does not name the cancelled session {holder}"
        other = next(name for name in claims.values() if name != holder)
        assert other not in text, f"{support.ticket_rel(ticket)} names {other}, which held another ticket"
        assert support.status_line(text) == support.status_line(before[ticket]), \
            f"the cancel changed the status of {ticket}: {support.status_line(text)}"


def test_cancel_agents_with_no_claim_succeeds_and_releases_nothing(project, pause, interface):
    """Nothing is released, so nothing is recorded; the freeze is set all the same (DEC-368)."""
    before, tickets = support.head(project), support.ticket_files(project)
    result = _cancel(pause, interface)
    assert support.listed(result, "cancelled") == []
    assert support.locks(project) == []
    assert support.head(project) == before, "a cancel that released nothing made a commit"
    assert support.ticket_files(project) == tickets, "a cancel that released nothing changed a ticket file"
    assert support.is_paused(project), f"gov pause --cancel-agents did not set {support.FREEZE_FLAG_REL}"


def test_cancel_agents_gives_the_same_result_on_repeat(project, sandbox, pause, interface, claims):
    """DEC-357: the repeat succeeds and leaves the project as the first run did."""
    _cancel(pause, interface)
    after, tickets = support.head(project), support.ticket_files(project)
    result = _cancel(pause, interface)
    assert support.listed(result, "cancelled") == [], f"the repeat released something: {result}"
    assert support.locks(project) == [], f"claims after the repeat: {support.locks(project)}"
    for ticket in claims:
        assert support.tasks(project, sandbox, "holder", ticket) is None, f"{ticket} is claimed after the repeat"
    assert support.head(project) == after, "the repeat made a commit"
    assert support.ticket_files(project) == tickets, "the repeat changed a ticket file"
    assert support.porcelain(project) == "", f"the repeat left changes:\n{support.porcelain(project)}"
    assert support.is_paused(project), "the repeat cleared the flag"
