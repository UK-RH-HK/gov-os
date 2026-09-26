"""REPAIR_DAG.yaml node R1-GA3 acceptance (REPAIR_PLAN.md section 2.8, RC-5: "pointer-only delivery"): "code and
test items carry their definition body slice (max_slice_chars, larger for a facet's top items); semantic items
carry chunk text; content already present is cited by item id... no symbol or semantic item has a 0-byte body."

``govbridge.route.real_routes`` (not this node's file to edit) still attaches only a bare
``"{kind} {qualified_name}"`` signature for a code-route symbol hit, an edge label for a CALLS/TESTS/READS_KEY/
CITED occurrence hit, and NO text at all for a semantic hit -- this node repairs it at the COMPILE layer
(``Compiler.item_from_hit``, via ``govbridge.compile.overflow.needs_content_slice``/``read_content_slice``). Every
id here is CS-* (Content Slices), unrelated to Review-8/Phase-2 (OC-BR-02); this file reuses
``tests/compile/conftest.py``'s shared fixture repo/view/registry (``compile_repobuilder.CODE_PATH`` already
carries a real, git-committed Rust function this file slices).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import compile_repobuilder as repobuilder

from govbridge.compile import packet as packetmod
from govbridge.compile import validate as validatemod
from govbridge.route.router import FAKE_ROUTES, FusedHit, RouteHit, RouteOccurrence, RouteSet


def _compiler(fixture_repo, view_path, registry_path, max_slice_chars=None, top_n=None):
    return packetmod.Compiler(task_spec={}, routes=FAKE_ROUTES, repo=str(fixture_repo.root), view_path=view_path,
                               registry_path=registry_path, rrf_k=60, graph_depth=1,
                               max_slice_chars=max_slice_chars, top_n=top_n)


def test_code_symbol_pointer_gets_its_full_definition_slice(fixture_repo, view_path, registry_path):
    """A code-route SYMBOL hit's own ``text`` is a bare ``"{kind} {qualified_name}"`` pointer
    (``real_routes._code_hit_from_definition``) -- the compiler must append the definition's own body, read fresh
    from Git at the occurrence's own (already-exact) line span, never just the pointer alone."""
    c = _compiler(fixture_repo, view_path, registry_path)
    occ = RouteOccurrence(ref="product", commit=fixture_repo.c1, path=repobuilder.CODE_PATH,
                           version_status="CANONICAL", line_start=2, line_end=4)
    hit = RouteHit(unit_id="fn:cx_rule", unit_kind="symbol", route="code", rank=1, occurrences=(occ,),
                   text="fn cx_rule", authority_class="EVIDENCE", lifecycle="ACTIVE")
    item = c.item_from_hit(FusedHit(hit=hit, fused_score=1.0, routes=("code",)), "G")

    assert item.text.startswith("fn cx_rule"), "the original pointer line must be kept, never discarded"
    assert "pub fn cx_rule() -> bool" in item.text, item.text
    assert "true" in item.text, item.text
    assert item.bytes_len() > 0


def test_semantic_chunk_with_no_text_gets_content_fetched(fixture_repo, view_path, registry_path):
    """``real_routes.semantic_route`` attaches ``text=None`` to every hit -- the exact "semantic hits with 0
    bytes" defect CAUSE_ANALYSIS.md measured. The compiler must never place a 0-byte semantic item."""
    c = _compiler(fixture_repo, view_path, registry_path)
    occ = RouteOccurrence(ref="product", commit=fixture_repo.c1, path=repobuilder.CODE_PATH,
                           version_status="CANONICAL", line_start=1, line_end=4)
    hit = RouteHit(unit_id="chunk:cx_module:1-4", unit_kind="chunk", route="semantic", rank=1, occurrences=(occ,),
                   text=None, authority_class="EVIDENCE", lifecycle="ACTIVE")
    item = c.item_from_hit(FusedHit(hit=hit, fused_score=1.0, routes=("semantic",)), "H")

    assert item.bytes_len() > 0, "a semantic item must never have a 0-byte body"
    assert "cx_rule" in item.text


