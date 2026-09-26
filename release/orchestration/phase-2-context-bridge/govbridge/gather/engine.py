#!/usr/bin/env python3
"""``govbridge gather``'s core engine (REPAIR_PLAN.md section 2; OD-BR-05; REPAIR_DAG.yaml node R1-GA1): query
instantiation is ``govbridge.gather.instantiate``, the facet registry is ``govbridge.gather.facets``, telemetry
shaping is ``govbridge.gather.telemetry`` -- this module is the retrieval LOOP: decompose one query into facets,
retrieve every round's facets CONCURRENTLY with a deterministic merge order, page each facet with its own cursor,
and stop with a recorded reason from the fixed vocabulary.

Explicitly OUT of this node's scope (REPAIR_PLAN.md section 2.5/2.7; REPAIR_DAG.yaml nodes R1-GA2/R1-GA3), so never
implemented here:

* **adaptive follow-up** -- extracting new identifiers (record ids, symbols, path literals, test names, commits,
  requirement citations) FROM the merged evidence and issuing new queries for them. The extension point exists
  (``identifier_extractor``) so R1-GA2 can add triggered rounds without reshaping this loop, but this module never
  supplies one of its own;
* **version reconciliation** -- the ``versions`` facet is registered (``config/facets.yaml``) and always reported
  ``MISSING`` with its disclosed reason, never silently dropped from a gather's own facet-coverage accounting;
* **compilation** -- facet quotas, content-vs-pointer delivery and hierarchical evidence notes are
  ``govbridge.compile``'s job (R1-GA3 wires ``gather`` into it); this module returns a merged, deduplicated,
  provenance-bearing hit list and its own telemetry, nothing more.

Merge/dedup here reuses ``govbridge.route.router.dedupe`` (never re-implemented): after every round the CUMULATIVE
hit list, built by walking the round's facets in the REGISTRY's own declared order (never thread-completion order --
REPAIR_PLAN.md section 2.3), is deduplicated afresh. This is what makes the merged result byte-identical however
many threads ran the round concurrently, and whatever batch size paged it.
"""
from __future__ import annotations

import concurrent.futures
import dataclasses
import os
from typing import Callable, Optional

from govbridge.core import taskctx as taskctxmod
from govbridge.core.yamlutil import canonical_json, load_yaml_file, sha256_text
from govbridge.gather import facets as facetsmod
from govbridge.gather import telemetry as telemetrymod
from govbridge.route import router as routermod

STOP_FACETS_COVERED = "FACETS_COVERED"
STOP_NO_UNRESOLVED_IDENTIFIERS = "NO_UNRESOLVED_IDENTIFIERS"
STOP_MARGINAL_GAIN_ONLY_DUPLICATES = "MARGINAL_GAIN_ONLY_DUPLICATES"
STOP_MAX_ROUNDS = "MAX_ROUNDS"
STOP_BUDGET_REACHED_WITH_UNRESOLVED = "BUDGET_REACHED_WITH_UNRESOLVED"

#: OD-BR-05 section 5 / REPAIR_PLAN.md section 2.6, verbatim: the fixed, closed stopping-reason vocabulary. "Top-k
#: returned" is never a member -- there is deliberately no "ran out of rounds because k was reached" reason.
STOP_REASONS = (
    STOP_FACETS_COVERED, STOP_NO_UNRESOLVED_IDENTIFIERS, STOP_MARGINAL_GAIN_ONLY_DUPLICATES, STOP_MAX_ROUNDS,
    STOP_BUDGET_REACHED_WITH_UNRESOLVED,
)

_MISSING_GENERIC_REASON = "no matching evidence found in this facet's scope"

_budgets_cache: dict = {}


def _budgets_path() -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    return os.path.join(GOV_BRIDGE_DOMAIN, "config", "budgets.yaml")


def _load_budgets(path: Optional[str] = None) -> dict:
    resolved = path or _budgets_path()
    cached = _budgets_cache.get(resolved)
    if cached is None:
        cached = load_yaml_file(resolved) or {}
        _budgets_cache[resolved] = cached
    return cached


