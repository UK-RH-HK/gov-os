"""``govbridge.gather.followup`` (REPAIR_DAG.yaml node R1-GA2; OD-BR-05 sections 3 and 6). Real-view tests build a
small, synthetic, THREE-ref Git fixture (``tests/fixtures/gather/followup/followup_repobuilder.py``) through the
REAL lexical/exact/code routes (``govbridge.route.real_routes``) and ``tests/fixtures/gather/test-facets.yaml``'s
lexical-only registry (never spawning the embedding subprocess, exactly like ``tests/gather/test_engine.py``'s own
real-view tests). Hermetic unit tests use ``FakeRouteSet``. Neither uses a public demonstration query text or a
run-1 answer (REPAIR-1 rule 2), and nothing here names a Review-8 item, an F-finding or a query-class id (OC-BR-02).
"""
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import pytest

from govbridge.core import taskctx as taskctxmod
from govbridge.core import view as viewmod
from govbridge.gather import engine as enginemod
from govbridge.gather import facets as facetsmod
from govbridge.gather import followup as followupmod
from govbridge.gather import identifiers as identifiersmod

FIXTURES_GATHER = Path(__file__).resolve().parents[1] / "fixtures" / "gather"
FIXTURES_FOLLOWUP = FIXTURES_GATHER / "followup"
sys.path.insert(0, str(FIXTURES_GATHER))
sys.path.insert(0, str(FIXTURES_FOLLOWUP))
import followup_repobuilder as repobuilder  # noqa: E402
from fake_routes import FakeRouteSet, make_hit  # noqa: E402

TEST_FACETS_PATH = str(FIXTURES_GATHER / "test-facets.yaml")


@pytest.fixture(autouse=True)
def _isolated_gather_env(tmp_path, monkeypatch):
    """R1-T1: hermetic -- no GOVBRIDGE_* leaked from another test, no process-cwd dependency (this file, and
    ``tests/fixtures/gather/followup/**``, are this node's own declared mutation_scope)."""
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    facetsmod.clear_cache()
    taskctxmod.reset()
    yield
    taskctxmod.reset()
    facetsmod.clear_cache()


def _query(text, id_="Q1", facets=None):
    q = {"id": id_, "text": text, "class": None, "subject": None}
    if facets is not None:
        q["facets"] = facets
    return q


@pytest.fixture
def built_repo(tmp_path):
    from govbridge.core import freshness
    br = repobuilder.build(tmp_path)
    r = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    assert r["trigger"] == "FULL"
    return br


@pytest.fixture
def real_routes_and_view(built_repo):
    from govbridge.route import real_routes
    routes = real_routes.build_real_routes(view_path=built_repo.view_path, repo=str(built_repo.root),
                                            registry_path=built_repo.registry_path)
    resolved_view = viewmod.resolve_view(viewmod.load_view(built_repo.view_path), repo=str(built_repo.root))
    return routes, resolved_view


def _run(built_repo, routes, resolved_view, text, max_followup_rounds=3):
    ctx = taskctxmod.TaskContext(source="test")
    return followupmod.gather_with_followup(
        _query(text, facets=["purpose"]), routes, task=ctx, batch_size=8, max_rounds=10, threads=1,
        max_followup_rounds=max_followup_rounds, resolved_view=resolved_view, repo=str(built_repo.root),
        facets_path=TEST_FACETS_PATH,
    )


def _paths(result) -> set:
    return {m["occurrence"]["path"] for m in result["merged"] if m.get("occurrence")}


def _trigger_values(result, kind) -> list:
    return [t["identifier"]["value"] for t in result["telemetry"]["follow_up_triggers"]
            if t["identifier"]["kind"] == kind]


# --- REPAIR_DAG.yaml node R1-GA2 acceptance check 1: four real input shapes, each reached within 3 rounds --------

