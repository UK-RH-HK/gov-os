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
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from typing import Optional

from govbridge.core import gitobj, store as corestore
from govbridge.code import resolve, store as codestore
from govbridge.code.adapters import rust_treesitter

LANGUAGE = "rust"


def _open_conn():
    conn = corestore.open_db()
    codestore.ensure_schema(conn)
    return conn


def _rs_paths(commit: str, repo: Optional[str] = None) -> list[str]:
    """Every path at ``commit`` whose name ends ``.rs`` -- exactly what ``git ls-tree -r --name-only <commit> |
    grep -c '\\.rs$'`` counts, regardless of the entry's Git mode (the code-route ``stats`` acceptance check
    compares against that literal shell pipeline)."""
    return [p for p in gitobj.ls_tree_paths(commit, repo=repo) if p.endswith(".rs")]


def _rs_blob_entries(commit: str, repo: Optional[str] = None) -> list[tuple[str, str]]:
    """[(path, blob_id)] for every real, readable ``.rs`` blob at ``commit`` (skips symlinks/submodules, which
    ``git ls-tree`` can in principle name with a ``.rs``-looking path but which carry no parseable text)."""
    out = []
    for entry in gitobj.ls_tree(commit, repo=repo):
        if entry.type == "blob" and entry.mode != "120000" and entry.path.endswith(".rs"):
            out.append((entry.path, entry.oid))
    return out


def ensure_indexed(conn, commit: str, repo: Optional[str] = None) -> list[tuple[str, str]]:
    """Parse and persist every ``.rs`` blob reachable at ``commit`` that is not already cached under the current
    adapter/grammar pin; return [(path, blob_id)] for the whole commit view (cached or freshly parsed alike)."""
    entries = _rs_blob_entries(commit, repo=repo)
    to_parse = []
    for path, blob_id in entries:
        row = conn.execute(
            "SELECT adapter_version, grammar_version FROM code_blob WHERE blob_id=?", (blob_id,)
        ).fetchone()
        stale = row is not None and (
            row[0] != rust_treesitter.ADAPTER_VERSION or row[1] != rust_treesitter.GRAMMAR_VERSION
        )
        if row is None or stale:
            if stale:
                codestore.clear_blob(conn, blob_id)
            to_parse.append((path, blob_id))

    with gitobj.CatFileBatch(repo=repo) as cat:
        for path, blob_id in to_parse:
            data = cat.read(blob_id)
            if data is None:
                continue
            parsed = rust_treesitter.parse_module(data, path)
            _persist(conn, blob_id, path, parsed)
    if to_parse:
        conn.commit()
    return entries


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
    commit_full = _resolve_commit(commit, repo)
    conn = _open_conn()
    entries = ensure_indexed(conn, commit_full, repo=repo)
    blob_ids = [b for _, b in entries]
    symbol_rows = codestore.symbols_for_blobs(conn, blob_ids)
    error_rows = codestore.parse_errors_for_blobs(conn, blob_ids)
    by_path: dict[str, list[dict]] = collections.defaultdict(list)
    for r in error_rows:
        by_path[r["path"]].append(
            {"start_line": r["start_line"], "end_line": r["end_line"], "start_col": r["start_col"],
             "end_col": r["end_col"]}
        )
    files_with_parse_errors = [{"path": p, "spans": sorted(spans, key=lambda s: s["start_line"])}
                                for p, spans in sorted(by_path.items())]
    return {
        "commit": commit_full,
        "rs_files": len(_rs_paths(commit_full, repo=repo)),
        "definitions": len(symbol_rows),
        "fn_definitions": sum(1 for r in symbol_rows if r["kind"] in ("fn", "fn_sig")),
        "test_fns": sum(1 for r in symbol_rows if r["is_test"]),
        "files_with_parse_errors": files_with_parse_errors,
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


def callers(name: str, commit: str, repo: Optional[str] = None) -> dict:
    commit_full = _resolve_commit(commit, repo)
    conn = _open_conn()
    entries = ensure_indexed(conn, commit_full, repo=repo)
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
    return {"symbol": name, "commit": commit_full, "callers": rows}


def reads_key(key_name: str, commit: str, repo: Optional[str] = None) -> dict:
    """Literal-key consumers (ARCHITECTURE.md section 4.6, "Literal-key consumers"): every occurrence of the string
    literal ``key_name`` that is the argument of an accessor call on the same line (``d.str("mutation")``,
    ``r.get("mutation")``) -- a READS_KEY fact. Generic: this answers "who consumes attribute X" for any literal,
    never one name in particular."""
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
            result = callers(args.name, args.commit)
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
