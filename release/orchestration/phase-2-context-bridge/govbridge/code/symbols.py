#!/usr/bin/env python3
"""The code route's query surface (ARCHITECTURE.md section 4.6, DAG node B3): given a commit, lazily parse and
cache every Rust blob it reaches (``ensure_indexed``), then answer generic symbol/call/literal-key questions over
that commit's view -- ``stats``, ``callers`` and ``reads-key``. The operation is generic: it takes a symbol or
literal name as data and returns whatever the parse tables say, never special-casing any particular name, file or
lifecycle (OC-BR-02). An ambiguous call is always returned with every surviving candidate and its
``HEURISTIC_AMBIGUOUS`` label -- this module never collapses that to a single chosen target (BR-HO-0005 notes).

"Lazy per commit": parsing (the expensive step, ~1.56 s for the whole corpus, SO-12) is cached per blob in the
store and only ever redone for a blob this run has not seen before (or whose adapter/grammar version changed).
Resolution (the ~0.1 s step, SO-12) is never cached -- it is recomputed in memory, every query, from exactly the
blobs reachable at the commit being asked about, because it depends on that commit's whole symbol set, not on any
one call site alone (govbridge.code.resolve's module docstring).

Corpus-rule exclusion (BR-AR-0014 follow-up 1): ``ensure_indexed`` classifies every ``.rs`` blob through
``govbridge.core.corpus.classify_entry`` -- the SAME function/config (``config/corpus-rules.yaml``) every other
route already honours -- BEFORE ever parsing it. A blob whose verdict is anything other than ``INCLUDE`` (EXCLUDE,
METADATA_ONLY, LEXICAL_ONLY, NO_DEFAULT_RETRIEVAL -- generic, never only "EXCLUDE" by name) is never handed to
``rust_treesitter.parse_module`` and never gets a ``code_symbol``/``code_call_site``/``code_literal`` row; it is
recorded instead, with its rule id, in ``govbridge.code.store.code_excluded_blob`` (``put_excluded_blob``), so
``stats()`` can disclose it explicitly rather than the blob simply looking unindexed. This is the ONE place in the
code route that classification happens -- both the eager builder (``govbridge.code.build.code_layer_builder``,
which passes its already-loaded ``rules``) and every lazy caller (``stats``/``callers``/``reads-key``/
``history diff``, or a query at a ``history`` commit) go through this SAME function, so neither path can diverge
from the other or from what the exact/lexical/semantic routes already exclude. ``rules``, if not given, defaults to
loading the real ``config/corpus-rules.yaml`` (``_default_rules``) -- the same "resolve from GOV_BRIDGE_DOMAIN when
the caller does not say otherwise" convention ``govbridge.code.adapters.python_ast._default_view_path`` already
uses, so every EXISTING caller of ``ensure_indexed`` (the CLI below, ``govbridge.code.history``,
``govbridge.graph.code_bridge`` -- none of which pass ``rules``) gets real corpus-rule enforcement automatically,
with no signature change visible to them.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Optional

from govbridge import GOV_BRIDGE_DOMAIN
from govbridge.core import corpus, gitobj, store as corestore
from govbridge.code import resolve, store as codestore
from govbridge.code.adapters import rust_treesitter

LANGUAGE = "rust"
INCLUDE_EFFECT = "INCLUDE"  # config/corpus-rules.yaml's own vocabulary (govbridge.core.corpus.Rule.effect); every
                            # other effect (EXCLUDE, METADATA_ONLY, LEXICAL_ONLY, NO_DEFAULT_RETRIEVAL) means "not
                            # code-indexable" here, generically -- see this module's own docstring.


def _open_conn():
    conn = corestore.open_db()
    codestore.ensure_schema(conn)
    return conn


def _open_conn_readonly():
    """The query-time counterpart of :func:`_open_conn` (BR-DAG-AMEND-R1-17 item 5): a connection that CANNOT
    write, by construction (``store.open_db_readonly()``'s ``mode=ro&immutable=1``), and never calls
    ``codestore.ensure_schema`` either -- a query never creates the code layer's tables, only the eager builder
    (``govbridge.code.build.code_layer_builder``, at BUILD time) does. Paired with :func:`ensure_indexed_readonly`,
    this module's own read-only counterpart to :func:`ensure_indexed`."""
    return corestore.open_db_readonly()


class StoreNeedsRebuild(RuntimeError):
    """The code-route twin of ``govbridge.lexical.query.StoreNeedsRebuild`` (BR-DAG-AMEND-R1-17 item 5) -- same
    discipline, same shape: raised by :func:`ensure_indexed_readonly` when a commit's ``.rs`` blobs are not already
    classified/parsed by the eager code layer (``govbridge.code.build.code_layer_builder``, at BUILD time). A query
    (``stats``/``definitions``/``callers``/``reads_key``, and ``govbridge.route.real_routes``'s code route) never
    builds the code layer itself -- never a silent, slower fallback to parsing here, and never a write."""
    CODE = "STORE_NEEDS_REBUILD"

    def __init__(self, missing: str):
        self.missing = missing
        super().__init__(
            f"{self.CODE}: {missing} is missing from this store -- rebuild it (e.g. "
            f"`python -m govbridge index rebuild`) before running a code-route query against it; a query path "
            f"never builds the code layer itself"
        )


def _default_rules_path() -> str:
    return str(Path(GOV_BRIDGE_DOMAIN) / "config" / "corpus-rules.yaml")


def _default_rules() -> list:
    return corpus.load_rules(_default_rules_path())


def _rs_paths(commit: str, repo: Optional[str] = None) -> list[str]:
    """Every path at ``commit`` whose name ends ``.rs`` -- exactly what ``git ls-tree -r --name-only <commit> |
    grep -c '\\.rs$'`` counts, regardless of the entry's Git mode (the code-route ``stats`` acceptance check
    compares against that literal shell pipeline). Deliberately independent of corpus-rule classification: this is
    "how many .rs paths exist", not "how many are code-indexable" (``files_excluded`` in ``stats()`` answers that)."""
    return [p for p in gitobj.ls_tree_paths(commit, repo=repo) if p.endswith(".rs")]


def _rs_tree_entries(commit: str, repo: Optional[str] = None) -> list["gitobj.TreeEntry"]:
    """Every real, readable ``.rs`` blob's full tree entry at ``commit`` (skips symlinks/submodules, which
    ``git ls-tree`` can in principle name with a ``.rs``-looking path but which carry no parseable text). The full
    ``TreeEntry`` (not just ``(path, blob_id)``) is what ``govbridge.core.corpus.classify_entry`` needs -- mode,
    type and size, exactly the same object ``govbridge.core.corpus.coverage_for_ref``/``freshness.core_layer_builder``
    already classify against."""
    out = []
    for entry in gitobj.ls_tree(commit, repo=repo):
        if entry.type == "blob" and entry.mode != "120000" and entry.path.endswith(".rs"):
            out.append(entry)
    return out


def ensure_indexed(conn, commit: str, repo: Optional[str] = None, rules: Optional[list] = None) \
        -> list[tuple[str, str]]:
    """Classify (``govbridge.core.corpus.classify_entry``) and, for every INCLUDE-verdict blob, parse and persist
    it -- both only for a blob not already cached (classified-excluded, or parsed under the current adapter/
    grammar pin) -- for every ``.rs`` blob reachable at ``commit``. Returns [(path, blob_id)] for the WHOLE commit
    view, included and excluded blobs alike (unchanged contract: every existing caller uses this to enumerate the
    commit's ``.rs`` paths, and an excluded blob_id simply never matches any code_symbol/code_call_site/
    code_literal row downstream). ``rules`` defaults to the real ``config/corpus-rules.yaml`` when not given (this
    module's own docstring); the eager builder passes its own already-loaded list instead of reloading it once per
    eager ref."""
    entries = _rs_tree_entries(commit, repo=repo)
    if rules is None:
        rules = _default_rules()

    to_classify = []
    for entry in entries:
        if codestore.is_excluded(conn, entry.oid):
            continue  # already classified excluded -- sticky, never reclassified (module docstring)
        row = conn.execute(
            "SELECT adapter_version, grammar_version FROM code_blob WHERE blob_id=?", (entry.oid,)
        ).fetchone()
        stale = row is not None and (
            row[0] != rust_treesitter.ADAPTER_VERSION or row[1] != rust_treesitter.GRAMMAR_VERSION
        )
        if row is None or stale:
            if stale:
                codestore.clear_blob(conn, entry.oid)
            to_classify.append(entry)

    if to_classify:
        with gitobj.CatFileBatch(repo=repo) as cat:
            sniffer = corpus.ContentSniffer(cat)
            for entry in to_classify:
                verdict = corpus.classify_entry(entry, rules, sniffer)
                if verdict.effect != INCLUDE_EFFECT:
                    codestore.put_excluded_blob(conn, entry.oid, entry.path, verdict.rule_id, verdict.effect)
                    continue
                data = cat.read(entry.oid)
                if data is None:
                    continue
                parsed = rust_treesitter.parse_module(data, entry.path)
                _persist(conn, entry.oid, entry.path, parsed)
        conn.commit()
    return [(e.path, e.oid) for e in entries]


def _code_schema_exists(conn) -> bool:
    return conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='code_blob'"
    ).fetchone() is not None


