#!/usr/bin/env python3
"""The persisted "lineage" store layer (BR-AR-0019, R1-RL reopening ruling): TESTS-beyond-a-direct-call (CLI
dispatch, test-registry shape), DEPENDS_ON_DATA and CITES_REQUIREMENT edges, computed for every reachable INCLUDEd
blob and registered as a build-manifest layer with its own digest -- so the reproducibility (two from-clean builds
-> identical digest, nonzero rows per edge kind) and freshness-NOOP properties this programme requires of every
PERSISTED capability (BR-DAG-AMEND-3's fix for B5's graph rows; B3R's rejection of an empty-manifest lazy code
layer) cover these edges too, exactly like ``govbridge.authority.layer`` already covers record_def/DEFINES/
SUPERSEDES.

Why this file lives under ``govbridge/code/`` rather than ``govbridge/graph/`` (where a reader would expect a
graph-edge layer to register itself): ``govbridge/graph/__init__.py`` -- the usual place a layer package runs its
own ``register_layer``/``register_layer_builder`` calls at import time -- is OUTSIDE this node's mutation scope
(R1-RL's ``mutation_scope`` names individual files under ``govbridge/graph/``, never a ``**`` wildcard there).
``govbridge/code/__init__.py`` IS inside scope (``govbridge/code/**``), and is already imported by every
``ensure_all_layer_packages_imported()`` walk (it registers the "code" layer). The functions that actually DERIVE
each edge stay exactly where R1-RL's brief puts them, in ``govbridge/graph/derive.py``; this module only walks the
corpus once per ELIGIBLE REF per build, and calls them -- it invents no new derivation logic of its own.

Always a FULL re-derivation on every build (like ``govbridge.authority.layer.build``'s own documented rule): these
edges are cheap enough to recompute from the already-classified corpus in one pass (no chunking), and are
recomputed globally after every non-NOOP build anyway (ARCHITECTURE.md section 3's rule for this row of its
table).

**BR-AR-0019 reopening (third pass), Defect A: this layer must walk every canonical-view ref its edges are ABOUT,
not just "records".** ``config/canonical-view.yaml`` assigns paths to an OWNING ref per partition (the product
partition: ``PRODUCT_CODE`` plus ``probes/**``/``telemetry/**``, owned by the ``product`` ref, pinned); the
"records" ref this layer previously walked alone can hold an older, non-canonical copy of that same code. Fixed
generically, the SAME way ``govbridge.code.build.eager_ref_names`` already selects the "code" layer's own eager ref
set -- by ``RefSpec.role``/``RefSpec.layers``, never by a ref's NAME (this module reuses that exact function rather
than re-deriving its own selection: a lineage edge is an edge ABOUT code, so wherever code is eagerly indexed is
exactly where a lineage edge can legitimately be derived, from THAT ref's own content). Every row now carries its
OWN ``ref_name``/``commit_id`` (the primary key gained both, so a stale ref's own edges are never silently
overwritten by, or conflated with, a canonical ref's edges for the same logical (src, type, dst, derivation)) and
its own ``version_status``/``canonical_ref``/``canonical_commit`` (``govbridge.core.view.ResolvedView``'s own
vocabulary -- CANONICAL / CANONICAL_FALLBACK / SAME_AS_CANONICAL / HISTORICAL_VERSION / HISTORY_ONLY -- computed
via ``_version_status`` below, which mirrors ``classify_occurrence`` exactly rather than re-implementing its
partition/fallback semantics; see that function's own docstring for why it is a safe, measured substitution of
already-fetched tree data for repeated git subprocess calls, not a parallel algorithm that could silently
diverge). ``stats["by_ref"]`` reports blobs-scanned/edges/edges-by-type per ref, on top of the pre-existing
corpus-wide totals (kept as the SUM across refs, so every existing acceptance check and test that reads a top-level
stats key keeps meaning exactly what it always meant).
"""
from __future__ import annotations

