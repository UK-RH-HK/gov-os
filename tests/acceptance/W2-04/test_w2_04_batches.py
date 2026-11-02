"""KPI 7 (S7; DEC-860): never one giant query or context; ranked batches, stacked, and what is left is named.

The supplementary evidence is gathered by retrieval in batches, in order of relevance, and stacked in that order into
the room the ceiling leaves; when room is left after one batch the next is taken. Stacking is strict rank order: it
stops at the first item that does not fit. ``further_batch`` lists, in rank order, ``{"id", "path"}`` of the ranked
items not stacked for lack of room, beginning with the first that did not fit, at most one batch long; empty when
nothing was left. A supplementary lookup failure is named in ``dropped`` by its kind (W2-L180).

The ledger (README, "The planted projects") has 48 matching pages, every fourth one large, and room for all of them
at the default ceiling. One batch is one of the context's own lookups of ranked evidence, and the packet shows each
under ``supplementary_batches`` (the addendum's S7a, DEC-1005, deciding run 1's package P-1): ``items`` (the ``{id,
path}`` it read, in rank order) and ``limit`` (the most it could read). Round 2 reads the batches there; no stand-in
wraps the retrieval's entry, which the context no longer reaches.

Addendum 3's S7 (DEC-1025 item 2, the repair round) adds the room ending exactly: on a batch's last item, inside a
batch, or a room of 0. ``further_batch`` still names what is left, in rank order and at most one batch long, and its
items are in ``dropped`` as ``budget exceeded``. An item of ``further_batch`` need not be one a batch read, so
round 2's ``…at_most_one_batch_long`` now compares it with the rank order, not with the batches' reads.

Red reasons, today: the packet has no ``supplementary_batches`` and no ``further_batch``; one retrieval call gives at
most 20 items, so most pages are never stacked; an item that does not fit is skipped and a smaller one below it is
stacked. The lookup failure case passes today for the naming (W2-L180 was fixed in W1-24's follow-up).
"""

from __future__ import annotations

import sqlite3

import pytest

import w2_04_support as s


def _full(api, ledger):
    return api.gov(ledger.root, s.LEDGER_TICKET).packet


def _all_pages():
    return [f"docs/ledger/page-{number:02d}.md" for number in range(s.LEDGER_PAGES)]


def _stacked(packet):
    return [(item["id"], item["path"]) for item in packet[s.K_SUPPLEMENTARY]]


