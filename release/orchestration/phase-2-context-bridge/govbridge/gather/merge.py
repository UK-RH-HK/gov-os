#!/usr/bin/env python3
"""Provenance-preserving merge (REPAIR_PLAN.md section 2.7; REPAIR_DAG.yaml node R1-GA2; OD-BR-05 section 6 "merge
before compilation"). ``govbridge.gather.engine`` (R1-GA1) already deduplicates a round's hits by content identity
(``govbridge.route.router.dedupe``/``dedupe_key``) to keep its merged evidence set thread-count-independent, but it
keeps only ONE representative ``RouteHit`` per key -- provenance (which route/facet/round/trigger contributed it)
and the other, non-representative occurrences are not this node's to invent inside ``engine.py`` (out of this
node's mutation scope; REPAIR_PLAN.md section 2's own diagram: "merge" is the step AFTER retrieval, never
reimplemented inside the retrieval loop itself). This module is that merge step, built on top of ``engine.gather``'s
own output and :mod:`govbridge.gather.followup`'s triggered-round hits:

* **deduplicate** by the SAME ``(blob, line span)``/unit-id identity ``dedupe_key`` already uses (never a second,
  diverging notion of "the same item");
* **provenance**: every ``(route, facet, round, trigger)`` that contributed to one merged item, never collapsed
  away by dedup;
* **occurrence collapse**: a hit's OWN ``occurrences`` tuple already carries one ``RouteOccurrence`` per ref where
  the underlying route found this content (``govbridge.lexical.query``'s per-ref identity, already computed) --
  this module picks the single most-canonical one as the representative and reduces every other ref to a compact
  per-ref STATUS summary, so a caller never has to print more than one occurrence row per item (this node's own
  acceptance check: "no search hit lists more than one occurrence row plus a ref summary");
* **authority/lifecycle filtering stays exactly what the resolver already decided** (REPAIR_PLAN.md section 2.7:
  "authority and lifecycle filtering unchanged (A only from the resolver)") -- this module never sets, upgrades or
  removes ``authority_class``/``lifecycle`` on any hit; it only DISCLOSES a non-ladder class's mandatory banner
  (``govbridge.authority.classes.NON_LADDER``), the same banner the compiler is already required to render, so a
  superseded/withdrawn item's own restriction (never section A, only its declared ``allowed_sections``) is visible
  at the merge layer too, not just after compilation.
"""
from __future__ import annotations

import dataclasses
from typing import Optional

from govbridge.authority import classes as classesmod
from govbridge.route import router as routermod
from govbridge.route.router import RouteHit, RouteOccurrence

#: the SAME version-status preference order ``govbridge.route.router._prefer`` already uses to pick a
#: representative occurrence -- reused, never re-derived, so "most canonical" means the same thing everywhere in
#: this domain.
_STATUS_ORDER = ("CANONICAL", "SAME_AS_CANONICAL", "CANONICAL_FALLBACK", "HISTORICAL_VERSION", "HISTORY_ONLY",
                  "ABSENT")


def _status_rank(status: Optional[str]) -> int:
    try:
        return _STATUS_ORDER.index(status)
    except ValueError:
        return len(_STATUS_ORDER)


@dataclasses.dataclass(frozen=True)
class ProvenanceEntry:
    """One contribution to a merged item. ``round`` is ``"base"`` for a hit produced by ``engine.gather``'s own
    facet-paging rounds (whose own output does not itemise which round/facet produced which hit -- see this
    module's own caller, ``govbridge.gather.followup``, for why that is a disclosed, out-of-scope limitation of
    R1-GA1's return shape, not something this module papers over) and an integer (0-based, 1-based at the trigger
    layer -- ``followup`` numbers its OWN rounds starting at 1) for a triggered follow-up round. ``trigger`` is
    ``None`` for a base-round contribution, and an :class:`govbridge.gather.identifiers.Identifier`-shaped dict for
    a follow-up one."""
    route: Optional[str]
    facet: Optional[str]
    round: object  # "base" | int
    trigger: Optional[dict] = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def banner_for(authority_class: Optional[str]) -> Optional[str]:
    """The mandatory rendering banner for a non-ladder class (``govbridge.authority.classes.ALL_CLASSES``) --
    ``None`` for a ladder class (which carries no banner at all) or an unrecognised/absent class. Never invents a
    new banner text: this is a straight lookup of the SAME constant the compiler is already bound to render."""
    spec = classesmod.ALL_CLASSES.get(authority_class) if authority_class else None
    return spec.banner if spec is not None else None


def allowed_sections_for(authority_class: Optional[str]) -> tuple:
    """``()`` for a ladder class (any admissible section, ARCHITECTURE.md section 5.1) or an unknown class; the
    declared, restricted tuple for a non-ladder class (e.g. ``EVIDENCE_WITHDRAWN`` -> ``("E", "F")``) -- this is
    what "filtered to E" MEANS for a superseded/withdrawn item: never admissible in A, restricted to exactly these
    sections, and this module changes none of it."""
    spec = classesmod.ALL_CLASSES.get(authority_class) if authority_class else None
    return spec.allowed_sections if spec is not None else ()


def is_non_ladder(authority_class: Optional[str]) -> bool:
    spec = classesmod.ALL_CLASSES.get(authority_class) if authority_class else None
    return spec is not None and not spec.ladder


