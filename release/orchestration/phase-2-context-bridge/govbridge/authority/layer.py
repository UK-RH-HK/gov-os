#!/usr/bin/env python3
"""The persisted authority/graph layer (ARCHITECTURE.md section 8.1): ``record_def``, ``authority_edge`` and
``class_lifecycle`` rows in the shared store, registered through ``govbridge.core.manifest``/``.freshness``'s
layer-registration API so the build manifest and ``freshness rebuild --layer authority`` cover B5's tables without
editing ``govbridge/core/**``.

This is a CACHE, never a source of truth: ``govbridge.authority.resolver`` and ``.lifecycle`` never read it (they
read Git directly at call time -- ARCHITECTURE.md section 5.3 item 6, the W10 outage property: with the index
deleted, section A is still byte-identical). ``class_lifecycle`` rows are produced by calling
``govbridge.authority.lifecycle.classify`` -- the SAME function ``lifecycle show``/``resolver`` call live -- so a
persisted row always equals the call-time computation by construction (tests/authority/test_layer.py asserts this
on the fixture repo).

Edges persisted here are the ones cheap enough for a whole-view pass: DEFINES (from the id-grammar scan already
needed for ``record_def``) plus registry-derived SUPERSEDES/AMENDS/lifecycle_override edges (bounded to the
registry's own handful of entries). MENTIONS/CITES_*/CODE_CITES/EVIDENCE_MAP and the B3-dependent CALLS/READS_KEY/
TESTS stay on-demand, bounded, targeted lookups in ``govbridge.graph.derive`` (a whole-corpus MENTIONS/CITES scan
for every one of ~1,000+ record ids is a different, much larger operation than this layer's job; I1 may promote
them into this layer once the real code route is wired, without changing this schema's shape).
"""
from __future__ import annotations

import contextlib
import functools
import hashlib
import sqlite3
from typing import Optional

from govbridge.authority import classes as classesmod
from govbridge.authority import lifecycle as lifecyclemod
from govbridge.authority import records as recordsmod
from govbridge.authority import registry as registrymod
from govbridge.core import manifest as manifestmod
from govbridge.core import freshness as freshnessmod
from govbridge.core.manifest import LayerDigest

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS record_def (
    id TEXT NOT NULL,
    path TEXT NOT NULL,
    commit_id TEXT NOT NULL,
    blob_id TEXT,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    rule TEXT NOT NULL,
    local INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, path, line_start)
);
CREATE INDEX IF NOT EXISTS record_def_by_id ON record_def(id);
-- REPAIR_DAG.yaml node R1-GA1 (second reopening): built HERE, at BUILD time (ensure_schema runs as part of this
-- layer's own build, never at query time), for govbridge.route.real_routes's authority-class scope filter (Tier
-- A: JOIN record_def ON path, then class_lifecycle ON id). Without it, that join was a full scan of every record
-- for every candidate row; a query path may only ever READ this index, never create it.
CREATE INDEX IF NOT EXISTS record_def_by_path ON record_def(path);

CREATE TABLE IF NOT EXISTS authority_edge (
    src TEXT NOT NULL,
    type TEXT NOT NULL,
    dst TEXT NOT NULL,
    derivation TEXT NOT NULL,
    evidence_occurrence TEXT,
    evidence_line INTEGER,
    note TEXT,
    PRIMARY KEY (src, type, dst, derivation)
);
CREATE INDEX IF NOT EXISTS authority_edge_by_dst ON authority_edge(dst);
CREATE INDEX IF NOT EXISTS authority_edge_by_type ON authority_edge(type);

CREATE TABLE IF NOT EXISTS class_lifecycle (
    unit TEXT PRIMARY KEY,
    cls TEXT NOT NULL,
    lifecycle TEXT NOT NULL,
    derivation TEXT NOT NULL,
    path TEXT,
    commit_id TEXT,
    line_start INTEGER,
    line_end INTEGER
);
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Idempotent: safe to call on a bare connection that has never seen this layer (govbridge.core.manifest.
    build_manifest calls every registered digest unconditionally, including from another node's tests that only
    opened B1's core schema)."""
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def clear_layer_tables(conn: sqlite3.Connection) -> None:
    ensure_schema(conn)
    conn.execute("DELETE FROM record_def")
    conn.execute("DELETE FROM authority_edge")
    conn.execute("DELETE FROM class_lifecycle")
    conn.commit()


def put_record_def(conn: sqlite3.Connection, d: recordsmod.Definition, commit: str, blob: Optional[str]) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO record_def(id, path, commit_id, blob_id, line_start, line_end, rule, local) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (d.id, d.path, commit, blob, d.line_start, d.line_end, d.rule, 1 if d.local else 0),
    )


def put_edge(conn: sqlite3.Connection, edge) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO authority_edge(src, type, dst, derivation, evidence_occurrence, evidence_line, note) "
        "VALUES (?,?,?,?,?,?,?)",
        (edge.src, edge.type, edge.dst, edge.derivation, edge.evidence_occurrence, edge.evidence_line, edge.note),
    )