def ensure_indexed_readonly(conn, commit: str, repo: Optional[str] = None) -> list[tuple[str, str]]:
    """The query-time counterpart of :func:`ensure_indexed` (BR-DAG-AMEND-R1-17 item 5): every ``.rs`` blob
    reachable at ``commit`` must ALREADY be classified (recorded in ``code_excluded_blob``) or parsed (recorded in
    ``code_blob``, at the current adapter/grammar version) by the eager code layer
    (``govbridge.code.build.code_layer_builder``, run at BUILD time by ``govbridge.core.freshness``) -- this
    function only ever READS ``sqlite_master``/``code_blob``/``code_excluded_blob``, never classifies, parses or
    persists anything itself. A blob this store has not already indexed raises :class:`StoreNeedsRebuild` (never a
    silent, slower fallback to building it here, and never a write) -- exactly the discipline
    ``govbridge.lexical.query.StoreNeedsRebuild``/``govbridge.semantic.vectors.StoreNeedsRebuild`` already use for
    their own build-time structures. Every existing caller of ``ensure_indexed`` that legitimately needs the LAZY,
    build-on-demand behaviour (``govbridge.code.build.code_layer_builder`` itself, at build time; ``govbridge.code.
    history``'s own historical-commit diffs; ``govbridge.graph.code_bridge``) keeps calling ``ensure_indexed``
    unchanged -- this function is additive, used only by this module's own query surface
    (``stats``/``definitions``/``callers``/``reads_key``) and by ``govbridge.route.real_routes``'s code route."""
    entries = _rs_tree_entries(commit, repo=repo)
    if not entries:
        return []
    if not _code_schema_exists(conn):
        raise StoreNeedsRebuild(
            f"table 'code_blob' (govbridge.code.build) -- the code layer has never been built on this store"
        )
    for entry in entries:
        if codestore.is_excluded(conn, entry.oid):
            continue  # already classified excluded, at build time -- never reclassified (module docstring)
        row = conn.execute(
            "SELECT adapter_version, grammar_version FROM code_blob WHERE blob_id=?", (entry.oid,)
        ).fetchone()
        if row is None:
            raise StoreNeedsRebuild(
                f"code_blob row for {entry.path!r} ({entry.oid}) at commit {commit} (govbridge.code.build)"
            )
        if row[0] != rust_treesitter.ADAPTER_VERSION or row[1] != rust_treesitter.GRAMMAR_VERSION:
            raise StoreNeedsRebuild(
                f"code_blob row for {entry.path!r} ({entry.oid}) is stale -- adapter/grammar version changed "
                f"(govbridge.code.build)"
            )
    return [(e.path, e.oid) for e in entries]