def _budget_total_bytes(budget_profile: Optional[str], path: Optional[str] = None) -> Optional[int]:
    """Gather's OWN overall byte budget for one query (``config/budgets.yaml``'s ``gather.max_bytes_per_query``),
    deliberately separate from ``profiles.<name>.total_kb`` (config/budgets.yaml's own comment explains why: that
    number bounds the FINAL COMPILED packet, after R1-GA3's facet quotas, and gather intentionally over-fetches
    relative to it). ``budget_profile``, when a caller explicitly passes one, OPTS IN to a byte cap tied to that
    named compile profile instead -- never the default, since it would make gather's own stopping point (and its
    merged evidence set) depend on an unrelated compile-time setting."""
    if budget_profile:
        profiles = _load_budgets(path).get("profiles") or {}
        prof = profiles.get(budget_profile)
        if prof and prof.get("total_kb") is not None:
            return int(prof["total_kb"]) * 1024
    gather_cfg = _load_budgets(path).get("gather") or {}
    val = gather_cfg.get("max_bytes_per_query")
    return int(val) if val is not None else None


def _budget_max_items(path: Optional[str] = None) -> Optional[int]:
    gather_cfg = _load_budgets(path).get("gather") or {}
    val = gather_cfg.get("max_items_per_query")
    return int(val) if val is not None else None


def _hit_bytes(hit) -> int:
    if hit.text:
        return len(hit.text.encode("utf-8"))
    return 64  # a small, fixed estimate for a pointer-only hit (no text payload of its own)


@dataclasses.dataclass
class _FacetState:
    """Per-route progress for one facet. ``*_count`` and ``*_exhausted`` are tracked PER ROUTE (never just per
    facet) so each route's own coverage target is independent -- REPAIR_DAG.yaml node R1-GA1 acceptance check 3
    ("an identical merged evidence set; more rounds for the smaller batch") holds because a route's OWN accumulated
    count converges on the SAME fixed target (``facet.effective_target_items()``) whatever ``batch_size`` a caller
    passes; only the number of rounds needed to reach it changes."""
    name: str
    facet: "facetsmod.Facet"
    lexical_offset: int = 0
    lexical_count: int = 0
    lexical_exhausted: bool = False
    semantic_offset: int = 0
    semantic_count: int = 0
    semantic_exhausted: bool = False
    exact_done: bool = False
    exact_count: int = 0
    code_cursor: dict = dataclasses.field(default_factory=dict)
    code_count: int = 0
    code_exhausted: bool = False
    item_count: int = 0        # this facet's own DEDUPED contribution to the global merge (informational/telemetry)
    rounds_run: int = 0

    def route_satisfied(self, route: str, target_items: int) -> bool:
        if route == "lexical":
            return self.lexical_exhausted or self.lexical_count >= target_items
        if route == "semantic":
            return self.semantic_exhausted or self.semantic_count >= target_items
        if route == "exact":
            return self.exact_done
        if route == "code":
            return self.code_exhausted or self.code_count >= target_items
        return True

    def all_routes_satisfied(self, target_items: int) -> bool:
        return all(self.route_satisfied(r, target_items) for r in self.facet.routes) if self.facet.routes else True

    def raw_total(self) -> int:
        """This facet's own accumulated, scope-filtered (but not yet cross-facet-deduped) count -- the right basis
        for "did THIS facet find anything at all" (MISSING disclosure), independent of whether another facet
        happened to surface the same item first in registry order (that would make ``item_count``, the
        cross-facet-deduped contribution, read 0 even though this facet genuinely found something)."""
        return self.lexical_count + self.semantic_count + self.code_count + self.exact_count


