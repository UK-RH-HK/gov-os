"""KPI success 1 and failure 1: one packet and one hash per ticket, whatever order the retrieval returns its
items in; a context that differs between two computations still fails the check, naming the ticket [DEC-768].

The retrieval stand-in (README, "The retrieval stand-in") returns the real retrieval's items in another order.
Every case here is one in which the order cannot decide what the packet holds: every supplementary item is
dropped (a mandatory input past the ceiling, this repository's shape at ``c9537e39``), the retrieval returns
nothing, or the index is missing. So the same packet is owed under every order.

Red reasons, today: the cases marked *red* fail because the ``dropped`` list comes out in the order the
retrieval returned its items, so the packet and its hash differ (the check prints ``FAIL: <ticket>``). The
other cases pass today; they hold what the fix must keep.
"""

from __future__ import annotations

import collections

import pytest

import w2_54_support as S

ORDERS = ("reverse", "rotate", "shuffle")


def _evidence_ids(box, ticket_id):
    """The ids of the items the stand-in returned for ``ticket_id``'s last retrieval call."""
    calls = [call for call in box.calls() if call["ticket"] in (ticket_id, None)]
    assert calls, f"the retrieval's public entry was never called for {ticket_id}: {box.calls()}"
    return [item[0] for item in calls[-1]["out"]]


def test_the_stand_in_reaches_the_retrieval_s_public_entry_with_tied_and_same_id_items(box, indexed):
    """The harness: computing the context calls ``gov.retrieval.retrieve.retrieve``, and its items include
    several with the same id (one record in many sections) beside items of other ids. Passes today."""
    S.packet(box, indexed, S.TK_BIG, "identity")
    ids = _evidence_ids(box, S.TK_BIG)
    counts = collections.Counter(ids)
    assert len(ids) >= 10, f"the retrieval returned too few items for the cases to mean anything: {ids}"
    assert len(counts) >= 5, f"the retrieval returned too few distinct ids: {counts}"
    assert max(counts.values()) >= 2, f"no two items share an id: {counts}"


def test_two_computations_with_the_retrieval_s_own_order_give_one_packet(box, indexed):
    """Two computations of one ticket in one store, the retrieval unchanged: one packet, one hash."""
    first = S.packet(box, indexed, S.TK_BIG, "identity")
    second = S.packet(box, indexed, S.TK_BIG, "identity")
    assert first[S.K_HASH] == second[S.K_HASH]
    assert S.canonical(first) == S.canonical(second)


@pytest.mark.parametrize("order", ORDERS)
def test_every_order_of_the_retrieval_s_items_gives_the_same_packet_and_hash(box, indexed, order):
    """*Red.* The ticket's mandatory input is past the default ceiling, so every supplementary item is dropped.
    The retrieval returning the same items in another order (``order``) gives the same packet, ``dropped``
    included, and the same hash."""
    expected = S.packet(box, indexed, S.TK_BIG, "identity")
    other = S.packet(box, indexed, S.TK_BIG, order)
    last = box.calls()[-1]
    assert last["out"] != last["in"] and sorted(last["out"]) == sorted(last["in"]), \
        f"the stand-in did not return the same items in another order: {last}"
    assert other[S.K_DROPPED] == expected[S.K_DROPPED], (
        f"the dropped list follows the order the retrieval returned (order {order!r}):\n"
        f"retrieval's own order: {[entry.get('id') for entry in expected[S.K_DROPPED]]}\n"
        f"{order}: {[entry.get('id') for entry in other[S.K_DROPPED]]}")
    assert other[S.K_HASH] == expected[S.K_HASH], "two orders of the same items give two hashes"
    assert S.canonical(other) == S.canonical(expected), "two orders of the same items give two packets"