def _room(packet):
    """The room the ceiling leaves after the ticket's text and the mandatory inputs, in the packet's own figures."""
    return packet[s.K_BUDGET]["limit"] - (packet[s.K_TOKENS] - s.supplementary_tokens(packet))


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
    """Rewrite-Reason: DEC-1005 (P-W2-04-2 (A)). Room for every page (the case above): the batches are taken until the
    evidence ends. Every batch but the last read as many items as its limit (one that read fewer ended the evidence,
    so nothing was left to take); the last read fewer than its limit, or none; every item the batches read is
    stacked, in their order; so the stack holds more than one batch whenever the matching evidence passes one batch.
    No batch reads more items than the room has tokens (each item costs at least one): never one giant query."""
    packet = _full(retrieval_api, ledger)
    taken = s.batches(packet)
    read, stacked = s.read_items(packet), _stacked(packet)
    assert taken, f"room for every page, yet `{s.K_BATCHES}` names no batch: {taken}"
    sizes = [(len(entry["items"]), entry["limit"]) for entry in taken]
    assert all(read_ == limit for read_, limit in sizes[:-1]), (
        f"a batch read fewer items than its limit and yet another was taken (items, limit): {sizes}")
    assert sizes[-1][0] < sizes[-1][1], (
        f"room is left and the last batch read its limit, yet no next batch was taken (items, limit): {sizes}")
    assert stacked == read, (f"room for everything, yet the stack is not every item the batches read, in order:\n"
                             f"read {len(read)}: {read[:4]}...\nstacked {len(stacked)}: {stacked[:4]}...")
    if len(read) > taken[0]["limit"]:
        assert len(taken) >= 2 and len(stacked) > max(limit for _, limit in sizes), (
            f"the evidence passes one batch (limit {taken[0]['limit']}, {len(read)} items) and the room holds it, "
            f"yet the stack holds no more than one batch: {sizes}")
    room = _room(packet)
    assert all(limit <= room for _, limit in sizes), \
        f"a batch could read more items than the room has tokens ({room}): {sizes}"


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
    """Rewrite-Reason: DEC-1005 (P-W2-04-2 (A)). Rewrite-Reason: DEC-1025 (P-W2-04-8 (a), addendum 3's S7: an item
    of ``further_batch`` need not be one a batch read). Under the tight budget, read through
    ``supplementary_batches``: the stack is the first items of the batches' items, in order; ``further_batch``
    begins with the first ranked item that was not stacked, continues in **rank order** (the order a room-for-all
    run stacks, R2; before DEC-1025, the batches' own reads), holds no stacked item, and is no longer than the
    largest batch's limit."""
    full = _full(retrieval_api, ledger)
    ranked, _, budget = _tight_budget(full)
    order = [(rid, path) for rid, path, _ in ranked]

    packet = retrieval_api.gov(ledger.root, s.LEDGER_TICKET, "--budget", budget).packet

    taken = s.batches(packet)
    read, stacked = s.read_items(packet), _stacked(packet)
    assert taken, f"`{s.K_BATCHES}` names no batch, yet items are stacked: {stacked[:4]}"
    one_batch = max(entry["limit"] for entry in taken)
    assert stacked == read[:len(stacked)], (f"the stack is not the first items the batches read, in order:\n"
                                            f"stacked {stacked}\nread    {read[:len(stacked) + 2]}")
    further = packet.get(s.K_FURTHER)
    assert isinstance(further, list) and 0 < len(further) <= one_batch, \
        f"`{s.K_FURTHER}` holds {further if not isinstance(further, list) else len(further)} items; one batch is " \
        f"at most {one_batch}"
    pairs = [(item["id"], item["path"]) for item in further]
    assert pairs == order[len(stacked):len(stacked) + len(pairs)], (
        f"`{s.K_FURTHER}` is not the ranked items from the first that was not stacked, in rank order:\n"
        f"{pairs}\nranked after the stack: {order[len(stacked):len(stacked) + len(pairs)]}")
    assert not set(stacked) & set(pairs), f"`{s.K_FURTHER}` holds stacked items: {sorted(set(stacked) & set(pairs))}"


# --------------------------------------------------------------------------
# Addendum 3's S7 (F2; DEC-1025 item 2): the room ends exactly on a stacked item, or there is none at all
# --------------------------------------------------------------------------

EXACT_SHAPES = ("the room ends on a batch's last item", "the room ends inside a batch", "no room")
BUDGET_EXCEEDED = "budget exceeded"


