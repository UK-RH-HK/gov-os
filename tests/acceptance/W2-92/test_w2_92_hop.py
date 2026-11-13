"""KPI success 8 (DEC-1071, DEC-1072) and the failure line "a partial supersession that drops its target from what
is current": one bounded hop.

From what the record route or the closure reached, retrieval follows CITES, UNDER and OF_TASK out and AMENDS and
SUPERSEDES in (from the changed decision to its changer), at most 12 records, after today's closure chunks. A
question that reaches no record gets today's bundle.

Each question is a record's title alone: the record route reaches the record, and no word of the question is in the
record the hop must bring, so only the hop can bring it (no id is in the question, so the lexical route's id boost
brings nothing). Each case first checks that today's bundle (the integrated code ``support.LINKS_BASE`` on the same
marina) holds the named record and not the hop's record. A record is in a bundle when an evidence item holds its
text. No reranker, no vector, no code index.

Not a case here: "adopted only under DEC-1071's rule (all 80 not lower, the halves' gap not wider)" is the CTO's
measure, verified by the evidence file (README map).
"""

from __future__ import annotations

import pytest

import w2_92_support as support

T = support.TITLE_OF


def _holds(bundle, rid):
    return support.holds_text(bundle, support.TEXT_OF[rid])


def _held(bundle, rids):
    return [rid for rid in rids if _holds(bundle, rid)]


# (case, the record the question names by its title, the records the hop brings); for DAEO-lk02 the hop starts from
# DAEO-lk01, which today's closure reaches by depends_on
HOPS = [
    ("a ticket's sources", support.LK_TICKET, ["DEC-411"]),
    ("a ticket's closes", support.LK_TICKET, ["DEC-412"]),
    ("a checkpoint's task", support.LK_CHECKPOINT, [support.LK_TASK]),
    ("a close record's task, decisions_applied and requirements_implemented", support.LK_CLOSE,
     [support.LK_TASK, "DEC-413", support.LK_REQ]),
    ("a spec's decisions", support.LK_SPEC, ["DEC-414"]),
    ("a change record's decisions_carried, decisions_recorded and decisions_read", support.LK_CHANGE,
     ["DEC-415", "DEC-416", "DEC-417"]),
    ("a decision's Under", "DEC-421", ["DEC-422", "DEC-423"]),
    ("a changer stated on the changer (Changes)", "DEC-432", ["DEC-431"]),
    ("a changer stated on the changed entry (Changed by)", "DEC-432", ["DEC-433"]),
    ("a changer by Amends", "DEC-435", ["DEC-434"]),
    ("a partial supersession by Supersedes naming a part", "DEC-437", ["DEC-436"]),
    ("a partial supersession in free text", "DEC-438", ["DEC-439"]),
    ("a whole supersession by Replaces", "DEC-442", ["DEC-441"]),
    ("a whole supersession by Supersedes on a later line", "DEC-444", ["DEC-443"]),
    ("a whole supersession by Changed by superseded by", "DEC-454", ["DEC-455"]),
    ("from a record the closure reached (depends_on)", support.LK_DEPENDENT, ["DEC-411", "DEC-412"]),
]


@pytest.mark.parametrize("case, named, brought", HOPS, ids=[case[0] for case in HOPS])
def test_s8_a_reached_record_brings_its_stated_links_in_one_hop(marina_ask, marina_base_ask, case, named, brought):
    question = T[named]
    today = marina_base_ask(question)
    reached = [named] + ([support.LK_TICKET] if named == support.LK_DEPENDENT else [])
    assert _held(today, reached) == reached, (
        f"premise: today's bundle for {question!r} does not hold {reached}: {support.paths(today)}")
    assert not _held(today, brought), (
        f"premise: today's bundle for {question!r} already holds {_held(today, brought)}, so the case cannot see "
        "the hop")
    bundle = marina_ask(question)
    assert _held(bundle, reached) == reached, f"the bundle for {question!r} lost {reached}: {support.paths(bundle)}"
    missing = [rid for rid in brought if not _holds(bundle, rid)]
    assert not missing, (
        f"{case}: the bundle for {question!r} (reaching {named}) does not bring {missing} in one hop: "
        f"{support.items(bundle)}")


PARTIAL = [("Supersedes naming a part", "DEC-437", "DEC-436"), ("free text", "DEC-438", "DEC-439")]