def test_top_item_gets_a_larger_slice_than_a_non_top_item(fixture_repo, view_path, registry_path, tmp_path):
    """REPAIR_PLAN.md section 2.8: "a larger slice for the facet's top items". A big synthetic file, a tiny
    ``max_slice_chars``, and ``top=True`` vs ``top=False`` on the SAME occurrence must yield different slice
    lengths -- the larger one strictly longer, both non-empty and both marked with the SAME truncation
    convention (never silently different formats)."""
    big_path = tmp_path / "big.rs"
    body_lines = [f"    let line_{i} = {i};" for i in range(400)]
    big_text = "pub fn big_fn() -> i32 {\n" + "\n".join(body_lines) + "\n    0\n}\n"
    big_path.write_text(big_text, encoding="utf-8")
    repobuilder.write(fixture_repo.root, "src/big_fn.rs", big_text)
    import subprocess
    subprocess.run(["git", "-C", str(fixture_repo.root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(fixture_repo.root), "-c", "user.email=t@example.com", "-c", "user.name=t",
                     "commit", "-q", "-m", "content-slice fixture: a big function"], check=True, capture_output=True)
    commit = subprocess.run(["git", "-C", str(fixture_repo.root), "rev-parse", "HEAD"],
                             check=True, capture_output=True, text=True).stdout.strip()

    c = _compiler(fixture_repo, view_path, registry_path, max_slice_chars=200)
    occ = RouteOccurrence(ref="product", commit=commit, path="src/big_fn.rs", version_status="CANONICAL",
                           line_start=1, line_end=402)
    hit = RouteHit(unit_id="fn:big_fn", unit_kind="symbol", route="code", rank=1, occurrences=(occ,),
                   text="fn big_fn", authority_class="EVIDENCE", lifecycle="ACTIVE")

    top_item = c.item_from_hit(FusedHit(hit=hit, fused_score=1.0, routes=("code",)), "G", top=True)
    plain_item = c.item_from_hit(FusedHit(hit=hit, fused_score=1.0, routes=("code",)), "G", top=False)

    assert top_item.bytes_len() > plain_item.bytes_len(), (top_item.bytes_len(), plain_item.bytes_len())
    assert "truncated" in top_item.text
    assert "truncated" in plain_item.text


def test_content_slice_truncation_is_marked_never_silent(fixture_repo, view_path, registry_path, tmp_path):
    c = _compiler(fixture_repo, view_path, registry_path, max_slice_chars=40)
    occ = RouteOccurrence(ref="product", commit=fixture_repo.c1, path=repobuilder.CODE_PATH,
                           version_status="CANONICAL", line_start=1, line_end=4)
    hit = RouteHit(unit_id="chunk:cx_module:trunc", unit_kind="chunk", route="semantic", rank=1, occurrences=(occ,),
                   text=None, authority_class="EVIDENCE", lifecycle="ACTIVE")
    item = c.item_from_hit(FusedHit(hit=hit, fused_score=1.0, routes=("semantic",)), "H")
    assert "truncated at 40 bytes" in item.text, item.text


def test_lexical_chunk_with_real_text_is_left_alone(fixture_repo, view_path, registry_path):
    """A lexical hit already carries real chunk text (``real_routes.lexical_route``) -- this node never re-fetches
    or alters it (RC-5 targets code/semantic pointers specifically, never something already real evidence)."""
    c = _compiler(fixture_repo, view_path, registry_path)
    occ = RouteOccurrence(ref="product", commit="0" * 40, path="does/not/exist.md", version_status="ABSENT",
                           line_start=1, line_end=1)
    hit = RouteHit(unit_id="chunk:x", unit_kind="chunk", route="lexical", rank=1, occurrences=(occ,),
                   text="already real lexical chunk text", authority_class="EVIDENCE", lifecycle="ACTIVE")
    item = c.item_from_hit(FusedHit(hit=hit, fused_score=1.0, routes=("lexical",)), "H")
    assert item.text == "already real lexical chunk text"


def test_compile_level_no_code_or_semantic_item_has_a_zero_byte_body(fixture_repo, view_path, registry_path,
                                                                       tmp_path):
    """The compile-level acceptance case (REPAIR_DAG.yaml node R1-GA3 acceptance check 1): a fixture with a
    pointer-only code hit and a text-less semantic hit, run through the FULL query -> gather -> compile path, must
    never place a 0-byte symbol/chunk item anywhere."""
    code_occ = RouteOccurrence(ref="records", commit=fixture_repo.c1, path=repobuilder.CODE_PATH,
                                version_status="CANONICAL", line_start=2, line_end=4)
    code_hit = RouteHit(unit_id="fn:cx_rule2", unit_kind="symbol", route="code", rank=1, occurrences=(code_occ,),
                         text="fn cx_rule", authority_class="EVIDENCE", lifecycle="ACTIVE")
    sem_occ = RouteOccurrence(ref="records", commit=fixture_repo.c1, path=repobuilder.CODE_PATH,
                               version_status="CANONICAL", line_start=1, line_end=4)
    sem_hit = RouteHit(unit_id="chunk:cx_module", unit_kind="chunk", route="semantic", rank=1,
                        occurrences=(sem_occ,), text=None, authority_class="EVIDENCE", lifecycle="ACTIVE")

    def fake_code(text=None, seeds=None, k=8, exclude=None, exclude_counter=None, **kw):
        return [code_hit]

    def fake_semantic(text=None, k=8, offset=0, exclude=None, exclude_counter=None, page_info_out=None, **kw):
        if page_info_out is not None:
            page_info_out["next_offset"] = None
        return [sem_hit] if offset == 0 else []

    routes = RouteSet(code=fake_code, semantic=fake_semantic)
    facets_path = tmp_path / "cs-facets.yaml"
    facets_path.write_text("""schema: govbridge-facets/1
default_batch_size: 20
default_target_items: 20
default_max_rounds: 2
default_threads: 1
facets:
  code_facet:
    routes: [code]
    scope_classes: null
    lifecycle_scope: null
    extra_terms: []
    min_share: 0.1
  semantic_facet:
    routes: [semantic]
    scope_classes: null
    lifecycle_scope: null
    extra_terms: []
    min_share: 0.1
class_facets: {}
""", encoding="utf-8")

    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-CS", "role": "test", "objective": "x",
        "view": view_path, "required_inputs": [], "seeds": [],
        # an explicit `routes` list (ARCHITECTURE.md section 7.2 / router.select_routes) so this query's own
        # route selection includes "code" -- the query TEXT's shape alone would not have triggered it, and this
        # node's own query-loop honours a query's declared routes exactly like every other compile did before it.
        "queries": [{"id": "CS-Q1", "text": "content slices fixture", "routes": ["semantic", "code"]}],
        "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED"], "budget_profile": "synthesis",
    }
    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(fixture_repo.root),
                                       registry_path=registry_path, facets_path=str(facets_path))
    assert result["status"] == packetmod.STATUS_OK

    checked = 0
    for items in result["sections"].values():
        for item in items:
            if item.unit_kind in ("symbol", "chunk"):
                assert item.bytes_len() > 0, f"{item.unit_kind}:{item.unit_id} has a 0-byte body"
                checked += 1
    assert checked >= 2, "both the code symbol and the semantic chunk must have been placed somewhere"


