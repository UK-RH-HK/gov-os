#!/usr/bin/env python3
"""Wires ``govbridge.graph.derive``'s CALLS/READS_KEY/TESTS functions (``callers_of``/``callees_of``/
``reads_key_of``/``tests_of``) against the REAL code route's tables (routed issue B5/BR-AR-0007: "Code-derived
edges (CALLS/READS_KEY/TESTS) are on-demand, tested only on a B3-schema fixture. Wire them against the real B3
tables, so why/impact reach code.").

Why this is a separate module, rather than a change to ``derive.py``'s own SQL: ``derive.py``'s four functions are
proven against ``tests/graph/test_derive.py``'s own synthetic ``_b3_shaped_conn()`` fixture -- a small, fixed
schema (``symbol``, ``call_site``, ``literal``, ``resolution``, no ``code_`` prefix, ``resolution`` persisted) that
is NOT B3's real schema (``code_symbol``/``code_call_site``/``code_literal``, no persisted ``resolution`` table --
B3's own OI-2: "a persisted-by-call-site cache would go stale across commits"). That test file is existing and
frozen. Rather than change ``derive.py``'s queries (which would break it), this module builds an in-memory
connection that HAS that exact small schema, populated from B3's real, persisted ``code_symbol``/``code_call_site``/
``code_literal`` rows for one commit's indexed blobs, with resolution computed in memory exactly the way
``govbridge.code.symbols.callers()`` already computes it (``govbridge.code.resolve``, never persisted). The result
is handed to ``why()``/``impact`` as ``code_conn`` -- ``derive.py`` itself never changes.
"""
from __future__ import annotations

import sqlite3
from typing import Optional

_SHAPED_SCHEMA = """
CREATE TABLE symbol (symbol_id TEXT, blob TEXT, kind TEXT, name TEXT, qualified_name TEXT,
                      module_path TEXT, start INTEGER, end INTEGER, is_test INTEGER);
CREATE TABLE call_site (blob TEXT, line INTEGER, caller_symbol TEXT, callee_text TEXT, callee_name TEXT,
                         call_kind TEXT);
CREATE TABLE literal (blob TEXT, line INTEGER, enclosing_symbol TEXT, value TEXT);
CREATE TABLE resolution (call_site INTEGER, target_symbol TEXT, label TEXT, n_candidates INTEGER);
"""


