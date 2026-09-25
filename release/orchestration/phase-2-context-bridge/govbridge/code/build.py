#!/usr/bin/env python3
"""The code layer's BUILD-time behaviour (ARCHITECTURE.md section 4.6, DAG node B3; this run: BR-AR-0014,
``HANDOFFS/BR-HO-0014-b3r-eager-code-layer.md``): an eager builder for every canonical-view ref whose role is not
``history``, plus the build-manifest digest that covers exactly that eager set.

The defect this fixes: until this run, ``govbridge.code`` was entirely **lazy** -- a commit's ``.rs`` blobs were
parsed only the first time a query (``stats``/``callers``/``reads-key``/``history diff``) asked for that commit
(``govbridge.code.symbols.ensure_indexed``). Two from-clean builds' manifests therefore never covered the same blob
set (whichever queries happened to run first, if any), and ``_code_layer_digest`` hashed only ``code_symbol`` rows
-- ``code_call_site``/``code_literal`` were not in the digest at all, though ARCHITECTURE.md section 8.1 requires
the per-layer digest to cover all three, and section 8.1's reproducibility check requires two from-clean builds to
produce the same ``manifest_sha256``.

``ensure_indexed``'s lazy, per-blob-cached parsing is left completely UNCHANGED here -- ``govbridge.code.symbols``/
``history``/``govbridge.graph.code_bridge`` all keep working exactly as before, including a
``callers --commit <history commit>`` query (acceptance check 4: "queries stay unchanged"). This module adds, ON
TOP of it:

1. ``eager_ref_names``: the eager ref set, derived generically from ``config/canonical-view.yaml`` -- an explicit
   per-ref ``layers`` list naming ``"code"``, or (when a ref's spec omits ``layers`` altogether) any role other
   than the architectural ``history`` category. Mirrors ``govbridge.semantic.profile.eligible_ref_names``'s own
   admission rule for its own layer name (restated here, not imported, so this package never crosses the B3/B4
   boundary). Reads only ``RefSpec.role``/``RefSpec.layers`` -- never a ref's NAME -- so no ref, symbol or file is
   ever special-cased (OC-BR-02); today this evaluates to ``{records, product, evidence}`` on the real
   ``config/canonical-view.yaml``, and to every non-``history`` named ref on the ``tests/fixtures/core`` view (which
   omits ``layers`` entirely -- the single-ref V8.3 collapse ARCHITECTURE.md section 10 describes falls out of the
   same rule, with no separate case).

2. ``code_layer_builder``, registered with ``govbridge.core.freshness.register_layer_builder("code", ...)`` -- the
   same extension-point pattern every sibling layer uses (``govbridge/semantic/freshness_layer.py``,
   ``govbridge/lexical/fts.py``). During ``index rebuild``/``update`` it calls the SAME ``ensure_indexed`` for
   every eager ref's *current* commit, then persists exactly which blobs that reached via
   ``govbridge.code.store.set_eager_blobs`` -- a full reset-then-set every call (never an incremental patch), so an
   eager ref that drops a blob (content changed, or the ref moved away from it) is reflected exactly as a
   from-clean build would see it (acceptance check 4, "incremental == full"). The actual expensive step (parsing)
   still only touches blobs ``ensure_indexed`` has not already cached -- ARCHITECTURE.md section 3's existing
   per-blob cache, unchanged -- so an eager ref that has not moved costs one cheap ``git ls-tree`` and no re-parse
   (SO-12: ~1.6 s to parse everything at one commit; well under section 12's ~1.5 s/commit estimate for this node).

3. ``code_layer_digest``, registered with ``govbridge.core.manifest.register_layer("code", ...)``: sha256 over the
   sorted ``code_symbol``, then ``code_call_site``, then ``code_literal`` rows, restricted by ``code_blob.eager`` to
   blobs reachable at the eager ref set as of the last build. A digest function only ever receives the open
   connection (``govbridge.core.manifest.LayerFn``'s signature) -- it cannot re-walk Git itself -- so membership
   has to be persisted DATA, read back the same way ``govbridge.semantic.freshness_layer.vector_layer_digest``
   reads its own cached status/pin id back from ``store_meta`` rather than recomputing them. Because
   ``ensure_indexed`` never sets ``eager`` (``govbridge.code.store``'s module docstring), a query that lazily
   parses a ``history``-only commit's blobs adds ``code_symbol``/``code_call_site``/``code_literal`` rows for
   blobs that are never eager, and the digest -- which only ever reads ``eager=1`` blobs -- does not change
   (acceptance check 3, "query-invariance").

Why one column rather than a second set of tables (BR-HO-0014's own "either/or, report which you chose"): the
marker is a single boolean fact about an already-identified ``code_blob`` row, and acceptance check 5 ("the digest
changes when a single call_site row, and separately a single literal row, differs") then reduces to an ordinary
join predicate over the SAME tables ``ensure_indexed`` already writes -- no second write path to keep in sync, and
no risk of the two tables' blob sets silently drifting apart.
"""
from __future__ import annotations

import hashlib
import sqlite3
from typing import Optional

from govbridge.core.manifest import LayerDigest
from govbridge.core.view import ResolvedView

LAYER_NAME = "code"
HISTORY_ROLE = "history"

FIELD_SEP = "\x1f"
ROW_SEP = "\x1e"