import hashlib
import sqlite3
from typing import Optional

from govbridge.core.manifest import LayerDigest

LAYER_NAME = "lineage"
INCLUDE_EFFECT = "INCLUDE"


def _is_test_python_path(path: str) -> bool:
    """A ``.py`` file inside a directory named ``tests``, at ANY depth -- generic (OC-BR-02: matches
    ``tests/foo.py`` at the repository root just as it matches a domain's own nested
    ``release/.../some-domain/tests/bar.py``; no domain name, symbol or path is hard-coded)."""
    if not path.endswith(".py"):
        return False
    parts = path.split("/")
    return "tests" in parts[:-1]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS lineage_edge (
    ref_name TEXT NOT NULL,
    commit_id TEXT NOT NULL,
    src TEXT NOT NULL,
    type TEXT NOT NULL,
    dst TEXT NOT NULL,
    derivation TEXT NOT NULL,
    evidence_occurrence TEXT,
    evidence_line INTEGER,
    note TEXT,
    version_status TEXT NOT NULL,
    canonical_ref TEXT,
    canonical_commit TEXT,
    PRIMARY KEY (ref_name, commit_id, src, type, dst, derivation)
);
CREATE INDEX IF NOT EXISTS lineage_edge_by_type ON lineage_edge(type);
CREATE INDEX IF NOT EXISTS lineage_edge_by_ref ON lineage_edge(ref_name);

CREATE TABLE IF NOT EXISTS lineage_unresolved (
    ref_name TEXT NOT NULL,
    commit_id TEXT NOT NULL,
    path TEXT,
    line INTEGER,
    candidate TEXT,
    form TEXT NOT NULL,
    reason TEXT
);
CREATE INDEX IF NOT EXISTS lineage_unresolved_by_form ON lineage_unresolved(form);
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Idempotent -- the same discipline every sibling layer's ``ensure_schema`` documents (BR-DAG-AMEND-3's own
    fix): ``govbridge.core.manifest.build_manifest`` calls every registered digest unconditionally, including on
    a connection this layer's own builder never touched."""
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def clear_layer_tables(conn: sqlite3.Connection) -> None:
    ensure_schema(conn)
    conn.execute("DELETE FROM lineage_edge")
    conn.execute("DELETE FROM lineage_unresolved")
    conn.commit()


def put_edge(conn: sqlite3.Connection, ref_name: str, commit_id: str, edge, version_status: str,
             canonical_ref: Optional[str], canonical_commit: Optional[str]) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO lineage_edge(ref_name, commit_id, src, type, dst, derivation, "
        "evidence_occurrence, evidence_line, note, version_status, canonical_ref, canonical_commit) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (ref_name, commit_id, edge.src, edge.type, edge.dst, edge.derivation, edge.evidence_occurrence,
         edge.evidence_line, edge.note, version_status, canonical_ref, canonical_commit),
    )


def put_unresolved(conn: sqlite3.Connection, ref_name: str, commit_id: str, item: dict) -> None:
    """BR-AR-0019 reopening, Gap 1 (extended in the third-pass Defect B to a second ``form``,
    ``"rust_harness_method"``): a citation or a harness-method call that never resolves to an edge is still
    counted here, with its reason -- never silently dropped."""
    conn.execute(
        "INSERT INTO lineage_unresolved(ref_name, commit_id, path, line, candidate, form, reason) "
        "VALUES (?,?,?,?,?,?,?)",
        (ref_name, commit_id, item.get("path"), item.get("line"), item.get("candidate"), item["form"],
         item.get("reason")),
    )