def put_class_lifecycle(conn: sqlite3.Connection, c: lifecyclemod.Classification) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO class_lifecycle(unit, cls, lifecycle, derivation, path, commit_id, line_start, "
        "line_end) VALUES (?,?,?,?,?,?,?,?)",
        (c.unit, c.cls, c.lifecycle, c.derivation, c.path, c.commit, c.line_start, c.line_end),
    )


@contextlib.contextmanager
def _cached_blob_reads():
    """A build's classify()-per-definition loop re-reads the same handful of files thousands of times over (many
    ids share one register/ledger blob); govbridge.core.gitobj has no cache of its own (each call is a fresh git
    subprocess, matching its "thin wrapper, no state" contract). Rather than edit gitobj.py, this wraps its two
    read primitives with a call-scoped memo for the duration of ONE build -- a caller-side optimisation, not a
    change to core's behaviour or return values (every wrapped call returns exactly what the original would)."""
    from govbridge.core import gitobj as gitobjmod

    original_blob_at, original_read_blob = gitobjmod.blob_at, gitobjmod.read_blob
    gitobjmod.blob_at = functools.lru_cache(maxsize=None)(original_blob_at)
    gitobjmod.read_blob = functools.lru_cache(maxsize=None)(original_read_blob)
    try:
        yield
    finally:
        gitobjmod.blob_at, gitobjmod.read_blob = original_blob_at, original_read_blob


