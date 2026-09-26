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
corpus once, per build, and calls them -- it invents no new derivation logic of its own.

Always a FULL re-derivation on every build (like ``govbridge.authority.layer.build``'s own documented rule): these
edges are cheap enough to recompute from the already-classified corpus in one pass (no chunking), and are
recomputed globally after every non-NOOP build anyway (ARCHITECTURE.md section 3's rule for this row of its
table).
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
    src TEXT NOT NULL,
    type TEXT NOT NULL,
    dst TEXT NOT NULL,
    derivation TEXT NOT NULL,
    evidence_occurrence TEXT,
    evidence_line INTEGER,
    note TEXT,
    PRIMARY KEY (src, type, dst, derivation)
);
CREATE INDEX IF NOT EXISTS lineage_edge_by_type ON lineage_edge(type);

CREATE TABLE IF NOT EXISTS lineage_unresolved (
    path TEXT NOT NULL,
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


def put_edge(conn: sqlite3.Connection, edge) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO lineage_edge(src, type, dst, derivation, evidence_occurrence, evidence_line, note) "
        "VALUES (?,?,?,?,?,?,?)",
        (edge.src, edge.type, edge.dst, edge.derivation, edge.evidence_occurrence, edge.evidence_line, edge.note),
    )


def put_unresolved(conn: sqlite3.Connection, item: dict) -> None:
    """BR-AR-0019 reopening, Gap 1: a citation that never resolves to an edge is still counted here, with its
    reason -- never silently dropped."""
    conn.execute(
        "INSERT INTO lineage_unresolved(path, line, candidate, form, reason) VALUES (?,?,?,?,?)",
        (item.get("path"), item.get("line"), item.get("candidate"), item["form"], item.get("reason")),
    )