def build_shaped_code_connection(commit: str, repo: Optional[str] = None) -> Optional[sqlite3.Connection]:
    """An in-memory connection matching ``govbridge.graph.derive``'s expected schema, for every ``.rs`` blob
    reachable at ``commit`` (already parsed/cached by the eager code-layer builder, ``govbridge.code.build`` -- this
    function never re-implements parsing or caching, only the SHAPE translation). Returns None if ``commit`` does
    not resolve, or if the code route module itself is unavailable (defensive: an import-time failure must never
    break ``why``/``impact``, matching the "honest MISSING, not an error" discipline ``derive.py`` already
    documents).

    BR-DAG-AMEND-R1-17 item 5 reopening: this is a QUERY, at query time -- it reads via
    ``codesymbols._open_conn_readonly()``/``codesymbols.ensure_indexed_readonly()`` (never
    ``_open_conn()``/``ensure_indexed``, which now BUILD, and which this function used to call, writing to the
    store on any commit the eager builder had not already reached). A commit whose ``.rs`` blobs the eager builder
    has not indexed raises the typed ``codesymbols.StoreNeedsRebuild`` -- deliberately NOT caught here (the
    pre-existing ``except Exception: return None`` around this call used to swallow it, indistinguishable from a
    genuinely code-less commit): a caller that wants the old "honest MISSING, never an error" degradation for this
    one, specific, typed condition catches it itself (``govbridge.route.real_routes``'s own code route does, and
    counts any other exception rather than swallowing it silently -- see that module's own
    ``_record_unexpected_exception``); ``govbridge.graph.impact`` does not catch anything here at all, so it now
    raises through, exactly like every other read-only query command (BR-DAG-AMEND-R1-15)."""
    try:
        from govbridge.code import resolve as coderesolve
        from govbridge.code import store as codestore
        from govbridge.code import symbols as codesymbols
    except Exception:
        return None

    try:
        commit_full = codesymbols._resolve_commit(commit, repo)
    except ValueError:
        return None

    real_conn = codesymbols._open_conn_readonly()
    entries = codesymbols.ensure_indexed_readonly(real_conn, commit_full, repo=repo)
    if not entries:
        return None
    blob_ids = [b for _, b in entries]

    symbol_rows = codestore.symbols_for_blobs(real_conn, blob_ids)
    call_rows = codestore.call_sites_for_blobs(real_conn, blob_ids)
    literal_rows = codestore.literals_for_blobs(real_conn, blob_ids)

    # resolution, computed in memory over exactly this commit's definitions -- B3's own design (govbridge.code.
    # resolve's module docstring): "recomputed in memory, every query, from exactly the blobs reachable at the
    # commit being asked about".
    defs_for_index = [
        coderesolve.Definition(symbol_id=r["symbol_id"], blob_id=r["blob_id"], path="", kind=r["kind"],
                                name=r["name"], qualified_name=r["qualified_name"], module_path=r["module_path"])
        for r in symbol_rows
    ]
    index = coderesolve.Index.build(defs_for_index)
    calls_for_resolve = [
        coderesolve.CallSite(call_site_id=r["call_site_id"], blob_id=r["blob_id"], path=r["path"], line=r["line"],
                              callee_text=r["callee_text"], callee_name=r["callee_name"], call_kind=r["call_kind"])
        for r in call_rows
    ]

    # B3's real tables key caller/enclosing symbols by symbol_id; derive.py's schema (and its frozen fixture) uses
    # a qualified_name string directly for `call_site.caller_symbol` / `literal.enclosing_symbol` -- translate.
    qualname_by_symbol_id = {r["symbol_id"]: r["qualified_name"] for r in symbol_rows}

    shaped = sqlite3.connect(":memory:")
    shaped.executescript(_SHAPED_SCHEMA)

    shaped.executemany(
        "INSERT INTO symbol VALUES (?,?,?,?,?,?,?,?,?)",
        [(r["symbol_id"], r["blob_id"], r["kind"], r["name"], r["qualified_name"], r["module_path"],
          r["start_line"], r["end_line"], r["is_test"]) for r in symbol_rows],
    )
    shaped.executemany(
        "INSERT INTO literal VALUES (?,?,?,?)",
        [(r["blob_id"], r["line"], qualname_by_symbol_id.get(r["enclosing_symbol"]), r["value"])
         for r in literal_rows],
    )

    # resolve.CallSite carries no `caller_symbol` (resolve_call needs only the callee side); zip against the RAW
    # rows (same order as calls_for_resolve, built from the same call_rows list) to recover it.
    for c, raw in zip(calls_for_resolve, call_rows):
        res = coderesolve.resolve_call(c, index)
        raw_caller_symbol = raw["caller_symbol"]
        caller_qname = qualname_by_symbol_id.get(raw_caller_symbol) if raw_caller_symbol else None
        cur = shaped.execute(
            "INSERT INTO call_site(blob, line, caller_symbol, callee_text, callee_name, call_kind) "
            "VALUES (?,?,?,?,?,?)",
            (c.blob_id, c.line, caller_qname, c.callee_text, c.callee_name, c.call_kind),
        )
        rowid = cur.lastrowid
        for target_sid in res.target_symbol_ids:
            if target_sid not in qualname_by_symbol_id:
                continue
            shaped.execute(
                "INSERT INTO resolution(call_site, target_symbol, label, n_candidates) VALUES (?,?,?,?)",
                (rowid, target_sid, res.label, res.n_candidates),
            )
    shaped.commit()
    return shaped