def _version_status(resolved_view, ref_trees: dict, ref_name: str, commit: str, path: str, blob_id: str) -> tuple:
    """(version_status, canonical_ref, canonical_commit) for one (ref_name, commit, path, blob_id) occurrence --
    Defect A item 2. Mirrors ``govbridge.core.view.ResolvedView.classify_occurrence`` EXACTLY for its two dominant
    branches (present at the partition owner; present at a NAMED fallback), reading them from ``ref_trees``
    (path -> blob_id maps this build already built for every eager ref, from the SAME ``git ls-tree`` walk the
    corpus scan needs anyway) instead of calling ``gitobj.blob_at`` again per blob per ref -- a build that walks 3
    refs x ~1100 blobs cannot afford ~3300 extra git subprocess round-trips for a fact its own tree walk already
    established for every NAMED ref. This is a measured DATA-SOURCE substitution, never a parallel reimplementation
    of ``classify_occurrence``'s partition/fallback LOGIC: ``partition_for`` itself is called unmodified, and the
    two branches this function cannot shortcut from local data alone (a "history"-glob fallback; a path absent
    from every named ref's own tree) delegate straight to the real, git-backed ``classify_occurrence`` -- both are
    rare in practice, so the delegation costs at most a handful of git calls, never thousands.
    ``tests/code/test_lineage_layer.py``'s own ``test_version_status_agrees_with_classify_occurrence`` cross-checks
    this against the real function directly, as a standing guard against divergence."""
    from govbridge.core import view as viewmod

    part = resolved_view.partition_for(path)
    owner_ref = resolved_view.named.get(part.owner)
    owner_commit = owner_ref.commit if owner_ref else None
    if owner_commit is not None and commit == owner_commit:
        return viewmod.VS_CANONICAL, part.owner, owner_commit
    owner_tree = ref_trees.get(part.owner)
    owner_blob = owner_tree.get(path) if owner_tree is not None else None
    if owner_blob is not None:
        status = viewmod.VS_SAME_AS_CANONICAL if blob_id == owner_blob else viewmod.VS_HISTORICAL_VERSION
        return status, part.owner, owner_commit
    for fb_name in part.fallback:
        if fb_name == "history":
            cls = resolved_view.classify_occurrence(path, commit, queried_blob=blob_id)
            return cls.status, cls.canonical_ref, cls.canonical_commit
        fb_ref = resolved_view.named.get(fb_name)
        if fb_ref is None:
            continue
        fb_tree = ref_trees.get(fb_name)
        fb_blob = fb_tree.get(path) if fb_tree is not None else None
        if fb_blob is not None:
            status = (viewmod.VS_CANONICAL_FALLBACK if commit == fb_ref.commit else
                      (viewmod.VS_SAME_AS_CANONICAL if blob_id == fb_blob else viewmod.VS_HISTORICAL_VERSION))
            return status, fb_name, fb_ref.commit
    cls = resolved_view.classify_occurrence(path, commit, queried_blob=blob_id)
    return cls.status, cls.canonical_ref, cls.canonical_commit


def _empty_ref_stats() -> dict:
    return {
        "blobs_scanned": 0, "edges": 0, "edges_by_type": {}, "edges_by_derivation": {},
        "cites_requirement_resolved_to_section": 0,
        "cites_requirement_resolved_to_document_only": 0,
        "cites_requirement_unresolved_by_reason": {},
        "cites_requirement_path_line_unresolved_by_reason": {},
        "rust_cli_dispatch_variants": 0, "rust_cli_bin_helpers": 0, "rust_cli_wrapper_functions": 0,
        "rust_cli_harness_wrapper_methods": 0, "rust_cli_test_files_scanned": 0,
        "rust_cli_harness_dispatch_edges_declared_type": 0, "rust_cli_harness_dispatch_edges_unique_name": 0,
        "rust_harness_method_unresolved_by_reason": {},
        # BR-AR-0019 reopening (fourth pass): test-registry (c) telemetry -- rows recognised (by the widened,
        # any-depth schema walk) and, of the entries those rows carry, how many resolved through each of
        # requirement 3's three buckets (see govbridge.graph.edges's own comments on the four registry labels).
        "test_registry_rows": 0,
    }


