"""``govbridge.gather.merge`` (REPAIR_DAG.yaml node R1-GA2): provenance-preserving deduplication, occurrence
collapse and the authority/lifecycle pass-through. Fully hermetic -- every hit here is a synthetic ``RouteHit``
(``tests/fixtures/gather/fake_routes.py``'s own idiom), never a real store or a public demonstration query
(REPAIR-1 rule 2). Nothing here names a Review-8 item, an F-finding or a query-class id (OC-BR-02).
"""
from __future__ import annotations

import sys
from pathlib import Path

from govbridge.authority import classes as classesmod
from govbridge.gather import merge as mergemod
from govbridge.route.router import RouteHit, RouteOccurrence

FIXTURES_GATHER = Path(__file__).resolve().parents[1] / "fixtures" / "gather"
sys.path.insert(0, str(FIXTURES_GATHER))
from fake_routes import make_hit  # noqa: E402


def _occ(ref, status, path="a/x.md", commit="c0", line_start=1, line_end=2, canonical_ref=None,
         canonical_commit=None):
    return RouteOccurrence(ref=ref, commit=commit, path=path, version_status=status, line_start=line_start,
                            line_end=line_end, canonical_ref=canonical_ref, canonical_commit=canonical_commit)


# --- provenance-preserving deduplication: the same item via three routes is one item, three provenance rows -------

def test_same_item_found_by_three_routes_merges_to_one_item_with_three_provenance_entries():
    occ = _occ("records", "CANONICAL")
    lex = RouteHit(unit_id="U1", unit_kind="occurrence", route="lexical", rank=1, occurrences=(occ,), text="t")
    sem = RouteHit(unit_id="U1", unit_kind="occurrence", route="semantic", rank=1, occurrences=(occ,), text="t")
    code = RouteHit(unit_id="U1", unit_kind="occurrence", route="code", rank=1, occurrences=(occ,), text="t")

    acc = mergemod.MergeAccumulator()
    acc.add([lex], facet="purpose", round="base")
    acc.add([sem], facet="purpose", round="base")
    acc.add([code], facet="followup:symbol", round=1, trigger={"kind": "symbol", "value": "U1"})
    items = acc.items()

    assert len(items) == 1
    item = items[0]
    assert len(item.provenance) == 3
    routes_seen = sorted(p.route for p in item.provenance)
    assert routes_seen == ["code", "lexical", "semantic"]
    # the follow-up contribution's own trigger is preserved verbatim, the base ones carry none.
    triggers = [p.trigger for p in item.provenance]
    assert triggers.count(None) == 2
    assert {"kind": "symbol", "value": "U1"} in triggers


def test_merge_hit_stream_convenience_form_matches_the_accumulator():
    occ = _occ("records", "CANONICAL")
    h1 = RouteHit(unit_id="U9", unit_kind="occurrence", route="lexical", rank=1, occurrences=(occ,), text="t")
    h2 = RouteHit(unit_id="U9", unit_kind="occurrence", route="exact", rank=1, occurrences=(occ,), text="t")
    items = mergemod.merge_hit_stream([
        ([h1], "lexical", "purpose", "base", None),
        ([h2], "exact", "followup:record_id", 1, {"kind": "record_id", "value": "U9"}),
    ])
    assert len(items) == 1
    assert len(items[0].provenance) == 2


def test_distinct_items_never_collapse():
    occ = _occ("records", "CANONICAL")
    h1 = RouteHit(unit_id="U1", unit_kind="occurrence", route="lexical", rank=1, occurrences=(occ,), text="t")
    h2 = RouteHit(unit_id="U2", unit_kind="occurrence", route="lexical", rank=1, occurrences=(occ,), text="t")
    acc = mergemod.MergeAccumulator()
    acc.add([h1, h2], facet="purpose", round="base")
    assert len(acc.items()) == 2


def test_chunk_hits_dedupe_by_blob_and_line_span_like_the_router():
    """``dedupe_key`` for a "chunk" hit is (blob marker, path, line_start, line_end) -- the SAME identity
    ``govbridge.route.router.dedupe`` already uses, never a second notion invented here."""
    h1 = make_hit("A", "same/path.md")
    h2 = make_hit("B", "same/path.md")  # different unit_id, SAME (path, line_start, line_end) -> same chunk
    acc = mergemod.MergeAccumulator()
    acc.add([h1], facet="purpose", round="base")
    acc.add([h2], facet="purpose", round="base")
    assert len(acc.items()) == 1


# --- occurrence collapse: one canonical occurrence, plus a per-ref summary (never a raw multi-row dump) -----------