# ---------------------------------------------------------------------------------------------------------------
# BR-DAG-AMEND-R1-11 (routing of R1-RM's own MET_WITH_DISCLOSED_LIMIT row): an OVERSIZE mandatory item with NO
# declared selector additionally delivers, IN FULL, the sections the gather facet vocabulary scores as relevant --
# never removing anything from A, keeping the MANDATORY_PARTIAL_DELIVERY notice and the exact-tiling verify rule
# intact. Uses the REAL, default facet registry (config/facets.yaml) deliberately -- this is the one behaviour
# that must be reproducible by govbridge.compile.validate's blind re-derivation with NO facets_path override at
# all (see govbridge.compile.overflow.select_oversize_facet_sections's own docstring).
# ---------------------------------------------------------------------------------------------------------------

def _write_oversize_facet_fixture(fixture_repo) -> str:
    parts = ["# CS-OVERSIZE -- an oversize mandatory record for BR-DAG-AMEND-R1-11\n"]
    parts.append("\n## Decision rationale\n\nTHIS-IS-THE-DECISION-SECTION-BODY, distinctive and searchable.\n")
    parts.append("\n## Enforcement notes\n\nTHIS-IS-THE-ENFORCEMENT-SECTION-BODY, also distinctive.\n")
    i = 0
    total = sum(len(p) for p in parts)
    while total < 30_000:
        i += 1
        section = f"\n## Part {i}\n\nGenerated filler body text for part {i}, repeated to exceed the per-item cap.\n"
        parts.append(section)
        total += len(section)
    text = "".join(parts)
    rel = "runtime/oversize_facet_fixture.md"
    (fixture_repo.root / rel).parent.mkdir(parents=True, exist_ok=True)
    (fixture_repo.root / rel).write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(fixture_repo.root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(fixture_repo.root), "-c", "user.email=t@example.com", "-c", "user.name=t",
                     "commit", "-q", "-m", "BR-DAG-AMEND-R1-11 fixture: an oversize record with facet-matching "
                     "and facet-unmatching headings"], check=True, capture_output=True)
    return rel


