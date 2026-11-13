"""KPI success 1 and failure 1: one packet and one hash per ticket, whatever order the retrieval returns its
items in; a context that differs between two computations still fails the check, naming the ticket [DEC-768].

Rewrite-Reason: W2-04's KPIs 2 and 4 (CAP-15.d, DEC-860), DEC-1005 (README, "W2-04 (DEC-1005)"). The context no
longer reaches the retrieval's public entry (P-W2-04-2 (A)), so the stand-in that reordered that entry's items sees
nothing. Each case keeps the behaviour it guarded, observed where W2-04 puts it: in the packet's ``supplementary``,
``dropped``, ``further_batch`` and ``supplementary_batches``. The orders are produced from outside: the same files
written in another order into another project at the same commit, their index's rows inserted in another order, and
other hash seeds (``reverse``, ``rotate``, ``shuffle``). TK-W254-BIG's mandatory input (about 25,000 tokens) refuses
at the default ceiling (W2-04, S2), so its cases give it a budget from the packet's own figures that holds its
mandatory inputs and about half its evidence: they test dropping under pressure. A budget below the mandatory inputs
refuses. The check's two computations run in one process; between them the stand-in at the context's public entry
puts the project into another state (another order of the store's rows, or one document fewer), and every reproduced
refusal would be a ``REFUSED:`` line, not green evidence: the check cases use tickets that fit.

Red reasons, today: TK-W254-BIG's context is ``ok: true`` over its ceiling (no ``CONTEXT_OVER_CEILING``); the packet
has no ``supplementary_batches`` or ``further_batch``; a budget below the mandatory inputs gives ``ok: true``. The
three check cases pass today: the base's context is order-stable and the check compares hashes; they hold what the
change must keep.
"""

from __future__ import annotations

import collections
import shutil

import pytest

import w2_54_support as S

ORDERS = ("reverse", "rotate", "shuffle")
SEEDS = {"base": "0", "reverse": "1", "rotate": "2", "shuffle": "54"}   # PYTHONHASHSEED of each computation
TICKETS = (S.TK_SMALL, S.TK_BIG, S.TK_OTHER)


def _need_gitleaks(box):
    if not box.has_gitleaks():
        pytest.fail("gitleaks is not on PATH: the lexical index of the fixture cannot be built", pytrace=False)


def _seeded(box, name):
    return box.env(PYTHONHASHSEED=SEEDS[name])


@pytest.fixture(scope="module")
def tied(box):
    """The context project with the tied files and a second small ticket, indexed at once (rows in path order)."""
    _need_gitleaks(box)
    return S.order_project(box, box.workdir / "tied" / "repo", S.tied_corpus(TICKETS))


@pytest.fixture(scope="module")
def orders(box, tied):
    """For each order: the same files written in that order into another project, at the same commit, its index's
    rows inserted file by file in that order of the documents' paths. The fixture holds its premise: the same commit,
    the same rows, in another order."""
    files = S.tied_corpus(TICKETS)
    documents = [rel for rel in files if rel.startswith("docs/")]
    base = S.row_order(tied)
    built = {}
    for how in ORDERS:
        project = S.order_project(box, box.workdir / f"tied-{how}" / "repo", files, written=S.in_order(files, how),
                                  rows=S.in_order(documents, how))
        assert S.head(project) == S.head(tied), f"the fixture is wrong: the {how} project is another commit"
        rows = S.row_order(project)
        assert rows != base and sorted(rows) == sorted(base), \
            f"the fixture is wrong: the {how} store does not give the same rows in another order"
        built[how] = project
    return built


_BIG = {}


def _big(box, tied):
    """TK-W254-BIG's budget under pressure and its packet with room for all (README, "W2-04 (DEC-1005)"), computed
    once, in the first case that asks (so that a refusal or an ok over the ceiling fails that case, not a fixture)."""
    if "value" not in _BIG:
        _BIG["value"] = S.pressure_budget(box, tied, S.TK_BIG)
    return _BIG["value"]


def _big_packet(box, project, budget, name):
    packet = S.packet_of(S.context_run(box, project, S.TK_BIG, "--budget", budget, env=_seeded(box, name)))
    assert packet[S.K_SUPPLEMENTARY] and packet[S.K_FURTHER], (
        f"the fixture is wrong: with a budget of {budget}, TK-W254-BIG stacks {len(packet[S.K_SUPPLEMENTARY])} items "
        f"and leaves {packet.get(S.K_FURTHER)!r}: no pressure")
    return packet


