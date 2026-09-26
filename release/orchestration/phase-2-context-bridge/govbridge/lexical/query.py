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
from typing import Callable, Optional

from govbridge.core import pathrules, store, telemetry, view as viewmod
from govbridge.core.yamlutil import canonical_json, sha256_text
from govbridge.lexical import fts as ftsmod  # noqa: F401  (package import registers this layer, see __init__.py)

def _load_default_k() -> int:
    """OD-BR-05 section 9 ("do not hard-code 8k as the architecture limit... a configurable per-retrieval batch
    size only") / REPAIR_DAG.yaml node R1-GA1 ("batch_size from configuration (no hard-coded 8)"). The single
    configuration-default loader is ``govbridge.gather.facets.default_batch_size`` (``config/facets.yaml``'s own
    ``default_batch_size``); imported lazily, never at this module's own import time, so this leaf module (B2, no
    dependency on the gather package) never takes a hard import-time dependency on it, and a caller that uses this
    module stand-alone (before R1-GA1's config file exists, or with it missing/unreadable) still gets the exact
    value the architecture always used -- a pure source-of-truth move, never a behaviour change by default."""
    try:
        from govbridge.gather.facets import default_batch_size
        return default_batch_size()
    except Exception:
        return 8


#: MEMORY_POLICY.yaml:20 retrieval.default_k -- resolved through the ONE configuration-default loader above.
DEFAULT_K = _load_default_k()
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


_scope_indexes_ensured = False

#: this node's OWN small derived-cache table, added to the shared store.db exactly the way every other layer
#: (lexical_fts, vector, record_def/class_lifecycle) already adds its own tables to the SAME file -- never a change
#: to a table another node owns.
SCOPE_PATH_CACHE_TABLE = "gather_scope_path_cache"


def _ensure_scope_indexes(conn) -> None:
    """Two query-time-only preparations, attempted at most once per process (module-level flag) and never allowed
    to fail the caller (wrapped in try/except; the caller's own try/except around the scoped query itself is a
    second safety net regardless):

    1. An index on ``record_def(path)`` (``govbridge.authority.layer``, out of this node's mutation scope, is
       indexed by ``id`` only) -- Tier A's ``JOIN record_def rd ON rd.path = rdo.path`` in :func:`_scope_sql` would
       otherwise be a full scan of every record for every candidate row. A pure, idempotent (``IF NOT EXISTS``)
       addition to an EXISTING table's EXISTING column -- no schema owned by this node, no data changed.
    2. ``gather_scope_path_cache(blob_id, path)`` -- a DEDUPLICATED copy of ``occurrence(blob_id, path)``. The real
       ``occurrence`` table is keyed by ``(ref_name, commit_id, path)``: on this corpus it holds ~500k rows for only
       ~8k distinct ``(blob_id, path)`` pairs (many refs/historical commits repeating the SAME path for the SAME
       blob). Tier B's ``EXISTS (... WHERE occ.blob_id = ? AND path GLOB ...)`` against the raw table means SQLite
       must walk every one of a popular blob's (sometimes 500+) occurrence rows before it can conclude "no match" --
       REPAIR_DAG.yaml node R1-GA1 reopening: this was the ACTUAL cost behind the corpus-scale timeout the SQL
       push-down first hit (measured directly: ~4-6s per scoped COUNT/SELECT on this store, before this cache).
       Querying the deduplicated cache instead cuts that to a handful of rows per blob. Rebuilt fresh once per
       process (an ``INSERT OR IGNORE`` is a cheap no-op for rows already present), so it can never go stale within
       one gather() session and is never more than one process-start stale across sessions -- a performance cache
       only; a stale/missing cache degrades to the SAME safe fallback path (this whole function is best-effort)."""
    global _scope_indexes_ensured
    if _scope_indexes_ensured:
        return
    try:
        conn.execute("CREATE INDEX IF NOT EXISTS record_def_by_path ON record_def(path)")
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {SCOPE_PATH_CACHE_TABLE} (blob_id TEXT NOT NULL, path TEXT NOT NULL, "
            f"PRIMARY KEY (blob_id, path))"
        )
        conn.execute(
            f"INSERT OR IGNORE INTO {SCOPE_PATH_CACHE_TABLE} (blob_id, path) "
            f"SELECT DISTINCT blob_id, path FROM occurrence"
        )
        conn.commit()
    except Exception:
        pass
    _scope_indexes_ensured = True