def test_three_ref_fixture_collapses_to_one_canonical_occurrence_plus_a_ref_summary():
    """REAL INPUT SHAPES item 6: "the three-ref view, where the same path has different blobs per ref"."""
    occs = (
        _occ("records", "CANONICAL"),
        _occ("product", "SAME_AS_CANONICAL"),
        _occ("evidence", "HISTORICAL_VERSION"),
    )
    hit = RouteHit(unit_id="U1", unit_kind="chunk", route="lexical", rank=1, occurrences=occs, text="t")
    canonical, ref_summary = mergemod.collapse_occurrences(hit.occurrences)
    assert canonical.ref == "records"
    assert canonical.version_status == "CANONICAL"
    assert ref_summary["identical"] == ["records", "product"]
    assert ref_summary["different"] == ["evidence"]
    assert "identical at refs records, product" in ref_summary["note"]
    assert "differs at evidence" in ref_summary["note"]


def test_merged_item_to_dict_carries_exactly_one_occurrence_row_plus_a_ref_summary():
    occs = (_occ("records", "CANONICAL"), _occ("product", "HISTORICAL_VERSION"))
    hit = RouteHit(unit_id="U1", unit_kind="chunk", route="lexical", rank=1, occurrences=occs, text="t")
    acc = mergemod.MergeAccumulator()
    acc.add([hit], facet="purpose", round="base")
    d = acc.items()[0].to_dict()
    assert isinstance(d["occurrence"], dict)  # ONE row, never a list
    assert d["occurrence"]["ref"] == "records"
    assert d["ref_summary"]["different"] == ["product"]
    assert "occurrences" not in d  # the raw, multi-row field is never surfaced from a merged item


def test_history_only_and_absent_occurrences_are_bucketed_never_dropped():
    occs = (_occ("records", "CANONICAL"), _occ("history-1", "HISTORY_ONLY"), _occ("evidence", "ABSENT"))
    canonical, ref_summary = mergemod.collapse_occurrences(occs)
    assert canonical.ref == "records"
    assert ref_summary["history_only"] == ["history-1"]
    assert ref_summary["absent"] == ["evidence"]


def test_collapse_occurrences_of_a_single_occurrence_is_a_no_op_summary():
    occs = (_occ("records", "CANONICAL"),)
    canonical, ref_summary = mergemod.collapse_occurrences(occs)
    assert canonical.ref == "records"
    assert ref_summary["identical"] == ["records"]
    assert ref_summary["different"] == [] and ref_summary["history_only"] == [] and ref_summary["absent"] == []


def test_collapse_occurrences_of_empty_tuple_is_honest_not_a_crash():
    canonical, ref_summary = mergemod.collapse_occurrences(())
    assert canonical is None
    assert ref_summary["note"] == "no occurrence"


# --- authority/lifecycle: unchanged pass-through; a superseded/withdrawn item is filtered to E with its banner ----

def test_superseded_item_keeps_its_evidence_withdrawn_class_and_exposes_its_banner():
    occ = _occ("records", "CANONICAL")
    hit = RouteHit(unit_id="OLD-1", unit_kind="record", route="lexical", rank=1, occurrences=(occ,),
                   text="an old, superseded record", authority_class="EVIDENCE_WITHDRAWN", lifecycle="SUPERSEDED")
    acc = mergemod.MergeAccumulator()
    acc.add([hit], facet="decisions_history", round="base")
    item = acc.items()[0]
    d = item.to_dict()
    assert d["authority_class"] == "EVIDENCE_WITHDRAWN"
    assert d["lifecycle"] == "SUPERSEDED"
    expected_banner = classesmod.ALL_CLASSES["EVIDENCE_WITHDRAWN"].banner
    assert d["banner"] == expected_banner
    assert "WITHDRAWN" in d["banner"]
    assert d["allowed_sections"] == ["E", "F"]
    assert "A" not in d["allowed_sections"]


def test_merge_never_invents_or_upgrades_an_authority_class():
    """REPAIR_PLAN.md section 2.7: "authority and lifecycle filtering unchanged (A only from the resolver)" --
    merge is a pure pass-through of whatever the resolver/route already decided."""
    occ = _occ("records", "CANONICAL")
    hit = RouteHit(unit_id="U1", unit_kind="chunk", route="lexical", rank=1, occurrences=(occ,), text="t",
                   authority_class=None, lifecycle=None)
    acc = mergemod.MergeAccumulator()
    acc.add([hit], facet="purpose", round="base")
    d = acc.items()[0].to_dict()
    assert d["authority_class"] is None
    assert d["lifecycle"] is None
    assert d["banner"] is None


def test_ladder_class_carries_no_banner_and_is_admissible_anywhere():
    assert mergemod.banner_for("EVIDENCE") is None
    assert mergemod.allowed_sections_for("EVIDENCE") == ()
    assert not mergemod.is_non_ladder("EVIDENCE")
    assert mergemod.is_non_ladder("EVIDENCE_WITHDRAWN")


def test_banner_and_sections_for_unknown_class_are_honestly_empty():
    assert mergemod.banner_for(None) is None
    assert mergemod.banner_for("NOT-A-REAL-CLASS") is None
    assert mergemod.allowed_sections_for("NOT-A-REAL-CLASS") == ()