def test_a_record_citing_an_id_defined_elsewhere_is_reached_within_three_rounds(built_repo, real_routes_and_view):
    routes, resolved_view = real_routes_and_view
    result = _run(built_repo, routes, resolved_view, "citing record explains a rule")
    assert result["followup_rounds"] <= 3
    assert repobuilder.BuiltRepo.id_defined_elsewhere in _trigger_values(result, identifiersmod.KIND_RECORD_ID)
    assert "area_two/RECORD-DEFINED.md" in _paths(result)
    # the trigger is recorded against (at least) one item that carried it (REPAIR_PLAN.md section 2.5: "records
    # its trigger") -- the SAME path can legitimately surface as more than one merged item (a whole-chunk lexical
    # hit and a precise, exact-route occurrence are different content-identity units, never force-collapsed).
    definition_items = [m for m in result["merged"] if m["occurrence"]["path"] == "area_two/RECORD-DEFINED.md"]
    assert definition_items
    all_triggers = [p["trigger"] for m in definition_items for p in m["provenance"] if p["trigger"] is not None]
    assert any(t["value"] == repobuilder.BuiltRepo.id_defined_elsewhere for t in all_triggers)


def test_a_function_whose_tests_live_in_another_directory_is_reached_within_three_rounds(
        built_repo, real_routes_and_view):
    routes, resolved_view = real_routes_and_view
    result = _run(built_repo, routes, resolved_view, "harness test widget mod_a")
    assert result["followup_rounds"] <= 3
    paths = _paths(result)
    assert "area_three/lib.rs" in paths          # the definition of compute_zed
    assert "area_four/tests/test_lib.rs" in paths  # its test, in a DIFFERENT top-level directory
    lib_item = next(m for m in result["merged"] if m["occurrence"]["path"] == "area_three/lib.rs")
    assert any(p["trigger"] is not None for p in lib_item["provenance"])


def test_a_joined_path_literal_is_reached_within_three_rounds(built_repo, real_routes_and_view):
    routes, resolved_view = real_routes_and_view
    result = _run(built_repo, routes, resolved_view, "load values path join area_data")
    assert result["followup_rounds"] <= 3
    assert repobuilder.BuiltRepo.joined_data_path in _trigger_values(result, identifiersmod.KIND_JOINED_PATH_LITERAL)
    assert "area_data/values.yaml" in _paths(result)
    data_items = [m for m in result["merged"] if m["occurrence"]["path"] == "area_data/values.yaml"]
    resolved_items = [m for m in data_items if m["resolution"] == "HEURISTIC_JOINED_PATH"]
    assert resolved_items, [m["resolution"] for m in data_items]
    triggers = [p["trigger"] for p in resolved_items[0]["provenance"] if p["trigger"] is not None]
    assert any(t["kind"] == identifiersmod.KIND_JOINED_PATH_LITERAL for t in triggers)


def test_a_comment_requirement_citation_is_reached_within_three_rounds_and_resolves_to_its_section(
        built_repo, real_routes_and_view):
    routes, resolved_view = real_routes_and_view
    result = _run(built_repo, routes, resolved_view, "enforce budget rule engine")
    assert result["followup_rounds"] <= 3
    assert "runtime/engine.rs" in _paths(result)
    doc_items = [m for m in result["merged"] if m["occurrence"]["path"] == repobuilder.BuiltRepo.requirement_doc]
    assert doc_items
    # resolved to the NUMBERED SECTION (line 3, "## 2 Budget rule"), never the whole document -- at least one of
    # the (possibly several, differently-routed) merged items for this path is the precise section slice.
    section_items = [m for m in doc_items if m["resolution"] == "HEURISTIC_COMMENT_SECTION"]
    assert section_items, [(m["resolution"], m["occurrence"]) for m in doc_items]
    assert section_items[0]["occurrence"]["line_start"] == 3
    triggers = [p["trigger"] for p in section_items[0]["provenance"] if p["trigger"] is not None]
    assert any(t["kind"] == identifiersmod.KIND_REQUIREMENT_CITATION for t in triggers)