def _merge_counts(agg: dict, add: dict) -> None:
    for k, v in add.items():
        if isinstance(v, dict):
            bucket = agg.setdefault(k, {})
            for kk, vv in v.items():
                bucket[kk] = bucket.get(kk, 0) + vv
        else:
            agg[k] = agg.get(k, 0) + v


def _test_symbol_counts_for_ref(conn: sqlite3.Connection, ref_name: str, commit: str) -> dict:
    """{qualified_name: count} for every ``is_test=1`` ``code_symbol`` row reachable at ``(ref_name, commit)`` --
    BR-AR-0019 reopening (fourth pass), requirement 3. Joins the ALREADY-SHARED ``conn``'s own ``occurrence``
    table (B1's own, always populated before this layer runs -- see this function's own caller for why) against
    ``code_symbol`` (B3's own, populated by the "code" layer's eager builder for every eager ref); never opens a
    second connection to the store (see the caller's own comment for the concrete isolation bug that caused).
    ``code_symbol`` may not exist at all yet on a bare/isolated connection (a unit test that calls
    ``lineage_layer_builder`` directly, never through a full ``freshness.run()`` -- the "code" layer's own builder
    then never ran on this ``conn``) -- an empty dict in that case, the SAME honest-MISSING degrade every other
    code-route-optional function in this module documents, never a crash."""
    from collections import Counter

    try:
        rows = conn.execute(
            "SELECT cs.qualified_name FROM code_symbol cs JOIN occurrence o ON o.blob_id = cs.blob_id "
            "WHERE o.ref_name = ? AND o.commit_id = ? AND cs.is_test = 1", (ref_name, commit),
        ).fetchall()
    except sqlite3.OperationalError:
        return {}
    return Counter(r[0] for r in rows)