def test_oversize_mandatory_item_delivers_facet_matching_sections_in_full(fixture_repo, view_path, registry_path):
    rel = _write_oversize_facet_fixture(fixture_repo)
    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-CS-OVERSIZE", "role": "test", "objective": "x",
        "view": view_path, "required_inputs": [{"path": f"{rel}@records", "reason": "test"}],
        "seeds": [], "queries": [], "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED"], "budget_profile": "bounded-builder",
    }
    result = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    a_rows = {i.unit_id: i for i in result["sections"]["A"]}
    assert rel in a_rows, "nothing is ever removed from A"
    item = a_rows[rel]
    assert "[section map:" in item.text

    # the facet-matching sections are delivered IN FULL, inline.
    assert "THIS-IS-THE-DECISION-SECTION-BODY" in item.text, item.text[:2000]
    assert "THIS-IS-THE-ENFORCEMENT-SECTION-BODY" in item.text
    assert "DELIVERED IN FULL" in item.text

    # a facet-unmatching section ("Part N") stays by-reference only -- its generated body text never appears.
    assert "Generated filler body text for part 1," not in item.text

    notice = next(n for n in result["manifest"]["notices"]
                  if n["type"] == "MANDATORY_PARTIAL_DELIVERY" and n["id"] == rel)
    delivered_names = {d["name"] for d in notice["delivered"]}
    assert any("Decision rationale" in n for n in delivered_names), delivered_names
    assert any("Enforcement notes" in n for n in delivered_names), delivered_names
    undelivered_names = {d["name"] for d in notice["undelivered_ranges"]}
    assert any(n.startswith("Part ") for n in undelivered_names)
    # delivered + undelivered partition the disclosure map exactly (no name in both, none missing).
    assert delivered_names & undelivered_names == set()

    # packet verify (including the exact-tiling coverage check and the rendered-body re-extraction/recomposition
    # check) still passes -- BR-DAG-AMEND-R1-11 explicitly keeps both rules unchanged.
    assert validatemod.verify_packet(result["manifest"], task_spec, repo=str(fixture_repo.root),
                                      registry_path=registry_path, rendered=result["rendered"]) == []


def test_oversize_mandatory_item_facet_selection_is_deterministic_across_two_compiles(fixture_repo, view_path,
                                                                                       registry_path):
    """govbridge.compile.validate's blind re-derivation (``_composition_context_class``) supplies no task, no
    query set and no facets_path at all when it recomposes an A item's expected body -- so the facet-based
    selection MUST be reproducible from (mi, dparts, repo, per_item_cap_bytes) alone. Two independent compiles of
    the SAME fixture must select the exact same sections and render byte-identical packets."""
    rel = _write_oversize_facet_fixture(fixture_repo)
    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-CS-OVERSIZE-2", "role": "test", "objective": "x",
        "view": view_path, "required_inputs": [{"path": f"{rel}@records", "reason": "test"}],
        "seeds": [], "queries": [], "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED"], "budget_profile": "bounded-builder",
    }
    r1 = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=str(fixture_repo.root),
                                   registry_path=registry_path)
    r2 = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=str(fixture_repo.root),
                                   registry_path=registry_path)
    assert r1["rendered"] == r2["rendered"]
    assert r1["packet_sha256"] == r2["packet_sha256"]


def test_mf_big_style_fixture_with_no_facet_matching_headings_is_unaffected(fixture_repo, view_path, registry_path):
    """A "Part N"-only oversize document (no heading matches any gather facet term) delivers NOTHING in full --
    the exact pre-R1-GA3 behaviour (R1-RM's own tests/compile/test_mandatory_fidelity.py::
    test_oversize_item_never_ends_mid_content, not in this node's mutation scope to touch, asserts this same
    invariant on its own MF-BIG fixture; this test proves the same property generically, in this node's own
    fixture, without depending on that file)."""
    parts = ["# CS-PLAIN -- an oversize record with no facet-matching headings at all\n"]
    i = 0
    total = sum(len(p) for p in parts)
    while total < 30_000:
        i += 1
        section = f"\n## Part {i}\n\nGenerated filler body text for part {i}, repeated to exceed the per-item cap.\n"
        parts.append(section)
        total += len(section)
    text = "".join(parts)
    rel = "runtime/oversize_plain_fixture.md"
    (fixture_repo.root / rel).parent.mkdir(parents=True, exist_ok=True)
    (fixture_repo.root / rel).write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(fixture_repo.root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(fixture_repo.root), "-c", "user.email=t@example.com", "-c", "user.name=t",
                     "commit", "-q", "-m", "BR-DAG-AMEND-R1-11 fixture: a plain oversize record"],
                    check=True, capture_output=True)

    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-CS-PLAIN", "role": "test", "objective": "x",
        "view": view_path, "required_inputs": [{"path": f"{rel}@records", "reason": "test"}],
        "seeds": [], "queries": [], "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED"], "budget_profile": "bounded-builder",
    }
    result = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    notice = next(n for n in result["manifest"]["notices"]
                  if n["type"] == "MANDATORY_PARTIAL_DELIVERY" and n["id"] == rel)
    assert notice["delivered"] == []
    assert validatemod.verify_packet(result["manifest"], task_spec, repo=str(fixture_repo.root),
                                      registry_path=registry_path, rendered=result["rendered"]) == []