def build(conn: sqlite3.Connection, resolved_view, rules, repo: Optional[str], from_clean: bool,
          changed_refs: Optional[list] = None, view_path: Optional[str] = None,
          registry_path: Optional[str] = None) -> dict:
    """The ``authority`` layer builder (freshness.py's BuilderFn signature). Always a full re-derivation of THIS
    layer regardless of ``from_clean``/``changed_refs``: record ids and edges are cheap to recompute from the
    already-built core layer's blobs (no chunking, one pass) and cross-artefact facts are recomputed globally after
    every non-NOOP build anyway (ARCHITECTURE.md section 3's own rule for this row of its table)."""
    ensure_schema(conn)
    clear_layer_tables(conn)

    stats = {"record_defs": 0, "edges": 0, "class_lifecycle_rows": 0, "edges_by_label": {}}

    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    rules_path = os.path.join(GOV_BRIDGE_DOMAIN, "config", "corpus-rules.yaml")
    grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
    # reuse the CALLER's already-resolved view (never reload a second, possibly mismatched, canonical-view.yaml):
    # freshness.py's generic layer-builder loop calls every registered builder with whatever resolved view ITS
    # caller built. This registry's own class_rules/section_anchors/supersessions cite THIS domain's real repo
    # content by path+line+quote (ARCHITECTURE.md section 5.2 rule 2) -- they are meaningless, by construction, on
    # a foreign fixture repo (another node's own test, using its own synthetic tree, that happens to call
    # freshness.run() without a --layer filter and so reaches every registered builder, this one included). Rather
    # than abort THAT caller's unrelated build, an authority-registry mismatch here means "nothing of this layer
    # applies to this view": the tables stay empty and the reason is recorded, exactly like an absent code route
    # is MISSING rather than an error elsewhere in this domain.
    try:
        reg = registrymod.load(registry_path or registrymod._default_registry_path(), repo=repo,
                                resolved_view=resolved_view)
        mandatory_items = lifecyclemod._load_mandatory_items(repo=repo, resolved_view=resolved_view)
    except (registrymod.QuoteVerificationError, FileNotFoundError, KeyError, ValueError) as e:
        stats["skipped_reason"] = f"{type(e).__name__}: {e}"
        return stats

    commit = resolved_view.ref_commit("records")
    scan = recordsmod.scan_ref(commit, grammar, rules_path, repo=repo, keep_text=True)

    from govbridge.core import gitobj
    from govbridge.graph import edges as E

    # scan.text_by_path already holds every scanned blob's decoded text (records.scan_ref's own single pass, run
    # with keep_text=True above); classify() accepts it as pre_text so this loop never re-reads the same blob from
    # Git a second time -- with ~3,000+ definitions sharing a few hundred register/ledger/gate files, a second
    # per-definition Git read was the dominant cost of this build. _cached_blob_reads() still guards the few paths
    # (e.g. a definition whose file scan_ref excluded as non-text) that fall back to a live read.
    with _cached_blob_reads():
        for def_id, def_list in scan.definitions.items():
            d = def_list[0]
            blob = scan.blob_by_path.get(d.path) or gitobj.blob_at(commit, d.path, repo=repo)
            put_record_def(conn, d, commit, blob)
            stats["record_defs"] += 1

            defines_edge = E.Edge(src=f"{d.path}@{commit}:{d.line_start}", type=E.DEFINES, dst=def_id,
                                   derivation=E.EXACT_DEFINITION, evidence_occurrence=f"{d.path}@{commit}",
                                   evidence_line=d.line_start)
            put_edge(conn, defines_edge)
            stats["edges"] += 1
            stats["edges_by_label"][E.DEFINES] = stats["edges_by_label"].get(E.DEFINES, 0) + 1

            c = lifecyclemod.classify(def_id, path=d.path, commit=commit, line_start=d.line_start,
                                       line_end=d.line_end, reg=reg, mandatory_items=mandatory_items, repo=repo,
                                       pre_text=scan.text_by_path.get(d.path))
            put_class_lifecycle(conn, c)
            stats["class_lifecycle_rows"] += 1

    seen_sup = set()
    for sup in reg.supersessions:
        key = (sup.from_id, "SUPERSEDES", sup.to_id)
        if key in seen_sup:
            continue
        seen_sup.add(key)
        e = E.Edge(src=sup.from_id, type=E.SUPERSEDES, dst=sup.to_id, derivation=E.REGISTRY_CITED,
                    evidence_occurrence=f"{sup.cite.path}:{sup.cite.line}", evidence_line=sup.cite.line,
                    note=sup.scope)
        put_edge(conn, e)
        stats["edges"] += 1
        stats["edges_by_label"][E.SUPERSEDES] = stats["edges_by_label"].get(E.SUPERSEDES, 0) + 1

    conn.commit()
    return stats


def record_id_for_occurrence(conn: sqlite3.Connection, path: str, line_start: Optional[int],
                              line_end: Optional[int]) -> Optional[str]:
    """The record id (if any) whose persisted ``record_def`` span at ``path`` contains/overlaps
    ``[line_start, line_end]`` -- an INDEXED lookup (no git-grep, no whole-corpus scan) used to give a retrieval
    hit its real classification unit instead of a bare path. Among several candidates the narrowest (smallest)
    span wins (the most specific enclosing section); a non-local definition is preferred over a local one
    (RECORD#LOCAL) when both cover the same lines. ``line_start``/``line_end`` absent means "the whole occurrence"
    (line 1).

    BR-DAG-AMEND-R1-17 item 6: does NOT call ``ensure_schema`` -- this is a QUERY-time lookup (called from every
    route via ``classify_hit`` below), and the authority layer's schema is built once, eagerly, at BUILD time
    (``authority.layer.build``), the same "built at build time, read at query time" split ``govbridge.lexical.
    query``/``govbridge.semantic.search`` already follow. A store whose authority layer was never built at all
    raises a plain ``sqlite3.Error`` (no ``record_def`` table) -- ``classify_hit``'s own ``except sqlite3.Error``
    around this call already degrades that to "no record id found," exactly the outcome ``ensure_schema`` used to
    produce by creating the (then-empty) table first."""
    ls = line_start if line_start is not None else 1
    le = line_end if line_end is not None else ls
    rows = conn.execute(
        "SELECT id FROM record_def WHERE path=? AND line_start<=? AND line_end>=? "
        "ORDER BY local ASC, (line_end - line_start) ASC LIMIT 1",
        (path, le, ls),
    ).fetchone()
    return rows[0] if rows else None