def _scan_one_ref(conn: sqlite3.Connection, resolved_view, ref_trees: dict, ref_name: str, commit: str, rules,
                   repo: Optional[str], grammar) -> dict:
    """One ref's own full corpus walk: classify, derive every edge kind exactly as R1-RL's brief describes, tag
    each row/unresolved-item with THIS ref's own ``(ref_name, commit)`` and version status, and return this ref's
    own stats dict (the caller sums these into the build-wide aggregate -- see ``lineage_layer_builder``)."""
    from govbridge.core import gitobj, corpus
    from govbridge.core.yamlutil import load_yaml_text
    from govbridge.graph import derive as D
    from govbridge.graph import edges as E
    from govbridge.code import rust_cli as RC

    ref_stats = _empty_ref_stats()

    # BR-AR-0019 reopening (fourth pass), requirement 3: {qualified_name: count} for every is_test=1 code-layer
    # symbol reachable at THIS ref's own commit -- computed ONCE per ref (never per registry entry), reused by
    # every test_registry_edges_in_doc call below. Read from the SAME shared `conn` this whole build already has
    # open (via the "core" layer's own `occurrence` table, ALWAYS populated before any sibling layer's builder
    # runs -- core_layer_builder registers first, structurally: nothing can call
    # ensure_all_layer_packages_imported() without govbridge.core.freshness, which OWNS that registration, already
    # being loaded), joined against code_symbol (populated by the "code" layer's OWN eager builder for every
    # eager ref, the SAME ref set Defect A already reuses -- see this module's own docstring). Deliberately NEVER
    # a second sqlite3 connection to the store (an earlier version of this fix called
    # govbridge.code.symbols.ensure_indexed via its own _open_conn(), which opens a SEPARATE connection to
    # whatever GOVBRIDGE_STORE currently names and sets PRAGMA journal_mode=WAL on it -- harmless in isolation, but
    # a second concurrent writer to the SAME on-disk store file, whose own commit/WAL-checkpoint behaviour bumped
    # the file's change-counter as an observable side effect completely unrelated to this feature, breaking
    # tests/core/test_freshness.py's OWN "two GOVBRIDGE_STORE values build independent stores" byte-for-byte
    # isolation guarantee -- found and fixed before this reopening's return, never shipped).
    test_symbol_counts = _test_symbol_counts_for_ref(conn, ref_name, commit)

    def _record_for_blob(edges: list, blob_id: str, path: str) -> None:
        """Every edge kind below is derived FROM one already-read file (blob_id, path) -- its own version status
        (Defect A item 2) is therefore exactly that file's own occurrence status in this ref, computed once per
        file (not per edge, and not at all when the file produced no edges) and applied to every edge that file
        produced."""
        if not edges:
            return
        status, canon_ref, canon_commit = _version_status(resolved_view, ref_trees, ref_name, commit, path, blob_id)
        for e in edges:
            put_edge(conn, ref_name, commit, e, status, canon_ref, canon_commit)
            ref_stats["edges"] += 1
            ref_stats["edges_by_type"][e.type] = ref_stats["edges_by_type"].get(e.type, 0) + 1
            deriv_key = f"{e.type}:{e.derivation}"
            ref_stats["edges_by_derivation"][deriv_key] = ref_stats["edges_by_derivation"].get(deriv_key, 0) + 1
            if e.type == E.CITES_REQUIREMENT:
                if e.derivation == E.HEURISTIC_COMMENT_SECTION:
                    ref_stats["cites_requirement_resolved_to_section"] += 1
                elif e.derivation == E.HEURISTIC_SECTION_UNRESOLVED:
                    ref_stats["cites_requirement_resolved_to_document_only"] += 1

    # Gap 2, pass A: a clap CLI's #[derive(Subcommand)] enums, its CARGO_BIN_EXE helper(s), any test-local wrapper
    # FUNCTION and any test-harness wrapper METHOD (Defect B) can each live in ANY .rs file THIS REF's own tree
    # carries -- accumulated globally over this ref's whole corpus, before pass B resolves a single test call
    # against them.
    rust_bin_helpers: set = set()
    rust_wrappers: dict = {}
    rust_dispatch_maps: list = []
    rust_test_files: list = []          # [(path, text)]
    rust_impl_candidate_texts: list = []  # [text] -- pre-filtered candidates for find_impl_wrapper_methods

    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        for entry in gitobj.ls_tree(commit, repo=repo):
            if entry.type != "blob":
                continue
            verdict = corpus.classify_entry(entry, rules, sniffer)
            if verdict.effect != INCLUDE_EFFECT:
                continue
            path = entry.path
            is_code = any(path.startswith(d) for d in D.CODE_DIRS)
            is_test_py = _is_test_python_path(path)
            # Gap 2's own scan is intentionally NOT gated to CODE_DIRS -- see the original module docstring's own
            # rationale (a CLI definition/CARGO_BIN_EXE helper/#[test] fn can legitimately live anywhere a .rs
            # file does).
            is_rust = path.endswith(".rs")
            is_yaml = path.endswith((".yaml", ".yml"))
            if not (is_code or is_test_py or is_rust or is_yaml):
                continue
            is_binary, text = sniffer.get(entry.oid)
            if is_binary:
                continue
            ref_stats["blobs_scanned"] += 1

            if is_code:
                _record_for_blob(D.depends_on_data_edges(text, path, commit, repo=repo), entry.oid, path)
                cr_edges, cr_unresolved = D.cites_requirement_edges_in_text(text, path, commit, repo=repo)
                _record_for_blob(cr_edges, entry.oid, path)
                for item in cr_unresolved:
                    put_unresolved(conn, ref_name, commit, item)
                    bucket = (ref_stats["cites_requirement_unresolved_by_reason"] if item["form"] == "section"
                              else ref_stats["cites_requirement_path_line_unresolved_by_reason"])
                    bucket[item["reason"]] = bucket.get(item["reason"], 0) + 1
            if is_test_py:
                _record_for_blob(D.cli_dispatch_tests_edges(text, path, commit, repo=repo), entry.oid, path)
            if is_rust:
                if "CARGO_BIN_EXE" in text:
                    rust_bin_helpers |= RC.find_cargo_bin_exe_helpers(text)
                if "derive(Subcommand)" in text or "derive(Parser)" in text:
                    rust_dispatch_maps.append(RC.build_dispatch_map(text))
                if "#[test]" in text:
                    rust_test_files.append((path, text, entry.oid))
                if RC.impl_wrapper_candidate(text):
                    rust_impl_candidate_texts.append(text)
            if is_yaml:
                try:
                    doc = load_yaml_text(text)
                except Exception:
                    doc = None
                if doc is not None:
                    # counted separately (a row with an EMPTY `tests: []` still counts as a recognised row, even
                    # though it produces zero edges) -- the edges themselves always come from the one real
                    # function, test_registry_edges_in_doc, never reimplemented inline here.
                    ref_stats["test_registry_rows"] += sum(1 for _ in D._iter_registry_rows(doc))
                    _record_for_blob(D.test_registry_edges_in_doc(
                        doc, path, commit, test_symbol_counts=test_symbol_counts, grammar=grammar,
                    ), entry.oid, path)

    # Gap 2, pass B: every wrapper (free function OR Defect B's harness METHOD) needs the FULL bin-helper set
    # (defined in one file, reused by many others), so wrapper detection runs only now, once pass A above has
    # finished collecting every helper across THIS ref's whole tree.
    rust_dispatch = RC.merge_dispatch_maps(rust_dispatch_maps)
    ref_stats["rust_cli_dispatch_variants"] = len(rust_dispatch)
    ref_stats["rust_cli_bin_helpers"] = len(rust_bin_helpers)
    if rust_bin_helpers and rust_dispatch:
        for text in rust_impl_candidate_texts:
            rust_wrappers.update(RC.find_impl_wrapper_methods(text, rust_bin_helpers))
        for path, text, _oid in rust_test_files:
            rust_wrappers.update(RC.find_wrapper_functions(text, rust_bin_helpers))
        ref_stats["rust_cli_wrapper_functions"] = len(rust_wrappers)
        ref_stats["rust_cli_harness_wrapper_methods"] = sum(1 for k in rust_wrappers if "::" in k)
        for path, text, oid in rust_test_files:
            ref_stats["rust_cli_test_files_scanned"] += 1
            rc_edges, rc_unresolved = RC.rust_cli_dispatch_tests_edges(text, path, commit, rust_dispatch,
                                                                        rust_bin_helpers, rust_wrappers)
            _record_for_blob(rc_edges, oid, path)
            for e in rc_edges:
                if e.derivation == E.HEURISTIC_RUST_CLI_HARNESS_UNIQUE_METHOD:
                    ref_stats["rust_cli_harness_dispatch_edges_unique_name"] += 1
                elif "receiver resolved via declared_type" in (e.note or ""):
                    ref_stats["rust_cli_harness_dispatch_edges_declared_type"] += 1
            for item in rc_unresolved:
                item.setdefault("path", path)
                put_unresolved(conn, ref_name, commit, item)
                bucket = ref_stats["rust_harness_method_unresolved_by_reason"]
                bucket[item["reason"]] = bucket.get(item["reason"], 0) + 1

    return ref_stats


