"""KPI success 2 [CAP-23.a] and failure 1: the exclusive claim lock.

"A second claim on a held ticket fails with the holder named (O_EXCL lock in
.tickets/.claims/)" and "Two agents hold the same claim" must never happen.

Every call is made in a new process, so a claim is always tested against a
holder whose process has ended: a claim lasts until it is released.
"""

from __future__ import annotations

import pytest

import w1_09_support as support

TICKET, OTHER = "TST-a001", "TST-a002"
FIRST, SECOND = "engineer:session-1", "engineer:session-2"


@pytest.fixture()
def tickets(project):
    project.ticket(TICKET, "W9-01")
    project.ticket(OTHER, "W9-02")
    project.settle()
    return project


# ---- a claim

def test_a_claim_on_a_free_ticket_names_the_ticket_and_its_holder(tickets):
    outcome = tickets.claim(TICKET, FIRST)
    assert outcome.ok, f"a claim on a free ticket failed: {outcome.describe()}"
    assert isinstance(outcome.value, dict) and outcome.value.get("ticket") == TICKET \
        and outcome.value.get("holder") == FIRST, f"claim did not return the ticket and its holder: {outcome.value!r}"


def test_a_claim_is_a_lock_file_in_the_claims_folder(tickets):
    """The lock is ``.tickets/.claims/<ticket id>``, it names the holder, and the claim adds no other file."""
    before = support.tree(tickets.root)
    assert tickets.claim(TICKET, FIRST).ok
    lock = tickets.lock(TICKET)
    assert lock.is_file() and not lock.is_symlink(), f"the claim left no lock file {support.CLAIMS_REL}/{TICKET}"
    assert FIRST in lock.read_text(encoding="utf-8"), "the lock file does not name the holder"
    added = sorted(set(support.tree(tickets.root)) - set(before) - {support.CLAIMS_REL})
    assert added == [f"{support.CLAIMS_REL}/{TICKET}"], f"the claim added other files: {added}"


def test_the_holder_of_a_ticket_is_reported(tickets):
    assert tickets.holder(TICKET) is None, "a ticket nobody claimed has a holder"
    assert tickets.claim(TICKET, FIRST).ok
    assert tickets.holder(TICKET) == FIRST
    assert tickets.holder(OTHER) is None, "a claim on one ticket gave another ticket a holder"


# ---- a second claim

def test_a_second_claim_on_a_held_ticket_fails_with_the_holder_named(tickets):
    assert tickets.claim(TICKET, FIRST).ok
    second = tickets.claim(TICKET, SECOND)
    details = support.assert_error(second, support.CLAIM_HELD, "a second claim on a held ticket")
    assert details.get("holder") == FIRST, f"the collision error does not name the holder: {second.error!r}"
    assert details.get("ticket") == TICKET, f"the collision error does not name the ticket: {second.error!r}"
    assert FIRST in second.error["message"], f"the collision message does not name the holder: {second.error!r}"


def test_a_failed_claim_leaves_the_first_claim_as_it_was(tickets):
    assert tickets.claim(TICKET, FIRST).ok
    lock = tickets.lock(TICKET).read_bytes()
    assert not tickets.claim(TICKET, SECOND).ok
    assert tickets.holder(TICKET) == FIRST, "the second claim took the ticket from its holder"
    assert tickets.lock(TICKET).read_bytes() == lock, "the second claim rewrote the lock file"


def test_claims_on_different_tickets_do_not_collide(tickets):
    assert tickets.claim(TICKET, FIRST).ok
    other = tickets.claim(OTHER, SECOND)
    assert other.ok, f"a claim on another ticket failed: {other.describe()}"
    assert (tickets.holder(TICKET), tickets.holder(OTHER)) == (FIRST, SECOND)


def test_one_holder_may_hold_several_tickets(tickets):
    assert tickets.claim(TICKET, FIRST).ok
    assert tickets.claim(OTHER, FIRST).ok, "a holder of one ticket could not claim another"


def test_a_lock_file_that_exists_is_a_held_claim_whatever_it_holds(tickets):
    """Exclusive creation: a lock file left empty by a session that died while claiming still holds the ticket."""
    lock = tickets.lock(TICKET)
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_bytes(b"")
    support.assert_error(tickets.claim(TICKET, SECOND), support.CLAIM_HELD, "a claim on a ticket with a lock file")
    assert lock.read_bytes() == b"", "the claim wrote into a lock file that already existed"


# ---- failure 1: two agents hold the same claim

