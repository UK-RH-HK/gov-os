#!/usr/bin/env python3
"""The lexical route's read path: ``govbridge.lexical.query`` (ARCHITECTURE.md section 4.3, node B2's second
deliverable). Turns an FTS5 ``MATCH`` into ``RetrievedItem``s: the chunk id as unit id (ARCHITECTURE.md section 2
identity table), occurrence(s) from B1's ``occurrence`` table (one row per ``(ref, commit, path)`` the hit's blob
is known at), and each occurrence's version status from ``govbridge.core.view`` -- never re-implemented here.

**Authority class and lifecycle** (ARCHITECTURE.md section 5) are assigned by ``govbridge.authority`` (node B5,
not a dependency of B2: B2 depends only on B1). Every ``RetrievedItem`` below carries ``authority_class=None``,
``lifecycle=None`` and says so explicitly, rather than guessing or leaving the omission silent -- the same
discipline ``govbridge.core.exact.id_lookup`` uses ahead of the id-grammar landing (node B5): "not yet available",
never a fabricated default. ARCHITECTURE.md section 4 is explicit that no route may itself assign a class: "All
routes read the same store. All return RetrievedItems carrying the unit id, occurrence(s), version status, the
authority class and lifecycle already assigned by section 5" -- i.e. assigned upstream of the route, by the
resolver/classifier, not fabricated by it.

**retrieval_exclusions** (``schemas/task-spec.yaml``, ARCHITECTURE.md section 7.2: "applied to every route, the
resolver excepted") are glob patterns matched against occurrence paths. An occurrence matching any given glob is
dropped from that hit's occurrence list; a hit left with zero surviving occurrences is dropped entirely, never
shown with an empty occurrence list.

**Latency.** ARCHITECTURE.md section 4.3 cites SO-15/SO-16's 5-6 ms/query figure, measured on the raw FTS5
``MATCH`` plus the occurrence join (``fts_spike.py``) -- not on Git-backed version-status classification, which
the spike never performed. ``latency_ms`` below measures the same thing the architecture measured (the SQL search
path), so it is comparable to the cited figure and to the "< 100 ms" acceptance target; version-status
classification (subprocess-backed, via ``govbridge.core.view``) runs afterwards and is not counted in it.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
from typing import Optional

from govbridge.core import pathrules, store, telemetry, view as viewmod
from govbridge.core.yamlutil import canonical_json, sha256_text
from govbridge.lexical import fts as ftsmod  # noqa: F401  (package import registers this layer, see __init__.py)

#: MEMORY_POLICY.yaml:20 retrieval.default_k
DEFAULT_K = 8
#: how many candidate rows to pull from FTS5 before exclusion-filtering trims to k; generous enough that excluding
#: a handful of occurrences rarely starves the caller of k results, without scanning the whole table.
_OVERFETCH_FLOOR = 50
_OVERFETCH_MULTIPLIER = 5

NOT_YET_ASSIGNED = "NOT_YET_ASSIGNED: authority class/lifecycle are assigned by govbridge.authority (node B5, not a B2 dependency)"


@dataclasses.dataclass(frozen=True)
class Occurrence:
    ref: str
    commit: str
    path: str
    version_status: str
    canonical_ref: Optional[str]
    canonical_commit: Optional[str]

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class RetrievedItem:
    """ARCHITECTURE.md section 2 "Packet item" / section 4 RetrievedItem shape, as far as a route alone can fill
    it in: unit id, route, raw score, rank, occurrence(s) with version status. ``authority_class``/``lifecycle``
    are filled in downstream (node B5's resolver, consumed by node B6's compiler) -- see module docstring."""
    item_id: str  # the chunk_id (ARCHITECTURE.md section 2: sha256(blob||chunker_version||start||end)[:24])
    route: str
    raw_score: float
    rank: int
    blob_id: str
    start_line: int
    end_line: int
    text: str
    occurrences: list  # list[Occurrence]
    delivery: str = "RETRIEVED"
    authority_class: Optional[str] = None
    lifecycle: Optional[str] = None
    classification_note: str = NOT_YET_ASSIGNED

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["occurrences"] = [o.to_dict() if isinstance(o, Occurrence) else o for o in self.occurrences]
        return d


def _default_paths(repo: Optional[str] = None) -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    return os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")


def _occurrences_for_blob(conn, blob_id: str, resolved: "viewmod.ResolvedView") -> list[Occurrence]:
    rows = conn.execute(
        "SELECT ref_name, commit_id, path FROM occurrence WHERE blob_id=? ORDER BY ref_name, commit_id, path",
        (blob_id,),
    ).fetchall()
    out = []
    for ref_name, commit_id, path in rows:
        cls = resolved.classify_occurrence(path, commit_id, queried_blob=blob_id)
        out.append(Occurrence(ref=ref_name, commit=commit_id, path=path, version_status=cls.status,
                               canonical_ref=cls.canonical_ref, canonical_commit=cls.canonical_commit))
    return out


def query(text: str, k: int = DEFAULT_K, exclude: Optional[list[str]] = None, view_path: Optional[str] = None,
          repo: Optional[str] = None, record_telemetry: bool = True) -> dict:
    """Run ``text`` (an FTS5 MATCH expression -- a phrase, NEAR(), a bareword query, ...) against the lexical
    index and return up to ``k`` RetrievedItems, ranked by BM25 (ascending: SQLite's bm25() is a cost, lower is
    better -- ORDER BY score ASC is the correct direction, matching fts_spike.py). ``exclude`` is a list of globs
    (retrieval_exclusions): an occurrence whose path matches any of them is dropped; a hit left with no surviving
    occurrence is dropped entirely.
    """
    view_path = view_path or _default_paths(repo)
    conn = store.open_db()
    ftsmod.ensure_schema(conn)

    fetch_n = max(k * _OVERFETCH_MULTIPLIER, _OVERFETCH_FLOOR) if exclude else k
    t0 = time.monotonic()
    rows = conn.execute(
        "SELECT chunk_id, blob_id, start_line, end_line, text, bm25(lexical_fts) AS score "
        "FROM lexical_fts WHERE lexical_fts MATCH ? ORDER BY score ASC LIMIT ?",
        (text, fetch_n),
    ).fetchall()
    total_matches = conn.execute(
        "SELECT count(*) FROM lexical_fts WHERE lexical_fts MATCH ?", (text,)
    ).fetchone()[0]
    latency_ms = round((time.monotonic() - t0) * 1000, 3)

    resolved = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)

    hits: list[RetrievedItem] = []
    for chunk_id, blob_id, start_line, end_line, chunk_text, score in rows:
        occs = _occurrences_for_blob(conn, blob_id, resolved)
        if exclude:
            occs = [o for o in occs if pathrules.any_glob_match(o.path, exclude) is None]
            if not occs:
                continue
        hits.append(RetrievedItem(item_id=chunk_id, route="lexical", raw_score=score, rank=len(hits) + 1,
                                   blob_id=blob_id, start_line=start_line, end_line=end_line, text=chunk_text,
                                   occurrences=occs))
        if len(hits) >= k:
            break

    result = {
        "query": text, "k": k, "exclude": list(exclude) if exclude else [], "route": "lexical",
        "total_matching_chunks": total_matches, "latency_ms": latency_ms,
        "hits": [h.to_dict() for h in hits],
    }
    if record_telemetry:
        try:
            telemetry.write_row("queries", {
                "route": "lexical", "query_sha256": sha256_text(canonical_json({"q": text, "exclude": result["exclude"]})),
                "k": k, "hits": len(hits), "total_matching_chunks": total_matches, "latency_ms": latency_ms,
            })
        except Exception:
            pass  # telemetry is best-effort; a write failure must never fail a query
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.lexical.query")
    p.add_argument("text", help="an FTS5 MATCH expression, e.g. a quoted phrase")
    p.add_argument("--k", type=int, default=DEFAULT_K)
    p.add_argument("--exclude", action="append", default=None, metavar="GLOB",
                    help="retrieval_exclusions glob; repeatable")
    p.add_argument("--view")
    p.add_argument("--json", action="store_true", help="print the full JSON result (default: a short summary)")
    args = p.parse_args(argv)

    result = query(args.text, k=args.k, exclude=args.exclude, view_path=args.view)
    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        print(f"query={result['query']!r} k={result['k']} exclude={result['exclude']} "
              f"total_matching_chunks={result['total_matching_chunks']} latency_ms={result['latency_ms']}")
        for h in result["hits"]:
            occ = "; ".join(f"{o['ref']}@{o['commit'][:10]}:{o['path']}:{h['start_line']}-{h['end_line']}"
                             f"[{o['version_status']}]" for o in h["occurrences"])
            print(f"  #{h['rank']} score={h['raw_score']:.3f} chunk={h['item_id']} {occ}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
