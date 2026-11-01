"""KPI 7 (S7; DEC-860): never one giant query or context; ranked batches, stacked, and what is left is named.

The supplementary evidence is gathered by retrieval in batches, in order of relevance, and stacked in that order into
the room the ceiling leaves; when room is left after one batch the next is taken. Stacking is strict rank order: it
stops at the first item that does not fit. ``further_batch`` lists, in rank order, ``{"id", "path"}`` of the ranked
items not stacked for lack of room, beginning with the first that did not fit, at most one batch long; empty when
nothing was left. A supplementary lookup failure is named in ``dropped`` by its kind (W2-L180).

The ledger (README, "The planted projects") has 48 matching pages, every fourth one large, and room for all of them
at the default ceiling. One batch is what one call of the retrieval's public entry returns (README, package P-1);
the ``log`` stand-in records each call.

Red reasons, today: one retrieval call gives at most 20 items, so most pages are never stacked; an item that does not
fit is skipped and a smaller one below it is stacked; the packet has no ``further_batch``. The lookup failure case
passes today (W2-L180 was fixed in W1-24's follow-up).
"""

from __future__ import annotations

import sqlite3

import w2_04_support as s


def _full(api, ledger, mode=None):
    api.reset_log()
    env = api.env(mode=mode) if mode else None
    return api.gov(ledger.root, s.LEDGER_TICKET, env=env).packet


def _all_pages():
    return [f"docs/ledger/page-{number:02d}.md" for number in range(s.LEDGER_PAGES)]


def test_with_room_for_all_every_matching_item_is_stacked_in_rank_order(retrieval_api, ledger):
    packet = _full(retrieval_api, ledger)
    s.assert_holds_its_ceiling(packet, ledger.text(f".tickets/{s.LEDGER_TICKET}.md"))
    stacked = s.ledger_paths(packet[s.K_SUPPLEMENTARY])
    missing = sorted(set(_all_pages()) - set(stacked))
    assert not missing, f"room is left, yet {len(missing)} of {s.LEDGER_PAGES} matching pages are not stacked: " \
                        f"{missing[:6]}..."
    assert stacked == sorted(stacked), f"the pages (ranked by path by the lexical route) are not in rank order: {stacked}"
    assert packet.get(s.K_FURTHER) == [], \
        f"room for everything, yet `{s.K_FURTHER}` is {packet.get(s.K_FURTHER, 'absent')!r}"


def test_when_room_is_left_after_one_batch_the_next_batch_is_taken(retrieval_api, ledger):
    packet = _full(retrieval_api, ledger, mode="log")
    calls = retrieval_api.calls()
    assert calls, "the retrieval's public entry (gov.retrieval.retrieve.retrieve) was never called"
    one_batch = max(len(call["out"]) for call in calls)
    stacked = s.ledger_paths(packet[s.K_SUPPLEMENTARY])
    assert len(calls) >= 2 and len(stacked) > one_batch, (
        f"{len(calls)} retrieval call(s), the largest returning {one_batch} items, and {len(stacked)} pages stacked: "
        f"the stack holds no more than one batch although room is left")


def _ranked(packet):
    return [(item["id"], item["path"], int(item["tokens"])) for item in packet[s.K_SUPPLEMENTARY]]


def _tight_budget(full):
    """From the full stack (rank order, everything fitted): the first item ``k`` with a smaller item ranked below it,
    and a budget that holds the items above ``k`` and is one token short of ``k`` itself, so that the smaller one
    below would fit."""
    ranked = _ranked(full)
    mandatory = full[s.K_TOKENS] - s.supplementary_tokens(full)
    for k in range(1, len(ranked)):
        if any(later[2] < ranked[k][2] for later in ranked[k + 1:]):
            above = sum(item[2] for item in ranked[:k])
            return ranked, k, mandatory + above + ranked[k][2] - 1
    raise AssertionError(f"the fixture is wrong: no stacked item has a smaller one ranked below it: {ranked}")