def test_claims_raced_from_separate_processes_give_exactly_one_holder(api, project):
    """Eight processes claim one ticket at the same moment, four times over: one holds it, seven are told who."""
    tickets = [project.ticket(f"TST-r00{round_}", f"W9-1{round_}") for round_ in range(support.RACE_ROUNDS)]
    project.settle()
    for ticket in tickets:
        holders = [f"engineer:racer-{number}" for number in range(support.RACE_CONTENDERS)]
        outcomes = api.race("claim", project.root, [(ticket, holder) for holder in holders])
        winners = [holder for holder, outcome in zip(holders, outcomes) if outcome.ok]
        assert len(winners) == 1, f"{len(winners)} processes hold the claim on {ticket}: {winners}"
        for holder, outcome in zip(holders, outcomes):
            if holder == winners[0]:
                continue
            details = support.assert_error(outcome, support.CLAIM_HELD, f"the claim of {holder} that lost the race")
            assert details.get("holder") == winners[0], \
                f"{holder} lost the race and was told the holder is {details.get('holder')!r}, not {winners[0]}"
        assert project.holder(ticket) == winners[0], "the recorded holder is not the process that won the claim"


# ---- release

def test_a_released_ticket_can_be_claimed_again(tickets):
    assert tickets.claim(TICKET, FIRST).ok
    released = tickets.release(TICKET, FIRST)
    assert released.ok, f"the holder could not release its claim: {released.describe()}"
    assert tickets.holder(TICKET) is None, "a released ticket still has a holder"
    assert not tickets.lock(TICKET).exists(), "the release left the lock file"
    again = tickets.claim(TICKET, SECOND)
    assert again.ok, f"a released ticket could not be claimed: {again.describe()}"
    assert tickets.holder(TICKET) == SECOND


def test_a_release_by_another_than_the_holder_fails_and_the_claim_stays(tickets):
    assert tickets.claim(TICKET, FIRST).ok
    details = support.assert_error(tickets.release(TICKET, SECOND), support.CLAIM_NOT_HELD,
                                   "a release by another than the holder")
    assert details.get("holder") == FIRST, f"the error does not name the holder: {details!r}"
    assert tickets.holder(TICKET) == FIRST, "a release by another took the claim away"


def test_a_release_of_a_ticket_nobody_holds_fails(tickets):
    support.assert_error(tickets.release(TICKET, FIRST), support.CLAIM_NOT_HELD, "a release of a free ticket")


# ---- what cannot be claimed

def test_a_claim_on_a_ticket_that_does_not_exist_fails_and_leaves_no_lock(tickets):
    before = support.tree(tickets.root)
    details = support.assert_error(tickets.claim("TST-zzzz", FIRST), support.TICKET_NOT_FOUND,
                                   "a claim on a ticket that does not exist")
    assert details.get("ticket") == "TST-zzzz"
    after = support.tree(tickets.root)
    after.pop(support.CLAIMS_REL, None)   # an empty claims folder is not a claim
    assert after == before, "a claim on a ticket that does not exist wrote in the project"


@pytest.mark.parametrize("ticket", ["sub/TST-b001", "../outside", ".claims/../TST-a001", "/TST-a001"])
def test_a_ticket_id_with_a_path_separator_is_no_ticket(tickets, ticket):
    """Such an id names no ticket even where a file answers to the path, and nothing is written for it."""
    support.write(tickets.root, ".tickets/sub/TST-b001.md", support.ticket_text("TST-b001", "W9-08"))
    support.write(tickets.root, "outside.md", support.ticket_text("outside", "W9-09"))
    (tickets.root / support.CLAIMS_REL).mkdir(parents=True, exist_ok=True)
    before = support.tree(tickets.root)
    support.assert_error(tickets.claim(ticket, FIRST), support.TICKET_NOT_FOUND,
                         f"a claim on the ticket id {ticket!r}")
    assert support.tree(tickets.root) == before, f"a claim on the ticket id {ticket!r} wrote in the project"
    assert sorted(path.name for path in tickets.root.parent.iterdir()) == ["project"], \
        f"a claim on the ticket id {ticket!r} wrote beside the project"


def test_a_closed_ticket_cannot_be_claimed(tickets):
    tickets.set_status(TICKET, "closed")
    tickets.settle()
    details = support.assert_error(tickets.claim(TICKET, FIRST), support.TICKET_CLOSED, "a claim on a closed ticket")
    assert details.get("ticket") == TICKET
    assert not tickets.lock(TICKET).exists(), "a claim on a closed ticket left a lock file"
