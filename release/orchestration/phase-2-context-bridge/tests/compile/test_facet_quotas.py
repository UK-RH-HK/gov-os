"""REPAIR_DAG.yaml node R1-GA3 acceptance (REPAIR_PLAN.md section 2.8, RC-4): "facet quotas (a minimum share for
every requested facet that has candidates) and a drop order that is round-robin across facets; a resolution label
is never a global sort key; per-facet drops are disclosed with continuation handles."

A synthetic fixture puts a "small" facet's tiny candidate set BEHIND a "big" facet's 300-candidate set, ranked
strictly worse in every way ``sort_key`` compares (same class, same lifecycle, and enumerated LAST in the merged
list, so its fused score is the smallest of all). Without a facet quota, ordinary rank-first budget dropping would
starve "small" completely; the quota must keep it. Every id here is GQ-* (Gather Quotas), unrelated to
Review-8/Phase-2 (OC-BR-02); this file reuses ``tests/compile/conftest.py``'s shared fixture repo/view/registry
(the same one node B6 and every sibling compile test already share) -- only the facet registry and the budget
profile are this node's own, small, synthetic overrides.
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

from govbridge.compile import packet as packetmod
from govbridge.route.router import RouteHit, RouteOccurrence, RouteSet

BIG_N = 300
SMALL_N = 3


def _pool(n: int, route: str, unit_prefix: str, path: str) -> list:
    hits = []
    for i in range(n):
        # a DISTINCT path per pool: router.dedupe_key keys a "chunk" hit on (blob-path, line_start, line_end), so
        # two pools sharing one path with overlapping line numbers would silently collide and dedupe into each
        # other -- never the intent of this fixture (each pool must arrive at the merge as its own distinct set
        # of items).
        occ = RouteOccurrence(ref="records", commit="0" * 40, path=path, version_status="ABSENT",
                               line_start=i + 1, line_end=i + 1)
        hits.append(RouteHit(unit_id=f"{unit_prefix}-{i:04d}", unit_kind="chunk", route=route, rank=i + 1,
                              occurrences=(occ,), text=f"{unit_prefix} candidate {i}: some retrieved content",
                              authority_class="EVIDENCE", lifecycle="ACTIVE"))
    return hits


BIG_POOL = _pool(BIG_N, "lexical", "GQ-BIG", "fixtures/gq/big.md")
SMALL_POOL = _pool(SMALL_N, "semantic", "GQ-SMALL", "fixtures/gq/small.md")


def _paged(pool: list):
    def _route(text=None, k=8, offset=0, exclude=None, exclude_counter=None, page_info_out=None,
               scope_classes=None, lifecycle_scope=None, **kw):
        page = pool[offset:offset + (k or len(pool))]
        if page_info_out is not None:
            next_off = offset + len(page)
            page_info_out["next_offset"] = next_off if next_off < len(pool) else None
            page_info_out["total_matching_chunks"] = len(pool)
        return list(page)
    return _route


def _write_facets(tmp_path: Path) -> str:
    p = tmp_path / "gq-facets.yaml"
    p.write_text("""schema: govbridge-facets/1
default_batch_size: 350
default_target_items: 400
default_max_rounds: 3
default_threads: 1
facets:
  big:
    routes: [lexical]
    scope_classes: null
    lifecycle_scope: null
    extra_terms: []
    min_share: 0.02
    # govbridge.gather.facets.Facet.effective_target_items falls back to the PARAMETERLESS
    # default_target_items() (the real, global config/facets.yaml's own default_target_items: 16) whenever a row
    # does not set its own target_items -- it never threads a custom facets_path through that fallback. Set
    # explicitly here so this fixture's own facets.yaml is genuinely self-contained.
    target_items: 320
  small:
    routes: [semantic]
    scope_classes: null
    lifecycle_scope: null
    extra_terms: []
    min_share: 0.5
    target_items: 10
class_facets: {}
""", encoding="utf-8")
    return str(p)


def _write_budgets(tmp_path: Path) -> str:
    p = tmp_path / "gq-budgets.yaml"
    p.write_text("""schema: govbridge-budgets/1