def _scope_sql(blob_col: str, start_col: str, end_col: str, scope_classes: Optional[tuple],
               lifecycle_scope: Optional[tuple], scope_path_globs: Optional[tuple]) -> tuple:
    """A SQL fragment (``''`` or ``' AND (...)'``) plus its bound params, restricting rows to a facet's declared
    authority-class/lifecycle scope -- PUSHED DOWN into SQL so a scoped facet's page is already in scope, rather
    than filtered client-side after the fact (REPAIR_DAG.yaml node R1-GA1 reopening: a scoped facet must not page
    through corpus-wide rankings, advancing its cursor without advancing its count). Reuses the SAME tables
    ``govbridge.authority`` already persists (``record_def``/``class_lifecycle``, the B5 cache layer built by
    ``govbridge.authority.layer``) and the store's own ``occurrence`` table -- no new schema, and no Python
    ``import`` of ``govbridge.authority`` (this module stays a B1-only dependency; the caller,
    ``govbridge.route.real_routes``, is the one place that already knows about authority classes and translates
    them into these plain, generic SQL-facing parameters -- a class or lifecycle name is never spelled out here).

    Two tiers, OR'd together:

    * **Tier A** -- a RECORD-BACKED span: the occurrence's ``(path, line)`` falls inside a ``record_def`` row whose
      ``class_lifecycle`` cache entry matches ``scope_classes`` AND ``lifecycle_scope``. Precise on both axes.
    * **Tier B** -- a bare PATH GLOB (translated by the caller from the registry's own ``class_rules``, in the SAME
      glob syntax SQLite's ``GLOB`` operator uses) matches an occurrence's path. Class-only: no lifecycle signal
      exists for content outside a record, so Tier B is skipped whenever ``lifecycle_scope`` is given (never a
      wrong-lifecycle false positive let through by the path alone).

    This is a PRE-FILTER, not the final word: the caller still runs the real classifier on every survivor and may
    still drop one it disagrees with -- kept as an assertion, disclosed in telemetry, never the primary mechanism."""
    if not scope_classes and not scope_path_globs:
        return "", []
    clauses: list = []
    params: list = []
    if scope_classes:
        cls_placeholders = ",".join("?" for _ in scope_classes)
        # gather_scope_path_cache (see _ensure_scope_indexes), never the raw occurrence table -- same rationale as
        # Tier B: joining record_def straight off occurrence would re-walk every historical (ref, commit) repeat of
        # a popular blob's path before ever reaching record_def's own small table.
        tier_a = (
            f"EXISTS (SELECT 1 FROM {SCOPE_PATH_CACHE_TABLE} rdo "
            f"JOIN record_def rd ON rd.path = rdo.path AND rd.line_start <= {end_col} AND rd.line_end >= {start_col} "
            f"JOIN class_lifecycle cl ON cl.unit = rd.id "
            f"WHERE rdo.blob_id = {blob_col} AND cl.cls IN ({cls_placeholders})"
        )
        params.extend(scope_classes)
        if lifecycle_scope:
            lc_placeholders = ",".join("?" for _ in lifecycle_scope)
            tier_a += f" AND cl.lifecycle IN ({lc_placeholders})"
            params.extend(lifecycle_scope)
        tier_a += ")"
        clauses.append(tier_a)
    if scope_path_globs and not lifecycle_scope:
        glob_or = " OR ".join("occ2.path GLOB ?" for _ in scope_path_globs)
        # gather_scope_path_cache (see _ensure_scope_indexes), never the raw occurrence table: the SAME blob/path
        # pair repeats once per historical (ref, commit) on occurrence (hundreds of times for a popular blob), so
        # matching against the deduplicated cache is the difference between a handful of row checks and hundreds.
        clauses.append(f"EXISTS (SELECT 1 FROM {SCOPE_PATH_CACHE_TABLE} occ2 WHERE occ2.blob_id = {blob_col} "
                        f"AND ({glob_or}))")
        params.extend(scope_path_globs)
    if not clauses:
        return "", []
    return " AND (" + " OR ".join(clauses) + ")", params


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


