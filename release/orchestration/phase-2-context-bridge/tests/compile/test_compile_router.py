"""``govbridge.route.router`` unit tests: deterministic route selection, reciprocal-rank fusion strictly within one
(section, authority-stratum) group, and dedup by (blob, overlapping line range) / record id with the canonical
occurrence winning over a SAME_AS_CANONICAL copy (ARCHITECTURE.md section 7.2).
"""
from govbridge.authority import records as recordsmod
from govbridge.route import router as routermod
from govbridge.route.router import RouteHit, RouteOccurrence


def _grammar():
    return recordsmod.load_grammar(recordsmod._default_grammar_path())


def test_select_routes_lexical_always_runs():
    assert "lexical" in routermod.select_routes({"text": "short"}, grammar=_grammar())


def test_select_routes_semantic_for_long_natural_language_queries():
    routes = routermod.select_routes({"text": "why does this mechanism exist in the first place"}, grammar=_grammar())
    assert "semantic" in routes
    assert "lexical" in routes


def test_select_routes_semantic_absent_for_short_queries():
    routes = routermod.select_routes({"text": "one two"}, grammar=_grammar())
    assert "semantic" not in routes


def test_select_routes_exact_for_id_shaped_token():
    routes = routermod.select_routes({"text": "what does D-0006 require"}, grammar=_grammar())
    assert "exact" in routes


def test_select_routes_exact_for_path_token():
    routes = routermod.select_routes({"text": "see runtime/src/init.rs for the definition"}, grammar=_grammar())
    assert "exact" in routes


def test_select_routes_code_for_symbol_shaped_token():
    routes = routermod.select_routes({"text": "who calls foo::bar in this module"}, grammar=_grammar())
    assert "code" in routes


def test_select_routes_explicit_override_wins_verbatim():
    routes = routermod.select_routes({"text": "irrelevant text", "routes": ["semantic"]}, grammar=_grammar())
    assert routes == ("semantic",)


def test_fuse_combines_ranks_reciprocally_and_sorts_descending():
    occ = RouteOccurrence(ref="records", commit="c1", path="a.yaml", version_status="CANONICAL")
    hit_a = RouteHit(unit_id="A", unit_kind="record", route="lexical", rank=1, occurrences=(occ,))
    hit_b = RouteHit(unit_id="B", unit_kind="record", route="lexical", rank=2, occurrences=(occ,))
    hit_a_semantic = RouteHit(unit_id="A", unit_kind="record", route="semantic", rank=3, occurrences=(occ,))

    fused = routermod.fuse({"lexical": [hit_a, hit_b], "semantic": [hit_a_semantic]}, rrf_k=60)
    ids = [f.hit.unit_id for f in fused]
    assert ids[0] == "A"  # A was boosted by both routes; B by only one
    a_fused = next(f for f in fused if f.hit.unit_id == "A")
    assert a_fused.routes == ("lexical", "semantic")
    assert abs(a_fused.fused_score - (1 / 61 + 1 / 63)) < 1e-9


def test_dedupe_prefers_canonical_occurrence_over_same_as_canonical():
    canonical = RouteOccurrence(ref="product", commit="c1", path="a.yaml", version_status="CANONICAL")
    same_as = RouteOccurrence(ref="records", commit="c2", path="a.yaml", version_status="SAME_AS_CANONICAL")
    hit_same_as = RouteHit(unit_id="X", unit_kind="chunk", route="lexical", rank=1, occurrences=(same_as,))
    hit_canonical = RouteHit(unit_id="X", unit_kind="chunk", route="semantic", rank=1, occurrences=(canonical,))

    out = routermod.dedupe([hit_same_as, hit_canonical])
    assert len(out) == 1
    assert out[0].occurrences[0].version_status == "CANONICAL"


def test_stratum_key_never_lets_score_cross_a_rank_or_lifecycle_boundary():
    active_rank1 = routermod.stratum_key("OWNER_DECISION", "ACTIVE")
    active_rank6 = routermod.stratum_key("EVIDENCE", "ACTIVE")
    superseded_rank1 = routermod.stratum_key("OWNER_DECISION", "SUPERSEDED")
    assert active_rank1 != active_rank6
    assert active_rank1 != superseded_rank1