def eager_ref_names(resolved: ResolvedView) -> set[str]:
    """Every NAMED ref (never a ``history``-glob ref -- ``resolved.history`` -- ARCHITECTURE.md section 4.6/
    BR-HO-0014: "every canonical-view ref whose role is not history") whose ``config/canonical-view.yaml`` spec
    admits the "code" layer: an explicit ``layers`` list naming ``"code"``, or -- when a spec omits ``layers``
    altogether -- any role other than the architectural ``history`` category. See this module's own docstring for
    why this is generic (OC-BR-02): only ``RefSpec.role``/``RefSpec.layers`` are ever inspected, never a name."""
    eager: set[str] = set()
    for name in resolved.named:
        spec = next((r for r in resolved.config.refs if r.name == name), None)
        if spec is None:
            continue
        if spec.layers is not None:
            if LAYER_NAME in spec.layers:
                eager.add(name)
        elif spec.role != HISTORY_ROLE:
            eager.add(name)
    return eager


def code_layer_builder(conn: sqlite3.Connection, resolved: ResolvedView, rules, repo, from_clean: bool,
                        changed_refs: Optional[list[str]] = None) -> dict:
    """The eager half of BR-HO-0014 item 1: parse every eager ref's CURRENT commit through the same
    ``ensure_indexed`` a query would use, then persist exactly which blobs that reached (module docstring, item 2).
    ``changed_refs`` is accepted -- every builder shares ``govbridge.core.freshness.BuilderFn``'s signature -- but
    not needed for correctness: an eager ref that did not move costs one cheap ``ensure_indexed`` call (its blobs
    are already cached) and eager membership must be recomputed for the FULL current eager set every call
    regardless, to stay exactly incremental == full (module docstring, item 2) -- ``govbridge.semantic.
    freshness_layer.semantic_layer_builder`` accepts the same parameter for the same reason and does not use it
    either."""
    from govbridge.code import store as codestore
    from govbridge.code import symbols as symbolsmod

    codestore.ensure_schema(conn)
    eager_refs = eager_ref_names(resolved)

    before = conn.execute("SELECT COUNT(*) FROM code_blob").fetchone()[0]
    reachable: set[str] = set()
    rs_files = 0
    for ref_name in sorted(eager_refs):
        commit = resolved.named[ref_name].commit
        entries = symbolsmod.ensure_indexed(conn, commit, repo=repo)
        rs_files += len(entries)
        reachable.update(blob_id for _, blob_id in entries)
    after = conn.execute("SELECT COUNT(*) FROM code_blob").fetchone()[0]

    codestore.set_eager_blobs(conn, reachable)

    return {
        "blobs": max(0, after - before), "occurrences": 0, "chunks": 0,
        "eager_refs": sorted(eager_refs), "eager_blobs": len(reachable), "rs_occurrences": rs_files,
    }


def _hash_rows(rows, tag: str, h) -> int:
    """Feed every row of one table's result set into ``h``, tagged with the table name so rows from two different
    tables can never hash the same as rows from a third combination of the other two (BR-HO-0014 item 2: the digest
    covers three tables' rows, concatenated in a FIXED order -- symbol, then call_site, then literal)."""
    n = 0
    tag_bytes = tag.encode("utf-8") + FIELD_SEP.encode()
    for row in rows:
        h.update(tag_bytes)
        h.update(FIELD_SEP.join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(ROW_SEP.encode())
        n += 1
    return n


def code_layer_digest(conn: sqlite3.Connection) -> LayerDigest:
    """``layers.code`` in the build manifest (ARCHITECTURE.md section 8.1): sha256 over the sorted ``code_symbol``,
    then ``code_call_site``, then ``code_literal`` rows for exactly the blobs ``code_layer_builder`` last marked
    eager -- never whatever a lazy query happens to have parsed (module docstring, item 3: "query-invariant").
    Self-defends with ``ensure_schema()`` first, the same discipline every sibling digest function documents
    (``govbridge.semantic.freshness_layer.vector_layer_digest``'s own docstring), because
    ``govbridge.core.manifest.build_manifest`` calls every registered digest unconditionally, including a
    connection this layer's own builder never touched."""
    from govbridge.code import store as codestore

    codestore.ensure_schema(conn)
    blob_ids = codestore.eager_blob_ids(conn)
    h = hashlib.sha256()
    if not blob_ids:
        return LayerDigest(rows=0, digest=h.hexdigest(), extra={"blobs_parsed": 0})

    placeholders = ",".join("?" * len(blob_ids))
    symbol_rows = conn.execute(
        f"SELECT symbol_id, blob_id, kind, name, qualified_name, module_path, start_line, end_line, is_test, "
        f"derivation FROM code_symbol WHERE blob_id IN ({placeholders}) ORDER BY symbol_id", blob_ids,
    ).fetchall()
    call_rows = conn.execute(
        f"SELECT call_site_id, blob_id, path, line, caller_symbol, callee_text, callee_name, call_kind "
        f"FROM code_call_site WHERE blob_id IN ({placeholders}) ORDER BY call_site_id", blob_ids,
    ).fetchall()
    literal_rows = conn.execute(
        f"SELECT blob_id, path, line, enclosing_symbol, value FROM code_literal "
        f"WHERE blob_id IN ({placeholders}) ORDER BY blob_id, path, line, value, enclosing_symbol", blob_ids,
    ).fetchall()

    n_symbol = _hash_rows(symbol_rows, "code_symbol", h)
    n_call = _hash_rows(call_rows, "code_call_site", h)
    n_literal = _hash_rows(literal_rows, "code_literal", h)

    return LayerDigest(rows=n_symbol + n_call + n_literal, digest=h.hexdigest(), extra={
        "blobs_parsed": len(blob_ids), "symbol_rows": n_symbol, "call_site_rows": n_call,
        "literal_rows": n_literal,
    })