def _persist(conn, blob_id: str, path: str, parsed) -> None:
    codestore.put_blob(
        conn, blob_id, path, LANGUAGE, rust_treesitter.ADAPTER_ID, rust_treesitter.ADAPTER_VERSION,
        rust_treesitter.GRAMMAR_VERSION, ok_parse=not parsed.has_error, error_count=len(parsed.parse_errors),
    )
    # Symbol ids are computed with the *ORIGINAL* parsed qualname/line, then symbols are reloaded by symbol_id for
    # the caller->id linkage below (a call's caller_qualified_name is resolved to the enclosing fn's symbol_id).
    qual_to_sid: dict[str, str] = {}
    for s in parsed.symbols:
        sid = codestore.symbol_id(blob_id, s.kind, s.qualified_name, s.start_line)
        codestore.put_symbol(conn, sid, blob_id, s.kind, s.name, s.qualified_name, s.module_path, s.start_line,
                              s.end_line, s.is_test, s.derivation)
        if s.kind in ("fn", "fn_sig"):
            qual_to_sid.setdefault(s.qualified_name, sid)
    ordinal_by_key: dict[tuple, int] = collections.defaultdict(int)
    for c in parsed.calls:
        key = (c.line, c.callee_text)
        ordinal = ordinal_by_key[key]
        ordinal_by_key[key] += 1
        cid = codestore.call_site_id(blob_id, c.line, c.callee_text, ordinal)
        caller_sid = qual_to_sid.get(c.caller_qualified_name) if c.caller_qualified_name else None
        codestore.put_call_site(conn, cid, blob_id, path, c.line, caller_sid, c.callee_text, c.callee_name,
                                 c.call_kind)
    for lit in parsed.literals:
        enclosing_sid = qual_to_sid.get(lit.enclosing_qualified_name) if lit.enclosing_qualified_name else None
        codestore.put_literal(conn, blob_id, path, lit.line, enclosing_sid, lit.value)
    for err in parsed.parse_errors:
        codestore.put_parse_error(conn, blob_id, path, err.start_line, err.end_line, err.start_col, err.end_col)


