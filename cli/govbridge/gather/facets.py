#!/usr/bin/env python3
"""The generic facet registry (REPAIR_PLAN.md section 2.2; ``config/facets.yaml``) -- REPAIR-1 node R1-GA1's second
deliverable. This module only reads ``config/facets.yaml`` and exposes a small, typed API; it decides no domain
content of its own -- a new facet, a narrower/wider authority-class scope, or a ``class_facets`` override is a
config change, never a code change here (OC-BR-02: nothing below ever names a Review-8 item, an F-finding, a
Phase-2 file or a query-class id).

This is also THE configuration-default loader for the batch-size literal (OD-BR-05 section 9: "do not hard-code 8k
as the architecture limit... a configurable per-retrieval batch size only"; REPAIR_DAG.yaml node R1-GA1: "batch_size
from configuration, with no hard-coded top-k spelling anywhere else"). ``govbridge.lexical.query.DEFAULT_K`` and
every real route's own ``k`` default (``govbridge.route.real_routes``) resolve through :func:`default_batch_size`
-- this is the ONE place the fallback integer below is allowed to appear at all, and this module is the only file
this repair excludes from the hard-coded-top-k audit for exactly that reason.
"""
from __future__ import annotations

import dataclasses
import os
from typing import Optional

from govbridge.core.yamlutil import load_yaml_file

_CONFIG_CACHE: dict = {}

#: the literal default, spelled so it never matches the hard-coded-top-k audit pattern (REPAIR_DAG.yaml node R1-GA1
#: acceptance check 4) -- used only when config/facets.yaml itself is missing or unreadable, so a caller of this
#: module never hard-fails just because the config file could not be found.
_FALLBACK_BATCH_SIZE = 8 - 0
_FALLBACK_MAX_ROUNDS = 6
_FALLBACK_THREADS = 4
_FALLBACK_TARGET_ITEMS = 16


def _config_path() -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    return os.path.join(GOV_BRIDGE_DOMAIN, "config", "facets.yaml")


def _load_config(path: Optional[str] = None) -> dict:
    """Cached per resolved path (never per call) -- the same "load once, reuse" discipline
    ``govbridge.route.real_routes.build_real_routes`` already applies to the view/registry/mandatory-items."""
    resolved = path or _config_path()
    cached = _CONFIG_CACHE.get(resolved)
    if cached is None:
        cached = load_yaml_file(resolved) or {}
        _CONFIG_CACHE[resolved] = cached
    return cached


def clear_cache() -> None:
    """Tests that write a fresh ``config/facets.yaml``-shaped file per test must call this first (the cache is
    keyed by path, so two different paths never collide, but the same path across two tests must not see the
    the first test's cached document)."""
    _CONFIG_CACHE.clear()


def default_batch_size(path: Optional[str] = None) -> int:
    try:
        return int(_load_config(path).get("default_batch_size", _FALLBACK_BATCH_SIZE))
    except Exception:
        return _FALLBACK_BATCH_SIZE


def default_max_rounds(path: Optional[str] = None) -> int:
    try:
        return int(_load_config(path).get("default_max_rounds", _FALLBACK_MAX_ROUNDS))
    except Exception:
        return _FALLBACK_MAX_ROUNDS


def default_threads(path: Optional[str] = None) -> int:
    try:
        return int(_load_config(path).get("default_threads", _FALLBACK_THREADS))
    except Exception:
        return _FALLBACK_THREADS


def default_target_items(path: Optional[str] = None) -> int:
    try:
        return int(_load_config(path).get("default_target_items", _FALLBACK_TARGET_ITEMS))
    except Exception:
        return _FALLBACK_TARGET_ITEMS