def _code_kwargs_for_mode(code_mode: Optional[str], batch_size: int, state: _FacetState) -> dict:
    """Which edge kinds ``real_routes.code_route`` should expand, and whether/how it should page them, for one
    facet's ``code_mode`` (``config/facets.yaml``). REPAIR_DAG.yaml node R1-GA1 uses R1-RL's paging for ``callers``
    (``dependents``) and ``tests_of`` (``tests``); ``callees_of`` has no R1-RL paging, so ``dependencies`` (callees
    only) is single-shot, fanout-capped, exactly as ``code_route`` always behaved -- a disclosed, honest boundary,
    never a silent gap."""
    if code_mode == "dependencies":
        return {"include_callers": False, "include_callees": True, "include_tests": False,
                "include_reads_key": False}
    if code_mode == "dependents":
        return {"include_callers": True, "include_callees": False, "include_tests": False,
                "include_reads_key": True, "page_size": batch_size, "cursor_in": dict(state.code_cursor),
                "cursor_out": state.code_cursor}
    if code_mode == "tests":
        return {"include_callers": False, "include_callees": False, "include_tests": True,
                "include_reads_key": False, "page_size": batch_size, "cursor_in": dict(state.code_cursor),
                "cursor_out": state.code_cursor}
    return {}  # plain code route (e.g. "enforcement"): every edge kind, unpaged -- code_route's own default


def _run_facet_round(facet: "facetsmod.Facet", state: _FacetState, base_text: str, routes, batch_size: int,
                      target_items: int, exclude, exclude_counter, seeds: Optional[list]) -> tuple:
    """One page of one facet, over whichever of its routes are not yet SATISFIED (REPAIR_PLAN.md section 2.2: "its
    routes"). A route is satisfied once its own accumulated count reaches ``target_items`` or it is exhausted; an
    already-satisfied route is skipped entirely this round (never re-queried), and this function never requests
    more than ``min(batch_size, target_items - already_have)`` from a route it does call -- so a route's final
    accumulated count is always exactly ``min(target_items, total_available)``, WHATEVER ``batch_size`` was, and
    only the number of rounds needed to get there depends on it (REPAIR_DAG.yaml node R1-GA1 acceptance check 3).

    Returns ``(filtered_hits, raw_hits)``. ``filtered_hits`` is narrowed to this facet's own
    ``scope_classes``/``lifecycle_scope`` (ARCHITECTURE.md section 5.3 rule 5: placement/scope is class/lifecycle-
    only, never a route's own job) -- a route has no notion of "facet," so this is the ONE place a scoped facet's
    out-of-scope candidates are dropped, and is also WHY a scoped facet (``requirement``, ``decisions_active``/
    ``decisions_history``) can legitimately need more than one round: a page of otherwise-plentiful but
    out-of-scope candidates advances the route's cursor without advancing its count. ``raw_hits`` is EVERY hit this
    round actually fetched, before that filter -- the caller uses it (never ``filtered_hits``) to tell "this round
    turned up fresh, unseen evidence that a scope filter happened to reject" apart from "this round turned up
    nothing genuinely new at all" (MARGINAL_GAIN_ONLY_DUPLICATES): the latter, never the former, is a stopping
    condition."""
    hits: list = []
    raw_hits: list = []
    text = facet.query_text(base_text)

    if "lexical" in facet.routes and not state.route_satisfied("lexical", target_items):
        k = min(batch_size, target_items - state.lexical_count)
        info: dict = {}
        page_raw = routes.run("lexical", text=text, k=k, offset=state.lexical_offset, exclude=exclude,
                               exclude_counter=exclude_counter, page_info_out=info)
        raw_hits.extend(page_raw)
        page_hits = facet.filter_in_scope(page_raw)
        hits.extend(page_hits)
        state.lexical_count += len(page_hits)
        next_offset = info.get("next_offset")
        state.lexical_exhausted = next_offset is None
        if next_offset is not None:
            state.lexical_offset = next_offset

    if "semantic" in facet.routes and not state.route_satisfied("semantic", target_items):
        k = min(batch_size, target_items - state.semantic_count)
        info = {}
        page_raw = routes.run("semantic", text=text, k=k, offset=state.semantic_offset, exclude=exclude,
                               exclude_counter=exclude_counter, page_info_out=info)
        raw_hits.extend(page_raw)
        page_hits = facet.filter_in_scope(page_raw)
        hits.extend(page_hits)
        state.semantic_count += len(page_hits)
        next_offset = info.get("next_offset")
        state.semantic_exhausted = next_offset is None
        if next_offset is not None:
            state.semantic_offset = next_offset

    if "exact" in facet.routes and not state.route_satisfied("exact", target_items):
        k = min(batch_size, target_items)
        page_raw = routes.run("exact", text=text, k=k, exclude=exclude, exclude_counter=exclude_counter)
        raw_hits.extend(page_raw)
        page_hits = facet.filter_in_scope(page_raw)
        hits.extend(page_hits)
        state.exact_count += len(page_hits)
        state.exact_done = True  # an id lookup, never paged -- one call is always "satisfied"

    if "code" in facet.routes and not state.route_satisfied("code", target_items):
        k = min(batch_size, target_items - state.code_count)
        code_kwargs = _code_kwargs_for_mode(facet.code_mode, k, state)
        if seeds:
            page_raw = routes.run("code", seeds=list(seeds), k=k, exclude=exclude,
                                   exclude_counter=exclude_counter, **code_kwargs)
        else:
            page_raw = routes.run("code", text=text, k=k, exclude=exclude,
                                   exclude_counter=exclude_counter, **code_kwargs)
        raw_hits.extend(page_raw)
        page_hits = facet.filter_in_scope(page_raw)
        hits.extend(page_hits)
        state.code_count += len(page_hits)
        if facet.code_mode in ("dependents", "tests"):
            state.code_exhausted = (not state.code_cursor) or all(v is None for v in state.code_cursor.values())
        else:
            state.code_exhausted = True  # dependencies (callees-only) and plain code: single-shot, unpaged

    return hits, raw_hits