def _definitions(conn, blob_ids: list[str], path_by_blob: dict[str, str]) -> list[resolve.Definition]:
    return [
        resolve.Definition(symbol_id=r["symbol_id"], blob_id=r["blob_id"],
                            path=path_by_blob.get(r["blob_id"], ""), kind=r["kind"], name=r["name"],
                            qualified_name=r["qualified_name"], module_path=r["module_path"])
        for r in codestore.symbols_for_blobs(conn, blob_ids)
    ]


def _call_sites(conn, blob_ids: list[str]) -> list[resolve.CallSite]:
    return [
        resolve.CallSite(call_site_id=r["call_site_id"], blob_id=r["blob_id"], path=r["path"], line=r["line"],
                          callee_text=r["callee_text"], callee_name=r["callee_name"], call_kind=r["call_kind"])
        for r in codestore.call_sites_for_blobs(conn, blob_ids)
    ]


def _resolve_commit(commit: str, repo: Optional[str]) -> str:
    full = gitobj.resolve_commit(commit, repo=repo)
    if full is None:
        raise ValueError(f"commit {commit!r} does not resolve")
    return full


def stats(commit: str, repo: Optional[str] = None) -> dict:
    # NOT converted to the read-only path (BR-DAG-AMEND-R1-17 item 5's own read-only discipline binds the QUERY
    # surface real_routes.py's code route actually calls -- definitions_readonly/callers_readonly below, and
    # ensure_indexed_readonly itself); this is a diagnostic/inspection command (govbridge.code.symbols's own CLI,
    # `python -m govbridge.code.symbols stats`), not one of BR-DAG-AMEND-R1-15's enumerated query commands, and
    # every existing caller (tests/code/test_symbols_integration.py, tests/code/test_corpus_exclusion.py) already
    # relies on its lazy, build-on-first-use behaviour against a commit no eager build has ever touched -- keeping
    # it lazy is "no silent narrowing" for those callers, not an omission of this repair.
    commit_full = _resolve_commit(commit, repo)
    conn = _open_conn()
    entries = ensure_indexed(conn, commit_full, repo=repo)
    blob_ids = [b for _, b in entries]
    symbol_rows = codestore.symbols_for_blobs(conn, blob_ids)
    error_rows = codestore.parse_errors_for_blobs(conn, blob_ids)
    excluded_rows = codestore.excluded_for_blobs(conn, blob_ids)
    by_path: dict[str, list[dict]] = collections.defaultdict(list)
    for r in error_rows:
        by_path[r["path"]].append(
            {"start_line": r["start_line"], "end_line": r["end_line"], "start_col": r["start_col"],
             "end_col": r["end_col"]}
        )
    files_with_parse_errors = [{"path": p, "spans": sorted(spans, key=lambda s: s["start_line"])}
                                for p, spans in sorted(by_path.items())]
    # BR-AR-0014 follow-up 1: an explicit, disclosed exclusion (rule id + effect) rather than a blob that simply
    # looks unindexed -- every entry here has ZERO code_symbol/code_call_site/code_literal rows, by construction
    # (ensure_indexed never parses an excluded blob).
    files_excluded = [{"path": r["path"], "rule_id": r["rule_id"], "effect": r["effect"]}
                       for r in sorted(excluded_rows, key=lambda r: r["path"])]
    return {
        "commit": commit_full,
        "rs_files": len(_rs_paths(commit_full, repo=repo)),
        "definitions": len(symbol_rows),
        "fn_definitions": sum(1 for r in symbol_rows if r["kind"] in ("fn", "fn_sig")),
        "test_fns": sum(1 for r in symbol_rows if r["is_test"]),
        "files_with_parse_errors": files_with_parse_errors,
        "files_excluded": files_excluded,
        "adapter": {"id": rust_treesitter.ADAPTER_ID, "version": rust_treesitter.ADAPTER_VERSION,
                    "grammar_version": rust_treesitter.GRAMMAR_VERSION},
    }