def test_the_stand_in_reaches_the_retrieval_s_public_entry_with_tied_and_same_id_items(box, tied):
    """The harness, re-pointed to what the packet shows (was: the stand-in at the retrieval's entry saw these items).
    With room for all its evidence, the batches TK-W254-BIG's context takes read at least 10 items of at least 5
    ids, several items of one record (sharing its id, or its file where items are named one by one), and the four
    tied files, whose stacked items have one text."""
    _, everything = _big(box, tied)
    read = S.batch_items(everything)
    ids = collections.Counter(rid for rid, _ in read)
    paths = collections.Counter(path for _, path in read)
    assert len(read) >= 10, f"the batches read too few items for the cases to mean anything: {read}"
    assert len(ids) >= 5, f"the batches read too few distinct ids: {ids}"
    assert max(ids.values()) >= 2 or max(paths.values()) >= 2, f"no record gives two items: {ids}"
    assert set(S.TIE_PATHS) <= set(paths), f"the batches did not read the tied files: {sorted(paths)}"
    texts = {item.get("text") for item in everything[S.K_SUPPLEMENTARY] if item.get("path") in S.TIE_PATHS}
    assert len(texts) == 1, f"the tied files' items do not have one text: {texts}"


def test_two_computations_with_the_retrieval_s_own_order_give_one_packet(box, tied):
    """Two computations of TK-W254-BIG under pressure, in one store, each in a process of its own: one packet, one
    hash."""
    budget, _ = _big(box, tied)
    first, second = _big_packet(box, tied, budget, "base"), _big_packet(box, tied, budget, "base")
    assert first[S.K_HASH] == second[S.K_HASH]
    assert S.canonical(first) == S.canonical(second)


@pytest.mark.parametrize("order", ORDERS)
def test_every_order_of_the_retrieval_s_items_gives_the_same_packet_and_hash(box, tied, orders, order):
    """*Red.* TK-W254-BIG under pressure (its mandatory inputs fit, about half its evidence is stacked and the rest
    left). The same files and commit, with the project's files, the store's rows and the hash seed in another order
    (``order``), give the same packet, ``dropped``, ``further_batch`` and ``supplementary_batches`` included, and the
    same hash."""
    budget, _ = _big(box, tied)
    expected = _big_packet(box, tied, budget, "base")
    other = _big_packet(box, orders[order], budget, order)
    assert other[S.K_DROPPED] == expected[S.K_DROPPED], (
        f"the dropped list follows the order the files, the store or the process give (order {order!r}):\n"
        f"in path order: {[entry.get('id') for entry in expected[S.K_DROPPED]]}\n"
        f"{order}: {[entry.get('id') for entry in other[S.K_DROPPED]]}")
    assert S.batch_items(other) == S.batch_items(expected) and other[S.K_FURTHER] == expected[S.K_FURTHER], \
        f"the batches or what is left follow the order (order {order!r})"
    assert other[S.K_HASH] == expected[S.K_HASH], "two orders of the same items give two hashes"
    assert S.canonical(other) == S.canonical(expected), "two orders of the same items give two packets"