def classify_hit(conn: sqlite3.Connection, path: Optional[str], commit: Optional[str],
                  line_start: Optional[int] = None, line_end: Optional[int] = None,
                  reg: Optional[registrymod.Registry] = None, mandatory_items: Optional[dict] = None,
                  repo: Optional[str] = None, view_path: Optional[str] = None) -> "lifecyclemod.Classification":
    """Real authority classification for a RETRIEVED route hit -- never a MandatoryItem; section A stays
    resolver-only (ARCHITECTURE.md section 5.3 rule 1), so a class computed here can never be mistaken for
    authority, whatever it says. Routed issue B4/BR-AR-0006 OI-3 ("retrieved results carry placeholder
    UNCLASSIFIED/UNKNOWN ... wire B5's classifier into every route's results"), closed by I1/BR-AR-0009 here so
    every route (lexical/semantic/code/graph) shares one implementation.

    Tries an INDEXED lookup first: if ``record_id_for_occurrence`` identifies a real record id owning this
    (path, line) span, and this store's authority layer already classified that id (the persisted
    ``class_lifecycle`` cache, the SAME ``lifecycle.classify()`` call ``authority.layer.build()`` made), that row
    is returned directly -- no recomputation, no extra Git reads. Otherwise ``lifecycle.classify()`` is called
    fresh, with the found id (full rule 1-4 classification) or the bare path (registry section_anchors-by-path and
    class_rules only -- the honest ceiling for an arbitrary chunk of text that is not itself one whole record).

    BR-DAG-AMEND-R1-17 item 6: does NOT call ``ensure_schema`` -- a QUERY must never build the authority layer's
    schema (``govbridge.route.real_routes``'s own connection moved to ``store.open_db_readonly()`` for exactly this
    reason, and a read-only connection cannot run ``ensure_schema``'s ``CREATE TABLE``/``executescript`` anyway).
    The schema is built once, eagerly, by ``authority.layer.build()`` at BUILD time; a store that never ran it
    degrades gracefully below (``record_id_for_occurrence``'s own ``sqlite3.Error``, caught here) rather than
    being silently repaired by the query itself."""
    unit = None
    if path:
        try:
            unit = record_id_for_occurrence(conn, path, line_start, line_end)
        except sqlite3.Error:
            unit = None
    if unit is not None:
        cached = conn.execute(
            "SELECT unit, cls, lifecycle, derivation, path, commit_id, line_start, line_end "
            "FROM class_lifecycle WHERE unit=?", (unit,)
        ).fetchone()
        if cached is not None:
            return lifecyclemod.Classification(
                unit=cached[0], cls=cached[1], lifecycle=cached[2], derivation=cached[3],
                notes=["classify_hit: from the persisted class_lifecycle cache"],
                path=cached[4], commit=cached[5], line_start=cached[6], line_end=cached[7],
            )
    return lifecyclemod.classify(unit or (path or ""), path=path, commit=commit, line_start=line_start,
                                  line_end=line_end, reg=reg, mandatory_items=mandatory_items, repo=repo,
                                  view_path=view_path)


def digest(conn: sqlite3.Connection) -> LayerDigest:
    """Ensures its own schema FIRST (the same fix B2 applied to its lexical layer digest): govbridge.core.manifest.
    build_manifest() calls every registered layer digest unconditionally, including on a bare connection from a
    test that only exercises govbridge.core and never built this layer."""
    ensure_schema(conn)
    rows = conn.execute(
        "SELECT id, path, commit_id, blob_id, line_start, line_end, rule, local FROM record_def "
        "ORDER BY id, path, line_start"
    ).fetchall()
    rows += conn.execute(
        "SELECT src, type, dst, derivation, evidence_occurrence, evidence_line, note FROM authority_edge "
        "ORDER BY src, type, dst, derivation"
    ).fetchall()
    rows += conn.execute(
        "SELECT unit, cls, lifecycle, derivation, path, commit_id, line_start, line_end FROM class_lifecycle "
        "ORDER BY unit"
    ).fetchall()
    h = hashlib.sha256()
    for row in rows:
        h.update("\x1f".join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(b"\x1e")
    counts = {
        "record_def": conn.execute("SELECT COUNT(*) FROM record_def").fetchone()[0],
        "authority_edge": conn.execute("SELECT COUNT(*) FROM authority_edge").fetchone()[0],
        "class_lifecycle": conn.execute("SELECT COUNT(*) FROM class_lifecycle").fetchone()[0],
    }
    return LayerDigest(rows=sum(counts.values()), digest=h.hexdigest(), extra=counts)


manifestmod.register_layer("authority", digest)
freshnessmod.register_layer_builder("authority", build)