def test_rust_mod_fn_test_path_resolves_by_trailing_segment(built_repo, real_routes_and_view):
    """REAL INPUT SHAPES item 2: the code layer's ``qualified_name`` for a free/mod-nested Rust fn carries no
    module path, so ``mod_a::test_widget`` (mentioned as plain text) must be resolved by its trailing segment."""
    routes, resolved_view = real_routes_and_view
    result = _run(built_repo, routes, resolved_view, "harness test widget mod_a")
    assert repobuilder.BuiltRepo.rust_test_path in _trigger_values(result, identifiersmod.KIND_RUST_TEST_PATH)
    harness_items = [m for m in result["merged"] if m["occurrence"]["path"] == "runtime/harness.rs"]
    resolved_items = [m for m in harness_items if m["resolution"] == "HEURISTIC_TRAILING_SEGMENT"]
    assert resolved_items, "the trailing-segment resolution must reach the real fn definition"


def test_commit_hashes_40_hex_and_short_are_extracted_and_resolved(built_repo, real_routes_and_view):
    """REAL INPUT SHAPES item 5: a 40-hex AND a short commit hash, both mentioned in prose."""
    routes, resolved_view = real_routes_and_view
    result = _run(built_repo, routes, resolved_view, "changelog fixed short form")
    assert repobuilder.BuiltRepo.commit_hash_40 in _trigger_values(result, identifiersmod.KIND_COMMIT)
    assert repobuilder.BuiltRepo.commit_hash_short in _trigger_values(result, identifiersmod.KIND_COMMIT)
    assert "area_six/CHANGELOG.md" in _paths(result)


def test_rust_mod_fn_ambiguous_trailing_segment_gets_a_distinct_heuristic_label(tmp_path):
    """The SAME trailing-segment fallback, but the bare name is genuinely ambiguous (two ``test_widget`` symbols in
    two different modules) -- REAL INPUT SHAPES item 2: "a distinct heuristic label where the full path is not
    unique". A separate, single-purpose fixture (``build_ambiguous_rust_test``) so the main fixture's own
    resolution stays unambiguous."""
    from govbridge.core import freshness
    from govbridge.route import real_routes

    br = repobuilder.build_ambiguous_rust_test(tmp_path)
    r = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    assert r["trigger"] == "FULL"
    routes = real_routes.build_real_routes(view_path=br.view_path, repo=str(br.root),
                                            registry_path=br.registry_path)
    ident = identifiersmod.Identifier(kind=identifiersmod.KIND_RUST_TEST_PATH, value="mod_a::test_widget")
    hits = followupmod.resolve_identifier(ident, routes, batch_size=8)
    assert len(hits) == 2  # never silently collapsed to the first match
    assert all(h.resolution == "HEURISTIC_TRAILING_SEGMENT_AMBIGUOUS" for h in hits)
    assert len({h.unit_id for h in hits}) == 2


# --- version reconciliation: a three-ref fixture, product-owned partition (REAL INPUT SHAPES item 6) --------------

def test_three_ref_fixture_version_reconciliation_reports_the_product_owned_difference(
        built_repo, real_routes_and_view):
    routes, resolved_view = real_routes_and_view
    result = _run(built_repo, routes, resolved_view, "citing record explains a rule")
    versions = result["versions"]
    assert versions["missing"] is False
    shared = next(item for item in versions["items"] if item["path"] == repobuilder.BuiltRepo.shared_path)
    assert shared["canonical_role"] == "product"  # never a hardcoded ref name -- decided by role, generically
    statuses = {r["ref_name"]: r["status"] for r in shared["per_ref"]}
    assert statuses["product"] == "CANONICAL"
    assert statuses["records"] == "DIFFERENT"
    assert statuses["evidence"] == "DIFFERENT"
    assert "differs at" in shared["summary"]


def test_a_path_untouched_across_refs_reports_identical_everywhere(built_repo, real_routes_and_view):
    routes, resolved_view = real_routes_and_view
    result = _run(built_repo, routes, resolved_view, "enforce budget rule engine")
    versions = result["versions"]
    doc_entry = next(item for item in versions["items"] if item["path"] == repobuilder.BuiltRepo.requirement_doc)
    statuses = {r["status"] for r in doc_entry["per_ref"]}
    assert statuses == {"CANONICAL", "IDENTICAL"}