def collapse_occurrences(occurrences: tuple) -> tuple:
    """``(canonical_occurrence, ref_summary)``. ``canonical_occurrence`` is the single most-canonical
    ``RouteOccurrence`` (never more than one -- this node's own acceptance check). ``ref_summary`` is
    ``{"identical": [...], "different": [...], "history_only": [...], "absent": [...], "note": "..."}``, built
    purely from each occurrence's OWN, already-computed ``version_status`` (never re-derived): ``CANONICAL``/
    ``SAME_AS_CANONICAL``/``CANONICAL_FALLBACK`` count as "identical to canonical", ``HISTORICAL_VERSION`` as
    "different", ``HISTORY_ONLY`` and ``ABSENT`` kept in their own buckets -- REAL INPUT SHAPES item 6: "the
    three-ref view, where the same path has different blobs per ref"."""
    if not occurrences:
        return None, {"identical": [], "different": [], "history_only": [], "absent": [], "note": "no occurrence"}
    ordered = sorted(occurrences, key=lambda o: _status_rank(o.version_status))
    canonical = ordered[0]
    identical, different, history_only, absent = [], [], [], []
    for o in occurrences:
        if o.version_status in ("CANONICAL", "SAME_AS_CANONICAL", "CANONICAL_FALLBACK"):
            identical.append(o.ref)
        elif o.version_status == "HISTORICAL_VERSION":
            different.append(o.ref)
        elif o.version_status == "HISTORY_ONLY":
            history_only.append(o.ref)
        else:
            absent.append(o.ref)
    parts = []
    if identical:
        parts.append(f"identical at refs {', '.join(identical)}")
    if different:
        parts.append(f"differs at {', '.join(different)}")
    if history_only:
        parts.append(f"history-only at {', '.join(history_only)}")
    if absent:
        parts.append(f"absent at {', '.join(absent)}")
    note = "; ".join(parts) if parts else "single occurrence"
    return canonical, {"identical": identical, "different": different, "history_only": history_only,
                        "absent": absent, "note": note}


@dataclasses.dataclass
class MergedItem:
    """One item of a merge's final output: exactly one ``RouteHit``'s worth of content, one canonical occurrence
    (never a raw multi-row dump), a per-ref summary, and every provenance entry that contributed it (REPAIR_PLAN.md
    section 2.7: "keep provenance for every item: each route, facet, round and trigger that produced it")."""
    hit: RouteHit
    provenance: list  # list[ProvenanceEntry]
    canonical_occurrence: Optional[RouteOccurrence]
    ref_summary: dict

    def to_dict(self) -> dict:
        d = {
            "unit_id": self.hit.unit_id, "unit_kind": self.hit.unit_kind, "route": self.hit.route,
            "delivery": self.hit.delivery, "text": self.hit.text, "authority_class": self.hit.authority_class,
            "lifecycle": self.hit.lifecycle, "tier": self.hit.tier, "resolution": self.hit.resolution,
            "occurrence": self.canonical_occurrence.to_dict() if self.canonical_occurrence is not None else None,
            "ref_summary": self.ref_summary,
            "provenance": [p.to_dict() for p in self.provenance],
            "banner": banner_for(self.hit.authority_class),
            "allowed_sections": list(allowed_sections_for(self.hit.authority_class)),
        }
        return d


class MergeAccumulator:
    """Accumulates hits across ANY number of calls (a base round, then one call per resolved follow-up
    identifier), grouped by ``dedupe_key`` (``govbridge.route.router.dedupe_key`` -- never a second identity
    notion), so the SAME item found via three different routes across three different rounds collapses to ONE
    :class:`MergedItem` carrying three :class:`ProvenanceEntry` rows -- this node's own acceptance check."""

    def __init__(self) -> None:
        self._order: list = []
        self._hits: dict = {}         # key -> representative RouteHit (most-canonical so far)
        self._occurrences: dict = {}  # key -> list[RouteOccurrence], accumulated across every contribution
        self._provenance: dict = {}   # key -> list[ProvenanceEntry]

    def add(self, hits: list, route: Optional[str] = None, facet: Optional[str] = None, round=None,
            trigger: Optional[dict] = None) -> None:
        for hit in hits:
            key = routermod.dedupe_key(hit)
            if key not in self._hits:
                self._order.append(key)
                self._hits[key] = hit
                self._occurrences[key] = []
                self._provenance[key] = []
            else:
                current = self._hits[key]
                best = current
                if hit.occurrences and current.occurrences:
                    best = current if _status_rank(current.occurrences[0].version_status) <= _status_rank(
                        hit.occurrences[0].version_status) else hit
                elif hit.occurrences and not current.occurrences:
                    best = hit
                self._hits[key] = best
            self._occurrences[key].extend(hit.occurrences)
            self._provenance[key].append(ProvenanceEntry(
                route=route if route is not None else hit.route, facet=facet, round=round, trigger=trigger,
            ))

    def items(self) -> list:
        out: list = []
        for key in self._order:
            hit = self._hits[key]
            occs = tuple(self._dedupe_occs(self._occurrences[key]))
            canonical, ref_summary = collapse_occurrences(occs)
            out.append(MergedItem(hit=hit, provenance=list(self._provenance[key]),
                                   canonical_occurrence=canonical, ref_summary=ref_summary))
        return out

    @staticmethod
    def _dedupe_occs(occs: list) -> list:
        seen: set = set()
        out: list = []
        for o in occs:
            k = (o.ref, o.commit, o.path, o.line_start, o.line_end)
            if k in seen:
                continue
            seen.add(k)
            out.append(o)
        return out


def merge_hit_stream(contributions: list) -> list:
    """A convenience one-shot form of :class:`MergeAccumulator`: ``contributions`` is a list of
    ``(hits, route, facet, round, trigger)`` tuples (``route``/``facet``/``trigger`` may be ``None``). Returns
    ``list[MergedItem]`` in first-seen order."""
    acc = MergeAccumulator()
    for hits, route, facet, round_, trigger in contributions:
        acc.add(hits, route=route, facet=facet, round=round_, trigger=trigger)
    return acc.items()