def lineage_layer_builder(conn: sqlite3.Connection, resolved_view, rules, repo: Optional[str], from_clean: bool,
                           changed_refs: Optional[list] = None) -> dict:
    from govbridge.core import gitobj, corpus
    from govbridge.core.yamlutil import load_yaml_text
    from govbridge.graph import derive as D
    from govbridge.graph import edges as E
    from govbridge.code import rust_cli as RC

    ensure_schema(conn)
    clear_layer_tables(conn)

    commit = resolved_view.ref_commit("records")
    stats = {
        "blobs_scanned": 0, "edges": 0, "edges_by_type": {},
        # BR-AR-0019 reopening, Gap 1 telemetry: "report the real-view counts: resolved to section, resolved to
        # document only, unresolved by reason" -- specifically for the <doc> section N / §N citation form.
        "cites_requirement_resolved_to_section": 0,
        "cites_requirement_resolved_to_document_only": 0,
        "cites_requirement_unresolved_by_reason": {},
        # the plain <doc>:<line> form's own unresolved count, tracked separately (never conflated with the
        # section-form breakdown above, which is what the ruling's three-way split names).
        "cites_requirement_path_line_unresolved_by_reason": {},
        # Gap 2 telemetry: the clap dispatch map / CARGO_BIN_EXE helper / wrapper-function counts this build found,
        # over the whole corpus, before any test file was even looked at.
        "rust_cli_dispatch_variants": 0, "rust_cli_bin_helpers": 0, "rust_cli_wrapper_functions": 0,
        "rust_cli_test_files_scanned": 0,
    }

    def _record(edges: list) -> None:
        for e in edges:
            put_edge(conn, e)
            stats["edges"] += 1
            stats["edges_by_type"][e.type] = stats["edges_by_type"].get(e.type, 0) + 1
            if e.type == E.CITES_REQUIREMENT:
                if e.derivation == E.HEURISTIC_COMMENT_SECTION:
                    stats["cites_requirement_resolved_to_section"] += 1
                elif e.derivation == E.HEURISTIC_SECTION_UNRESOLVED:
                    stats["cites_requirement_resolved_to_document_only"] += 1

    def _record_unresolved(items: list) -> None:
        for item in items:
            put_unresolved(conn, item)
            bucket = (stats["cites_requirement_unresolved_by_reason"] if item["form"] == "section"
                      else stats["cites_requirement_path_line_unresolved_by_reason"])
            bucket[item["reason"]] = bucket.get(item["reason"], 0) + 1

    # Gap 2, pass A: a clap CLI's #[derive(Subcommand)] enums, its CARGO_BIN_EXE helper(s) and any test-local
    # wrapper function(s) can each live in ANY .rs file under CODE_DIRS -- accumulated globally, over the WHOLE
    # corpus, before pass B resolves a single test call against them (a test file can be read, and often is
    # committed, before the CLI definition file in tree order; nothing may assume otherwise).
    rust_bin_helpers: set = set()
    rust_wrappers: dict = {}
    rust_dispatch_maps: list = []
    rust_test_files: list = []  # [(path, text)] -- resolved in pass B, once every map above is complete

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
            # Gap 2's own scan is intentionally NOT gated to CODE_DIRS: a clap CLI definition, a CARGO_BIN_EXE
            # helper or a #[test] fn spawning the binary can legitimately live anywhere a .rs file does (this
            # repository's own held-out verification-evidence trees, e.g. release/verification/**/heldout-tests/,
            # measurably do) -- unlike a code-COMMENT citation (DEPENDS_ON_DATA/CITES_REQUIREMENT), which stays
            # scoped to CODE_DIRS to avoid scanning unrelated prose for string-literal/comment shapes.
            is_rust = path.endswith(".rs")
            is_yaml = path.endswith((".yaml", ".yml"))
            if not (is_code or is_test_py or is_rust or is_yaml):
                continue
            is_binary, text = sniffer.get(entry.oid)
            if is_binary:
                continue
            stats["blobs_scanned"] += 1

            if is_code:
                _record(D.depends_on_data_edges(text, path, commit, repo=repo))
                cr_edges, cr_unresolved = D.cites_requirement_edges_in_text(text, path, commit, repo=repo)
                _record(cr_edges)
                _record_unresolved(cr_unresolved)
            if is_test_py:
                _record(D.cli_dispatch_tests_edges(text, path, commit, repo=repo))
            if is_rust:
                if "CARGO_BIN_EXE" in text:
                    rust_bin_helpers |= RC.find_cargo_bin_exe_helpers(text)
                if "derive(Subcommand)" in text or "derive(Parser)" in text:
                    rust_dispatch_maps.append(RC.build_dispatch_map(text))
                if "#[test]" in text:
                    rust_test_files.append((path, text))
            if is_yaml:
                try:
                    doc = load_yaml_text(text)
                except Exception:
                    doc = None
                if doc is not None:
                    _record(D.test_registry_edges_in_doc(doc, path, commit))

    # Gap 2, pass B: every wrapper function needs the FULL bin-helper set (a helper defined in one file, e.g.
    # tests/certification/common.rs, is routinely reused by wrapper functions in many other test files), so
    # wrapper-detection runs only now, once pass A above has finished collecting every helper.
    rust_dispatch = RC.merge_dispatch_maps(rust_dispatch_maps)
    stats["rust_cli_dispatch_variants"] = len(rust_dispatch)
    stats["rust_cli_bin_helpers"] = len(rust_bin_helpers)
    if rust_bin_helpers and rust_dispatch:
        for path, text in rust_test_files:
            wrappers = RC.find_wrapper_functions(text, rust_bin_helpers)
            rust_wrappers.update(wrappers)
        stats["rust_cli_wrapper_functions"] = len(rust_wrappers)
        for path, text in rust_test_files:
            stats["rust_cli_test_files_scanned"] += 1
            _record(RC.rust_cli_dispatch_tests_edges(text, path, commit, rust_dispatch, rust_bin_helpers,
                                                      rust_wrappers))

    conn.commit()
    return stats


def lineage_layer_digest(conn: sqlite3.Connection) -> LayerDigest:
    ensure_schema(conn)
    rows = conn.execute(
        "SELECT src, type, dst, derivation, evidence_occurrence, evidence_line, note FROM lineage_edge "
        "ORDER BY type, src, dst, derivation"
    ).fetchall()
    h = hashlib.sha256()
    by_type: dict = {}
    for row in rows:
        h.update("edge\x1f".encode("utf-8"))
        h.update("\x1f".join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(b"\x1e")
        by_type[row[1]] = by_type.get(row[1], 0) + 1

    unresolved_rows = conn.execute(
        "SELECT path, line, candidate, form, reason FROM lineage_unresolved ORDER BY form, path, line, candidate"
    ).fetchall()
    by_form: dict = {}
    for row in unresolved_rows:
        h.update("unresolved\x1f".encode("utf-8"))
        h.update("\x1f".join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(b"\x1e")
        by_form[row[3]] = by_form.get(row[3], 0) + 1

    return LayerDigest(rows=len(rows) + len(unresolved_rows), digest=h.hexdigest(),
                        extra={"rows_by_type": by_type, "unresolved_rows": len(unresolved_rows),
                               "unresolved_by_form": by_form})