def test_versions_facet_is_honestly_missing_when_nothing_resolved_a_path(real_routes_and_view):
    from govbridge.gather import versions as versionsmod
    _routes, resolved_view = real_routes_and_view
    report = versionsmod.versions_facet(resolved_view, [])
    assert report["missing"] is True
    assert report["items"] == []
    assert report["missing_reason"]


def test_versions_facet_is_honestly_missing_with_no_resolved_view_at_all():
    from govbridge.gather import versions as versionsmod
    report = versionsmod.versions_facet(None, ["some/path.md"])
    assert report["missing"] is True
    assert report["items"] == []


# --- the visited set prevents the same identifier from being resolved twice (REPAIR_PLAN.md section 2.5) ---------

def test_visited_set_resolves_the_same_identifier_only_once(built_repo, real_routes_and_view):
    """``ZK-0001`` is mentioned in the CITING record's own text AND (again) inside the record it cites -- a naive
    loop would try to resolve it twice; the visited set must not."""
    routes, resolved_view = real_routes_and_view
    result = _run(built_repo, routes, resolved_view, "citing record explains a rule")
    id_triggers = [t for t in result["telemetry"]["follow_up_triggers"]
                   if t["identifier"]["kind"] == identifiersmod.KIND_RECORD_ID
                   and t["identifier"]["value"] == repobuilder.BuiltRepo.id_citing]
    assert len(id_triggers) == 1
    assert result["visited_identifiers"].count({"kind": identifiersmod.KIND_RECORD_ID,
                                                 "value": repobuilder.BuiltRepo.id_citing}) == 1


# --- read-only store (BR-DAG-AMEND-R1-15): a gather with follow-up rounds against store.open_db_readonly ----------

