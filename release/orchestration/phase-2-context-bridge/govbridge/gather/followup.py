#!/usr/bin/env python3
"""``govbridge.gather``'s adaptive follow-up and merge (REPAIR_PLAN.md sections 2.5/2.7; REPAIR_DAG.yaml node
R1-GA2; OD-BR-05 sections 3 and 6). Builds on ``govbridge.gather.engine``'s (R1-GA1) extension points -- it never
forks that loop: one call to :func:`gather_with_followup` runs the base engine ONCE for round 0 (unchanged, with
every one of R1-GA1's own tested properties -- parallel facets, paging, the fixed stopping vocabulary), then adds
SEQUENTIAL, TRIGGERED rounds on top: extract identifiers from the round's own evidence
(:mod:`govbridge.gather.identifiers`), resolve each one through the existing routes or through R1-RL's persisted
lineage layer, and merge everything with provenance (:mod:`govbridge.gather.merge`). Version reconciliation
(:mod:`govbridge.gather.versions`) is spliced in as the ``versions`` facet's real content when it was requested,
replacing ``engine.gather``'s own always-``MISSING`` placeholder for that facet name.

**Read-only (BR-DAG-AMEND-R1-15).** Every SELECT this module or :mod:`govbridge.gather.identifiers` issues against
``lineage_edge``/``occurrence`` opens its OWN connection via ``govbridge.core.store.open_db_readonly`` -- this
module adds no cache, index or table of its own, and never opens a read-write connection itself. The underlying
``RouteSet`` (built by the caller, exactly like every other ``gather`` consumer) is NOT this module's to change:
the code route's own query-time write (``code/symbols.py``'s lazy ``ensure_indexed``) and hit classification's
``ensure_schema`` call are BR-DAG-AMEND-R1-17's fix, routed to R1-XC in parallel -- see this module's own
:func:`gather_with_followup` docstring and this node's checkpoint ``open_issues`` for exactly where that shows up.
"""
from __future__ import annotations

import dataclasses
from typing import Optional

from govbridge.core import gitobj
from govbridge.core import store as storemod
from govbridge.core import taskctx as taskctxmod
from govbridge.core.yamlutil import canonical_json, sha256_text
from govbridge.gather import engine as enginemod
from govbridge.gather import facets as facetsmod
from govbridge.gather import identifiers as identifiersmod
from govbridge.gather import merge as mergemod
from govbridge.gather import telemetry as telemetrymod
from govbridge.gather import versions as versionsmod
from govbridge.graph import derive as derivemod
from govbridge.route.router import RouteHit, RouteOccurrence

#: REPAIR_DAG.yaml node R1-GA2 acceptance check 1: "reached within 3 rounds" -- the default follow-up depth. A
#: caller may still raise/lower it; this is only the configuration-free default (mirroring
#: govbridge.gather.facets's own "one literal default, everything else configuration" discipline for THIS module's
#: own new knob, which config/facets.yaml -- out of this node's mutation scope -- does not carry).
DEFAULT_MAX_FOLLOWUP_ROUNDS = 3
#: a bound on how many items one identifier's own resolution may add, so a single pathological identifier (an
#: extremely common symbol, say) cannot silently balloon a follow-up round -- REPAIR_PLAN.md section 2.5's "a
#: visited set prevents loops" plus this domain's general "within budget" discipline for paged code-route calls.
DEFAULT_MAX_ITEMS_PER_IDENTIFIER = 50
#: OD-BR-05 section 5's "explicit task/context budget reached, with unresolved coverage disclosed": real prose
#: evidence is dense with identifier-shaped tokens (a real-view measurement on this domain's own CONTROL-A found
#: 81 distinct candidates from just 31 "purpose"-facet items -- record ids, path/joined-path literals, symbols and
#: commit hashes are all common English/code shapes), and EACH one costs at least one route call. Without a
#: per-round cap, a single round's own identifier fan-out -- never the number of ROUNDS, which max_followup_rounds
#: already bounds -- can make one gather call arbitrarily expensive on a real corpus. Capped, never silently
#: truncated: exceeding it stops with BUDGET_REACHED_WITH_UNRESOLVED and discloses exactly which identifiers were
#: deferred (telemetry's own unresolved_identifiers).
DEFAULT_MAX_IDENTIFIERS_PER_ROUND = 20
_MAX_SLICE_CHARS = 1600