def _row_for_call(c: resolve.CallSite, res: resolve.Resolution, defs_by_id: dict) -> dict:
    targets = [defs_by_id[sid] for sid in res.target_symbol_ids if sid in defs_by_id]
    return {
        "at": f"{c.path}:{c.line}",
        "callee_text": c.callee_text,
        "call_kind": c.call_kind,
        "label": res.label,
        "n_candidates": res.n_candidates,
        "targets": [{"path": d.path, "qualified_name": d.qualified_name, "symbol_id": d.symbol_id}
                    for d in targets],
    }


def definitions(name: str, commit: str, repo: Optional[str] = None) -> dict:
    """Every definition (across the whole commit's parsed ``.rs`` blobs) whose bare ``name`` or ``qualified_name``
    matches ``name`` exactly, or whose ``qualified_name`` ends ``::name`` -- the "given symbol names, return each
    definition" half of ARCHITECTURE.md section 4.6's generic chain probe (``callers``/``reads_key`` already exist
    as their own commands; this is the definition-SITE lookup the code route needs to show a symbol's own
    location, with lines, not only its callers). Generic: takes any name as data, never special-cases one.

    NOT converted to the read-only path: existing callers (tests/code/test_definitions_lookup.py) rely on its lazy,
    build-on-first-use behaviour. ``govbridge.route.real_routes``'s code route uses :func:`definitions_readonly`
    instead (BR-DAG-AMEND-R1-17 item 5)."""
    commit_full = _resolve_commit(commit, repo)
    conn = _open_conn()
    entries = ensure_indexed(conn, commit_full, repo=repo)
    return _definitions_result(conn, name, commit_full, entries)


def _definitions_result(conn, name: str, commit_full: str, entries: list[tuple[str, str]]) -> dict:
    path_by_blob = {b: p for p, b in entries}
    blob_ids = [b for _, b in entries]
    rows = codestore.symbols_for_blobs(conn, blob_ids)
    hits = [
        r for r in rows
        if r["name"] == name or r["qualified_name"] == name or r["qualified_name"].endswith("::" + name)
    ]
    hits.sort(key=lambda r: (path_by_blob.get(r["blob_id"], ""), r["start_line"]))
    return {
        "symbol": name, "commit": commit_full,
        "definitions": [
            {"path": path_by_blob.get(r["blob_id"], ""), "qualified_name": r["qualified_name"], "kind": r["kind"],
             "start_line": r["start_line"], "end_line": r["end_line"], "blob_id": r["blob_id"],
             "symbol_id": r["symbol_id"]}
            for r in hits
        ],
    }