def test_a_budget_below_the_mandatory_inputs_gives_the_same_packet_under_any_order(box, indexed):
    """*Red.* ``gov context --budget``: with a ceiling below the mandatory inputs alone, every supplementary
    item is dropped, and the reversed order of the retrieval's items gives the same packet and hash."""
    alone = S.packet(box, indexed, S.TK_SMALL, "empty")
    budget = max(1, int(alone["tokens"]) // 2)
    expected = S.packet(box, indexed, S.TK_SMALL, "identity", "--budget", str(budget))
    assert expected[S.K_SUPPLEMENTARY] == [] and expected[S.K_DROPPED], \
        f"with a budget of {budget} the fixture should drop every supplementary item: {S.canonical(expected)[:800]}"
    reversed_ = S.packet(box, indexed, S.TK_SMALL, "reverse", "--budget", str(budget))
    assert reversed_[S.K_DROPPED] == expected[S.K_DROPPED], \
        "under --budget the dropped list follows the order the retrieval returned"
    assert reversed_[S.K_HASH] == expected[S.K_HASH]
    assert S.canonical(reversed_) == S.canonical(expected)


@pytest.mark.parametrize("order", ("identity", "reverse"))
def test_nothing_is_dropped_or_added_every_item_stays_in_the_packet_once(box, indexed, order):
    """A context otherwise unchanged keeps its contents: each item the retrieval returned is one entry of
    ``dropped`` (items with the same id stay apart, none is merged, none is added), and the entries are the same
    under any order. Passes today (the entries are there, only their order changes)."""
    expected = S.packet(box, indexed, S.TK_BIG, "identity")
    packet = S.packet(box, indexed, S.TK_BIG, order)
    returned = collections.Counter(_evidence_ids(box, S.TK_BIG))
    dropped = collections.Counter(entry.get("id") for entry in packet[S.K_DROPPED] if entry.get("id") in returned)
    assert packet[S.K_SUPPLEMENTARY] == [], "a ticket past the ceiling holds no supplementary item"
    assert dropped == returned, f"the dropped list does not hold each returned item once:\n" \
                                f"returned: {dict(returned)}\ndropped: {dict(dropped)}"
    assert S.multiset(packet[S.K_DROPPED]) == S.multiset(expected[S.K_DROPPED]), \
        "the order of the retrieval's items changed what is dropped, not only its order"


def test_a_ticket_whose_items_fit_keeps_every_item_and_drops_nothing(box, indexed):
    """A ticket whose supplementary part fits the default ceiling keeps every item the retrieval returned and
    drops none: the fix adds nothing to ``dropped`` and takes nothing from ``supplementary``. Passes today."""
    packet = S.packet(box, indexed, S.TK_SMALL, "identity")
    returned = collections.Counter(_evidence_ids(box, S.TK_SMALL))
    kept = collections.Counter(item.get("id") for item in packet[S.K_SUPPLEMENTARY])
    assert packet[S.K_DROPPED] == [], f"something is dropped from a context that fits: {packet[S.K_DROPPED]}"
    assert kept == returned, f"the supplementary part does not hold each item once:\n{dict(returned)}\n{dict(kept)}"


def test_an_empty_retrieval_result_gives_one_packet(box, indexed):
    """The retrieval returns no item: two computations give one packet and one hash, with nothing supplementary
    and nothing of the retrieval's in ``dropped``. Passes today."""
    first = S.packet(box, indexed, S.TK_BIG, "empty")
    second = S.packet(box, indexed, S.TK_BIG, "empty")
    assert first[S.K_SUPPLEMENTARY] == [] and first[S.K_DROPPED] == []
    assert first[S.K_HASH] == second[S.K_HASH] and S.canonical(first) == S.canonical(second)


@pytest.mark.parametrize("ticket_id", (S.TK_SMALL, S.TK_BIG))
def test_a_store_whose_index_is_missing_gives_one_packet_under_any_order(box, unindexed, ticket_id):
    """No lexical index: two computations, one with the retrieval's order reversed, give one packet and one
    hash. Passes today."""
    first = S.packet(box, unindexed, ticket_id, "identity")
    second = S.packet(box, unindexed, ticket_id, "reverse")
    assert first[S.K_HASH] == second[S.K_HASH] and S.canonical(first) == S.canonical(second)


def test_the_check_is_green_when_two_computations_see_two_orders(box, big_only):
    """*Red.* The context-reproducibility check, run as its declaration says, computes the ticket's context
    twice; the retrieval returns its items in one order the first time and reversed the second. One packet, one
    hash: the check is green. Today it prints ``FAIL: TK-W254-BIG: <hash> != <hash>`` and exits 1."""
    done = S.context_check(box, big_only, "alternate")
    calls = [call for call in box.calls() if call["ticket"] in (S.TK_BIG, None)]
    assert len({S.canonical(call["out"]) for call in calls}) >= 2, \
        f"the check's computations did not see two orders of the retrieval's items: {calls}"
    assert done.returncode == 0, f"two orders of the same items fail the check\n{done.describe()}"


def test_a_context_whose_items_differ_still_fails_the_check_naming_the_ticket(box, big_only):
    """Failure line 1. The second computation's retrieval returns one item fewer: the items and the hash
    differ, the check is not green and names the ticket. Passes today."""
    done = S.context_check(box, big_only, "drop-alternate")
    assert len({len(call["out"]) for call in box.calls()}) >= 2, \
        f"the check's computations did not see two different sets of items: {box.calls()}"
    assert done.returncode != 0, f"a context that differs between two computations is green\n{done.describe()}"
    assert S.TK_BIG in done.stdout, f"the check does not name the ticket {S.TK_BIG}\n{done.describe()}"


def test_the_check_names_only_the_ticket_whose_context_differs(box, indexed):
    """Failure line 1, two tickets: only the second ticket's items differ between its two computations. The
    check is not green and names that ticket, and not the one whose context is stable. Passes today."""
    done = S.context_check(box, indexed, "drop-alternate", target=S.TK_BIG)
    assert done.returncode != 0, f"a context that differs between two computations is green\n{done.describe()}"
    assert S.TK_BIG in done.stdout, f"the check does not name the ticket {S.TK_BIG}\n{done.describe()}"
    assert S.TK_SMALL not in done.stdout + done.stderr, \
        f"the check names {S.TK_SMALL}, whose context did not change\n{done.describe()}"