def lineage_layer_builder(conn: sqlite3.Connection, resolved_view, rules, repo: Optional[str], from_clean: bool,
                           changed_refs: Optional[list] = None) -> dict:
    from govbridge.code import build as codebuild
    from govbridge.core import gitobj

    ensure_schema(conn)
    clear_layer_tables(conn)

    # BR-AR-0019 reopening (fourth pass): loaded ONCE, reused for every ref -- the SAME
    # config/id-grammar.yaml every other id-grammar consumer in this domain loads (recordsmod._default_grammar_
    # path(), never a second copy). Both the IMPORT (govbridge.authority's own package __init__ eagerly reads
    # config/state-aliases.yaml at import time, module-cached process-wide the first time anything imports it --
    # a minimal test fixture that lacks that unrelated file would otherwise crash HERE, the first place in a
    # given process that happens to import govbridge.authority, purely an artifact of import order/caching, never
    # a real-domain concern) and the grammar load itself are guarded: a fixture/domain whose grammar file is
    # minimal or absent (most of this node's OWN unit tests write only "version: 1") degrades to None --
    # test_registry_edges_in_doc's own id-grammar bucket then simply never triggers, an honest MISSING, never a
    # crash (the same discipline every other code-route-optional function in this module already documents).
    try:
        from govbridge.authority import records as recordsmod
        grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
    except Exception:
        grammar = None

    # Defect A: the same eager-ref selection the "code" layer already makes -- RefSpec.role/layers, never a ref
    # NAME (see this module's own docstring). On this repository's real config/canonical-view.yaml this evaluates
    # to {records, product, evidence}; on a single-ref fixture/test view it is exactly that one ref, so every
    # PRE-EXISTING test and acceptance check keeps meaning exactly what it always meant.
    eager_refs = sorted(codebuild.eager_ref_names(resolved_view))

    # Pass 0: every eager ref's own path -> blob_id map, from one extra (cheap: one process, not one per blob)
    # `git ls-tree` per ref -- see `_version_status`'s own docstring for why this avoids ~3300 extra git calls.
    ref_trees: dict = {}
    for ref_name in eager_refs:
        commit = resolved_view.ref_commit(ref_name)
        ref_trees[ref_name] = {e.path: e.oid for e in gitobj.ls_tree(commit, repo=repo) if e.type == "blob"}

    stats = _empty_ref_stats()
    stats["eager_refs"] = eager_refs
    stats["by_ref"] = {}

    for ref_name in eager_refs:
        commit = resolved_view.ref_commit(ref_name)
        ref_stats = _scan_one_ref(conn, resolved_view, ref_trees, ref_name, commit, rules, repo, grammar)
        stats["by_ref"][ref_name] = ref_stats
        _merge_counts(stats, ref_stats)

    conn.commit()
    return stats