def test_gather_with_followup_against_a_read_only_store_leaves_its_sha256_unchanged(
        built_repo, real_routes_and_view, tmp_path):
    """A gather run WITH triggered follow-up rounds, against a read-only store file, must not write -- neither
    ``govbridge.gather.identifiers``/``versions``/``followup``'s own SELECTs (which this node adds), nor whatever
    the underlying routes already do. This query deliberately stays on the lexical+exact path: the code route's
    own query-time write (``code/symbols.py``'s lazy ``ensure_indexed``) and hit classification's ``ensure_schema``
    call are BR-DAG-AMEND-R1-17's fix, routed to R1-XC in parallel (this node's checkpoint ``open_issues``)."""
    import hashlib

    from govbridge.core import store as storemod

    routes, resolved_view = real_routes_and_view
    db_path = storemod.db_path()
    before = hashlib.sha256(db_path.read_bytes()).hexdigest()

    os.chmod(db_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    os.chmod(db_path.parent, stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    try:
        ro_conn = storemod.open_db_readonly()
        ctx = taskctxmod.TaskContext(source="test")
        result = followupmod.gather_with_followup(
            _query("citing record explains a rule", facets=["purpose"]), routes, task=ctx, batch_size=8,
            max_rounds=10, threads=1, max_followup_rounds=3, resolved_view=resolved_view, repo=str(built_repo.root),
            facets_path=TEST_FACETS_PATH, conn=ro_conn,
        )
        ro_conn.close()
    finally:
        os.chmod(db_path.parent, stat.S_IRWXU)
        os.chmod(db_path, stat.S_IRUSR | stat.S_IWUSR)

    after = hashlib.sha256(db_path.read_bytes()).hexdigest()
    assert after == before
    assert result["followup_rounds"] >= 1
    assert len(result["merged"]) > 0


# --- resolve_identifier never raises, even for an identifier it cannot resolve at all -----------------------------

def test_resolve_identifier_of_an_unknown_kind_is_empty_not_an_error():
    ident = identifiersmod.Identifier(kind="not-a-real-kind", value="whatever")
    assert followupmod.resolve_identifier(ident, FakeRouteSet()) == []


def test_resolve_identifier_that_finds_nothing_is_empty_not_an_error(built_repo, real_routes_and_view):
    routes, _resolved_view = real_routes_and_view
    ident = identifiersmod.Identifier(kind=identifiersmod.KIND_RECORD_ID, value="ZK-9999")
    assert followupmod.resolve_identifier(ident, routes, batch_size=8) == []


# --- hermetic: follow-up rounds stop with the fixed vocabulary, never invented reasons -----------------------------

def test_followup_stops_with_no_unresolved_identifiers_when_the_base_round_has_nothing_to_chase():
    routes = FakeRouteSet(lexical=[make_hit("U1", "a/x.md", text="plain text with no identifiers at all")])
    ctx = taskctxmod.TaskContext(source="test")
    result = followupmod.gather_with_followup(_query("plain", facets=["purpose"]), routes, task=ctx, batch_size=8,
                                                threads=1, max_followup_rounds=3, facets_path=TEST_FACETS_PATH)
    assert result["followup_rounds"] == 0
    assert result["stop_reason"] in enginemod.STOP_REASONS


class _EverEscalatingExactRoutes:
    """A hermetic fake whose ``exact`` route always returns a hit naming a BRAND NEW record id (never repeating),
    so a follow-up loop that did not respect ``max_followup_rounds`` would run forever -- proves STOP_MAX_ROUNDS
    fires from the FOLLOW-UP loop itself, not just the base engine's own vocabulary."""

    def __init__(self):
        self.calls = 0

    def run(self, name, **kwargs):
        if name == "lexical":
            return [make_hit("SEED", "a/x.md", text="XZ-0000 is the seed identifier.")]
        if name == "exact":
            self.calls += 1
            nxt = f"XZ-{self.calls:04d}"
            return [make_hit(f"H{self.calls}", f"dir{self.calls}/f.md", text=f"{nxt} leads to more.")]
        return []


def test_followup_stops_at_max_followup_rounds_never_looping_forever():
    routes = _EverEscalatingExactRoutes()
    ctx = taskctxmod.TaskContext(source="test")
    result = followupmod.gather_with_followup(_query("XZ-0000 seed", facets=["purpose"]), routes, task=ctx,
                                                batch_size=8, threads=1, max_followup_rounds=3,
                                                facets_path=TEST_FACETS_PATH)
    assert result["followup_rounds"] == 3
    assert result["stop_reason"] == enginemod.STOP_MAX_ROUNDS


def test_a_round_with_more_identifiers_than_budget_stops_disclosed_never_silently_dropped():
    """OD-BR-05 section 5: real prose is dense with identifier-shaped tokens (a real-view measurement on this
    domain's own CONTROL-A found 81 candidates from just 31 items) -- a per-round cap is necessary, and exceeding
    it must stop with BUDGET_REACHED_WITH_UNRESOLVED, naming every deferred identifier, never silently dropping
    it."""
    text = " ".join(f"ZZ-{i:04d}" for i in range(5))  # 5 distinct id-grammar-shaped tokens, one round
    routes = FakeRouteSet(lexical=[make_hit("U1", "a/x.md", text=text)])
    ctx = taskctxmod.TaskContext(source="test")
    result = followupmod.gather_with_followup(_query("five ids", facets=["purpose"]), routes, task=ctx,
                                                batch_size=8, threads=1, max_followup_rounds=3,
                                                max_identifiers_per_round=2, facets_path=TEST_FACETS_PATH)
    assert result["followup_rounds"] == 1
    assert result["stop_reason"] == enginemod.STOP_BUDGET_REACHED_WITH_UNRESOLVED
    chased = {t["identifier"]["value"] for t in result["telemetry"]["follow_up_triggers"]}
    assert len(chased) == 2
    deferred = {i["value"] for i in result["telemetry"]["unresolved_identifiers"]}
    assert len(deferred) == 3
    assert chased.isdisjoint(deferred)
    assert chased | deferred == {f"ZZ-{i:04d}" for i in range(5)}
