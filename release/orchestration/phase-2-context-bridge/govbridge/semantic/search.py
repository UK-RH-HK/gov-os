"""The semantic route's query CLI/API (ARCHITECTURE.md section 4.5, node B4 acceptance check 4):
``python -m govbridge.semantic.search '<query>' --json``.

Every route "returns RetrievedItems carrying the unit id, occurrence(s), version status, the authority class and
lifecycle already assigned by section 5" (ARCHITECTURE.md section 4) -- but that assignment is
``govbridge.authority``'s job (node B5), which is not in this node's ``depends_on`` and is not merged into this
branch's base. Rather than guess at a classifier, this module assigns the two placeholder values section 5.1
already defines for exactly this situation -- ``UNCLASSIFIED`` / ``UNKNOWN`` ("Otherwise the unit is
UNCLASSIFIED/UNKNOWN", section 5.2 rule 5) -- through a ``classify`` hook that a caller may override once real
classification exists, without editing this file. Because the semantic route can only ever land items in sections
B-H with delivery RETRIEVED (never A/D.1, SEMANTIC_ROUTE.md section 1; ARCHITECTURE.md section 5.3), an
UNCLASSIFIED/UNKNOWN item here can never be mistaken for authority. ``version_status`` needs no such placeholder:
it is computed from the real, already-built canonical view (``govbridge.core.view``), exactly as the exact route
does (``govbridge/core/exact.py``).
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Callable, Optional

from govbridge.core import store, view as viewmod
from govbridge.semantic import modelpin, runner, vectors

Classifier = Callable[[str], tuple]  # blob_id -> (authority_class, lifecycle)


def default_classify(_blob_id: str) -> tuple:
    return "UNCLASSIFIED", "UNKNOWN"


def _default_paths(repo: Optional[str] = None) -> tuple:
    from govbridge import GOV_BRIDGE_DOMAIN
    return (str(Path(GOV_BRIDGE_DOMAIN) / "config" / "canonical-view.yaml"),)


def _representative_occurrence(conn: sqlite3.Connection, blob_id: str, resolved: viewmod.ResolvedView):
    rows = conn.execute(
        "SELECT ref_name, commit_id, path FROM occurrence WHERE blob_id=? ORDER BY ref_name, path", (blob_id,)
    ).fetchall()
    if not rows:
        return None
    primary_names = {r.name for r in resolved.config.refs if r.role == "primary"}
    for ref_name, commit_id, path in rows:
        if ref_name in primary_names:
            return ref_name, commit_id, path
    return rows[0]


def search(query: str, k: int = 10, store_root: Optional[Path] = None, view_path: Optional[str] = None,
           repo: Optional[str] = None, threads: int = 4, classify: Classifier = default_classify,
           offset: int = 0, scope_classes: Optional[tuple] = None, lifecycle_scope: Optional[tuple] = None,
           scope_path_globs: Optional[tuple] = None) -> dict:
    """``offset`` (REPAIR_PLAN.md section 2.4, "lexical and semantic take an offset"): pages through
    ``vectors.search``'s own deterministic, tie-broken ranking. One extra candidate is always requested beyond
    ``k`` (never returned) purely to learn whether a further page exists, without needing a second, separate
    "how many vectors are there" query -- ``next_offset`` is ``offset + k`` when that extra candidate showed up,
    else ``None`` (this page reached the end of the ranking).

    ``scope_classes``/``lifecycle_scope``/``scope_path_globs`` (REPAIR_DAG.yaml node R1-GA1 reopening): threaded
    straight through to ``vectors.search``, which restricts the candidate set BEFORE the top-k ranking runs --
    "restrict the candidate set by class before top-k", never a client-side filter after the fact."""
    root = store_root or store.store_root()
    # REPAIR_DAG.yaml node R1-GA1 (second reopening, coordinator addendum): this is a QUERY path (the one
    # gather's semantic facets actually call through govbridge.route.real_routes.semantic_route), so it opens the
    # store via store.open_db_readonly() -- a connection that cannot write, by construction -- rather than
    # store.open_db()'s read-write connection. ``vectors.create_table`` (a build-time CREATE TABLE/INDEX IF NOT
    # EXISTS) is dropped from this call site to match: the ``vector`` table already exists on any store this route
    # can usefully run against (the semantic layer builder creates it), so calling it here was always redundant
    # with the real build step -- and on a store that genuinely lacks it, the search below now fails with a plain,
    # clear "no such table: vector" rather than this query path quietly creating its own empty table to search.
    conn = store.open_db_readonly(root=root)

    pin = modelpin.load_model_pin(modelpin.default_pin_path())
    pin_id = modelpin.compute_pin_id(pin)
    outputs = runner.embed([query], mode="query", dimensions=pin.dimensions, pin_id=pin_id,
                            extra_args=["--threads", str(threads)])
    qvec = outputs["vectors"][0]

    overfetched = vectors.search(conn, qvec, k + 1, pin_id, offset=offset, scope_classes=scope_classes,
                                  lifecycle_scope=lifecycle_scope, scope_path_globs=scope_path_globs)
    has_more = len(overfetched) > k
    hits = overfetched[:k]

    (default_view,) = _default_paths(repo)
    view_path = view_path or default_view
    resolved = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)

    results = []
    for rank, (chunk_id, score) in enumerate(hits, start=1):
        crow = conn.execute(
            "SELECT blob_id, start_line, end_line FROM chunk WHERE chunk_id=?", (chunk_id,)
        ).fetchone()
        if crow is None:
            continue
        blob_id, start_line, end_line = crow
        occ = _representative_occurrence(conn, blob_id, resolved)
        item = {
            "id": chunk_id,
            "route": "semantic",
            "rank": rank,
            "score": score,
            "delivery": "RETRIEVED",
        }
        if occ is not None:
            ref_name, commit_id, path = occ
            item["occurrence"] = {"ref": ref_name, "commit": commit_id, "path": path,
                                   "line_start": start_line, "line_end": end_line}
            classification = resolved.classify_occurrence(path, commit_id, queried_blob=blob_id)
            item["version_status"] = classification.status
            item["canonical_ref"] = classification.canonical_ref
            item["canonical_commit"] = classification.canonical_commit
        else:
            item["occurrence"] = None
            item["version_status"] = "ABSENT"
            item["canonical_ref"] = None
            item["canonical_commit"] = None
        authority_class, lifecycle = classify(blob_id)
        item["authority_class"] = authority_class
        item["lifecycle"] = lifecycle
        results.append(item)

    next_offset = (offset + k) if has_more else None
    return {"query": query, "k": k, "offset": offset, "next_offset": next_offset, "pin_id": pin_id,
            "route": "semantic", "results": results}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.semantic.search")
    p.add_argument("query")
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--json", action="store_true")
    p.add_argument("--store")
    p.add_argument("--view")
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--offset", type=int, default=0, help="resume paging at this offset (REPAIR_PLAN.md section 2.4)")
    args = p.parse_args(argv)

    result = search(args.query, k=args.k, store_root=Path(args.store) if args.store else None,
                     view_path=args.view, threads=args.threads, offset=args.offset)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
