#!/usr/bin/env python3
"""The lexical route's index (ARCHITECTURE.md section 4.3, node B2): one FTS5 virtual table over the chunk rows
``govbridge.core`` already decided belong in the corpus (``store.db``'s ``chunk`` table, keyed by blob). This
module owns exactly two tables of its own, both new:

* ``lexical_fts`` -- the FTS5 index itself, ``tokenize = "porter unicode61 tokenchars '_'"``
  (``MEMORY_POLICY.yaml:15`` names the base tokenizer ``porter unicode61``; the ``tokenchars '_'`` addition is
  ARCHITECTURE.md section 4.3's "one deliberate addition", so snake_case identifiers such as
  ``partition_floor_rules_against_kernel`` stay a single token instead of splitting on ``_``).
* ``lexical_indexed_blob`` -- bookkeeping: which blobs have already been folded into the FTS index, so a rebuild
  only touches chunks belonging to a newly-seen blob (ARCHITECTURE.md section 3: "chunks + FTS rows ... keyed by
  (blob, chunker_version, corpus-rules sha) ... invalidated by ... a new blob").

Registers ``lexical_layer_builder`` with ``govbridge.core.freshness`` (so ``freshness rebuild --layer lexical``
can reach it) and ``lexical_layer_digest`` with ``govbridge.core.manifest`` (so the build manifest carries this
layer's digest) at import time of this module -- see ``govbridge/lexical/__init__.py``.
"""
from __future__ import annotations

import hashlib
from typing import Optional

from govbridge.core import freshness as freshnessmod
from govbridge.core import manifest as manifestmod

#: MEMORY_POLICY.yaml:15 base tokenizer, plus ARCHITECTURE.md section 4.3's tokenchars '_' addition. Part of the
#: layer's pin: changing it must be reflected in the digest's `extra` block so a stale FTS table is never silently
#: reused as if it were built with a different tokenizer (the same discipline core.chunking.CHUNKER_VERSION uses).
TOKENIZE = "porter unicode61 tokenchars '_'"
LAYER_NAME = "lexical"

FIELD_SEP = "\x1f"
ROW_SEP = "\x1e"

SCHEMA_SQL = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS lexical_fts USING fts5(
    chunk_id UNINDEXED,
    blob_id UNINDEXED,
    start_line UNINDEXED,
    end_line UNINDEXED,
    text,
    tokenize = "{TOKENIZE}"
);
CREATE TABLE IF NOT EXISTS lexical_indexed_blob (
    blob_id TEXT PRIMARY KEY
);
"""


def ensure_schema(conn) -> None:
    """Idempotent: safe to call on every build and every query, same convention as
    ``govbridge.core.store.open_db``'s ``CREATE TABLE IF NOT EXISTS``."""
    conn.executescript(SCHEMA_SQL)


def clear_layer_tables(conn) -> None:
    """A FULL rebuild of this layer only -- never touches core's own tables (``occurrence``/``blob``/``chunk``
    belong to ``govbridge.core.store``, not this module)."""
    conn.execute("DELETE FROM lexical_fts")
    conn.execute("DELETE FROM lexical_indexed_blob")
    conn.commit()


def build(conn, from_clean: bool = False) -> dict:
    """Fold every chunk whose blob is not yet in the FTS index into it. Pure with respect to Git and the view: by
    the time this runs, ``govbridge.core``'s own layer builder has already turned Git content into ``chunk`` rows;
    this function never shells out to Git itself. A blob already indexed is never re-inserted (no duplicate rows
    on a repeated incremental build), matching ARCHITECTURE.md section 3's per-layer invalidation rule.
    """
    ensure_schema(conn)
    if from_clean:
        clear_layer_tables(conn)
    rows = conn.execute(
        "SELECT c.chunk_id, c.blob_id, c.start_line, c.end_line, c.text FROM chunk c "
        "WHERE c.blob_id NOT IN (SELECT blob_id FROM lexical_indexed_blob) ORDER BY c.chunk_id"
    ).fetchall()
    new_blobs = set()
    for chunk_id, blob_id, start_line, end_line, text in rows:
        conn.execute(
            "INSERT INTO lexical_fts(chunk_id, blob_id, start_line, end_line, text) VALUES (?,?,?,?,?)",
            (chunk_id, blob_id, start_line, end_line, text),
        )
        new_blobs.add(blob_id)
    if new_blobs:
        conn.executemany(
            "INSERT OR IGNORE INTO lexical_indexed_blob(blob_id) VALUES (?)",
            [(b,) for b in sorted(new_blobs)],
        )
        conn.execute("INSERT INTO lexical_fts(lexical_fts) VALUES('optimize')")
    conn.commit()
    return {"blobs": len(new_blobs), "occurrences": 0, "chunks": len(rows)}


def lexical_layer_builder(conn, resolved, rules, repo, from_clean: bool,
                           changed_refs: Optional[list] = None) -> dict:
    """The ``govbridge.core.freshness`` layer-builder signature (``BuilderFn``). ``resolved``/``rules``/``repo``/
    ``changed_refs`` are accepted for signature compatibility with every other registered builder (core calls
    every builder the same way) but unused here: this layer's whole input is the ``chunk`` table core already
    built from them -- see ``build()`` above."""
    return build(conn, from_clean=from_clean)


def _rows_digest(rows: list[tuple]) -> str:
    h = hashlib.sha256()
    for row in rows:
        h.update(FIELD_SEP.join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(ROW_SEP.encode())
    return h.hexdigest()


def lexical_layer_digest(conn) -> "manifestmod.LayerDigest":
    """Safe to call on ANY connection ``store.open_db()`` can produce, even one this layer has never built into
    (``store.open_db()`` only creates core's own schema; each layer creates its own lazily). Without this,
    ``govbridge.core.manifest.build_manifest()`` -- which calls every REGISTERED layer's digest function
    unconditionally -- would raise ``no such table`` the moment this package is merely imported alongside a
    connection nothing has indexed yet (e.g. a bare fixture connection in another node's test module, once both
    packages are imported in the same process at node I1). A never-built layer reports a deterministic empty
    digest, the same shape ``occurrence_layer_digest``/``chunk_layer_digest`` give for an empty-but-present core
    table."""
    ensure_schema(conn)
    rows = conn.execute(
        "SELECT chunk_id, blob_id, start_line, end_line, text FROM lexical_fts ORDER BY chunk_id"
    ).fetchall()
    return manifestmod.LayerDigest(rows=len(rows), digest=_rows_digest(rows), extra={"tokenize": TOKENIZE})


freshnessmod.register_layer_builder(LAYER_NAME, lexical_layer_builder)
manifestmod.register_layer(LAYER_NAME, lexical_layer_digest)