def gather(query: dict, routes, *, task=None, seeds: Optional[list] = None, facet_names: Optional[list] = None,
           batch_size: Optional[int] = None, max_rounds: Optional[int] = None, threads: Optional[int] = None,
           exclude: Optional[list] = None, budget_profile: Optional[str] = None, facets_path: Optional[str] = None,
           budgets_path: Optional[str] = None,
           identifier_extractor: Optional[Callable[[list], list]] = None) -> dict:
    """The OD-BR-05 retrieval loop for ONE query (already instantiated -- ``govbridge.gather.instantiate``).
    ``routes`` is a ``govbridge.route.router.RouteSet`` (real or fake, exactly like every other node that consumes
    one). ``identifier_extractor`` is R1-GA2's extension point (module docstring): a callable, ``list[RouteHit] ->
    list``, run once per round over that round's own new hits; this node passes ``None`` by default and merely
    discloses whatever it returns, never acting on it (no new facets, no new rounds triggered by it here)."""
    task = task or taskctxmod.current()
    exclude = task.merge_exclude(exclude)
    exclude_counter = taskctxmod.ExclusionCounter()

    batch_size = batch_size if batch_size is not None else facetsmod.default_batch_size(facets_path)
    max_rounds = max_rounds if max_rounds is not None else facetsmod.default_max_rounds(facets_path)
    threads = threads if threads is not None else facetsmod.default_threads(facets_path)

    all_facets = facetsmod.load_facets(facets_path)
    requested_names = query.get("facets") if facet_names is None else facet_names
    if requested_names is not None and len(requested_names) == 0:
        # An explicit, empty facet override: nothing to retrieve and nothing to chase -- REPAIR_PLAN.md section 2.6's
        # NO_UNRESOLVED_IDENTIFIERS reading taken literally ("no unresolved identifiers" is vacuously true when
        # there was never anything to resolve), distinct from FACETS_COVERED's "every requested facet has an item".
        telem = telemetrymod.GatherTelemetry(query_id=query.get("id", "?"))
        telem.stop_reason = STOP_NO_UNRESOLVED_IDENTIFIERS
        telem.excluded_hits = exclude_counter.count
        return {
            "query": {"id": query.get("id"), "text": query.get("text")}, "batch_size": batch_size,
            "max_rounds": max_rounds, "threads": threads, "facets": [], "stop_reason": telem.stop_reason,
            "merged": [], "merged_sha256": sha256_text(canonical_json([])),
            "telemetry": telem.summary(final_bytes=0), "excluded_hits": exclude_counter.count,
        }

    names = tuple(facetsmod.facets_for_query({**query, "facets": requested_names}, facets_path))
    selected = [(n, all_facets[n]) for n in names if n in all_facets]

    states = {n: _FacetState(name=n, facet=f) for n, f in selected}
    merged: list = []
    telem = telemetrymod.GatherTelemetry(query_id=query.get("id", "?"))
    base_text = query.get("text") or ""

    for n, f in selected:
        if f.synthetic:
            states[n].exhausted = True
            telem.record_round(telemetrymod.FacetRoundStat(
                facet=n, round=0, routes=tuple(f.routes), candidate_items=0, candidate_bytes=0, new_items=0,
                new_bytes=0, exhausted=True, missing=True, missing_reason=f.missing_reason,
            ))

    active = [n for n, f in selected if not f.synthetic]
    total_bytes_budget = _budget_total_bytes(budget_profile, budgets_path)
    max_items_budget = _budget_max_items(budgets_path)

    round_idx = 0
    stop_reason: Optional[str] = None
    new_identifiers: list = []
    raw_seen: set = set()  # dedupe_key of every hit EVER fetched (pre-scope-filter), across every facet/round

    if not active:
        # Every selected facet was synthetic (currently only "versions"), or none matched at all: there is nothing
        # to page and nothing to chase, so this is "covered" (vacuously, and every synthetic facet already recorded
        # its own disclosed MISSING row above) -- 0 non-synthetic rounds, never a bare stop_reason of None.
        stop_reason = STOP_FACETS_COVERED

    while active:
        if round_idx >= max_rounds:
            stop_reason = STOP_MAX_ROUNDS
            break

        results_by_facet: dict = {}
        if threads and threads > 1 and len(active) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
                future_to_name = {
                    ex.submit(_run_facet_round, all_facets[n], states[n], base_text, routes, batch_size,
                              all_facets[n].effective_target_items(), exclude, exclude_counter, seeds): n
                    for n in active
                }
                for fut in concurrent.futures.as_completed(future_to_name):
                    results_by_facet[future_to_name[fut]] = fut.result()
        else:
            for n in active:
                results_by_facet[n] = _run_facet_round(all_facets[n], states[n], base_text, routes, batch_size,
                                                         all_facets[n].effective_target_items(), exclude,
                                                         exclude_counter, seeds)

        # Deterministic merge (REPAIR_PLAN.md section 2.3): walk facets in REGISTRY order, never completion order,
        # so the thread count can only change wall-clock time, never the merged content or its order.
        round_new_raw_unique = 0   # drives MARGINAL_GAIN_ONLY_DUPLICATES -- genuinely fresh RAW content, pre-scope
        round_hits_flat: list = []
        for n, f in selected:
            if n not in results_by_facet:
                continue
            hits, raw_hits = results_by_facet[n]
            round_hits_flat.extend(hits)
            for rh in raw_hits:
                key = routermod.dedupe_key(rh)
                if key not in raw_seen:
                    raw_seen.add(key)
                    round_new_raw_unique += 1
            before = len(merged)
            merged = routermod.dedupe(merged + hits)
            # dedupe() preserves first-seen order and `merged` (before this call) already held only distinct keys,
            # so merged[before:] is EXACTLY the set of genuinely new items this facet contributed this round, in
            # their first-seen order -- never `hits[:new_count]`, which need not be the same items at all.
            new_items = merged[before:]
            new_count = len(new_items)
            states[n].item_count += new_count
            states[n].rounds_run += 1
            target_items = f.effective_target_items()
            satisfied = states[n].all_routes_satisfied(target_items)
            missing = satisfied and states[n].raw_total() == 0
            telem.record_round(telemetrymod.FacetRoundStat(
                facet=n, round=round_idx, routes=tuple(f.routes), candidate_items=len(raw_hits),
                candidate_bytes=sum(_hit_bytes(h) for h in raw_hits), new_items=new_count,
                new_bytes=sum(_hit_bytes(h) for h in new_items), exhausted=satisfied,
                missing=missing, missing_reason=(_MISSING_GENERIC_REASON if missing else None),
            ))

        if total_bytes_budget is not None and sum(_hit_bytes(h) for h in merged) >= total_bytes_budget:
            stop_reason = STOP_BUDGET_REACHED_WITH_UNRESOLVED
            break
        if max_items_budget is not None and len(merged) >= max_items_budget:
            stop_reason = STOP_BUDGET_REACHED_WITH_UNRESOLVED
            break
        if round_idx > 0 and round_new_raw_unique == 0:
            # Every hit fetched this round (across every still-active facet, BEFORE scope filtering) was already
            # in raw_seen -- genuinely nothing new, not just "new but out of scope" (that case keeps a
            # scope-restricted facet active; see _run_facet_round's own docstring).
            stop_reason = STOP_MARGINAL_GAIN_ONLY_DUPLICATES
            break

        if identifier_extractor is not None:
            try:
                new_identifiers = list(identifier_extractor(round_hits_flat) or [])
            except Exception:
                new_identifiers = []

        # REPAIR_PLAN.md section 2.6: FACETS_COVERED is "every requested facet has at least one item, OR an
        # explicit MISSING reason." A facet drops out of `active` once EVERY route it uses is SATISFIED (reached
        # its fixed, batch-size-independent target_items, or is itself genuinely exhausted below that target) --
        # this is also why a scope-restricted facet (`requirement`, `decisions_active`/`decisions_history`) can
        # legitimately need more than one round: an out-of-scope page advances its cursor without advancing its
        # count, so it stays "active" until an in-scope page is found or the route truly runs out.
        active = [n for n in active if not states[n].all_routes_satisfied(all_facets[n].effective_target_items())]
        round_idx += 1
        if not active:
            # R1-GA1 never chases identifiers itself (module docstring) -- whatever identifier_extractor returned is
            # disclosed, never acted on, so reaching here always means "nothing left to page," never "nothing left
            # to chase" in the adaptive sense R1-GA2 will add.
            stop_reason = STOP_FACETS_COVERED
            break

    telem.stop_reason = stop_reason
    telem.unresolved_identifiers = list(new_identifiers)
    # `active` still holds whatever it was at the moment we broke out (its own reassignment runs at the END of
    # each loop body, except when max_rounds fires at the TOP of the next iteration, before any reassignment --
    # `active` is then still last round's post-processing value, which is exactly right: those are the facets that
    # would have run again). A facet that reached every route's target is never "unresolved," whether or not the
    # underlying route could still have given more.
    telem.unresolved_facets = [n for n in active if not states[n].all_routes_satisfied(all_facets[n].effective_target_items())]
    telem.excluded_hits = exclude_counter.count

    final_bytes = sum(_hit_bytes(h) for h in merged)
    merged_dicts = [h.to_dict() for h in merged]
    return {
        "query": {"id": query.get("id"), "text": query.get("text")},
        "batch_size": batch_size, "max_rounds": max_rounds, "threads": threads,
        "facets": [n for n, _ in selected],
        "stop_reason": stop_reason,
        "merged": merged_dicts,
        # Thread-count-independent digest (REPAIR_DAG.yaml node R1-GA1 acceptance check 2): the merge order above is
        # fixed by facet REGISTRY order, never by which thread happened to finish first, so this hash is identical
        # across --threads 1/4/16 for the same query, batch size and corpus.
        "merged_sha256": sha256_text(canonical_json(merged_dicts)),
        "telemetry": telem.summary(final_bytes=final_bytes),
        "excluded_hits": exclude_counter.count,
    }