def definitions_readonly(name: str, commit: str, repo: Optional[str] = None) -> dict:
    """The query-time counterpart of :func:`definitions` (BR-DAG-AMEND-R1-17 item 5): identical result shape and
    matching logic (:func:`_definitions_result`, shared by both), but reads the commit's already-indexed ``.rs``
    blobs via :func:`_open_conn_readonly`/:func:`ensure_indexed_readonly` instead of classifying/parsing/persisting
    them itself. Used by ``govbridge.route.real_routes``'s code route -- the actual query surface this item binds,
    per its own acceptance check (a gather against a file-level read-only store)."""
    commit_full = _resolve_commit(commit, repo)
    conn = _open_conn_readonly()
    entries = ensure_indexed_readonly(conn, commit_full, repo=repo)
    return _definitions_result(conn, name, commit_full, entries)


def _callers_result(conn, name: str, commit_full: str, entries: list[tuple[str, str]],
                     page_size: Optional[int], cursor: Optional[str]) -> dict:
    blob_ids = [b for _, b in entries]
    path_by_blob = {b: p for p, b in entries}
    definitions = _definitions(conn, blob_ids, path_by_blob)
    defs_by_id = {d.symbol_id: d for d in definitions}
    index = resolve.Index.build(definitions)
    calls = _call_sites(conn, blob_ids)

    simple_name = name.rsplit("::", 1)[-1]
    qualified_filter = name if "::" in name else None

    rows = []
    for c in calls:
        if c.callee_name != simple_name:
            continue
        res = resolve.resolve_call(c, index)
        if qualified_filter is not None:
            targets = [defs_by_id[sid] for sid in res.target_symbol_ids if sid in defs_by_id]
            if targets and not any(d.qualified_name == qualified_filter for d in targets):
                continue
        rows.append(_row_for_call(c, res, defs_by_id))
    rows.sort(key=lambda r: r["at"])

    result = {"symbol": name, "commit": commit_full, "callers": rows}
    if page_size is not None:
        offset = int(cursor) if cursor else 0
        page = rows[offset:offset + page_size]
        next_cursor = str(offset + page_size) if offset + page_size < len(rows) else None
        result["callers"] = page
        result["page_size"] = page_size
        result["cursor"] = cursor
        result["next_cursor"] = next_cursor
        result["total"] = len(rows)
    return result


def callers(name: str, commit: str, repo: Optional[str] = None, page_size: Optional[int] = None,
            cursor: Optional[str] = None) -> dict:
    """``page_size``/``cursor`` (R1-RL paging): a simple, deterministic offset cursor over the SAME sorted `rows`
    an unpaged call already computes -- omitted, the result is byte-identical to before (every existing caller);
    given, ``callers`` holds only that page, plus ``next_cursor`` (``None`` once exhausted) and ``total``, so
    following ``next_cursor`` to exhaustion yields exactly the union an unpaged call returns (the acceptance
    check).

    NOT converted to the read-only path: existing callers (tests/code/test_symbols_integration.py) rely on its
    lazy, build-on-first-use behaviour. ``govbridge.route.real_routes``'s code route uses :func:`callers_readonly`
    instead (BR-DAG-AMEND-R1-17 item 5)."""
    commit_full = _resolve_commit(commit, repo)
    conn = _open_conn()
    entries = ensure_indexed(conn, commit_full, repo=repo)
    return _callers_result(conn, name, commit_full, entries, page_size, cursor)


