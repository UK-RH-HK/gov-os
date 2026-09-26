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
    conn.commit()


def put_edge(conn: sqlite3.Connection, edge) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO lineage_edge(src, type, dst, derivation, evidence_occurrence, evidence_line, note) "
        "VALUES (?,?,?,?,?,?,?)",
        (edge.src, edge.type, edge.dst, edge.derivation, edge.evidence_occurrence, edge.evidence_line, edge.note),
    )


def lineage_layer_builder(conn: sqlite3.Connection, resolved_view, rules, repo: Optional[str], from_clean: bool,
                           changed_refs: Optional[list] = None) -> dict:
    from govbridge.core import gitobj, corpus
    from govbridge.core.yamlutil import load_yaml_text
    from govbridge.graph import derive as D

    ensure_schema(conn)
    clear_layer_tables(conn)

    commit = resolved_view.ref_commit("records")
    stats = {"blobs_scanned": 0, "edges": 0, "edges_by_type": {}}

    def _record(edges: list) -> None:
        for e in edges:
            put_edge(conn, e)
            stats["edges"] += 1
            stats["edges_by_type"][e.type] = stats["edges_by_type"].get(e.type, 0) + 1

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
            is_yaml = path.endswith((".yaml", ".yml"))
            if not (is_code or is_test_py or is_yaml):
                continue
            is_binary, text = sniffer.get(entry.oid)
            if is_binary:
                continue
            stats["blobs_scanned"] += 1

            if is_code:
                _record(D.depends_on_data_edges(text, path, commit, repo=repo))
                _record(D.cites_requirement_edges_in_text(text, path, commit, repo=repo))
            if is_test_py:
                _record(D.cli_dispatch_tests_edges(text, path, commit, repo=repo))
            if is_yaml:
                try:
                    doc = load_yaml_text(text)
                except Exception:
                    doc = None
                if doc is not None:
                    _record(D.test_registry_edges_in_doc(doc, path, commit))

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
        h.update("\x1f".join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(b"\x1e")
        by_type[row[1]] = by_type.get(row[1], 0) + 1
    return LayerDigest(rows=len(rows), digest=h.hexdigest(), extra={"rows_by_type": by_type})