def lineage_layer_digest(conn: sqlite3.Connection) -> LayerDigest:
    ensure_schema(conn)
    rows = conn.execute(
        "SELECT ref_name, commit_id, src, type, dst, derivation, evidence_occurrence, evidence_line, note, "
        "version_status, canonical_ref, canonical_commit FROM lineage_edge "
        "ORDER BY ref_name, commit_id, type, src, dst, derivation"
    ).fetchall()
    h = hashlib.sha256()
    by_type: dict = {}
    by_ref: dict = {}
    for row in rows:
        h.update("edge\x1f".encode("utf-8"))
        h.update("\x1f".join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(b"\x1e")
        by_type[row[3]] = by_type.get(row[3], 0) + 1
        by_ref[row[0]] = by_ref.get(row[0], 0) + 1

    unresolved_rows = conn.execute(
        "SELECT ref_name, commit_id, path, line, candidate, form, reason FROM lineage_unresolved "
        "ORDER BY ref_name, commit_id, form, path, line, candidate"
    ).fetchall()
    by_form: dict = {}
    for row in unresolved_rows:
        h.update("unresolved\x1f".encode("utf-8"))
        h.update("\x1f".join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(b"\x1e")
        by_form[row[5]] = by_form.get(row[5], 0) + 1

    return LayerDigest(rows=len(rows) + len(unresolved_rows), digest=h.hexdigest(),
                        extra={"rows_by_type": by_type, "rows_by_ref": by_ref, "unresolved_rows": len(unresolved_rows),
                               "unresolved_by_form": by_form})