def test_with_less_room_the_stack_stops_at_the_first_item_that_does_not_fit(retrieval_api, ledger):
    full = _full(retrieval_api, ledger)
    ranked, k, budget = _tight_budget(full)

    packet = retrieval_api.gov(ledger.root, s.LEDGER_TICKET, "--budget", budget).packet

    got = [(item["id"], item["path"]) for item in packet[s.K_SUPPLEMENTARY]]
    expected = [(rid, path) for rid, path, _ in ranked[:k]]
    assert got == expected, (
        f"with a budget of {budget} the stack should be the {k} items ranked above {ranked[k][1]} "
        f"({ranked[k][2]} tokens, which does not fit) and nothing ranked below it; got {got[max(0, k - 2):]} "
        f"at its end")
    s.assert_holds_its_ceiling(packet, ledger.text(f".tickets/{s.LEDGER_TICKET}.md"))


def test_further_batch_begins_with_the_first_item_that_did_not_fit_in_rank_order(retrieval_api, ledger):
    full = _full(retrieval_api, ledger)
    ranked, k, budget = _tight_budget(full)

    packet = retrieval_api.gov(ledger.root, s.LEDGER_TICKET, "--budget", budget).packet

    further = packet.get(s.K_FURTHER)
    assert isinstance(further, list) and further, f"`{s.K_FURTHER}` is {further!r}: it names nothing left"
    assert all(set(item) >= {"id", "path"} for item in further), further
    pairs = [(item["id"], item["path"]) for item in further]
    order = [(rid, path) for rid, path, _ in ranked]
    assert pairs[0] == order[k], f"`{s.K_FURTHER}` begins with {pairs[0]}, not the first item that did not fit, " \
                                 f"{order[k]}"
    assert pairs == order[k:k + len(pairs)], f"`{s.K_FURTHER}` is not the ranked items from {order[k]} on: {pairs}"
    stacked = {(item["id"], item["path"]) for item in packet[s.K_SUPPLEMENTARY]}
    assert not stacked & set(pairs), f"`{s.K_FURTHER}` holds stacked items: {sorted(stacked & set(pairs))}"


def test_further_batch_is_at_most_one_batch_long(retrieval_api, ledger):
    full = _full(retrieval_api, ledger)
    _, _, budget = _tight_budget(full)
    retrieval_api.reset_log()

    packet = retrieval_api.gov(ledger.root, s.LEDGER_TICKET, "--budget", budget,
                               env=retrieval_api.env(mode="log")).packet

    calls = retrieval_api.calls()
    assert calls, "the retrieval's public entry (gov.retrieval.retrieve.retrieve) was never called"
    one_batch = max(len(call["out"]) for call in calls)
    further = packet.get(s.K_FURTHER)
    assert isinstance(further, list) and 0 < len(further) <= one_batch, \
        f"`{s.K_FURTHER}` holds {further if not isinstance(further, list) else len(further)} items; one batch is " \
        f"at most {one_batch}"


def test_a_lookup_failure_is_named_in_dropped_by_its_kind(retrieval_api, tmp_path):
    """A damaged index (its chunk table gone) is named as the index unavailable; the packet is built, nothing is
    stacked, and the ticket's text stays whole. Passes today for the naming (W1-24's follow-up, DEC-552)."""
    project = s.build_project(tmp_path / "repo", s.ledger_files(pages=4))
    retrieval_api.build(project.root)
    connection = sqlite3.connect(project.root / s.STORE_REL)
    try:
        connection.execute("DROP TABLE lexical_chunk")
        connection.commit()
    finally:
        connection.close()

    packet = retrieval_api.gov(project.root, s.LEDGER_TICKET).packet

    assert packet[s.K_SUPPLEMENTARY] == [], packet[s.K_SUPPLEMENTARY]
    reasons = [str(entry.get("reason", "")) for entry in packet[s.K_DROPPED]]
    assert any(s.INDEX_UNAVAILABLE in reason.lower() for reason in reasons), \
        f"a damaged index is not named in `dropped` by its kind: {packet[s.K_DROPPED]}"