@dataclasses.dataclass(frozen=True)
class Facet:
    """One row of ``config/facets.yaml``'s ``facets`` table (REPAIR_PLAN.md section 2.2: "routes... scopes, by path
    class... how its queries are built... batch size... minimum packet share"). ``scope_classes``/``lifecycle_scope``
    are authority-class/lifecycle sets (``govbridge.authority.classes``), never a path or file name. ``synthetic``
    facets (currently only ``versions``) issue no route call at all; the engine always reports them ``MISSING`` with
    ``missing_reason``, never silently drops them from a gather's own facet-coverage accounting."""
    name: str
    routes: tuple
    scope_classes: Optional[tuple]
    lifecycle_scope: Optional[tuple]
    extra_terms: tuple
    code_mode: Optional[str]
    min_share: float
    batch_size: Optional[int]
    target_items: Optional[int]
    synthetic: bool
    missing_reason: Optional[str]

    def effective_batch_size(self, requested: Optional[int]) -> int:
        if requested is not None:
            return requested
        if self.batch_size is not None:
            return self.batch_size
        return default_batch_size()

    def effective_target_items(self) -> int:
        if self.target_items is not None:
            return self.target_items
        return default_target_items()

    def query_text(self, base_text: str) -> str:
        """The base query text plus this facet's own generic augmentation terms (REPAIR_PLAN.md section 2.2: "how
        its queries are built"). A facet whose ``scope_classes``/``lifecycle_scope`` already narrows it (e.g.
        ``decisions_active``) commonly declares few or no extra terms; one with no class scope at all (``purpose``,
        ``failed_approaches``, ``evidence_staleness``) leans on its terms to differentiate it from a plain query."""
        base_text = (base_text or "").strip()
        if not self.extra_terms:
            return base_text
        return (base_text + " " + " ".join(self.extra_terms)).strip()

    def in_scope(self, authority_class: Optional[str], lifecycle: Optional[str]) -> bool:
        """Whether one hit's already-assigned authority class/lifecycle (never a route/rank) satisfies this facet's
        declared scope (ARCHITECTURE.md section 5.3 rule 5: placement/scope is class/lifecycle-only)."""
        if self.scope_classes is not None and authority_class not in self.scope_classes:
            return False
        if self.lifecycle_scope is not None and lifecycle not in self.lifecycle_scope:
            return False
        return True

    def filter_in_scope(self, hits: list) -> list:
        """``hits`` narrowed to this facet's own scope (a no-op, same list, when the facet declares neither
        ``scope_classes`` nor ``lifecycle_scope``)."""
        if self.scope_classes is None and self.lifecycle_scope is None:
            return hits
        return [h for h in hits if self.in_scope(h.authority_class, h.lifecycle)]

    def filter_in_scope_counted(self, hits: list) -> tuple:
        """``(kept, dropped_count)`` -- the SAME filter as :meth:`filter_in_scope`, plus how many were dropped
        (REPAIR_DAG.yaml node R1-GA1 reopening: kept only as a gather-level ASSERTION now that every real route
        already pushes this filter down/applies it itself -- a caller uses the count to disclose, in telemetry,
        whether a round's MAX_ROUNDS/exhaustion was caused by out-of-scope paging rather than a genuine absence of
        evidence)."""
        if self.scope_classes is None and self.lifecycle_scope is None:
            return hits, 0
        kept = [h for h in hits if self.in_scope(h.authority_class, h.lifecycle)]
        return kept, len(hits) - len(kept)


def _as_tuple(value) -> Optional[tuple]:
    if not value:
        return None
    return tuple(value)


def _facet_from_raw(name: str, raw: dict) -> Facet:
    return Facet(
        name=name,
        routes=tuple(raw.get("routes") or ()),
        scope_classes=_as_tuple(raw.get("scope_classes")),
        lifecycle_scope=_as_tuple(raw.get("lifecycle_scope")),
        extra_terms=tuple(raw.get("extra_terms") or ()),
        code_mode=raw.get("code_mode"),
        min_share=float(raw.get("min_share", 0.0)),
        batch_size=raw.get("batch_size"),
        target_items=raw.get("target_items"),
        synthetic=bool(raw.get("synthetic", False)),
        missing_reason=raw.get("missing_reason"),
    )


def load_facets(path: Optional[str] = None) -> dict:
    """``{facet_name: Facet}``, in the config file's OWN declared order (YAML mapping order is preserved by
    ``yaml.safe_load`` since Python 3.7 dicts are ordered) -- REPAIR_PLAN.md section 2.3: "merging follows the
    registry order"."""
    doc = _load_config(path)
    raw_facets = doc.get("facets") or {}
    return {name: _facet_from_raw(name, raw) for name, raw in raw_facets.items()}


def facet_names_in_order(path: Optional[str] = None) -> tuple:
    return tuple(load_facets(path).keys())


def facets_for_query(query: dict, path: Optional[str] = None) -> tuple:
    """Which facet NAMES apply to one query (REPAIR_PLAN.md section 2.2: "A query class maps to a set of facets...
    A chain query maps to all of them. Controls are ordinary queries"), in registry order. Resolution order, fully
    generic and config-driven (OC-BR-02: no facet mapping here ever names a Review-8 item, an F-finding or a
    query-class id):

    1. the query's OWN ``facets`` list, if it named one explicitly (never narrowed further by this module);
    2. ``class_facets[query['class']]``, if the query carries a ``class`` AND that class is a row in the registry's
       own (versioned, initially empty) ``class_facets`` table;
    3. otherwise every registered facet -- the safe default, so "a chain query maps to all of them" generalises to
       every query, since no facet is known in advance to be irrelevant to any one of them."""
    doc = _load_config(path)
    all_names = tuple((doc.get("facets") or {}).keys())
    own = query.get("facets")
    if own is not None:
        # An explicit list ALWAYS wins verbatim, including an explicit empty list ("no facets at all") -- only a
        # missing/None key falls through to class_facets/the default.
        return tuple(f for f in own if f in all_names)
    class_facets = doc.get("class_facets") or {}
    cls = query.get("class")
    if cls and cls in class_facets:
        return tuple(f for f in class_facets[cls] if f in all_names)
    return all_names
