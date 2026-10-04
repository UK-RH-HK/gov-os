"""KPI success 4 [CAP-34.d]: a declined, revoked or stale gate, or a gate answered for another CIT, does not
authorise execution: the checker fails a ticket or change that cites one as its approval.

A gate is a decision package of W1-34: its state is its ``status`` alone and its CIT is its ``cit`` (DEC-328).

- **How a record cites a gate** follows package DP-3's recommended option: the citing record names the gates in
  its frontmatter key ``approval`` and its own CIT in ``cit``. Every test of the first group waits on DP-3.
- **What a dead package does to the tickets that wait on it** (DEC-308 leaves it to W1-11) follows package DP-4's
  recommended option: the checker fails every ticket that is not closed and is named in the ``constrains`` of a
  declined, revoked or stale package. The second group waits on DP-4.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import package, package_path, record, ticket, ticket_path

TICKET = "PROJ-aaaa"
OTHER_TICKET = "PROJ-bbbb"
CHANGE = "CIT-0007"
CHANGE_PATH = "docs/changes/CIT-0007.md"
GATE = "DP-0001"
CIT = "CIT-0007"
OTHER_CIT = "CIT-0008"


def citing_ticket(**keys):
    return {ticket_path(TICKET): ticket(TICKET, approval=[GATE], cit=CIT, **keys)}


def citing_change():
    """A change record (CIT-E) that cites the gate as its approval."""
    return {CHANGE_PATH: record(CHANGE, "change", "PROPOSED", approval=[GATE], cit=CIT)}


CITERS = {
    "ticket": (TICKET, ticket_path(TICKET), citing_ticket),
    "change": (CHANGE, CHANGE_PATH, citing_change),
}


def checked(api, project, files):
    project.put({**support.CLEAN, **files})
    return api.check(project.root)


# ---- a record that cites a gate as its approval (waits on DP-3)

@pytest.mark.parametrize("status", support.GATE_DEAD)
@pytest.mark.parametrize("citer", sorted(CITERS))
def test_a_declined_revoked_or_stale_gate_does_not_authorise(api, project, citer, status):
    citer_id, citer_path, files = CITERS[citer]
    found = checked(api, project, {**files(), package_path(GATE): package(GATE, status, CIT)})
    support.assert_flagged(found, support.GATE_NOT_AUTHORISING, [citer_id, GATE], [citer_path])


@pytest.mark.parametrize("citer", sorted(CITERS))
def test_a_gate_answered_for_another_cit_does_not_authorise(api, project, citer):
    citer_id, citer_path, files = CITERS[citer]
    found = checked(api, project, {**files(), package_path(GATE): package(GATE, support.GATE_ANSWERED, OTHER_CIT)})
    support.assert_flagged(found, support.GATE_NOT_AUTHORISING, [citer_id, GATE], [citer_path])


@pytest.mark.parametrize("citer", sorted(CITERS))
def test_a_gate_answered_for_the_same_cit_authorises(api, project, citer):
    citer_id, _, files = CITERS[citer]
    found = checked(api, project, {**files(), package_path(GATE): package(GATE, support.GATE_ANSWERED, CIT)})
    support.assert_not_flagged(found, support.GATE_NOT_AUTHORISING, [citer_id])


def test_an_open_gate_does_not_authorise(api, project):
    """The template of W1-34: "Only an answered gate of the same CIT permits the next actions"."""
    found = checked(api, project, {**citing_ticket(), package_path(GATE): package(GATE, support.GATE_OPEN, CIT)})
    support.assert_flagged(found, support.GATE_NOT_AUTHORISING, [TICKET, GATE], [ticket_path(TICKET)])


def test_one_dead_gate_among_the_cited_gates_fails_the_ticket(api, project):
    found = checked(api, project, {
        ticket_path(TICKET): ticket(TICKET, approval=["DP-0001", "DP-0002"], cit=CIT),
        package_path("DP-0001"): package("DP-0001", support.GATE_ANSWERED, CIT),
        package_path("DP-0002"): package("DP-0002", "REVOKED", CIT),
    })
    support.assert_flagged(found, support.GATE_NOT_AUTHORISING, [TICKET, "DP-0002"], [ticket_path(TICKET)])
    support.assert_not_flagged(found, support.GATE_NOT_AUTHORISING, [TICKET, "DP-0001"])


def test_only_the_record_that_cites_the_dead_gate_fails(api, project):
    found = checked(api, project, {
        **citing_ticket(),
        ticket_path(OTHER_TICKET): ticket(OTHER_TICKET, approval=["DP-0002"], cit=CIT),
        package_path(GATE): package(GATE, "DECLINED", CIT),
        package_path("DP-0002"): package("DP-0002", support.GATE_ANSWERED, CIT),
    })
    support.assert_flagged(found, support.GATE_NOT_AUTHORISING, [TICKET, GATE])
    support.assert_not_flagged(found, support.GATE_NOT_AUTHORISING, [OTHER_TICKET])


# ---- a ticket that waits on a dead package (waits on DP-4)

@pytest.mark.parametrize("status", support.GATE_DEAD)
def test_a_ticket_that_waits_on_a_declined_revoked_or_stale_package_fails(api, project, status):
    found = checked(api, project, {
        ticket_path(TICKET): ticket(TICKET),
        package_path(GATE): package(GATE, status, CIT, constrains=[TICKET]),
    })
    support.assert_flagged(found, support.TICKET_WAITS_ON_DEAD_GATE, [TICKET, GATE], [ticket_path(TICKET)])


@pytest.mark.parametrize("status", (support.GATE_OPEN, support.GATE_ANSWERED))
def test_a_ticket_that_waits_on_an_open_or_answered_package_is_not_failed_by_the_checker(api, project, status):
    """An open package holds its tickets through the READY rule (DEC-308); an answered one releases them."""
    found = checked(api, project, {
        ticket_path(TICKET): ticket(TICKET),
        package_path(GATE): package(GATE, status, CIT, constrains=[TICKET]),
    })
    support.assert_not_flagged(found, support.TICKET_WAITS_ON_DEAD_GATE, [TICKET])


def test_a_closed_ticket_named_by_a_dead_package_is_not_failed(api, project):
    found = checked(api, project, {
        ticket_path(TICKET): ticket(TICKET, status="closed"),
        package_path(GATE): package(GATE, "STALE", CIT, constrains=[TICKET]),
    })
    support.assert_not_flagged(found, support.TICKET_WAITS_ON_DEAD_GATE, [TICKET])