def test_a_budget_below_the_mandatory_inputs_gives_the_same_packet_under_any_order(box, tied, orders):
    """*Red.* ``gov context --budget`` below TK-W254-SMALL's mandatory inputs (half of the packet's own count of its
    ticket and mandatory inputs) refuses: ``ok: false``, ``CONTEXT_OVER_CEILING``, a non-zero exit (W2-04, S2); and
    every order of the files, the store and the hash seed gives the same refusal."""
    alone = S.fixed_part(S.packet_of(S.context_run(box, tied, S.TK_SMALL)))
    budget = max(1, alone // 2)
    expected = S.context_run(box, tied, S.TK_SMALL, "--budget", budget, env=_seeded(box, "base"))
    refusal = S.canonical(S.refused_over_ceiling(expected, S.TK_SMALL, budget)).replace(str(tied), "<project>")
    for how in ORDERS:
        other = S.context_run(box, orders[how], S.TK_SMALL, "--budget", budget, env=_seeded(box, how))
        got = S.canonical(other.envelope()).replace(str(orders[how]), "<project>")
        assert other.returncode == expected.returncode and got == refusal, \
            f"under the {how} order the refusal differs:\n{got[:800]}\n{refusal[:800]}"


@pytest.mark.parametrize("order", ("identity", "reverse"))
def test_nothing_is_dropped_or_added_every_item_stays_in_the_packet_once(box, tied, orders, order):
    """A context keeps its contents: each item its batches read is in the packet once, stacked in ``supplementary``
    or, left for lack of room, listed in ``dropped`` (items with the same id stay apart, none is merged, none is
    added); the stack is the first items the batches read; and the entries are the same under another order."""
    budget, _ = _big(box, tied)
    expected = _big_packet(box, tied, budget, "base")
    packet = _big_packet(box, tied if order == "identity" else orders[order], budget,
                         "base" if order == "identity" else order)
    read = S.batch_items(packet)
    kept = S.stacked(packet)
    assert kept == read[:len(kept)], f"the stack is not the first items the batches read:\n{kept}\n{read[:len(kept)]}"
    returned = collections.Counter(rid for rid, _ in read)
    left = returned - collections.Counter(rid for rid, _ in kept)
    dropped = collections.Counter(entry.get("id") for entry in packet[S.K_DROPPED] if entry.get("id") in returned)
    assert dropped == left, f"the dropped list does not hold each item read and not stacked once:\n" \
                            f"left: {dict(left)}\ndropped: {dict(dropped)}"
    assert S.multiset(packet[S.K_DROPPED]) == S.multiset(expected[S.K_DROPPED]), \
        "the order of the files, the store or the process changed what is dropped, not only its order"


def test_a_ticket_whose_items_fit_keeps_every_item_and_drops_nothing(box, tied):
    """TK-W254-SMALL with room for every item of its evidence (a budget from the packet's own figures): every item
    its batches read is stacked, once, in their order; nothing is dropped, nothing left for a further batch, and the
    last batch read fewer items than its limit (the evidence ended)."""
    packet = S.packet_of(S.context_run(box, tied, S.TK_SMALL, "--budget", S.room_for_all(box, tied, S.TK_SMALL)))
    read = S.batch_items(packet)
    assert packet[S.K_DROPPED] == [], f"something is dropped from a context that fits: {packet[S.K_DROPPED]}"
    assert packet[S.K_FURTHER] == [], f"something is left from a context that fits: {packet[S.K_FURTHER]}"
    assert read and S.stacked(packet) == read, \
        f"the supplementary part does not hold each item read once:\n{read}\n{S.stacked(packet)}"
    last = packet[S.K_BATCHES][-1]
    assert len(last["items"]) < last["limit"], f"room for all, yet the evidence did not end: {last}"


@pytest.fixture(scope="module")
def none(box):
    """A project whose ticket TK-W254-NONE matches no file the index holds (its tickets folder is product memory,
    so no ticket file is indexed, and no document holds a word of its title)."""
    _need_gitleaks(box)
    return S.order_project(box, box.workdir / "none" / "repo", S.none_corpus(), classes={"tickets": "product"})


def test_an_empty_retrieval_result_gives_one_packet(box, none):
    """The context's lookup finds nothing (no document the index holds has a word of the ticket's title, so
    ``gov retrieve`` of those words gives no evidence either): two computations, in processes with two hash seeds,
    give one packet and one hash, with nothing supplementary, nothing read, nothing left and nothing in ``dropped``.

    Rewrite-Reason: DEC-1074 (6): a ticket's sources now legitimately bring a record (W2-92 S8). The premise asked
    ``gov retrieve`` the ticket's title itself, which names TK-W254-NONE by its title: under W2-92 S8 the record
    route reaches the ticket and one hop brings its source, the big charter, so that question is no longer empty.
    The premise now asks the title's words in another order: a question that names no record (a title is found
    whole) and whose every word is asked of the index, so it is empty today and under S8 alike exactly when no
    document holds a word of the title. What the case asserts about the packet is unchanged."""
    asked = " ".join(reversed(S.NONE_TITLE.split()))
    assert asked.casefold() != S.NONE_TITLE.casefold(), "premise: the question would name the ticket by its title"
    found = S.gov(box, "retrieve", "--json", "--root", none, asked)
    assert found.envelope().get("ok") is True and found.envelope()["result"].get("evidence") == [], \
        f"the fixture is wrong: the project holds evidence for {asked!r}\n{found.describe()[:1500]}"
    budget = S.room_for_all(box, none, S.NONE_TICKET)
    first = S.packet_of(S.context_run(box, none, S.NONE_TICKET, "--budget", budget, env=_seeded(box, "base")))
    second = S.packet_of(S.context_run(box, none, S.NONE_TICKET, "--budget", budget, env=_seeded(box, "shuffle")))
    assert first[S.K_SUPPLEMENTARY] == [] and first[S.K_DROPPED] == [] and first[S.K_FURTHER] == []
    assert S.batch_items(first) == [], f"the lookup found nothing, yet its batches read: {S.batch_items(first)}"
    assert first[S.K_HASH] == second[S.K_HASH] and S.canonical(first) == S.canonical(second)


@pytest.fixture(scope="module")
def unindexed_reversed(box):
    """The ``unindexed`` project's files, written in the reverse order, at the same commit, with no lexical index."""
    files = S.corpus((S.TK_SMALL, S.TK_BIG))
    return S.order_project(box, box.workdir / "unindexed-reversed" / "repo", files,
                           written=S.in_order(files, "reverse"), index=False)


@pytest.mark.parametrize("ticket_id", (S.TK_SMALL, S.TK_BIG))
def test_a_store_whose_index_is_missing_gives_one_packet_under_any_order(box, unindexed, unindexed_reversed,
                                                                         ticket_id):
    """No lexical index: two computations, the second on the same files written in the reverse order (the same
    commit) under another hash seed, give one packet and one hash. TK-W254-BIG gets a budget that holds its
    mandatory inputs (from the refusal's own figures)."""
    assert S.head(unindexed_reversed) == S.head(unindexed), "the fixture is wrong: another commit"
    extra = ("--budget", S.room_for_all(box, unindexed, ticket_id)) if ticket_id == S.TK_BIG else ()
    first = S.packet_of(S.context_run(box, unindexed, ticket_id, *extra, env=_seeded(box, "base")))
    second = S.packet_of(S.context_run(box, unindexed_reversed, ticket_id, *extra, env=_seeded(box, "reverse")))
    assert first[S.K_HASH] == second[S.K_HASH] and S.canonical(first) == S.canonical(second)


# --------------------------------------------------------------------------
# The check: two computations in one process, the project put into another state between them
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def states(box, tmp_path_factory):
    """A project with two small tickets (TK-W254-SMALL, TK-W254-OTHER: they fit the default ceiling, so the check
    measures them rather than reproducing a refusal) and the tied files, and three saved stores: ``sorted`` (rows in
    path order), ``reversed`` (the same commit, rows in the reverse order of the documents), and ``drop`` (built on a
    branch where the first document TK-W254-SMALL stacks is gone). The big charter, which neither ticket cites, is
    left out: its one line of about 25,000 tokens would stop the stack at the default ceiling wherever it ranks."""
    _need_gitleaks(box)
    saved = tmp_path_factory.mktemp("w2-54-stores")
    files = {rel: text for rel, text in S.tied_corpus((S.TK_SMALL, S.TK_OTHER)).items()
             if rel != "docs/charter/big.md"}
    project = S.order_project(box, box.workdir / "states" / "repo", files)
    stores = {"sorted": S.save_store(project, saved / "sorted")}
    first = S.packet_of(S.context_run(box, project, S.TK_SMALL))
    gone = next((path for _, path in S.stacked(first) if path in files and not path.startswith(".tickets/")), None)
    assert gone, f"the fixture is wrong: TK-W254-SMALL stacks no document at the default ceiling: {S.stacked(first)}"
    S.build_index(box, project, rows=S.in_order([rel for rel in files if rel.startswith("docs/")], "reverse"))
    stores["reversed"] = S.save_store(project, saved / "reversed")
    assert S.row_order(stores["reversed"]) != S.row_order(stores["sorted"]), "the fixture is wrong: one row order"
    S.git(project, "checkout", "-q", "-b", "drop")
    S.git(project, "rm", "-q", gone)
    S.git(project, "commit", "-q", "-m", f"{gone} is gone")
    S.build_index(box, project)
    stores["drop"] = S.save_store(project, saved / "drop")
    S.git(project, "checkout", "-q", "main")
    made = {"project": project, "gone": gone,
            "sorted": {"branch": "main", "store": stores["sorted"]},
            "reversed": {"branch": "main", "store": stores["reversed"]},
            "drop": {"branch": "drop", "store": stores["drop"]}}
    S.put_state(project, made["sorted"])
    yield made
    shutil.rmtree(saved, ignore_errors=True)


def _seen(box, ticket_id):
    """The states the stand-in put the project into before the first two computations of ``ticket_id``."""
    return [call["state"] for call in box.calls() if call["ticket"] == ticket_id][:2]


def _check(box, made, names, target=None):
    try:
        return S.context_check_in_states(box, made["project"], [made[name] for name in names], target)
    finally:
        S.put_state(made["project"], made["sorted"])


def test_the_check_is_green_when_two_computations_see_two_orders(box, states):
    """The context-reproducibility check, run as its declaration says, computes each ticket's context twice; before
    the second computation the stand-in puts in the store built at the same commit with its rows in another order,
    so the two computations see the evidence in two orders. One packet, one hash: the check is green, names no
    ticket as failed, refused or in error. (Was: the retrieval's stand-in returned its items reversed the second
    time; the context no longer reaches it.)"""
    first = S.packet_of(S.context_run(box, states["project"], S.TK_SMALL))
    assert first[S.K_SUPPLEMENTARY], "the fixture is wrong: TK-W254-SMALL's context holds no evidence to order"
    done = _check(box, states, ("sorted", "reversed"))
    for ticket_id in (S.TK_SMALL, S.TK_OTHER):
        assert _seen(box, ticket_id) == [0, 1], \
            f"the check's computations of {ticket_id} did not see the two stores in turn: {box.calls()}"
    assert done.returncode == 0, f"two orders of the same evidence fail the check\n{done.describe()}"
    for word in ("FAIL", "REFUSED", "ERROR"):
        assert word not in done.stdout, f"the check prints {word} for a context two orders do not change\n" \
                                        f"{done.describe()}"


def test_a_context_whose_items_differ_still_fails_the_check_naming_the_ticket(box, states):
    """Failure line 1. Before each ticket's second computation the stand-in checks out the branch where a document
    the ticket stacks is gone, with the store built there: the items and the hash differ, the check is not green and
    names the ticket. Passes today."""
    S.put_state(states["project"], states["drop"])
    try:
        dropped = S.packet_of(S.context_run(box, states["project"], S.TK_SMALL))
    finally:
        S.put_state(states["project"], states["sorted"])
    kept = S.packet_of(S.context_run(box, states["project"], S.TK_SMALL))
    assert S.stacked(dropped) != S.stacked(kept), \
        f"the fixture is wrong: without {states['gone']} TK-W254-SMALL stacks the same items"
    done = _check(box, states, ("sorted", "drop"))
    assert _seen(box, S.TK_SMALL) == [0, 1], f"the check's computations did not see the two states: {box.calls()}"
    assert done.returncode != 0, f"a context that differs between two computations is green\n{done.describe()}"
    assert S.TK_SMALL in done.stdout, f"the check does not name the ticket {S.TK_SMALL}\n{done.describe()}"


def test_the_check_names_only_the_ticket_whose_context_differs(box, states):
    """Failure line 1, two tickets: only TK-W254-SMALL's second computation sees the document gone. The check is
    not green and names that ticket, and not the one whose context is stable. Passes today."""
    done = _check(box, states, ("sorted", "drop"), target=S.TK_SMALL)
    assert _seen(box, S.TK_SMALL) == [0, 1] and set(_seen(box, S.TK_OTHER)) == {0}, \
        f"the stand-in did not change the state for {S.TK_SMALL} alone: {box.calls()}"
    assert done.returncode != 0, f"a context that differs between two computations is green\n{done.describe()}"
    assert S.TK_SMALL in done.stdout, f"the check does not name the ticket {S.TK_SMALL}\n{done.describe()}"
    assert S.TK_OTHER not in done.stdout + done.stderr, \
        f"the check names {S.TK_OTHER}, whose context did not change\n{done.describe()}"