def query(text: str, k: int = DEFAULT_K, exclude: Optional[list[str]] = None, offset: int = 0,
          view_path: Optional[str] = None, repo: Optional[str] = None, record_telemetry: bool = True,
          classify: Optional["Callable[[RetrievedItem], tuple]"] = None,
          scope_classes: Optional[tuple] = None, lifecycle_scope: Optional[tuple] = None,
          scope_path_globs: Optional[tuple] = None) -> dict:
    """Run ``text`` (an FTS5 MATCH expression -- a phrase, NEAR(), a bareword query, ...) against the lexical
    index and return up to ``k`` RetrievedItems, ranked by BM25 (ascending: SQLite's bm25() is a cost, lower is
    better -- ORDER BY score ASC is the correct direction, matching fts_spike.py), with ``chunk_id`` ASC as a
    second, fully deterministic tiebreaker (two rows can legitimately tie on score; SQL's own tie order is not
    otherwise guaranteed stable). ``exclude`` is a list of globs (retrieval_exclusions): an occurrence whose path
    matches any of them is dropped; a hit left with no surviving occurrence is dropped entirely.

    ``offset`` (REPAIR_PLAN.md section 2.4, "every route accepts a cursor... lexical and semantic take an offset"):
    a caller (``govbridge.gather.engine``) pages by re-issuing the SAME query with an advancing ``offset``. The
    result's ``next_offset`` is the offset to resume at, or ``None`` once every FTS5-matching row (not just every
    KEPT, post-exclusion hit) has been consumed -- following it to exhaustion yields exactly the same union an
    unpaged, unbounded call would.

    ``classify``, an optional hook, ``RetrievedItem -> (authority_class, lifecycle)`` -- the SAME extension point
    ``govbridge.semantic.search`` already has (its ``Classifier`` callable), added here for symmetry so a caller
    (I1's real-route wiring, once ``govbridge.authority`` is on this branch's base -- B2 depends only on B1) can
    supply the real classifier without editing this file. Absent (the default), every hit still carries the
    original placeholder (``authority_class=None``, ``classification_note=NOT_YET_ASSIGNED``) -- unchanged.

    ``scope_classes``/``lifecycle_scope``/``scope_path_globs`` (REPAIR_DAG.yaml node R1-GA1 reopening): pushed
    down into the SQL itself (:func:`_scope_sql`) rather than filtered after the fact, so a SCOPED facet's page is
    already in scope -- ``total_matching_chunks``/exhaustion accounting is computed over the SAME scoped universe,
    never the unscoped one, so paging still terminates correctly."""
    view_path = view_path or _default_paths(repo)
    conn = store.open_db()
    ftsmod.ensure_schema(conn)

    scope_sql, scope_params = _scope_sql("lexical_fts.blob_id", "lexical_fts.start_line", "lexical_fts.end_line",
                                          scope_classes, lifecycle_scope, scope_path_globs)
    if scope_sql:
        _ensure_scope_indexes(conn)

    fetch_n = max(k * _OVERFETCH_MULTIPLIER, _OVERFETCH_FLOOR) if exclude else k
    t0 = time.monotonic()
    try:
        rows = conn.execute(
            "SELECT chunk_id, blob_id, start_line, end_line, text, bm25(lexical_fts) AS score "
            "FROM lexical_fts WHERE lexical_fts MATCH ?" + scope_sql +
            " ORDER BY score ASC, chunk_id ASC LIMIT ? OFFSET ?",
            (text, *scope_params, fetch_n, offset),
        ).fetchall()
        total_matches = conn.execute(
            "SELECT count(*) FROM lexical_fts WHERE lexical_fts MATCH ?" + scope_sql,
            (text, *scope_params),
        ).fetchone()[0]
    except Exception:
        # record_def/class_lifecycle may not exist yet on a store that never built the authority layer (a bare B1+
        # lexical store, or a test fixture); an honest, generic fall-back to the UNSCOPED query is a strict SUPERSET
        # (never drops evidence a caller could otherwise have seen), and the real classifier's own post-filter
        # (real_routes.py) still applies -- never a crash, never a silent narrower-than-intended result.
        rows = conn.execute(
            "SELECT chunk_id, blob_id, start_line, end_line, text, bm25(lexical_fts) AS score "
            "FROM lexical_fts WHERE lexical_fts MATCH ? ORDER BY score ASC, chunk_id ASC LIMIT ? OFFSET ?",
            (text, fetch_n, offset),
        ).fetchall()
        total_matches = conn.execute(
            "SELECT count(*) FROM lexical_fts WHERE lexical_fts MATCH ?", (text,)
        ).fetchone()[0]
    latency_ms = round((time.monotonic() - t0) * 1000, 3)

    resolved = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)

    hits: list[RetrievedItem] = []
    consumed = 0
    for chunk_id, blob_id, start_line, end_line, chunk_text, score in rows:
        consumed += 1
        occs = _occurrences_for_blob(conn, blob_id, resolved)
        if exclude:
            occs = [o for o in occs if pathrules.any_glob_match(o.path, exclude) is None]
            if not occs:
                continue
        item = RetrievedItem(item_id=chunk_id, route="lexical", raw_score=score, rank=len(hits) + 1,
                              blob_id=blob_id, start_line=start_line, end_line=end_line, text=chunk_text,
                              occurrences=occs)
        if classify is not None:
            try:
                cls, lifecycle = classify(item)
                item = dataclasses.replace(item, authority_class=cls, lifecycle=lifecycle,
                                            classification_note="classified by govbridge.authority")
            except Exception:
                pass  # a classifier failure must never fail the route; the placeholder stands
        hits.append(item)
        if len(hits) >= k:
            break

    # REPAIR_PLAN.md section 2.4: exhausted once the raw (pre-exclusion) SQL page itself came up short of what we
    # asked for; otherwise resume right after the last raw row this call actually looked at (never after only the
    # KEPT hits, or a caller would silently skip excluded candidates on the next page).
    exhausted = (offset + len(rows)) >= total_matches
    next_offset = None if exhausted else offset + consumed

    result = {
        "query": text, "k": k, "exclude": list(exclude) if exclude else [], "route": "lexical",
        "offset": offset, "next_offset": next_offset,
        "total_matching_chunks": total_matches, "latency_ms": latency_ms,
        "hits": [h.to_dict() for h in hits],
    }
    if record_telemetry:
        try:
            telemetry.write_row("queries", {
                "route": "lexical", "query_sha256": sha256_text(canonical_json({"q": text, "exclude": result["exclude"]})),
                "k": k, "offset": offset, "hits": len(hits), "total_matching_chunks": total_matches,
                "latency_ms": latency_ms,
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
    p.add_argument("--offset", type=int, default=0, help="resume paging at this offset (REPAIR_PLAN.md section 2.4)")
    p.add_argument("--view")
    p.add_argument("--json", action="store_true", help="print the full JSON result (default: a short summary)")
    args = p.parse_args(argv)

    result = query(args.text, k=args.k, exclude=args.exclude, offset=args.offset, view_path=args.view)
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
