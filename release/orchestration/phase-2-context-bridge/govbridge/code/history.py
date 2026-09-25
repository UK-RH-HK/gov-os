#!/usr/bin/env python3
"""Lazy per-commit symbol history (ARCHITECTURE.md section 4.6, "Symbol history (C6 temporal)"): ``DELETED_IN``
and ``INTRODUCED_IN`` facts, taken as the set difference between two commits' parsed Rust definitions. Both commits
are indexed through ``govbridge.code.symbols.ensure_indexed`` -- the usual lazy, per-blob cache, so a file unchanged
between the two commits is parsed once (govbridge.code.symbols' module docstring), and the same blob's symbols are
therefore identical whichever commit encounters it first.

This module is exact about the parse tables -- a symbol either has a definition (by ``(kind, qualified_name)``) at
a commit's view or it does not -- and says nothing about *why* it went; every fact it emits carries the
``EXACT_PARSE`` derivation label, never a heuristic one. It does not track renames or moves: a symbol that only
changed file or line keeps the same ``(kind, qualified_name)`` and is therefore never reported as deleted+
introduced (this is intentional, not an oversight -- see the module-level comment below ``diff``).
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from govbridge.core import gitobj, store as corestore
from govbridge.code import store as codestore, symbols as symbolsmod
from govbridge.code.adapters.rust_treesitter import DERIVATION_EXACT_PARSE

DELETED_IN = "DELETED_IN"
INTRODUCED_IN = "INTRODUCED_IN"


def _resolve_commit(commit: str, repo: Optional[str]) -> str:
    full = gitobj.resolve_commit(commit, repo=repo)
    if full is None:
        raise ValueError(f"commit {commit!r} does not resolve")
    return full


def _definition_set(conn, commit: str, repo: Optional[str]) -> dict:
    """{(kind, qualified_name): row} for every Rust definition reachable at ``commit``. Keyed by (kind,
    qualified_name) rather than by symbol_id (which also folds in the blob and the line, and so would treat a pure
    line-shift as a delete+introduce pair)."""
    entries = symbolsmod.ensure_indexed(conn, commit, repo=repo)
    blob_ids = [b for _, b in entries]
    path_by_blob = {b: p for p, b in entries}
    rows = codestore.symbols_for_blobs(conn, blob_ids)
    out: dict = {}
    for r in rows:
        key = (r["kind"], r["qualified_name"])
        if key in out:
            continue  # first occurrence wins; several defs can share a (kind, name) pair across files
        out[key] = {
            "kind": r["kind"], "name": r["name"], "qualified_name": r["qualified_name"],
            "path": path_by_blob.get(r["blob_id"], ""), "start_line": r["start_line"], "end_line": r["end_line"],
        }
    return out


def diff(from_commit: str, to_commit: str, repo: Optional[str] = None) -> dict:
    from_full = _resolve_commit(from_commit, repo)
    to_full = _resolve_commit(to_commit, repo)
    conn = corestore.open_db()
    codestore.ensure_schema(conn)

    before = _definition_set(conn, from_full, repo)
    after = _definition_set(conn, to_full, repo)

    deleted = []
    for key, row in before.items():
        if key not in after:
            deleted.append({**row, "event": DELETED_IN, "at_commit": to_full, "derivation": DERIVATION_EXACT_PARSE})
    introduced = []
    for key, row in after.items():
        if key not in before:
            introduced.append({**row, "event": INTRODUCED_IN, "at_commit": to_full,
                                "derivation": DERIVATION_EXACT_PARSE})

    deleted.sort(key=lambda r: (r["path"], r["start_line"]))
    introduced.sort(key=lambda r: (r["path"], r["start_line"]))
    return {"from": from_full, "to": to_full, "deleted": deleted, "introduced": introduced}


def deleted(from_commit: str, to_commit: str, repo: Optional[str] = None) -> dict:
    d = diff(from_commit, to_commit, repo=repo)
    return {"from": d["from"], "to": d["to"], "deleted": d["deleted"]}


def introduced(from_commit: str, to_commit: str, repo: Optional[str] = None) -> dict:
    d = diff(from_commit, to_commit, repo=repo)
    return {"from": d["from"], "to": d["to"], "introduced": d["introduced"]}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.code.history")
    sub = p.add_subparsers(dest="cmd", required=True)

    for name in ("deleted", "introduced", "diff"):
        sp = sub.add_parser(name)
        sp.add_argument("--from", dest="from_commit", required=True)
        sp.add_argument("--to", dest="to_commit", required=True)
        sp.add_argument("--json", action="store_true")

    args = p.parse_args(argv)
    try:
        if args.cmd == "deleted":
            result = deleted(args.from_commit, args.to_commit)
        elif args.cmd == "introduced":
            result = introduced(args.from_commit, args.to_commit)
        elif args.cmd == "diff":
            result = diff(args.from_commit, args.to_commit)
        else:
            return 2
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        return 1

    print(json.dumps(result, sort_keys=True) if args.json else json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