def callers_readonly(name: str, commit: str, repo: Optional[str] = None, page_size: Optional[int] = None,
                      cursor: Optional[str] = None) -> dict:
    """The query-time counterpart of :func:`callers` (BR-DAG-AMEND-R1-17 item 5): identical result shape and
    matching logic (:func:`_callers_result`, shared by both), but reads the commit's already-indexed ``.rs`` blobs
    via :func:`_open_conn_readonly`/:func:`ensure_indexed_readonly` instead of classifying/parsing/persisting them
    itself. Used by ``govbridge.route.real_routes``'s code route."""
    commit_full = _resolve_commit(commit, repo)
    conn = _open_conn_readonly()
    entries = ensure_indexed_readonly(conn, commit_full, repo=repo)
    return _callers_result(conn, name, commit_full, entries, page_size, cursor)


def reads_key(key_name: str, commit: str, repo: Optional[str] = None) -> dict:
    """Literal-key consumers (ARCHITECTURE.md section 4.6, "Literal-key consumers"): every occurrence of the string
    literal ``key_name`` that is the argument of an accessor call on the same line (``d.str("mutation")``,
    ``r.get("mutation")``) -- a READS_KEY fact. Generic: this answers "who consumes attribute X" for any literal,
    never one name in particular.

    NOT converted to the read-only path (BR-DAG-AMEND-R1-17 item 5): not called by ``govbridge.route.real_routes``
    at all, and existing callers (tests/code/test_symbols_integration.py) rely on its lazy, build-on-first-use
    behaviour."""
    commit_full = _resolve_commit(commit, repo)
    conn = _open_conn()
    entries = ensure_indexed(conn, commit_full, repo=repo)
    blob_ids = [b for _, b in entries]
    path_by_blob = {b: p for p, b in entries}
    definitions = _definitions(conn, blob_ids, path_by_blob)
    defs_by_id = {d.symbol_id: d for d in definitions}
    calls = _call_sites(conn, blob_ids)
    literal_rows = codestore.literals_for_blobs(conn, blob_ids)

    # "an accessor argument on the same line" (ARCHITECTURE.md section 4.6): a normal method call (`r.get(...)`),
    # or the same shape found by the macro-token scan when the accessor sits inside a macro's token tree, e.g.
    # `matches!(d.str("mutation").as_str(), ...)` -- tree-sitter never turns that into a field_expression call, so
    # only the macro_token scan sees it (govbridge.code.adapters.rust_treesitter._scan_macro_tokens).
    calls_by_line: dict[tuple[str, int], list[resolve.CallSite]] = collections.defaultdict(list)
    for c in calls:
        if c.call_kind in ("method", "macro_token"):
            calls_by_line[(c.blob_id, c.line)].append(c)

    rows = []
    for lit in literal_rows:
        if lit["value"] != key_name:
            continue
        accessors = calls_by_line.get((lit["blob_id"], lit["line"]), [])
        if not accessors:
            continue
        enclosing = defs_by_id.get(lit["enclosing_symbol"])
        rows.append({
            "at": f"{lit['path']}:{lit['line']}",
            "enclosing_symbol": enclosing.qualified_name if enclosing else None,
            "accessors": [c.callee_text for c in accessors],
        })
    rows.sort(key=lambda r: r["at"])
    return {"key": key_name, "commit": commit_full, "reads": rows}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.code.symbols")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_stats = sub.add_parser("stats")
    sp_stats.add_argument("--commit", required=True)
    sp_stats.add_argument("--json", action="store_true")

    sp_callers = sub.add_parser("callers")
    sp_callers.add_argument("name")
    sp_callers.add_argument("--commit", required=True)
    sp_callers.add_argument("--page-size", type=int, default=None)
    sp_callers.add_argument("--cursor", default=None)
    sp_callers.add_argument("--json", action="store_true")

    sp_reads = sub.add_parser("reads-key")
    sp_reads.add_argument("name")
    sp_reads.add_argument("--commit", required=True)
    sp_reads.add_argument("--json", action="store_true")

    args = p.parse_args(argv)
    try:
        if args.cmd == "stats":
            result = stats(args.commit)
        elif args.cmd == "callers":
            result = callers(args.name, args.commit, page_size=args.page_size, cursor=args.cursor)
        elif args.cmd == "reads-key":
            result = reads_key(args.name, args.commit)
        else:
            return 2
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        return 1

    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
