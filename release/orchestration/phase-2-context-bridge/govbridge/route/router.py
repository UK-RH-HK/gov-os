#!/usr/bin/env python3
"""Deterministic route selection and reciprocal-rank fusion (ARCHITECTURE.md section 7.2 "Routing and fusion",
section 9 "Replaceable embedding/index/runtime interfaces").

Node B6 (BR-HO-0008) never imports ``govbridge.lexical``, ``.semantic`` or ``.code`` -- those are B2/B3/B4, not a
dependency of this node. Every retrieval route is consumed through the ``RouteFn`` contract below, supplied by the
caller as a ``RouteSet``; every test in ``tests/compile`` injects an in-test fake implementing that same contract.
I1 wires the real B2/B3/B4 modules behind adapters that produce ``RouteHit``s, without editing this file (the real
adapters translate ``govbridge.lexical.query.RetrievedItem`` / ``govbridge.semantic.search`` results / the code
route's rows into this shape once; nothing about routing or fusion changes).

Fusion is reciprocal-rank (``rrf_k`` from ``config/budgets.yaml``, itself citing ``MEMORY_POLICY.yaml`` -- the
frozen product's own policy file, read as evidence, never as a runtime dependency of this package) **inside each
(section, authority stratum)**, never across strata: a stratum is the ``(rank, lifecycle_index)`` pair the hard
authority invariant already uses to order a section (ARCHITECTURE.md section 5.3 rule 5). Fusing within a stratum
only ever reorders items that were already going to land in the same place; it can never let a highly-ranked
retrieval hit jump a stratum boundary. That is what makes the ordering invariant hold regardless of what any route
returns.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Callable, Iterable, Optional

from govbridge.authority import classes as classesmod

DEFAULT_RRF_K = 60


# ---------------------------------------------------------------------------------------------------------------
# The normalised item every route hands to the compiler. Never a MandatoryItem (ARCHITECTURE.md section 5.3 rule 1:
# "no conversion function exists" between RetrievedItem/DerivedItem and MandatoryItem) -- RouteHit is the union of
# what B2/B3/B4's RetrievedItem and B5's DerivedItem carry, normalised to one shape so the compiler has exactly one
# retrieved/derived item type to route into sections B-H.
# ---------------------------------------------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class RouteOccurrence:
    ref: str
    commit: str
    path: str
    version_status: str
    canonical_ref: Optional[str] = None
    canonical_commit: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class RouteHit:
    """``unit_id`` follows ARCHITECTURE.md section 2's identity table for ``unit_kind`` (a chunk id for
    ``"chunk"``, a record id for ``"record"``, a qualified name for ``"symbol"``, ...). ``delivery`` is always
    RETRIEVED (a route hit) or DERIVED (a graph hop); the compiler decides delivery/section placement from
    ``authority_class``/``lifecycle`` alone, never from ``route`` or ``rank`` (ARCHITECTURE.md section 5.3 rule 5:
    "no score can invert the order")."""
    unit_id: str
    unit_kind: str  # "chunk" | "record" | "symbol" | "occurrence" | "commit" | "finding"
    route: str  # "exact" | "lexical" | "semantic" | "graph" | "code"
    rank: int  # 1-based rank WITHIN this route's own result list for this one query
    delivery: str = "RETRIEVED"  # "RETRIEVED" | "DERIVED"
    occurrences: tuple = ()  # (RouteOccurrence, ...)
    text: Optional[str] = None
    authority_class: Optional[str] = None
    lifecycle: Optional[str] = None
    edge_path: tuple = ()  # (dict, ...): graph hop labels, when route == "graph"

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["occurrences"] = [o.to_dict() if isinstance(o, RouteOccurrence) else o for o in self.occurrences]
        return d


RouteFn = Callable[..., list]  # (text=None, seeds=None, k=8, exclude=None) -> list[RouteHit]


def empty_route(**_kwargs) -> list:
    """The default for every unwired route slot: an honest, empty MISSING (the same discipline
    ``govbridge.graph.derive`` uses for ``conn=None``), never an error."""
    return []


@dataclasses.dataclass
class RouteSet:
    """The route callables the compiler was given (ARCHITECTURE.md section 9). An absent slot behaves exactly like
    ``empty_route``. ``FAKE_ROUTES`` (module level, below) is the all-empty set ``--fake-routes`` uses; a test
    supplies its own fakes that return specific ``RouteHit`` lists."""
    exact: RouteFn = empty_route
    lexical: RouteFn = empty_route
    semantic: RouteFn = empty_route
    code: RouteFn = empty_route

    def run(self, name: str, **kwargs) -> list:
        fn = getattr(self, name, None) or empty_route
        return list(fn(**kwargs) or [])


FAKE_ROUTES = RouteSet()


# ---------------------------------------------------------------------------------------------------------------
# Deterministic route selection (ARCHITECTURE.md section 7.2): "the exact route runs when a query contains an ID,
# path or symbol token; the code route runs for symbol-like tokens; the lexical route always runs; the semantic
# route runs for natural-language queries of at least four words; graph expansion runs from resolved seeds."
# ---------------------------------------------------------------------------------------------------------------

_PATH_TOKEN_RE = re.compile(r"[\w.\-/]*/[\w.\-]+\.[A-Za-z0-9_]{1,10}(?::\d+(?:-\d+)?)?")
_COMMIT_TOKEN_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
_SYMBOL_TOKEN_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)+\b|\b[a-z_][a-z0-9_]{2,}\(\)")


def _contains_id_token(text: str, grammar) -> bool:
    if grammar is None:
        return False
    return any(mp["regex"].search(text) for mp in grammar.mention_patterns)


def select_routes(query: dict, grammar=None) -> tuple:
    """Which route NAMES should run for one ``queries[]`` entry (``schemas/task-spec.yaml``:
    ``{id, text, routes?, target_section?}``). An explicit ``routes`` list on the query always wins verbatim
    (bounded to the known route names); otherwise selection is generic over the query TEXT's shape, never over its
    content (OC-BR-02: nothing here names a particular id, file or phase)."""
    explicit = query.get("routes")
    if explicit:
        return tuple(r for r in explicit if r in ("exact", "lexical", "semantic", "code", "graph"))

    text = query.get("text") or ""
    routes = ["lexical"]  # "the lexical route always runs"
    if _contains_id_token(text, grammar) or _PATH_TOKEN_RE.search(text) or _COMMIT_TOKEN_RE.search(text):
        routes.append("exact")
    if _SYMBOL_TOKEN_RE.search(text):
        routes.append("code")
    if len(text.split()) >= 4:
        routes.append("semantic")
    return tuple(routes)


# ---------------------------------------------------------------------------------------------------------------
# Reciprocal-rank fusion, strictly WITHIN one (section, authority stratum) group -- never across (ARCHITECTURE.md
# section 7.2). The caller (govbridge.compile.packet) is responsible for grouping hits by their eventual section
# and stratum before calling ``fuse``; this function only combines ranks for hits that are ALREADY known to share
# one group.
# ---------------------------------------------------------------------------------------------------------------

def stratum_key(cls: Optional[str], lifecycle: Optional[str]) -> tuple:
    """``(authority rank, lifecycle order index)`` -- the same two components ARCHITECTURE.md section 5.3 rule 5
    orders a section by. Fusion never crosses a boundary in this key."""
    spec = classesmod.ALL_CLASSES.get(cls) if cls else None
    rank = spec.rank if (spec is not None and spec.ladder) else len(classesmod.LADDER) + 1
    try:
        lc_idx = classesmod.LIFECYCLE_ORDER.index(lifecycle)
    except ValueError:
        lc_idx = len(classesmod.LIFECYCLE_ORDER) - 1
    return rank, lc_idx


def dedupe_key(hit: RouteHit) -> tuple:
    """(blob, overlapping line range) and record id are the two dedup axes ARCHITECTURE.md section 7.2 names. A
    chunk-kind hit dedupes by its first occurrence's (blob, start, end); anything else dedupes by its own unit id
    (a record/symbol/commit/finding id is already the whole-unit identity)."""
    if hit.unit_kind == "chunk" and hit.occurrences:
        o = hit.occurrences[0]
        return ("blob", o.path, o.line_start, o.line_end)
    return ("unit", hit.unit_kind, hit.unit_id)


def _occurrence_rank(occ: RouteOccurrence) -> int:
    order = (
        "CANONICAL", "SAME_AS_CANONICAL", "CANONICAL_FALLBACK", "HISTORICAL_VERSION", "HISTORY_ONLY", "ABSENT",
    )
    try:
        return order.index(occ.version_status)
    except ValueError:
        return len(order)


def _prefer(a: RouteHit, b: RouteHit) -> RouteHit:
    """Which of two hits deduped to the same key wins as the representative: the one with the more canonical
    occurrence wins (ARCHITECTURE.md section 7.2: "the canonical version wins over SAME_AS_CANONICAL copies")."""
    a_rank = _occurrence_rank(a.occurrences[0]) if a.occurrences else 99
    b_rank = _occurrence_rank(b.occurrences[0]) if b.occurrences else 99
    return a if a_rank <= b_rank else b


def dedupe(hits: Iterable[RouteHit]) -> list:
    """Collapse duplicate hits, keeping the most-canonical representative in FIRST-SEEN order."""
    order: list = []
    best: dict = {}
    for h in hits:
        key = dedupe_key(h)
        if key not in best:
            order.append(key)
            best[key] = h
        else:
            best[key] = _prefer(best[key], h)
    return [best[k] for k in order]


@dataclasses.dataclass(frozen=True)
class FusedHit:
    hit: RouteHit
    fused_score: float
    routes: tuple  # every route name that contributed to this fused score


def fuse(hits_by_route: dict, rrf_k: int = DEFAULT_RRF_K) -> list:
    """``hits_by_route``: ``{route_name: [RouteHit, ...]}``, each list already ranked 1..N by that route. Returns
    ``[FusedHit]`` sorted by descending fused score (ties broken by unit id, for full determinism), deduped and
    with score computed purely from RANK (never from a route's raw score, whose direction/scale differs by route --
    RRF's reciprocal-rank is the one comparison that is always "higher is better", ARCHITECTURE.md section 7.2)."""
    contrib: dict = {}  # dedupe_key -> {"hit": RouteHit, "score": float, "routes": set}
    for route_name, hit_list in hits_by_route.items():
        for hit in hit_list:
            key = dedupe_key(hit)
            entry = contrib.setdefault(key, {"hit": hit, "score": 0.0, "routes": set()})
            entry["hit"] = _prefer(entry["hit"], hit)
            entry["score"] += 1.0 / (rrf_k + hit.rank)
            entry["routes"].add(route_name)

    fused = [FusedHit(hit=e["hit"], fused_score=e["score"], routes=tuple(sorted(e["routes"])))
             for e in contrib.values()]
    fused.sort(key=lambda f: (-f.fused_score, f.hit.unit_id))
    return fused


def main(argv=None) -> int:  # pragma: no cover -- no standalone CLI use case; kept for module-run consistency
    import argparse
    p = argparse.ArgumentParser(prog="govbridge.route.router")
    p.parse_args(argv)
    print("govbridge.route.router: a library module, used by govbridge.compile.packet")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