@pytest.mark.parametrize("case, target, changer", PARTIAL, ids=[case[0] for case in PARTIAL])
def test_s8_a_partial_supersession_never_drops_its_target(marina_ask, case, target, changer):
    """The failure line: the target of a partial supersession stays current. Asked by its title, its own text is in
    the bundle, it is not in ``merge.dropped``, none of its register chunks is marked not in force, and its changer
    is brought beside it."""
    bundle = marina_ask(T[target])
    assert _holds(bundle, target), f"{target} ({case}) is not in its own bundle: {support.paths(bundle)}"
    dropped = [entry for entry in bundle["merge"]["dropped"] if entry.get("id") == target]
    assert not dropped, f"{target} ({case}) is dropped as not current: {dropped}"
    _, spans = support.links_register()
    marked = [item["start_line"] for item, entry in support.register_items(bundle, spans)
              if entry == target and support._says_not_in_force(support.what_the_item_says(bundle, item, entry))]
    assert not marked, f"{target} ({case}) is marked not in force (its chunks at lines {marked})"
    assert _holds(bundle, changer), (
        f"{target} ({case}) is in its bundle, but its changer {changer} is not brought: {support.items(bundle)}")


def test_s8_one_hop_brings_at_most_twelve_records(marina_ask, marina_base_ask):
    """DAEO-lk03 cites twenty decisions; asked by its title (batches large enough that nothing is left for a
    continuation), the bundle brings some of them and at most 12."""
    question = T[support.LK_MANY]
    today = marina_base_ask(question, batch_size=50)
    assert _holds(today, support.LK_MANY) and not _held(today, support.MANY_IDS), support.paths(today)
    bundle = marina_ask(question, batch_size=50)
    brought = _held(bundle, support.MANY_IDS)
    assert brought, f"the bundle for {question!r} brings none of {support.LK_MANY}'s twenty sources"
    assert len(brought) <= support.HOP_LIMIT, (
        f"one hop brought {len(brought)} records (at most {support.HOP_LIMIT}): {brought}")
    assert not bundle.get("continuation"), "premise: the batches left a continuation, so the count is not whole"


def test_s8_the_hop_comes_after_todays_closure_chunks(marina_ask):
    """Asked by DAEO-lk01's title, the chunks of the records today's closure reaches (the ticket and DAEO-lk02, by
    depends_on) come before the chunks the hop brings (DEC-411 and DEC-412)."""
    bundle = marina_ask(T[support.LK_TICKET])
    closure = {support.FRONT_RELS[support.LK_TICKET], support.FRONT_RELS[support.LK_DEPENDENT]}
    hop = [index for index, item in enumerate(bundle["evidence"])
           if any(support.TEXT_OF[rid] in item.get("text", "") for rid in ("DEC-411", "DEC-412"))]
    assert hop, f"the hop brought nothing for {T[support.LK_TICKET]!r}: {support.items(bundle)}"
    last = max(index for index, item in enumerate(bundle["evidence"]) if item["path"] in closure)
    assert last < min(hop), (
        f"a hop chunk (at {min(hop)}) comes before a closure chunk (at {last}): {support.items(bundle)}")


# (case, the record the question names, a record the hop must not bring)
ONE_WAY = [
    ("CITES is not followed in: a cited decision does not bring the ticket", "DEC-411", support.LK_TICKET),
    ("AMENDS is not followed out: a changer does not bring the decision it changes", "DEC-431", "DEC-432"),
    ("UNDER is not followed in: a governing decision does not bring the decision under it", "DEC-423", "DEC-421"),
    ("OF_TASK is not followed in: a task does not bring its checkpoint", support.LK_TASK, support.LK_CHECKPOINT),
    ("one hop, not two: DEC-421 does not bring DEC-424, which DEC-422 is under", "DEC-421", "DEC-424"),
]


@pytest.mark.parametrize("case, named, never", ONE_WAY, ids=[case[0].split(":")[0] for case in ONE_WAY])
def test_s8_the_hop_follows_each_link_its_one_way_once(marina_ask, case, named, never):
    """A guard (passes on the integrated code): the hop's directions and its single step, as S8 states them."""
    bundle = marina_ask(T[named])
    assert _holds(bundle, named), f"premise: {named} is not in its own bundle: {support.paths(bundle)}"
    assert not _holds(bundle, never), f"{case}; it is: {support.items(bundle)}"


TODAY = [("plain", support.WEATHER, {}), ("unknown id", f"{support.WEATHER} DEC-999", {}),
         ("batched", support.WEATHER, {"batch_size": 1})]


@pytest.mark.parametrize("case, question, kwargs", TODAY, ids=[case[0] for case in TODAY])
def test_s8_a_question_reaching_no_record_gets_todays_bundle(marina_ask, marina_base_ask, case, question, kwargs):
    """A guard: item for item and outside the evidence (``support.projection``), the integrated code's bundle."""
    before, after = support.projection(marina_base_ask(question, **kwargs)), support.projection(
        marina_ask(question, **kwargs))
    assert before["evidence"], f"premise: today's bundle for {question!r} is empty"
    assert after == before, (
        "the bundle changed: " + repr({key: [before.get(key), after.get(key)] for key in sorted(set(before) | set(after))
                                       if before.get(key) != after.get(key)}))