rrf_k: 60
graph_neighbour_depth: 1
parent_expansion_top_n: 3
max_slice_chars: 1600
per_item_cap_kb: 24
section_header_bytes: 256
profiles:
  gq-tiny:
    total_kb: 50
    section_caps_kb: {A: null, B: 1, C: 1, D: 1, E: 1, F: 1, G: 1, H: 2, I: 3, J: 3}
    g_fanout: {}
code_test_surfaces:
  source_extensions: []
  source_dirs: []
  test_path_globs: []
gather:
  max_items_per_query: 5000
  max_bytes_per_query: 20000000
  wall_time_budget_seconds: 60
""", encoding="utf-8")
    return str(p)


def test_facet_quota_keeps_the_small_facets_minimum_share(fixture_repo, view_path, registry_path,
                                                            task_spec_factory, tmp_path):
    routes = RouteSet(lexical=_paged(BIG_POOL), semantic=_paged(SMALL_POOL))
    task_spec = task_spec_factory(view_path, required_inputs=[], queries=[
        {"id": "GQ-Q1", "text": "a natural language query about gather quotas fixtures indeed"},
    ], budget_profile="gq-tiny")
    facets_path = _write_facets(tmp_path)
    budgets_path = _write_budgets(tmp_path)

    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(fixture_repo.root),
                                       registry_path=registry_path, budgets_path=budgets_path,
                                       facets_path=facets_path)
    assert result["status"] in (packetmod.STATUS_OK, packetmod.STATUS_BLOCKED_BUDGET)

    h_items = result["sections"]["H"]
    h_ids = {i.unit_id for i in h_items}
    small_kept = {u for u in h_ids if u.startswith("GQ-SMALL")}
    big_kept = {u for u in h_ids if u.startswith("GQ-BIG")}

    assert len(small_kept) == SMALL_N, (
        f"the 'small' facet's own minimum share must keep ALL {SMALL_N} of its candidates even though every one "
        f"of them ranks WORSE (enumerated last, so lowest fused_score) than all {BIG_N} 'big' candidates -- "
        f"got {sorted(small_kept)}"
    )
    assert big_kept, "the 'big' facet must still get most of the remaining budget"
    assert len(big_kept) < BIG_N, "the tiny H cap must still drop MOST of the big facet -- proves this is a real test"

    # section A is untouched by facet quotas (REPAIR_DAG.yaml node R1-GA3 acceptance check 1).
    assert result["sections"]["A"] == []

    # per-item facet tags (REPAIR_PLAN.md section 2.8): every H item carries its own facet tag, and the tag is the
    # facet that actually produced it (route-differentiated here, so there is no ambiguity to disclose).
    for item in h_items:
        assert item.facet_tags, item.unit_id
    small_items = [i for i in h_items if i.unit_id.startswith("GQ-SMALL")]
    assert all("small" in i.facet_tags for i in small_items)
    big_items = [i for i in h_items if i.unit_id.startswith("GQ-BIG")]
    assert all("big" in i.facet_tags for i in big_items)
    # per-item query tags: every kept item carries the query id that surfaced it.
    assert all("GQ-Q1" in i.query_ids for i in h_items)

    # the tags are VISIBLE to a reader, not just internal Python state: both the manifest row and the rendered
    # packet text itself carry them (REPAIR_PLAN.md section 2.8: "so an agent can find 'the tests for query X'").
    h_manifest_rows = {r["unit"]["id"]: r for r in result["manifest"]["sections"]["H"]["items"]}
    a_small_row = h_manifest_rows[next(iter(small_kept))]
    assert a_small_row["facet_tags"] == ["small"]
    assert a_small_row["query_ids"] == ["GQ-Q1"]
    assert "facets: ['small']" in result["rendered"]
    assert "queries: ['GQ-Q1']" in result["rendered"]

    # a facet drop record carries a continuation handle, never a bare "BUDGET" with no path forward. H is not one
    # of budgets.compact_drops's default compact_sections (only G is), so it keeps its raw per-item drop shape.
    h_drops = result["drops"].get("H") or []
    assert h_drops, "the big facet must have produced BUDGET drops given the tiny H cap"
    assert all(d.get("continuation") for d in h_drops)
    assert all(d.get("facet") == "big" for d in h_drops), "only the big facet should be over its own share here"


def test_a_query_with_only_one_candidate_facet_needs_no_quota_machinery(fixture_repo, view_path, registry_path,
                                                                          task_spec_factory, tmp_path):
    """A facet with NO candidates at all is disclosed as MISSING, never silently absent, and never blocks the
    facet(s) that DO have candidates from being placed."""
    routes = RouteSet(lexical=_paged(BIG_POOL[:5]))  # "small" (semantic) gets no route at all -> 0 candidates
    task_spec = task_spec_factory(view_path, required_inputs=[], queries=[
        {"id": "GQ-Q2", "text": "another natural language query, lexical only please"},
    ], budget_profile="gq-tiny")
    facets_path = _write_facets(tmp_path)
    budgets_path = _write_budgets(tmp_path)

    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(fixture_repo.root),
                                       registry_path=registry_path, budgets_path=budgets_path,
                                       facets_path=facets_path)
    missing = [n for n in result["manifest"]["notices"] if n["type"] == "FACET_MISSING" and n["query_id"] == "GQ-Q2"]
    assert any(n["facet"] == "small" for n in missing), result["manifest"]["notices"]
    kept_ids = {i.unit_id for i in result["sections"]["H"]}
    assert kept_ids, "the big facet's own candidates must still be placed"


def test_no_facet_tags_falls_back_to_plain_enforce_section_unaffected(fixture_repo, view_path, registry_path,
                                                                        task_spec_factory):
    """A compile with no queries at all (only seeds/mandatory inputs, the pre-R1-GA3 shape) never routes through
    the facet-quota machinery -- ``budgets.enforce_section_with_quotas`` degrades to plain ``enforce_section``
    whenever a section carries no ``facet_tags`` at all, so this compile's own sections are unaffected byte for
    byte by this node's existence."""
    task_spec = task_spec_factory(view_path, required_inputs=[], queries=[])
    result = packetmod.compile_packet(task_spec, repo=str(fixture_repo.root), registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK


# ---------------------------------------------------------------------------------------------------------------
# BR-DAG-AMEND-R1-15: "QUERY COMMANDS ARE READ-ONLY." A `compile_packet` whose queries now run through
# `govbridge.gather.followup.gather_with_followup` (this node's own wiring) must not write to the store either --
# reuses R1-GA1's own lexical-only fixture/facets registry (`tests/fixtures/gather/gather_repobuilder.py`,
# `tests/fixtures/gather/test-facets.yaml`), the SAME one `tests/core/test_scope_path_cache.py`'s own read-only
# proof uses, for the SAME reason: no embedding subprocess, no code-layer dependency (R1-XC's own separate,
# still-open item), just the real lexical route through this node's own new query-loop/gather integration.
# ---------------------------------------------------------------------------------------------------------------

_FIXTURES_GATHER = Path(__file__).resolve().parents[1] / "fixtures" / "gather"
sys.path.insert(0, str(_FIXTURES_GATHER))
import gather_repobuilder  # noqa: E402

_TEST_FACETS_PATH = str(_FIXTURES_GATHER / "test-facets.yaml")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_compile_against_a_read_only_store_never_writes_to_it(monkeypatch, tmp_path):
    from govbridge.core import store as storemod
    from govbridge.core import freshness
    from govbridge.route import real_routes

    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    br = gather_repobuilder.build(tmp_path)
    r1 = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    assert r1["trigger"] == "FULL"

    db_path = storemod.db_path(storemod.store_root())
    before_sha = _sha256_file(db_path)

    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-RO", "role": "test", "objective": "x",
        "view": br.view_path, "required_inputs": [], "seeds": [],
        "queries": [{"id": "RO-Q1", "text": gather_repobuilder.TERM, "routes": ["lexical"]}],
        "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED"], "budget_profile": "bounded-builder",
    }
    routes = real_routes.build_real_routes(view_path=br.view_path, repo=str(br.root),
                                            registry_path=br.registry_path)

    os.chmod(db_path, 0o444)
    try:
        result = packetmod.compile_packet(task_spec, routes=routes, repo=str(br.root),
                                           registry_path=br.registry_path, facets_path=_TEST_FACETS_PATH)
    finally:
        os.chmod(db_path, 0o644)

    assert result["status"] == packetmod.STATUS_OK
    gathered = result["gather_results"]["RO-Q1"]["merged"]
    assert gathered, "the read-only compile must still find real evidence, not silently nothing"

    after_sha = _sha256_file(db_path)
    assert after_sha == before_sha, "the store file's bytes changed across a read-only compile"
