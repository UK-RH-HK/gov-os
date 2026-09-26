"""``govbridge.route.real_routes`` (B6 open issue "the real B2/B3/B4 routes are not wired", closed by
I1/BR-AR-0009): the adapters translating the real lexical/semantic/code/exact routes into
``govbridge.route.router.RouteHit``, with REAL authority classification wired in (B4/BR-AR-0006 OI-3). A small,
self-contained fixture repo (never Review-8/Phase-2 content -- OC-BR-02): one YAML decision record and one Rust
function, classified through a minimal, purpose-built registry (``class_rules`` only -- distinct from every other
node's fixture registry, so this test never depends on their section_anchors verifying against THIS repo)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from govbridge.authority.classes import BRIDGE_STATE_PATH
from govbridge.core import freshness
from govbridge.route import real_routes


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))


def _build_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")

    (root / "spec" / "decisions").mkdir(parents=True)
    (root / "spec" / "decisions" / "D-0001.yaml").write_text(
        "id: D-0001\nstatus: ACTIVE\ntitle: a fixture decision about routing adapters\n", encoding="utf-8"
    )
    (root / "runtime" / "src").mkdir(parents=True)
    (root / "runtime" / "src" / "mod.rs").write_text("pub fn example_route_fn() {}\n", encoding="utf-8")

    state_path = root / BRIDGE_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "schema: bridge-orchestrator-state/1\n"
        "mandatory_bridge_inputs:\n  authority_classes: {}\n  items: []\n",
        encoding="utf-8",
    )

    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c1")
    _git(root, "branch", "-f", "product", "HEAD")
    return root


def _write_configs(tmp_path: Path) -> tuple:
    view_path = tmp_path / "canonical-view.yaml"
    view_path.write_text(
        "schema: govbridge-canonical-view/1\n"
        "view_id: rt-test-view\n"
        "refs:\n"
        "  - {name: records, ref: refs/heads/main, follow: tip, role: primary}\n"
        "  - {name: product, ref: refs/heads/product, follow: tip, role: product}\n"
        "partitions:\n"
        "  - {name: catchall, paths: ['**'], owner: records, fallback: [product]}\n",
        encoding="utf-8",
    )
    rules_path = tmp_path / "corpus-rules.yaml"
    rules_path.write_text(
        "schema: govbridge-corpus-rules/1\n"
        "rules:\n"
        "  - {id: INCLUDED, effect: INCLUDE, match: {}}\n",
        encoding="utf-8",
    )
    registry_path = tmp_path / "authority-registry.yaml"
    registry_path.write_text(
        "schema: govbridge-authority-registry/1\n"
        "class_rules:\n"
        "  - {glob: 'spec/decisions/*.yaml', class: ARCHITECTURE_DECISION}\n"
        "  - {glob: 'runtime/**', class: EVIDENCE}\n"
        "  - {glob: '**', class: UNCLASSIFIED}\n",
        encoding="utf-8",
    )
    return str(view_path), str(rules_path), str(registry_path)


def test_lexical_route_hits_carry_real_classification(tmp_path):
    repo_root = _build_repo(tmp_path)
    view_path, rules_path, registry_path = _write_configs(tmp_path)

    r = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)
    assert r["trigger"] == "FULL"

    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    hits = routes.lexical(text='"fixture decision"', k=5)
    assert hits
    assert any(h.authority_class == "ARCHITECTURE_DECISION" for h in hits), [h.authority_class for h in hits]
    assert all(h.lifecycle is not None for h in hits)
    assert all(h.delivery == "RETRIEVED" for h in hits)


def test_code_route_hits_carry_real_classification_and_real_definitions(tmp_path):
    # BR-DAG-AMEND-R1-17 item 6 (rule-5 correction, justified in this run's checkpoint `decisions`): this test used
    # to rely on codesymbols.ensure_indexed's OWN query-time build (the code layer had never been built -- no
    # freshness.run() call at all -- so the route's first-ever call parsed and persisted runtime/src/mod.rs itself,
    # on the spot). The code route now reads codesymbols.definitions_readonly/callers_readonly, which never build;
    # a real caller always builds the store first (the eager code-layer builder, govbridge.code.build), so this
    # test now does too -- never a narrower assertion, the same real classification and definitions as before.
    repo_root = _build_repo(tmp_path)
    view_path, rules_path, registry_path = _write_configs(tmp_path)
    r = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)
    assert r["trigger"] == "FULL"

    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    hits = routes.code(seeds=["example_route_fn"])
    assert hits
    definition_hits = [h for h in hits if h.unit_kind == "symbol"]
    assert definition_hits
    assert definition_hits[0].authority_class == "EVIDENCE"
    assert definition_hits[0].occurrences[0].path == "runtime/src/mod.rs"
    assert definition_hits[0].delivery == "RETRIEVED"


def test_exact_route_hits_carry_real_classification(tmp_path):
    # BR-DAG-AMEND-R1-17 item 6 (rule-5 correction, justified in this run's checkpoint `decisions`): this test used
    # to rely on authority.layer.classify_hit's OWN query-time ensure_schema() call to lazily create the (empty)
    # authority tables on a store that had never been built at all. classify_hit no longer does that, and
    # real_routes._conn() now opens the store via store.open_db_readonly() (which never creates a store that does
    # not exist yet) -- a real caller always builds the store first, so this test now does too.
    repo_root = _build_repo(tmp_path)
    view_path, rules_path, registry_path = _write_configs(tmp_path)
    r = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)
    assert r["trigger"] == "FULL"

    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    hits = routes.exact(text="example_route_fn")
    assert hits
    assert any(h.authority_class == "EVIDENCE" for h in hits), [h.authority_class for h in hits]


def test_safe_fts_query_never_raises_on_punctuated_free_text():
    from govbridge.route.real_routes import _safe_fts_query

    assert _safe_fts_query("consumers, dependents and uses of F1-DIRECTION") == (
        '"consumers" OR "dependents" OR "and" OR "uses" OR "of" OR "F1" OR "DIRECTION"'
    )
    assert _safe_fts_query('"already_quoted_phrase"') == '"already_quoted_phrase"'
    assert _safe_fts_query("") == '""'
    assert _safe_fts_query(None) == '""'


def test_lexical_route_survives_a_comma_bearing_free_text_query(tmp_path):
    repo_root = _build_repo(tmp_path)
    view_path, rules_path, registry_path = _write_configs(tmp_path)
    from govbridge.core import freshness
    freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)

    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    # this exact shape (a comma in free text) is what ARCHITECTURE.md section 7.3's "evidence both ways" query
    # templates produce, and what broke fts5 before _safe_fts_query existed.
    hits = routes.lexical(text="consumers, dependents and uses of example_route_fn", k=5)
    assert isinstance(hits, list)  # must not raise


# --- BR-DAG-AMEND-R1-17 items 5+6 combined acceptance ---------------------------------------------------------

def _write_all_route_facets(tmp_path: Path) -> str:
    """A minimal facets registry admitting every route (lexical, semantic, code, exact) across three facets, for
    this test alone -- distinct from tests/fixtures/gather/test-facets.yaml (which deliberately excludes semantic
    and code to stay fast)."""
    p = tmp_path / "all-route-facets.yaml"
    p.write_text(
        "schema: govbridge-facets/1\n"
        "purpose: minimal all-route facet registry for the R1-XC combined read-only acceptance test\n"
        "default_batch_size: 8\n"
        "default_max_rounds: 5\n"
        "default_threads: 1\n"
        "default_target_items: 8\n"
        "facets:\n"
        "  purpose:\n"
        "    routes: [lexical, semantic]\n"
        "    scope_classes: null\n"
        "    lifecycle_scope: null\n"
        "    extra_terms: []\n"
        "    min_share: 0.05\n"
        "  impl:\n"
        "    routes: [code]\n"
        "    extra_terms: []\n"
        "    min_share: 0.05\n"
        "  id_lookup:\n"
        "    routes: [exact]\n"
        "    extra_terms: []\n"
        "    min_share: 0.05\n"
        "class_facets: {}\n",
        encoding="utf-8",
    )
    return str(p)


def test_gather_every_route_and_classification_against_a_file_and_directory_read_only_store(tmp_path, monkeypatch):
    """The combined acceptance check for BR-DAG-AMEND-R1-17 items 5 and 6: before R1-XC this failed via THREE
    separate query-time write paths this run fixed -- real_routes._conn() (feeding authoritylayer.classify_hit's
    own ensure_schema() call), govbridge.code.symbols.ensure_indexed() called from real_routes' code route (both
    _shaped_code_conn() directly and, before this run split them, definitions()/callers()), and
    authority.layer.record_id_for_occurrence's own ensure_schema() call. A gather exercising EVERY route (lexical,
    semantic, code, exact) plus real hit classification, against a store that is genuinely read-only at the FILE
    level AND at its DIRECTORY level (chmod'd 0o444/0o555 -- the stricter of the two scenarios R1-GA1's own
    tests/core/test_scope_path_cache.py already covers for lexical/semantic), leaves the store file's sha256
    byte-identical."""
    import hashlib
    import os

    from govbridge.core import store as storemod
    from govbridge.gather import engine as enginemod

    # The real semantic route needs the shared, read-only model cache under the REAL $GOV_BRIDGE_HOME (this file's
    # own autouse _isolated_store fixture redirects it into an isolated tmp_path, for STORE isolation, exactly like
    # every other test here -- tests/semantic/conftest.py's own `built` fixture leaves it at its real default for
    # this exact reason). GOVBRIDGE_STORE (the index store itself) stays isolated either way.
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)

    repo_root = _build_repo(tmp_path)
    view_path, rules_path, registry_path = _write_configs(tmp_path)
    facets_path = _write_all_route_facets(tmp_path)

    r = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)
    assert r["trigger"] == "FULL"

    store_dir = storemod.store_root()
    db_path = storemod.db_path(store_dir)
    before_sha = hashlib.sha256(db_path.read_bytes()).hexdigest()

    os.chmod(db_path, 0o444)
    os.chmod(store_dir, 0o555)
    try:
        routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root),
                                                registry_path=registry_path)
        # "example_route_fn" is real content at every route: the .rs file itself (lexical/semantic chunk text,
        # code seed, and a literal git-grep match for exact) -- classified EVIDENCE by _write_configs' own registry
        # (runtime/**).
        query = {"id": "Q1", "text": "example_route_fn", "class": None, "subject": None,
                 "facets": ["purpose", "impl", "id_lookup"]}
        result = enginemod.gather(query, routes, seeds=["example_route_fn"], batch_size=8, max_rounds=5, threads=1,
                                   facets_path=facets_path)
    finally:
        os.chmod(store_dir, 0o755)
        os.chmod(db_path, 0o644)

    assert result["stop_reason"] in enginemod.STOP_REASONS
    merged_paths = [h["occurrences"][0]["path"] for h in result["merged"] if h["occurrences"]]
    assert merged_paths, "no route returned any hit at all -- this test proves nothing about classify_hit"
    assert "runtime/src/mod.rs" in merged_paths, merged_paths
    routes_run = {h["route"] for h in result["merged"]}
    assert routes_run == {"lexical", "semantic", "code", "exact"}, (
        f"not every route actually ran/contributed a hit: {routes_run}"
    )
    # real classification, through the now-read-only classify_hit/_conn() path -- never a placeholder: the
    # registry (_write_configs) classifies runtime/** as EVIDENCE, spec/decisions/*.yaml as ARCHITECTURE_DECISION,
    # and everything else (e.g. the bridge state file lexical/semantic also happen to surface) UNCLASSIFIED.
    code_hit_classes = {h["authority_class"] for h in result["merged"] if h["occurrences"][0]["path"] == "runtime/src/mod.rs"}
    assert code_hit_classes == {"EVIDENCE"}, (
        f"real classification did not run correctly through the read-only path: {code_hit_classes}"
    )
    merged_classes = {h.get("authority_class") for h in result["merged"]}
    assert merged_classes <= {"EVIDENCE", "ARCHITECTURE_DECISION", "UNCLASSIFIED"}, merged_classes

    after_sha = hashlib.sha256(db_path.read_bytes()).hexdigest()
    assert after_sha == before_sha, "the store file's bytes changed across a fully read-only gather run"