def _exact_cut(full, shape):
    """From the room-for-all run (rank order, everything stacked; R2): the number ``k`` of first ranked items whose
    tokens fill the room exactly. (a) ``k`` is the first batch's item count; where that batch holds every ranked
    item, all but the last. (b) ``k`` is inside the first batch: half its items. (c) ``k`` is 0."""
    ranked = _ranked(full)
    assert len(ranked) >= 4, f"the fixture is wrong: {len(ranked)} ranked items at the default ceiling"
    if shape == "no room":
        return ranked, 0
    first = len(s.batches(full)[0]["items"]) if s.batches(full) else 0
    assert first >= 1, f"the fixture is wrong: room for all, yet the first batch read nothing: {full[s.K_BATCHES]}"
    k = first if first < len(ranked) else len(ranked) - 1
    if shape == "the room ends inside a batch":
        k = max(1, k // 2)
    return ranked, k


def _room_of_each_batch(packet, room):
    """The room each batch had when it was taken: the room less the tokens of the items stacked before it."""
    stacked_tokens = [int(item["tokens"]) for item in packet[s.K_SUPPLEMENTARY]]
    rooms, before = [], 0
    for entry in s.batches(packet):
        rooms.append(room - sum(stacked_tokens[:before]))
        before += len(entry["items"])
    return rooms


@pytest.mark.parametrize("shape", EXACT_SHAPES)
def test_when_the_room_ends_exactly_further_batch_names_what_is_left(retrieval_api, ledger, shape):
    """Addendum 3's S7 (DEC-1025 item 2, P-W2-04-8 (a); S7a as written). The ceiling is set from the packet's own
    figures, so that the room the ticket's text and mandatory inputs leave is exactly the tokens of the first ``k``
    ranked items: on a batch's last item, inside a batch, or 0. The packet is ``ok: true`` and holds its ceiling at
    exactly the budget; the stack is the first ``k`` ranked items; ``further_batch`` is not empty, begins with the
    first ranked item not stacked, continues in rank order, holds no stacked item, and is at most one batch long
    (the largest ``limit`` of the run's batches; with no room, of the room-for-all run's). Those items are in
    ``dropped`` with the reason ``budget exceeded``. No batch is taken for a room of 0, and no batch's ``limit``
    exceeds the room it had when it was taken (each item costs at least one token)."""
    full = _full(retrieval_api, ledger)
    ranked, k = _exact_cut(full, shape)
    order = [(rid, path) for rid, path, _ in ranked]
    mandatory = full[s.K_TOKENS] - s.supplementary_tokens(full)
    room = sum(item[2] for item in ranked[:k])
    budget = mandatory + room

    answer = retrieval_api.gov(ledger.root, s.LEDGER_TICKET, "--budget", budget)

    packet = answer.packet
    stacked = _stacked(packet)
    assert stacked == order[:k], (f"the stack is not the first {k} ranked items, which fill the room exactly:\n"
                                  f"stacked {stacked[max(0, k - 3):]}\nranked  {order[max(0, k - 3):k + 1]}")

    further = packet.get(s.K_FURTHER)
    assert isinstance(further, list) and further, (
        f"the room ends exactly after {k} ranked items and {len(order) - k} remain, yet `{s.K_FURTHER}` is "
        f"{further!r}")
    assert all(isinstance(item, dict) and {"id", "path"} <= set(item) for item in further), further[:3]
    pairs = [(item["id"], item["path"]) for item in further]
    assert pairs[0] == order[k], \
        f"`{s.K_FURTHER}` begins with {pairs[0]}, not the first ranked item not stacked, {order[k]}"
    assert pairs == order[k:k + len(pairs)], (f"`{s.K_FURTHER}` is not the ranked items from {order[k]} on, in rank "
                                              f"order:\n{pairs}\nranked {order[k:k + len(pairs)]}")
    once = {pair for pair in order if order.count(pair) == 1}  # (id, path) names one ranked item only
    assert not set(stacked) & set(pairs) & once, \
        f"`{s.K_FURTHER}` holds stacked items: {sorted(set(stacked) & set(pairs) & once)}"
    left_for_room = {entry.get("id") for entry in packet[s.K_DROPPED]
                     if str(entry.get("reason", "")).lower() == BUDGET_EXCEEDED}
    missing = [pair for pair in pairs if pair[0] not in left_for_room]
    assert not missing, (f"items of `{s.K_FURTHER}` are not in `{s.K_DROPPED}` with the reason {BUDGET_EXCEEDED!r}: "
                         f"{missing[:4]}\n{s.K_DROPPED}: {packet[s.K_DROPPED][:6]}")

    taken = s.batches(packet)
    rooms = _room_of_each_batch(packet, room)
    sizes = [(len(entry["items"]), entry["limit"]) for entry in taken]
    assert all(left > 0 for left in rooms), \
        f"a batch was taken with no room left (room when taken: {rooms}; items, limit: {sizes})"
    assert all(limit <= left for (_, limit), left in zip(sizes, rooms)), \
        f"a batch could read more items than its room had tokens (items, limit: {sizes}; room when taken: {rooms})"
    if k == 0:
        assert stacked == [] and taken == [], (f"no room, yet items are stacked ({stacked[:3]}) or batches taken "
                                               f"({taken[:2]})")
        one_batch = max(entry["limit"] for entry in s.batches(full))
    else:
        assert taken, f"`{s.K_BATCHES}` names no batch, yet {len(stacked)} items are stacked"
        one_batch = max(limit for _, limit in sizes)
    assert len(pairs) <= one_batch, f"`{s.K_FURTHER}` holds {len(pairs)} items; one batch is at most {one_batch}"

    s.assert_holds_its_ceiling(packet, ledger.text(f".tickets/{s.LEDGER_TICKET}.md"))
    assert packet[s.K_TOKENS] == budget, (
        f"the room ({room}) is exactly the first {k} ranked items, so the packet is the budget ({budget}); "
        f"it is {packet[s.K_TOKENS]}")


def _small_ledger(tmp_path):
    return s.build_project(tmp_path / "repo", s.ledger_files(pages=4))


@pytest.mark.parametrize("shape", ("room for all", "a tight budget", "no index", "a damaged index"))
def test_supplementary_batches_is_present_and_of_its_form(retrieval_api, ledger, tmp_path, shape):
    """The addendum's S7a and "The packet's keys" (DEC-1005). Every packet built carries the keys it carried before
    this ticket and exactly four more, ``supplementary_batches`` among them: a list of ``{items, limit}``, the items
    ``{id, path}`` with ``len(items) <= limit``; the ``supplementary`` block is, item for item, the first items of the
    batches' items; it is part of the packet, so two builds give the same one. Where the lookup found nothing or
    failed, it is an empty list or the entries the context did take, and a failure is named in ``dropped``."""
    if shape in ("room for all", "a tight budget"):
        root = ledger.root
        args = () if shape == "room for all" else ("--budget", _tight_budget(_full(retrieval_api, ledger))[2])
    else:
        project = _small_ledger(tmp_path)
        if shape == "no index":
            retrieval_api.build(project.root, index=False)
        else:
            retrieval_api.build(project.root)
            connection = sqlite3.connect(project.root / s.STORE_REL)
            try:
                connection.execute("DROP TABLE lexical_chunk")
                connection.commit()
            finally:
                connection.close()
        root, args = project.root, ()

    packet = retrieval_api.gov(root, s.LEDGER_TICKET, *args).packet

    assert set(packet) == set(s.KEYS_BEFORE) | set(s.KEYS_ADDED), (
        f"the packet's keys are not those it carried before and the four the addendum adds: "
        f"{sorted(set(packet) ^ (set(s.KEYS_BEFORE) | set(s.KEYS_ADDED)))} differ")
    read, stacked = s.read_items(packet), _stacked(packet)
    assert stacked == read[:len(stacked)], \
        f"an item of `{s.K_SUPPLEMENTARY}` is not among the batches' items in order: {stacked[:4]} / {read[:4]}"
    if shape in ("no index", "a damaged index"):
        assert stacked == [] and packet[s.K_FURTHER] == [], (stacked, packet[s.K_FURTHER])
    if shape == "a damaged index":
        assert packet[s.K_DROPPED], f"the lookup failed and `{s.K_DROPPED}` names nothing: {packet[s.K_BATCHES]}"
    again = retrieval_api.gov(root, s.LEDGER_TICKET, *args).packet
    assert again[s.K_BATCHES] == packet[s.K_BATCHES] and again[s.K_HASH] == packet[s.K_HASH], \
        f"two builds give two `{s.K_BATCHES}` or two hashes"


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