def _hit_from_dict(d: dict) -> RouteHit:
    occs = tuple(RouteOccurrence(**o) for o in (d.get("occurrences") or []))
    kwargs = dict(d)
    kwargs["occurrences"] = occs
    return RouteHit(**kwargs)


def _read_only_conn():
    """The lineage/occurrence reader connection this module owns (identifiers.extract_from_lineage,
    versions.reconcile_path's own gitobj calls need no connection at all). ``None`` on any failure -- a store that
    was never built, or one this environment cannot open read-only -- is an honest MISSING for identifier
    extraction from the lineage layer, never a crash (the same discipline every other optional-store lookup in
    this domain already documents)."""
    try:
        return storemod.open_db_readonly()
    except Exception:
        return None


def _resolve_view_for(task, view_path: Optional[str], repo: Optional[str]):
    try:
        from govbridge.core import view as viewmod
        from govbridge import GOV_BRIDGE_DOMAIN
        import os
        vp = view_path or (task.view if getattr(task, "view", None) else None) or os.path.join(
            GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
        return viewmod.resolve_view(viewmod.load_view(vp), repo=repo)
    except Exception:
        return None


def _dedupe_hits_locally(hits: list) -> list:
    from govbridge.route import router as routermod
    return routermod.dedupe(hits)


# A shared, real repository (this domain's own worktree) is under concurrent access from other agents in this
# orchestration session -- a `git gc`/repack can transiently race an ordinary read (observed directly: a
# `cat-file blob <oid>` failing with "bad file" moments after `blob_at` resolved that same oid). None of
# govbridge.core.gitobj's own functions catch that for a caller; every direct gitobj call this module makes for
# ITS OWN resolution (never the routes, which are not this module's to change) goes through one of these three
# wrappers instead, degrading to an honest MISSING rather than propagating the exception.

def _safe_ls_tree_path(commit: str, path: str, repo: Optional[str]):
    try:
        return gitobj.ls_tree_path(commit, path, repo=repo)
    except Exception:
        return None


def _safe_ls_tree_paths(commit: str, repo: Optional[str], tree_cache: Optional[dict] = None) -> list:
    """``tree_cache``, when given, memoises one FULL ``git ls-tree -r`` per ``(commit, repo)`` for the lifetime of
    one :func:`gather_with_followup` call -- a real-view performance fix, not a persisted cache (BR-DAG-AMEND-R1-15
    is about the STORE; this is a plain in-process dict, created fresh and thrown away by every call, never shared
    across gathers or written anywhere). Without this, a round whose evidence carries many unresolved path/joined-
    path-literal identifiers against the SAME commit re-walks the whole tree once per identifier -- on this
    domain's own real, multi-thousand-file, multi-ref corpus that dominated wall time badly enough to make this
    node's own CONTROL-A acceptance-check run impractical (this node's checkpoint ``lessons``)."""
    key = (commit, repo)
    if tree_cache is not None and key in tree_cache:
        return tree_cache[key]
    try:
        result = gitobj.ls_tree_paths(commit, repo=repo)
    except Exception:
        result = []
    if tree_cache is not None:
        tree_cache[key] = result
    return result


def _safe_read_path(commit: str, path: str, repo: Optional[str]):
    try:
        return gitobj.read_path(commit, path, repo=repo)
    except Exception:
        return None


# ---------------------------------------------------------------------------------------------------------------
# Resolution: one Identifier -> zero or more new RouteHit, tagged with a resolution label. Every kind is resolved
# through the matching mechanism REPAIR_PLAN.md section 2.5 names: "exact id, code definitions or callers or
# tests, path resolution, or a section of a known document" -- reusing the EXISTING routes wherever one exists
# (never a second, parallel retrieval mechanism), and R1-RL's persisted lineage_edge only for the edge kinds no
# route surfaces at all (CLI-dispatch/test-registry TESTS, DEPENDS_ON_DATA, CITES_REQUIREMENT).
# ---------------------------------------------------------------------------------------------------------------

def _hit_from_git_slice(path: str, commit: str, ref: Optional[str], line_start: Optional[int],
                         line_end: Optional[int], resolution: str, repo: Optional[str] = None) -> Optional[RouteHit]:
    """A hit built directly from git content (never through a route) -- used only for the two lineage-edge-only
    kinds (``CITES_REQUIREMENT``'s resolved section, ``DEPENDS_ON_DATA``'s resolved data file) that no existing
    route can fetch content for. Deliberately carries NO authority classification
    (``authority_class=None, lifecycle=None``): the real classifier (``govbridge.authority.layer.classify_hit``)
    performs a query-time schema write (BR-DAG-AMEND-R1-17, routed to R1-XC in parallel), and this module adds no
    write of its own (BR-DAG-AMEND-R1-15) -- an honest, disclosed gap (this node's checkpoint ``open_issues``),
    never a silent misclassification. Never raises: ``gitobj.read_path`` itself already returns ``None`` for a
    path genuinely absent at ``commit``, but a real, shared-repository git call can also fail transiently (a
    concurrent ``git gc``/repack racing this read -- observed against the real, multi-agent-shared repository this
    domain lives in); that failure degrades to an honest MISSING here too, never a crash that would take down an
    entire gather over one unlucky git call."""
    raw = _safe_read_path(commit, path, repo)
    if raw is None:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    lines = text.splitlines()
    if line_start is not None:
        l1 = max(1, line_start)
        l2 = line_end if line_end is not None else l1
        snippet = "\n".join(lines[l1 - 1:l2])
    else:
        l1 = l2 = None
        snippet = text
    if len(snippet) > _MAX_SLICE_CHARS:
        snippet = snippet[:_MAX_SLICE_CHARS]
    occ = RouteOccurrence(ref=ref or "?", commit=commit, path=path, version_status="ABSENT",
                          line_start=l1, line_end=l2)
    unit_id = f"{path}:{l1}-{l2}" if l1 is not None else path
    return RouteHit(unit_id=unit_id, unit_kind="occurrence", route="graph", rank=1, delivery="DERIVED",
                     occurrences=(occ,), text=snippet, authority_class=None, lifecycle=None, resolution=resolution)


def _resolve_via_exact(identifier, routes, k: int, exclude, exclude_counter) -> list:
    hits = routes.run("exact", text=identifier.value, k=k, exclude=exclude, exclude_counter=exclude_counter)
    return [dataclasses.replace(h, resolution=h.resolution or "EXACT_ID") for h in hits]


def _resolve_via_code(name: str, routes, k: int, exclude, exclude_counter, resolution_label: Optional[str] = None,
                       max_items: int = DEFAULT_MAX_ITEMS_PER_IDENTIFIER) -> list:
    """Resolves ONE code-layer seed name through the existing code route, paging ``callers``/``tests`` (R1-RL's own
    cursors) to EXHAUSTION within ``max_items`` (this node's brief: "Page callers, tests_of and reads_key_of through
    their cursors, to exhaustion within budget") rather than the single page every OTHER caller of the code route
    takes."""
    collected: list = []
    cursor: dict = {}
    page_size = max(1, min(k, max_items))
    while True:
        remaining = max_items - len(collected)
        if remaining <= 0:
            break
        page = routes.run("code", seeds=[name], k=min(page_size, remaining), exclude=exclude,
                           exclude_counter=exclude_counter, include_callers=True, include_callees=True,
                           include_tests=True, include_reads_key=True, page_size=page_size, cursor_in=dict(cursor),
                           cursor_out=cursor)
        if not page:
            break
        if resolution_label:
            page = [dataclasses.replace(h, resolution=resolution_label) for h in page]
        collected.extend(page)
        if not cursor or all(v is None for v in cursor.values()):
            break
    return collected


def _resolve_symbol_or_rust_test_path(identifier, routes, k: int, exclude, exclude_counter) -> list:
    value = identifier.value
    hits = _resolve_via_code(value, routes, k, exclude, exclude_counter)
    if hits or "::" not in value:
        return hits
    # REAL INPUT SHAPES item 2: the code layer gives a free/mod-nested Rust fn a qualified_name WITHOUT its module
    # path, so a `mod::fn`-shaped identifier that finds nothing under its own full text is retried by its TRAILING
    # segment. Ambiguity (more than one distinct definition surfaces under the bare name) gets its own, distinct
    # heuristic label -- never silently collapsed to the first match.
    trailing = value.rsplit("::", 1)[-1]
    hits = _resolve_via_code(trailing, routes, k, exclude, exclude_counter)
    distinct_defs = {h.unit_id for h in hits if h.unit_kind == "symbol"}
    label = ("HEURISTIC_TRAILING_SEGMENT" if len(distinct_defs) <= 1
             else "HEURISTIC_TRAILING_SEGMENT_AMBIGUOUS")
    return [dataclasses.replace(h, resolution=label) for h in hits]


def _resolve_requirement_citation(identifier, resolved_view, repo: Optional[str],
                                   tree_cache: Optional[dict] = None) -> list:
    """Two shapes, both this node's brief's "sections of a known document":

    * a lineage-edge-derived citation (``identifier.note`` names the row's own derivation): ``identifier.value`` is
      ALREADY the resolved ``dst`` -- ``"<path>:<line>-<line>"`` (a resolved section/line) or a bare document path
      (``HEURISTIC_SECTION_UNRESOLVED`` -- the document resolved, the numbered heading did not; never dropped);
    * a text-extracted citation (``identifier.note`` carries ``"path:line l1=.. l2=.."``): resolved against the
      identifier's OWN source commit directly."""
    note = identifier.note or ""
    commit = identifier.source_commit
    ref = identifier.source_ref
    if "lineage_edge" in note:
        value = identifier.value
        if ":" in value and value.rsplit(":", 1)[-1].replace("-", "").isdigit():
            path, line_spec = value.rsplit(":", 1)
            l1_s, _, l2_s = line_spec.partition("-")
            l1, l2 = int(l1_s), int(l2_s) if l2_s else int(l1_s)
        else:
            path, l1, l2 = value, None, None
        label = "HEURISTIC_SECTION_UNRESOLVED" if l1 is None else "HEURISTIC_COMMENT_SECTION"
        hit = _hit_from_git_slice(path, commit, ref, l1, l2, label, repo=repo)
        return [hit] if hit is not None else []
    # text-extracted: identifier.value is a candidate document path; resolve it against the tree at commit.
    if commit is None:
        return []
    entry = _safe_ls_tree_path(commit, identifier.value, repo)
    resolved_path = identifier.value if entry is not None else None
    if resolved_path is None:
        matches = [p for p in _safe_ls_tree_paths(commit, repo, tree_cache)
                   if p == identifier.value or p.endswith("/" + identifier.value)]
        if len(matches) == 1:
            resolved_path = matches[0]
    if resolved_path is None:
        return []
    l1 = l2 = None
    label = "EXACT_COMMENT_CITATION"
    if "l1=" in note:
        try:
            fields = dict(part.split("=", 1) for part in note.split() if "=" in part)
            l1 = int(fields["l1"]) if fields.get("l1") not in (None, "None") else None
            l2 = int(fields["l2"]) if fields.get("l2") not in (None, "None", "") else l1
        except Exception:
            l1 = l2 = None
    elif "sec=" in note:
        # a "<doc> section N" / "<doc> §N" citation (derivemod.SECTION_CITE_RE): resolve the numbered heading the
        # SAME way cites_requirement_edges_in_text does (derivemod._first_heading_for_section, never a second
        # heading-numbering grammar), so the delivered slice is the cited SECTION, not the whole document.
        try:
            fields = dict(part.split("=", 1) for part in note.split() if "=" in part)
            section_no = fields.get("sec")
        except Exception:
            section_no = None
        if section_no:
            raw = _safe_read_path(commit, resolved_path, repo)
            try:
                decoded = raw.decode("utf-8") if raw is not None else None
            except UnicodeDecodeError:
                decoded = None
            found_line = derivemod._first_heading_for_section(decoded, section_no) if decoded is not None else None
            if found_line is not None:
                l1 = l2 = found_line
                label = "HEURISTIC_COMMENT_SECTION"
            else:
                label = "HEURISTIC_SECTION_UNRESOLVED"
    hit = _hit_from_git_slice(resolved_path, commit, ref, l1, l2, label, repo=repo)
    return [hit] if hit is not None else []


def _resolve_path_literal(identifier, routes, resolved_view, repo: Optional[str], k: int, exclude,
                           exclude_counter, tree_cache: Optional[dict] = None) -> list:
    commit = identifier.source_commit
    value = identifier.value
    resolved_path = None
    if commit is not None:
        if _safe_ls_tree_path(commit, value, repo) is not None:
            resolved_path = value
        else:
            matches = [p for p in _safe_ls_tree_paths(commit, repo, tree_cache)
                       if p == value or p.endswith("/" + value)]
            if len(matches) == 1:
                resolved_path = matches[0]
    if resolved_path is not None and commit is not None:
        label = "HEURISTIC_JOINED_PATH" if identifier.kind == identifiersmod.KIND_JOINED_PATH_LITERAL else "EXACT_LITERAL_PATH"
        hit = _hit_from_git_slice(resolved_path, commit, identifier.source_ref, None, None, label, repo=repo)
        if hit is not None:
            return [hit]
    # Fall back to a mention lookup via the exact route (still generic, still "path resolution" -- REPAIR_PLAN.md
    # section 2.5) when the literal did not resolve directly against its own source commit.
    return _resolve_via_exact(identifier, routes, k, exclude, exclude_counter)


def resolve_identifier(identifier, routes, *, resolved_view=None, repo: Optional[str] = None, batch_size: int = 8,
                        exclude=None, exclude_counter=None, tree_cache: Optional[dict] = None) -> list:
    """One :class:`govbridge.gather.identifiers.Identifier` -> ``list[RouteHit]``, each already tagged with a
    ``resolution`` label. Never raises: an identifier this module cannot resolve at all yields an empty list
    (recorded as a trigger with zero new items, never silently omitted from telemetry -- see
    :func:`gather_with_followup`). ``tree_cache``: an optional, call-scoped dict (see
    :func:`_safe_ls_tree_paths`) a caller resolving MANY identifiers in one gather should share across every one of
    these calls; omitted, each call that needs a whole-tree listing pays for its own."""
    K = identifiersmod
    kind = identifier.kind
    if kind == K.KIND_RECORD_ID:
        return _resolve_via_exact(identifier, routes, batch_size, exclude, exclude_counter)
    if kind == K.KIND_SYMBOL:
        return _resolve_via_code(identifier.value, routes, batch_size, exclude, exclude_counter)
    if kind == K.KIND_RUST_TEST_PATH:
        return _resolve_symbol_or_rust_test_path(identifier, routes, batch_size, exclude, exclude_counter)
    if kind == K.KIND_TESTS_OF:
        hits = _resolve_via_exact(identifier, routes, batch_size, exclude, exclude_counter)
        hits += _resolve_via_code(identifier.value, routes, batch_size, exclude, exclude_counter)
        return _dedupe_hits_locally(hits)
    if kind in (K.KIND_PATH_LITERAL, K.KIND_JOINED_PATH_LITERAL):
        return _resolve_path_literal(identifier, routes, resolved_view, repo, batch_size, exclude, exclude_counter,
                                      tree_cache=tree_cache)
    if kind == K.KIND_COMMIT:
        return _resolve_via_exact(identifier, routes, batch_size, exclude, exclude_counter)
    if kind == K.KIND_REQUIREMENT_CITATION:
        return _resolve_requirement_citation(identifier, resolved_view, repo, tree_cache=tree_cache)
    return []


# ---------------------------------------------------------------------------------------------------------------
# The orchestrator: round 0 through the unchanged base engine, then sequential triggered rounds.
# ---------------------------------------------------------------------------------------------------------------

def gather_with_followup(query: dict, routes, *, task=None, seeds: Optional[list] = None,
                          facet_names: Optional[list] = None, batch_size: Optional[int] = None,
                          max_rounds: Optional[int] = None, threads: Optional[int] = None,
                          exclude: Optional[list] = None, budget_profile: Optional[str] = None,
                          facets_path: Optional[str] = None, budgets_path: Optional[str] = None,
                          resolved_view=None, view_path: Optional[str] = None, repo: Optional[str] = None,
                          max_followup_rounds: int = DEFAULT_MAX_FOLLOWUP_ROUNDS,
                          max_items_per_identifier: int = DEFAULT_MAX_ITEMS_PER_IDENTIFIER,
                          max_identifiers_per_round: int = DEFAULT_MAX_IDENTIFIERS_PER_ROUND, grammar=None,
                          conn=None) -> dict:
    """OD-BR-05 sections 3 ("sequential/adaptive retrieval... the next query may be generated from the evidence
    returned by the previous query") and 6 ("merge before compilation... across all retrieval rounds"). Round 0 is
    exactly ``govbridge.gather.engine.gather`` (this node's base, never forked); every round after that is
    triggered by an identifier :mod:`govbridge.gather.identifiers` found in the PREVIOUS round's own new evidence,
    resolved through :func:`resolve_identifier`, with a visited set (REPAIR_PLAN.md section 2.5) so the same
    identifier is never chased twice. Returns the SAME shape ``engine.gather`` does (``query``, ``batch_size``,
    ``max_rounds``, ``threads``, ``facets``, ``stop_reason``, ``merged``, ``merged_sha256``, ``telemetry``,
    ``excluded_hits``), plus ``versions`` (this facet's real content, when requested) and
    ``followup_rounds``/``visited_identifiers`` for direct inspection.

    ``conn``: an already-open store connection to reuse for lineage-edge lookups (tests pass their own); omitted,
    this function opens (and closes) its own via ``store.open_db_readonly()`` -- BR-DAG-AMEND-R1-15, never a
    read-write connection of this module's own making."""
    task = task or taskctxmod.current()
    exclude_merged = task.merge_exclude(exclude)
    batch_size = batch_size if batch_size is not None else facetsmod.default_batch_size(facets_path)
    grammar = grammar if grammar is not None else identifiersmod._default_grammar()
    resolved_view = resolved_view if resolved_view is not None else _resolve_view_for(task, view_path, repo)

    base_result = enginemod.gather(
        query, routes, task=task, seeds=seeds, facet_names=facet_names, batch_size=batch_size,
        max_rounds=max_rounds, threads=threads, exclude=exclude, budget_profile=budget_profile,
        facets_path=facets_path, budgets_path=budgets_path,
    )

    owns_conn = conn is None
    if owns_conn:
        conn = _read_only_conn()

    acc = mergemod.MergeAccumulator()
    base_hits = [_hit_from_dict(d) for d in base_result["merged"]]
    # REPAIR_PLAN.md section 2.7: "keep provenance for every item". engine.gather's own output does not itemise
    # WHICH facet/round produced which hit (out of this node's mutation scope to change) -- "base" discloses
    # exactly that boundary rather than guessing at a facet/round this module cannot actually know.
    acc.add(base_hits, facet=None, round="base", trigger=None)

    telem = telemetrymod.GatherTelemetry(query_id=query.get("id", "?"))
    triggers_log: list = []
    visited: set = set()
    followup_rounds_run = 0
    followup_stop_reason: Optional[str] = None
    frontier = base_hits
    followup_exclude_counter = taskctxmod.ExclusionCounter()
    # A plain in-process dict, thrown away with this call (see _safe_ls_tree_paths's own docstring) -- never a
    # store cache, never shared across gathers.
    tree_cache: dict = {}

    deferred_identifiers: list = []
    try:
        round_idx = 1
        while round_idx <= max_followup_rounds:
            candidates = identifiersmod.extract_all(frontier, grammar=grammar, conn=conn, repo=repo)
            todo = [i for i in candidates if i.key() not in visited]
            if not todo:
                followup_stop_reason = enginemod.STOP_NO_UNRESOLVED_IDENTIFIERS
                break
            budget_exceeded = len(todo) > max_identifiers_per_round
            if budget_exceeded:
                # OD-BR-05 section 5: never a silent drop -- every identifier this round found but did not have
                # budget to chase is named, not merely counted, and the round still fully processes the ones it
                # DID take (deterministic prefix, extraction order) rather than stopping mid-identifier.
                deferred_identifiers.extend(i.to_dict() for i in todo[max_identifiers_per_round:])
                todo = todo[:max_identifiers_per_round]
            round_new_hits: list = []
            round_candidate_items = 0
            for ident in todo:
                visited.add(ident.key())
                resolved = resolve_identifier(ident, routes, resolved_view=resolved_view, repo=repo,
                                               batch_size=batch_size, exclude=exclude_merged,
                                               exclude_counter=followup_exclude_counter, tree_cache=tree_cache)
                resolved = resolved[:max_items_per_identifier]
                round_candidate_items += len(resolved)
                trigger_dict = ident.to_dict()
                acc.add(resolved, facet=f"followup:{ident.kind}", round=round_idx, trigger=trigger_dict)
                triggers_log.append({
                    "round": round_idx, "identifier": trigger_dict, "new_items": [h.unit_id for h in resolved],
                })
                round_new_hits.extend(resolved)
            telem.record_round(telemetrymod.FacetRoundStat(
                facet="followup", round=round_idx, routes=("followup",), candidate_items=round_candidate_items,
                candidate_bytes=sum(len((h.text or "").encode("utf-8")) for h in round_new_hits),
                new_items=len(round_new_hits), new_bytes=sum(len((h.text or "").encode("utf-8"))
                                                              for h in round_new_hits),
                exhausted=False,
            ))
            followup_rounds_run += 1
            if budget_exceeded:
                followup_stop_reason = enginemod.STOP_BUDGET_REACHED_WITH_UNRESOLVED
                break
            if not round_new_hits:
                followup_stop_reason = enginemod.STOP_MARGINAL_GAIN_ONLY_DUPLICATES
                break
            frontier = round_new_hits
            round_idx += 1
        else:
            followup_stop_reason = enginemod.STOP_MAX_ROUNDS

        merged_items = acc.items()
        distinct_paths = sorted({
            item.canonical_occurrence.path for item in merged_items
            if item.canonical_occurrence is not None and item.canonical_occurrence.path
        })
        # REPAIR_PLAN.md section 2.7: version reconciliation is this facet's real content, computed for every
        # gather (never gated behind config/facets.yaml's own facet-selection machinery, which is a COMPILE-time
        # quota concept, R1-GA3's -- gather always discloses it when there is at least one resolved path).
        versions_report = versionsmod.versions_facet(resolved_view, distinct_paths, repo=repo)
    finally:
        if owns_conn and conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    final_stop_reason = followup_stop_reason if followup_rounds_run > 0 else base_result["stop_reason"]
    total_excluded = base_result.get("excluded_hits", 0) + followup_exclude_counter.count
    telem.stop_reason = final_stop_reason
    telem.follow_up_triggers = triggers_log
    telem.unresolved_identifiers = base_result["telemetry"].get("unresolved_identifiers", []) + deferred_identifiers
    telem.unresolved_facets = base_result["telemetry"].get("unresolved_facets", [])
    telem.excluded_hits = total_excluded

    merged_dicts = [item.to_dict() for item in merged_items]
    final_bytes = sum(len((d.get("text") or "").encode("utf-8")) for d in merged_dicts)
    telemetry_summary = telem.summary(final_bytes=final_bytes)
    telemetry_summary["base_rounds"] = base_result["telemetry"].get("rounds", 0)
    telemetry_summary["base_stop_reason"] = base_result["stop_reason"]
    telemetry_summary["followup_rounds"] = followup_rounds_run

    result = {
        "query": base_result["query"], "batch_size": base_result["batch_size"],
        "max_rounds": base_result["max_rounds"], "threads": base_result["threads"],
        "facets": base_result["facets"], "stop_reason": final_stop_reason, "merged": merged_dicts,
        "merged_sha256": sha256_text(canonical_json(merged_dicts)), "telemetry": telemetry_summary,
        "excluded_hits": total_excluded, "followup_rounds": followup_rounds_run,
        "visited_identifiers": [{"kind": k, "value": v} for (k, v) in sorted(visited)],
    }
    if versions_report is not None:
        result["versions"] = versions_report
    return result


# ---------------------------------------------------------------------------------------------------------------
# `python -m govbridge.gather.followup` -- mirrors `govbridge gather`'s own argument shape (govbridge/cli.py's
# cmd_gather, out of this node's mutation_scope this wave -- RS owns it in this same parallel group). This is the
# node's own, in-scope way to exercise the SAME capability end to end (this node's checkpoint `decisions` requests
# that whoever next edits govbridge/cli.py in the RX -> GA1 -> RS -> RA sequence wires the top-level `gather`
# subcommand to this module instead of `govbridge.gather.engine` directly, a one-line import change).
# ---------------------------------------------------------------------------------------------------------------

def main(argv=None) -> int:
    import argparse
    import json
    import os
    import sys

    from govbridge.core.yamlutil import load_yaml_file
    from govbridge.gather import instantiate as instmod
    from govbridge.route import real_routes as real_routesmod

    p = argparse.ArgumentParser(prog="govbridge.gather.followup")
    p.add_argument("--task", required=True)
    p.add_argument("--query", required=True)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--max-rounds", type=int, default=None)
    p.add_argument("--max-followup-rounds", type=int, default=DEFAULT_MAX_FOLLOWUP_ROUNDS)
    p.add_argument("--max-identifiers-per-round", type=int, default=DEFAULT_MAX_IDENTIFIERS_PER_ROUND)
    p.add_argument("--threads", type=int, default=None)
    p.add_argument("--facets", action="append", metavar="NAME")
    p.add_argument("--exclude", action="append", metavar="GLOB")
    p.add_argument("--view")
    p.add_argument("--registry")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    from govbridge import GOV_BRIDGE_DOMAIN

    def _abs_path(maybe_rel: str) -> str:
        if os.path.isabs(maybe_rel):
            return maybe_rel
        if os.path.exists(maybe_rel):
            return maybe_rel
        return os.path.join(GOV_BRIDGE_DOMAIN, maybe_rel)

    task_spec = load_yaml_file(args.task)
    ctx = taskctxmod.load(args.task)
    raw_queries = task_spec.get("queries")
    doc = instmod.load_query_set(_abs_path(raw_queries) if isinstance(raw_queries, str) else raw_queries)
    try:
        query = instmod.resolve_query(doc, args.query)
    except instmod.QueryNotExecutable as exc:
        print(json.dumps(exc.to_dict(), indent=1, sort_keys=True), file=sys.stderr)
        return 1

    view_path = args.view or (_abs_path(task_spec["view"]) if task_spec.get("view") else None)
    routes = real_routesmod.build_real_routes(view_path=view_path, registry_path=args.registry)

    result = gather_with_followup(
        query, routes, task=ctx, seeds=task_spec.get("seeds"), facet_names=args.facets,
        batch_size=args.batch_size, max_rounds=args.max_rounds, threads=args.threads, exclude=args.exclude,
        max_followup_rounds=args.max_followup_rounds, max_identifiers_per_round=args.max_identifiers_per_round,
        view_path=view_path,
    )
    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        t = result["telemetry"]
        print(f"query={result['query']['id']!r} facets={result['facets']} base_rounds={t['base_rounds']} "
              f"followup_rounds={t['followup_rounds']} stop_reason={result['stop_reason']} "
              f"merged_items={len(result['merged'])} merged_sha256={result['merged_sha256']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
