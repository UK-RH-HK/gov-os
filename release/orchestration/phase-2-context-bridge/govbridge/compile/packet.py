#!/usr/bin/env python3
"""The bounded context compiler: ``govbridge.compile.packet`` (ARCHITECTURE.md sections 5.3, 7; node B6,
BR-HO-0008). ``compile()`` is the ONLY place that fills ``Packet.section_a`` -- and it fills it with nothing but the
resolver's own ``MandatoryItem``s, checked with ``isinstance`` at insertion, exactly as ARCHITECTURE.md section 5.3
rule 1 requires. Every other section (B-J) is filled from route hits (``govbridge.route.router.RouteHit``, consumed
only through the ``RouteSet`` the caller supplies -- see ``govbridge.route.router``) and graph hops
(``govbridge.graph.why``/``.history``/``.traverse``, both real B5 dependencies), placed purely as a function of
authority class and lifecycle (``place_item`` below) -- **never** of which route found them or how they scored.

``validate.py`` (a separate module) recomputes the resolver from scratch and checks every claim this module makes
about section A and about ordering; it is imported BY this module's ``--verify`` self-check path and by
``receipt.py``/a grader, never the reverse.

BR-DAG-AMEND-R1-23 (ONE RESOLVED VIEW PER OPERATION): ``compile_packet`` resolves ``config/canonical-view.yaml``
exactly ONCE for its whole lifetime (reusing ``routes.resolved_view`` when the caller passed real routes --
``real_routes_for``'s own one resolution -- or resolving fresh only for a ``--fake-routes``/``FAKE_ROUTES``
compile, which never had a view of its own to reuse), then threads that ONE view into ``resolver.resolve``,
``Compiler`` (which threads it into ``registrymod.load``), every per-seed ``why()``/``history()`` call, and every
per-query ``RouteSet``/``gather_with_followup`` call (the main query loop and D.2's own "both ways" gather alike).
Previously this module made four-plus INDEPENDENT resolutions per compile; a "records" ref moving between any two
of them (this whole domain runs on a live, actively-committed-to orchestration branch) could make one compile's
own section A, its route hits, and its follow-up identifiers disagree about which commit they were even answering
from.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import sys
from typing import Optional

from govbridge import GOV_BRIDGE_DOMAIN
from govbridge.authority import classes as classesmod
from govbridge.authority import records as recordsmod
from govbridge.authority import registry as registrymod
from govbridge.authority import resolver as resolvermod
from govbridge.compile import budgets as budgetsmod
from govbridge.compile import codeseeds as codeseedsmod
from govbridge.compile import codesurfaces as codesurfacesmod
from govbridge.compile import overflow as overflowmod
from govbridge.compile import render as rendermod
from govbridge.compile import sectionmap as sectionmapmod
from govbridge.core import gitobj, store as storemod, view as viewmod
from govbridge.core import taskctx as taskctxmod
from govbridge.core.manifest import bridge_code_tree
from govbridge.core.yamlutil import canonical_json, load_yaml_file, sha256_text
from govbridge.gather import facets as facetsmod
from govbridge.gather import instantiate as instantiatemod
from govbridge.gather.followup import gather_with_followup
from govbridge.graph import history as historymod
from govbridge.graph import traverse as traversemod
from govbridge.graph import why as whymod
from govbridge.route import router as routermod
from govbridge.route.router import FAKE_ROUTES, RouteHit, RouteOccurrence, RouteSet

STATUS_OK = "OK"
STATUS_BLOCKED = "BLOCKED"
STATUS_BLOCKED_BUDGET = "BLOCKED_BUDGET"


class SectionAViolation(TypeError):
    """Raised when something that is not a resolver-produced ``MandatoryItem`` is inserted into section A
    (ARCHITECTURE.md section 5.3 rule 1: "Packet.section_a accepts only MandatoryItem, checked with isinstance").
    ``Compiler.add`` refuses section "A" outright; only ``Compiler.add_to_a`` may fill it, and it re-checks the
    isinstance itself."""

# non-ladder classes route to exactly one section depending on delivery (ARCHITECTURE.md section 7.2's table plus
# section 5.1's per-class "where it may appear" column). A class not listed here falls back to its own
# ClassSpec.allowed_sections[0] (FIXTURE/UNCLASSIFIED -> H).
NON_LADDER_PINNED_SECTION = {
    "OWNER_DIRECTION_TO_TEST": "D.2",
    "HYPOTHESIS_TO_TEST": "D.3",
    "HYPOTHESIS_RELEVANT_OBSERVATION": "F",
    "EVIDENCE_WITHDRAWN": "F",
}
NON_LADDER_RETRIEVED_SECTION = {
    "OWNER_DIRECTION_TO_TEST": "D.2",
    "HYPOTHESIS_TO_TEST": "D.3",
    "HYPOTHESIS_RELEVANT_OBSERVATION": "F",
    "EVIDENCE_WITHDRAWN": "E",
    "FIXTURE": "H",
    "UNCLASSIFIED": "H",
}

LIFECYCLE_BANNERS = {
    classesmod.LIFECYCLE_SUPERSEDED: "SUPERSEDED: a current record supersedes this one; never cite it as authority.",
    classesmod.LIFECYCLE_WITHDRAWN: "WITHDRAWN: retained as evidence of a withdrawn or retracted claim.",
    classesmod.LIFECYCLE_HISTORICAL: "HISTORICAL: retained for lineage; not the current version.",
    classesmod.LIFECYCLE_PROPOSED: "PROPOSED: not yet in force.",
    classesmod.LIFECYCLE_UNKNOWN: "UNKNOWN: lifecycle could not be determined; never treated as ACTIVE.",
}

DELIVERY_TIER = {"MANDATORY": 0, "PINNED": 0, "RETRIEVED": 1, "DERIVED": 1}

# BR-AR-0015 reopening, defect 2: section G's own deterministic tier order, never overridden by rank or volume --
# T1 (pinned) < T2 (direct callers/callees/TESTS/READS_KEY of T1) < T3 (lexical/semantic/code retrieval hits) <
# T4 (reserved for a wider expansion no current pipeline stage produces). A non-G item's ``tier`` is always None,
# which this maps to ONE shared constant below every real tier -- it never perturbs a non-G item's relative order
# against another non-G item (every non-G item shares the exact same tier_rank), only ever adds a new, low-order
# tie-breaker AFTER class rank/lifecycle/delivery, which is where the ordering invariant already lived.
_G_TIER_ORDER = ("T1", "T2", "T3", "T4")


# ---------------------------------------------------------------------------------------------------------------
# PacketItem: the one internal shape every section's rendered/manifest row is built from -- constructed from a
# MandatoryItem (delivery MANDATORY/PINNED) or from a RouteHit/graph Edge (delivery RETRIEVED/DERIVED). Never the
# reverse: nothing converts a PacketItem back into a MandatoryItem, and nothing here EVER sets delivery=MANDATORY or
# PINNED except the resolver-sourced constructors below.
# ---------------------------------------------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class PacketItem:
    unit_kind: str
    unit_id: str
    section: str  # "A".."J" or "D.1"/"D.2"/"D.3"
    delivery: str  # MANDATORY | PINNED | RETRIEVED | DERIVED
    cls: Optional[str]
    lifecycle: str
    version_status: Optional[str]
    ref: Optional[str]
    commit: Optional[str]
    path: Optional[str]
    blob: Optional[str]
    line_start: Optional[int]
    line_end: Optional[int]
    text: str
    content_sha256: Optional[str]
    by_reference: bool
    route: str  # exact | lexical | semantic | graph | code | resolver | state
    raw_score: Optional[float]
    rank: Optional[int]
    fused_score: Optional[float]
    edge_path: tuple
    reason: Optional[str]
    banner: Optional[str]
    # BR-AR-0015 reopening, defect 2: section G's own deterministic tier ("T1".."T4") and, defect 3, the
    # resolution label for HOW this item's own identity was matched (never inferred from route/rank/text --
    # ARCHITECTURE.md section 5.3 rule 5 still decides ordering by class/lifecycle first; tier/resolution only
    # ever refine the order WITHIN an already-equal (rank, lifecycle, delivery-tier) group, and bound G's own
    # budget dropping). None outside G.
    tier: Optional[str] = None
    resolution: Optional[str] = None
    # BR-DAG node R1-RM (REPAIR_PLAN.md section 3 rule 4): ``content_sha256`` above is left UNCHANGED (still the
    # resolver's own recorded hash for a MANDATORY item, verbatim -- validate.py's independent re-derivation keys
    # on it staying exactly that, field-for-field). ``source_sha256`` is that SAME value under its honest name;
    # ``delivered_sha256`` is the sha256 of what ``text`` ACTUALLY contains. For a RETRIEVED/DERIVED item, or a
    # MANDATORY item delivered in full, the two coincide; for a MANDATORY item delivered as a section map plus a
    # partial selection (``MANDATORY_PARTIAL_DELIVERY``), they legitimately differ -- which is exactly the
    # distinction a receipt must be able to draw ("the receipt acknowledges what was delivered", never content
    # that was never sent). None outside a MANDATORY item that this module has actually resolved.
    source_sha256: Optional[str] = None
    delivered_sha256: Optional[str] = None
    # BR-DAG-AMEND reopening ("packet verify cannot detect silent truncation"): declared_sha256/declared_bytes are
    # an INDEPENDENT third measurement -- the hash/byte-count of ``resolver.declared_regions(mi)``, i.e. exactly
    # what the row's own occurrence/selectors DECLARE, recomputable from Git alone. ``packet verify`` recomputes
    # this FRESH (never trusts the stored value) and only then checks delivered_sha256 == declared_sha256, or a
    # MANDATORY_PARTIAL_DELIVERY notice whose ranges exactly tile the declared regions. None for anything that
    # is not a mandatory item resolved from a real occurrence (a directory item, or an unreadable path).
    declared_sha256: Optional[str] = None
    declared_bytes: Optional[int] = None
    # BR-DAG node R1-RM (REPAIR_PLAN.md section 3 rule 3): a by-reference directory mandatory item's member
    # manifest, propagated from ``resolver.MandatoryItem.directory_members`` so it is visible in the rendered
    # manifest too (never guessed at by a downstream reader). Empty/False for everything else.
    is_directory: bool = False
    directory_members: tuple = ()
    # REPAIR_DAG node R1-GA3 (REPAIR_PLAN.md section 2.8, RC-4/RC-5): "per-item tags: the query ids and facets each
    # item serves, so an agent can find 'the tests for query X'". Empty for anything not produced by
    # ``govbridge.gather`` (a seed-derived B/C/F/G item, section A, I, J) -- ``Compiler.add`` UNIONS these tuples
    # in when the SAME unit id is placed again for a different query/facet, rather than silently keeping only the
    # first query/facet that happened to reach a section first.
    query_ids: tuple = ()
    facet_tags: tuple = ()
    item_id: str = dataclasses.field(init=False)

    def __post_init__(self):
        iid = hashlib.sha256(
            f"{self.unit_kind}\x1f{self.unit_id}\x1f{self.section}\x1f{self.delivery}".encode()
        ).hexdigest()[:24]
        object.__setattr__(self, "item_id", iid)

    def bytes_len(self) -> int:
        return len((self.text or "").encode("utf-8"))


def sort_key(item: PacketItem) -> tuple:
    """ARCHITECTURE.md section 5.3 rule 5: "(pinned first, authority rank ascending, lifecycle order ACTIVE <
    PROPOSED < HISTORICAL/SUPERSEDED < WITHDRAWN < UNKNOWN, then fused score)". Ascending on this tuple is
    "most important first"; fused score is negated so a HIGHER score sorts earlier.

    BR-AR-0015 reopening, defect 2: TWO more tie-breakers are inserted AFTER delivery-tier/rank/lifecycle and
    BEFORE fused score -- section G's own tier (g_tier_rank: T1 < T2 < T3 < T4) and, within a tier, EXACT
    resolutions before HEURISTIC ones (exact_rank). Both are constant (and equal) across every NON-G item, so
    they never move a B/C/D/E/F/H item relative to another one; they only ever refine G's own internal order,
    which is the one section ARCHITECTURE.md section 5.3 rule 5 never spoke to (G did not exist as a tiered
    section before this reopening)."""
    spec = classesmod.ALL_CLASSES.get(item.cls)
    rank = spec.rank if (spec is not None and spec.ladder) else len(classesmod.LADDER) + 1
    try:
        lc_idx = classesmod.LIFECYCLE_ORDER.index(item.lifecycle)
    except ValueError:
        lc_idx = len(classesmod.LIFECYCLE_ORDER) - 1
    tier = DELIVERY_TIER.get(item.delivery, 1)
    try:
        g_tier_rank = _G_TIER_ORDER.index(item.tier)
    except ValueError:
        g_tier_rank = len(_G_TIER_ORDER)  # None (every non-G item) or an unrecognised tier -- one shared constant
    resolution = item.resolution or ""
    exact_rank = 0 if resolution.startswith("EXACT") or resolution == "DIRECT_SEED" else (1 if resolution else 2)
    return (tier, rank, lc_idx, g_tier_rank, exact_rank, -(item.fused_score or 0.0), item.unit_kind, item.unit_id)


def _is_adjudication(unit_id: str, grammar) -> bool:
    if grammar is None:
        return False
    for name, pat in grammar.id_families:
        if name == "adjudication" and pat.search(unit_id):
            return True
    return False


def d1_eligible(cls: Optional[str], lifecycle: str, unit_id: str, grammar) -> bool:
    if lifecycle != classesmod.LIFECYCLE_ACTIVE:
        return False
    if cls in ("OWNER_DECISION", "ARCHITECTURE_DECISION"):
        return True
    if cls == "ORCHESTRATION_RECORD" and _is_adjudication(unit_id, grammar):
        return True
    return False


def delivery_for_mandatory(cls: Optional[str]) -> str:
    """A resolver-sourced item is delivery MANDATORY when its class is ladder-admissible, and PINNED otherwise
    (ARCHITECTURE.md section 7.2: "mandatory but non-authoritative items... are PINNED"). The ONE place this
    decision is made, so ``place_item`` and ``item_from_mandatory`` never disagree about it."""
    spec = classesmod.ALL_CLASSES.get(cls)
    return "MANDATORY" if (spec is not None and spec.ladder) else "PINNED"


def place_item(cls: Optional[str], lifecycle: str, delivery: str, unit_id: str, grammar) -> tuple:
    """Where a (class, lifecycle, delivery) combination belongs, purely from the class table (ARCHITECTURE.md
    section 5.1/5.3) -- NEVER from route, rank or score. Returns ``(section, also_d1)``; ``also_d1`` is True only
    for a MANDATORY, D.1-eligible item already placed in A (its D.1 appearance is a reference, not a duplicate --
    see ``_reference_item``).

    BR-ARCH-RULING-1: section A membership is decided by the resolver together with the class's admissibility in
    A -- lifecycle never decides it. A resolver-returned (``delivery == "MANDATORY"``) item whose class is
    A-admissible goes to A **whatever its lifecycle**; a non-ACTIVE lifecycle stays visible via the item's banner
    (``Compiler.item_from_mandatory``) and a J notice (``compile_packet``), never by being moved out of A or
    relabelled ACTIVE. Lifecycle still gates D.1 (``d1_eligible`` below requires ACTIVE) and the E fallback, which
    applies only to RETRIEVED/DERIVED items now that MANDATORY no longer reaches it for an A-admissible class."""
    spec = classesmod.ALL_CLASSES.get(cls)
    if spec is None:
        return "H", False
    if not spec.ladder:
        table = NON_LADDER_PINNED_SECTION if delivery == "PINNED" else NON_LADDER_RETRIEVED_SECTION
        section = table.get(cls) or (spec.allowed_sections[0] if spec.allowed_sections else "H")
        return section, False

    if delivery == "MANDATORY" and spec.admissible_in_a:
        return "A", d1_eligible(cls, lifecycle, unit_id, grammar)
    if d1_eligible(cls, lifecycle, unit_id, grammar):
        return "D.1", False
    if lifecycle in (classesmod.LIFECYCLE_SUPERSEDED, classesmod.LIFECYCLE_HISTORICAL,
                      classesmod.LIFECYCLE_WITHDRAWN, classesmod.LIFECYCLE_PROPOSED):
        return "E", False
    return "H", False


def g_admissible(cls: Optional[str]) -> bool:
    """Whether a RETRIEVED/DERIVED item of ``cls`` may be redirected from H into G (BR-HO-0015 defect 3). Every
    NON-LADDER class carries a FIXED ``allowed_sections`` (ARCHITECTURE.md section 5.1) that never names G --
    ``UNCLASSIFIED``/``FIXTURE`` are H-only by construction -- so redirecting one into G would be an admissibility
    violation ``validate.py``'s independent re-derivation correctly refuses (``verify_placement``'s non-ladder
    branch). A LADDER class (e.g. ``EVIDENCE``, product code/tests' usual class) carries no such restriction
    (``ClassSpec.allowed_sections == ()`` means "any admissible section"), so the redirect applies only there."""
    spec = classesmod.ALL_CLASSES.get(cls)
    return spec is not None and spec.ladder


def _abs_path(maybe_rel: str) -> str:
    if os.path.isabs(maybe_rel):
        return maybe_rel
    if os.path.exists(maybe_rel):
        return maybe_rel
    return os.path.join(GOV_BRIDGE_DOMAIN, maybe_rel)


def _hit_from_merged(md: dict) -> RouteHit:
    """One row of ``gather_with_followup(...)["merged"]`` (``govbridge.gather.merge.MergedItem.to_dict()``) as a
    ``govbridge.route.router.RouteHit`` -- so the existing ``item_from_hit``/``FusedHit`` machinery this module
    already uses for a plain route hit needs no second construction path for gather's richer, provenance-bearing
    shape. ``md["occurrence"]`` is already a ``RouteOccurrence.to_dict()`` (the canonical occurrence gather's own
    merge step already chose -- ``govbridge.gather.merge.collapse_occurrences``), so this is a lossless, direct
    round-trip, never a re-derivation."""
    occ_d = md.get("occurrence")
    occs = (RouteOccurrence(**occ_d),) if occ_d else ()
    return RouteHit(unit_id=md.get("unit_id"), unit_kind=md.get("unit_kind"), route=md.get("route") or "gather",
                     rank=1, delivery=md.get("delivery") or "RETRIEVED", occurrences=occs, text=md.get("text"),
                     authority_class=md.get("authority_class"), lifecycle=md.get("lifecycle"), edge_path=(),
                     tier=md.get("tier"), resolution=md.get("resolution"))


def _read_excerpt(path: str, commit: str, l1: Optional[int], l2: Optional[int],
                   repo: Optional[str] = None, max_chars: Optional[int] = 4000) -> Optional[str]:
    """The text of ``path``@``commit`` (or lines ``l1``-``l2`` of it), or None if there is nothing to read -- a
    directory entry (a MandatoryItem's ``path`` may be a directory: resolver.py's own is_directory case carries
    no text), a missing object, or a decode failure. None is the honest, generic "no excerpt" result; the caller
    falls back to a reference note, never a crash.

    ``max_chars`` is a DISCLOSED excerpt cap for RETRIEVED/DERIVED callers only (``Compiler.item_from_edge_hop``;
    ``item_from_hit`` does not call this at all -- a route hit's own text is already bounded upstream). BR-DAG
    node R1-RM (REPAIR_PLAN.md section 3 rule 1, "no silent truncation"): a MANDATORY item is NEVER read through
    this default -- ``Compiler._mandatory_text`` always passes ``max_chars=None`` here, so a mandatory item's own
    excerpt is never silently cut by this function; an oversize mandatory item instead gets a section map plus a
    disclosed remainder (``Compiler._render_oversize_no_selector``), never a bare truncated string."""
    try:
        raw = gitobj.read_path(commit, path, repo=repo)
    except gitobj.GitError:
        return None
    if raw is None:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if l1 is not None:
        lines = text.splitlines(keepends=True)
        l2 = l2 or l1
        text = "".join(lines[max(l1 - 1, 0):l2])
    if max_chars is None:
        return text
    return text[:max_chars]


class Compiler:
    """Holds the per-compile context (repo, view, registry, grammar) so every ``_item_from_*`` helper can stay a
    short, testable method instead of a closure threading five arguments through."""

    def __init__(self, task_spec: dict, routes: RouteSet, repo: Optional[str], view_path: str,
                 registry_path: Optional[str], rrf_k: int, graph_depth: int, budgets_path: Optional[str] = None,
                 fanout: Optional[dict] = None, per_item_cap_bytes: Optional[int] = None,
                 max_slice_chars: Optional[int] = None, top_n: Optional[int] = None,
                 facets_path: Optional[str] = None,
                 resolved_view: Optional["viewmod.ResolvedView"] = None):
        self.task_spec = task_spec
        # BR-DAG node R1-RM: the same per-item cap ARCHITECTURE.md section 7.3 already names (24 KB by default,
        # config/budgets.yaml) decides when a MANDATORY item's own content is "oversize" enough to need a section
        # map instead of full delivery (REPAIR_PLAN.md section 3 rule 1/5: "a larger cap is not a fix"). Defaulted
        # so an existing direct ``Compiler(...)`` construction (a pre-reopening test) keeps working unmodified.
        self.per_item_cap_bytes = per_item_cap_bytes if per_item_cap_bytes is not None else 24 * 1024
        self.routes = routes or FAKE_ROUTES
        self.repo = repo
        self.view_path = view_path
        # BR-DAG-AMEND-R1-23: reuse the caller's own ONE resolution (compile_packet's own top-level
        # resolved_view, itself often routes.resolved_view) instead of a second, independent one here --
        # resolved_view=None (the default) preserves this exact fresh-resolution behaviour for a Compiler built
        # directly (a pre-reopening test, or any caller outside compile_packet's own top-level function).
        self.resolved_view = resolved_view if resolved_view is not None else \
            viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)
        self.registry_path = registry_path or registrymod._default_registry_path()
        self.reg = registrymod.load(self.registry_path, verify_commit="records", view_path=view_path, repo=repo,
                                     resolved_view=self.resolved_view)
        self.grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
        self.rrf_k = rrf_k
        self.graph_depth = graph_depth
        # BR-AR-0015 reopening, defect 2: per-symbol fan-out caps for G's T2 expansion (callers/callees/TESTS/
        # READS_KEY), read from the budget profile ("fan-out caps from the profile") -- defaults to the real
        # code_route adapter's own generous fallback when the caller gives none (e.g. an existing test that
        # predates this reopening).
        self.fanout = fanout or {}
        # REPAIR_DAG node R1-GA3 (REPAIR_PLAN.md section 2.8, RC-5): "content slices... up to max_slice_chars
        # (1,600), with a larger slice for the facet's top items" -- the SAME config/budgets.yaml value every
        # profile already carries (previously read only by govbridge.gather.followup's own hard-coded mirror of
        # it; this is the compiler's own copy, defaulted so an existing direct ``Compiler(...)`` construction that
        # predates this node keeps working unmodified).
        self.max_slice_chars = max_slice_chars if max_slice_chars is not None else 1600
        self.top_n = top_n if top_n is not None else 3
        self.facets_path = facets_path
        # R1-RX (OBS-BR-08, RC-8): the task's own retrieval_exclusions, PLUS whatever the ambient task context
        # (GOVBRIDGE_TASK / --task, govbridge.core.taskctx) additionally names -- one merged list, used by every
        # c.routes.run(...) call site below, never just the query loop. exclusion_counter accumulates how many
        # candidate hits every such call excluded, for the single J-notice disclosure at the end of compile_packet.
        self.task_ctx = taskctxmod.TaskContext(
            source="task_spec", retrieval_exclusions=tuple(task_spec.get("retrieval_exclusions") or ()))
        self.exclusions = self.task_ctx.merge_exclude(taskctxmod.current().retrieval_exclusions)
        self.exclusion_counter = taskctxmod.ExclusionCounter()
        self.notices: list = []
        self._seen: dict = {}  # section -> set(unit_id) -- prevents literal duplicate placement
        self._code_conn_cache = None
        self._code_conn_attempted = False
        self._product_commit_cache = None
        self._product_commit_attempted = False
        # BR-HO-0015 defect 3 (G row): the small, versioned config list that decides whether a RETRIEVED/DERIVED
        # item whose occurrence is product code or a test lands in G instead of H -- loaded once, from the SAME
        # budgets.yaml the profile itself comes from (falls back to the default path when the caller used the
        # default profile loader too).
        try:
            self.code_surface_rules = codesurfacesmod.load_rules(budgets_path)
        except Exception:
            self.code_surface_rules = codesurfacesmod.EMPTY_RULES

    def product_commit(self) -> Optional[str]:
        """The canonical PRODUCT ref's commit (``role: product`` in config/canonical-view.yaml, resolved by ROLE,
        never a hard-coded ref name -- OC-BR-02), cached for the whole compile. None (honest MISSING) if this view
        names no product-role ref."""
        if self._product_commit_attempted:
            return self._product_commit_cache
        self._product_commit_attempted = True
        for r in self.resolved_view.config.refs:
            if r.role == "product" and r.name in self.resolved_view.named:
                self._product_commit_cache = self.resolved_view.named[r.name].commit
                break
        return self._product_commit_cache

    def code_conn(self):
        """The shaped code-route connection (``govbridge.graph.code_bridge``) for the canonical PRODUCT ref
        (ARCHITECTURE.md section 4/7.2: "the code route at the canonical product ref"), built once per compile
        and reused for every seed -- routed issue B5/BR-AR-0007 ("wire [CALLS/READS_KEY/TESTS] against the real
        B3 tables, so why/impact reach code"). Returns None (honest MISSING, never an error) if there is no
        product-role ref in this view, or the code route itself is unavailable."""
        if self._code_conn_attempted:
            return self._code_conn_cache
        self._code_conn_attempted = True
        try:
            from govbridge.graph import code_bridge
            product_commit = self.product_commit()
            if product_commit:
                self._code_conn_cache = code_bridge.build_shaped_code_connection(product_commit, repo=self.repo)
        except Exception:
            self._code_conn_cache = None
        return self._code_conn_cache

    def code_seeds_for(self, seed: str) -> tuple:
        """Derives extra code-route symbol names and bare (no-enclosing-symbol) occurrences from ``seed`` when it
        names a RECORD rather than a code symbol directly (BR-HO-0015 defect 1: "nothing derives seed symbols from
        record seeds"). Returns ``(seed_names, seed_labels, bare_occurrences)`` -- ``seed_names`` always starts
        with ``seed`` itself (so a seed that already IS a symbol name keeps working exactly as before);
        ``seed_labels`` maps a derived name to how its citation was resolved; ``bare_occurrences`` is the
        ``code_route`` ``RouteFn``'s own dict shape. Honest MISSING (``([seed], {}, [])``) on any failure -- a
        record-citation scan must never break the seed pass's existing why/history/traverse/code hops."""
        seed_names = [seed]
        seed_labels: dict = {}
        bare_occurrences: list = []
        try:
            records_commit = self.resolved_view.ref_commit("records")
            product_commit = self.product_commit()
            if records_commit and product_commit:
                symbols_cited, occs_cited = codeseedsmod.cited_code_units(
                    seed, product_commit, records_commit, self.grammar, repo=self.repo)
                for sym in symbols_cited:
                    if sym.name not in seed_names:
                        seed_names.append(sym.name)
                    seed_labels[sym.name] = sym.label
                for occ in occs_cited:
                    bare_occurrences.append({"path": occ.path, "line": occ.line, "label": occ.label})
        except Exception:
            return [seed], {}, []
        return seed_names, seed_labels, bare_occurrences

    # -- construction from a MandatoryItem (delivery MANDATORY, or PINNED when its class is non-ladder) ----------

    def item_from_mandatory(self, mi: resolvermod.MandatoryItem, section: str) -> PacketItem:
        assert isinstance(mi, resolvermod.MandatoryItem)  # section 5.3 rule 1, enforced again at packet assembly
        spec = classesmod.ALL_CLASSES.get(mi.cls)
        delivery = delivery_for_mandatory(mi.cls)
        banner = spec.banner if spec is not None else None
        if section == "A" and mi.lifecycle != classesmod.LIFECYCLE_ACTIVE:
            # BR-ARCH-RULING-1 rule 2: "lifecycle stays visible and honest" -- a mandatory A item whose lifecycle
            # is not ACTIVE carries the same lifecycle banner a RETRIEVED item would (LIFECYCLE_BANNERS, used by
            # item_from_hit below). A ladder class never has its own class banner (spec.banner is None for every
            # LADDER row), so this never overwrites one -- it only ever replaces None.
            banner = LIFECYCLE_BANNERS.get(mi.lifecycle, banner)

        # declared_parts/declared_sha256 are the INDEPENDENT third measurement the BR-DAG-AMEND reopening asks
        # for: "the hash of exactly what the row declares" (whole file, anchored slice, or the ordered selector
        # parts), computed BEFORE `text` is built so `packet verify` has a ground truth that never depends on
        # this module's own rendering. See resolver.declared_parts's docstring for the three shapes.
        dparts = resolvermod.declared_parts(mi, repo=self.repo)
        declared_sha256, declared_bytes = resolvermod.declared_hash_and_bytes(dparts)
        text, delivered_sha256 = self._mandatory_text(mi, dparts)
        # source_sha256 is the resolver's OWN recorded hash, verbatim -- never a hash of this module's rendered
        # text (a directory-form item legitimately carries sha256=None; validate.py's independent re-derivation
        # compares content_sha256 against the freshly recomputed MandatoryItem field-for-field, so it must never
        # diverge from what the resolver itself reported).
        source_sha256 = mi.sha256
        return PacketItem(unit_kind="record", unit_id=mi.id, section=section, delivery=delivery, cls=mi.cls,
                           lifecycle=mi.lifecycle, version_status=None, ref=None, commit=mi.commit, path=mi.path,
                           blob=mi.blob, line_start=mi.line_start, line_end=mi.line_end, text=text,
                           content_sha256=source_sha256, by_reference=False, route="resolver", raw_score=None,
                           rank=None, fused_score=None, edge_path=(), reason=mi.reason, banner=banner,
                           source_sha256=source_sha256, delivered_sha256=delivered_sha256,
                           declared_sha256=declared_sha256, declared_bytes=declared_bytes,
                           is_directory=mi.is_directory, directory_members=mi.directory_members)

    # -- mandatory-item TEXT (BR-DAG node R1-RM, REPAIR_PLAN.md section 3): never a silent cut ------------------

    def _mandatory_text(self, mi: resolvermod.MandatoryItem, dparts: tuple) -> tuple:
        """``(text, delivered_sha256)``. ``text`` is the full body a MANDATORY item delivers -- exactly one of
        three shapes, and every one of them ends cleanly (never mid-content with no marker):

        * a directory item's member manifest (rule 3) -- always its own complete representation; delivered_sha256
          is None (its "declared" form is the member manifest, not a text body -- see ``declared_parts``);
        * a row with resolved ``parts`` (rule 2's ``keys``/``entries``/extra-``paths`` selectors) -- every part
          delivered in FULL; delivered_sha256 is ``resolver.hash_pieces`` over exactly those parts' own raw text,
          which is IDENTICAL, byte for byte, to how ``declared_sha256`` was computed from the SAME ``dparts`` --
          so delivered always equals declared here, by construction (a selector narrows what is DECLARED, not
          what is delivered of it);
        * the plain occurrence's own text -- delivered whole (delivered_sha256 == declared_sha256, the same
          ``hash_pieces`` scheme) when it fits the per-item cap, else a section map (rule 1) plus a
          ``MANDATORY_PARTIAL_DELIVERY`` notice and delivered_sha256 = None (nothing raw was sent; ``packet
          verify`` must find the notice and check its ranges tile the declared span -- see ``validate.py``).
        """
        if mi.is_directory:
            # the member manifest text IS the complete, honest representation of a directory item -- never
            # "partial" in the rule-1 sense -- so its delivered_sha256 mirrors source_sha256 (both independently
            # derived from the SAME member list; resolver.py's docstring on the directory sha256 derivation).
            return self._render_directory_manifest(mi), mi.sha256

        if not dparts:
            loc = f"{mi.path}@{mi.commit}"
            if mi.line_start is not None:
                loc += f":{mi.line_start}-{mi.line_end}"
            return f"[reference only: {loc}]", None

        if mi.parts:
            return self._render_selected_parts(mi, dparts)

        primary = dparts[0]
        if primary["bytes"] <= self.per_item_cap_bytes:
            return primary["text"], resolvermod.hash_pieces([primary["text"]])

        return self._render_oversize_no_selector(mi, primary)

    def _render_directory_manifest(self, mi: resolvermod.MandatoryItem) -> str:
        lines = [f"[directory manifest: {mi.path}@{mi.commit} -- {len(mi.directory_members)} member(s), by "
                 f"reference (REPAIR_PLAN.md section 3 rule 3); read any member by its exact path@commit/blob]"]
        for m in mi.directory_members:
            size = m.get("size")
            lines.append(f"- {m['path']}  (blob={m['blob']}, size={size if size is not None else 'unknown'}, "
                          f"class={m['cls']})")
        if not mi.directory_members:
            lines.append("(no tracked files under this directory at this commit)")
        return "\n".join(lines) + "\n"

    def _render_selected_parts(self, mi: resolvermod.MandatoryItem, dparts: tuple) -> tuple:
        pieces = [f"[selected: {len(dparts)} part(s) of {mi.path}@{mi.commit}, honouring the declared selector(s) "
                  f"verbatim (REPAIR_PLAN.md section 3 rule 2)]"]
        for part in dparts:
            loc = f"{part['path']}@{part['commit']}:{part['line_start']}-{part['line_end']}"
            pieces.append(f"--- {part['name']}  ({loc}) ---")
            pieces.append(part["text"])
        delivered_sha256 = resolvermod.hash_pieces([p["text"] for p in dparts])

        # a `keys`/`entries` selector narrows the PRIMARY occurrence itself -- disclose what else exists in it,
        # informationally (REPAIR_PLAN.md section 3's "declared selectors honoured" transparency). This notice is
        # never required for `packet verify` to PASS this item (delivered_sha256 == declared_sha256 already,
        # since dparts IS exactly what was declared): it is read-for-humans context, not a fidelity gate. A
        # `paths`-only row narrows nothing (every declared path is already delivered above in full), so there is
        # no "remainder" to disclose.
        narrowing_parts = [p for p in mi.parts if p["kind"] in ("keys", "entries")]
        if narrowing_parts and mi.line_start is None and mi.path is not None and mi.commit is not None:
            full = _read_excerpt(mi.path, mi.commit, None, None, repo=self.repo, max_chars=None)
            if full is not None:
                under = resolvermod._entries_under_from_parts(mi.parts)
                whole = sectionmapmod.flat_tiling(full, mi.path, entries_under=under,
                                                   id_patterns=resolvermod.ID_MENTION_REGEXES)
                delivered_names = {p["name"] for p in narrowing_parts}
                undelivered = [s for s in whole if s.name not in delivered_names]
                if undelivered:
                    self.notices.append({
                        "type": "MANDATORY_PARTIAL_DELIVERY", "id": mi.id, "path": mi.path, "commit": mi.commit,
                        "section_map": [s.to_dict() for s in whole],
                        "delivered": [{"name": p["name"], "line_start": p["line_start"], "line_end": p["line_end"],
                                       "sha256": p["sha256"]} for p in dparts],
                        "undelivered_ranges": [{"name": s.name, "line_start": s.line_start,
                                                 "line_end": s.line_end, "sha256": s.sha256} for s in undelivered],
                    })
        return "\n".join(pieces) + "\n", delivered_sha256

    def _render_oversize_no_selector(self, mi: resolvermod.MandatoryItem, primary: dict) -> tuple:
        """BR-DAG-AMEND-R1-11 (routing of R1-RM's own MET_WITH_DISCLOSED_LIMIT row): R1-RM could only ever disclose
        this item's sections BY REFERENCE, because no facet system existed yet in its own wave (R1-GA1 built it).
        This node additionally DELIVERS IN FULL whichever sections the gather facet vocabulary
        (``govbridge.compile.overflow.select_oversize_facet_sections``) scores as relevant -- a PURE function of
        the document's own content and the (default, versioned) facet registry alone, so
        ``govbridge.compile.validate``'s blind re-derivation (``_composition_context_class``, which supplies no
        task or query set at all) reproduces the exact same selection and therefore the exact same body, byte for
        byte. Nothing is ever removed from A; every un-selected section stays exactly the by-reference row it
        already was (REPAIR_PLAN.md section 3 rule 1's own coverage/tiling notice is unchanged in shape -- only
        some of its rows move from ``undelivered_ranges`` into ``delivered``, with their own real content now
        also printed above, inline)."""
        disclosure = resolvermod.oversize_disclosure_map(mi, repo=self.repo)
        lines = [f"[section map: {mi.path}@{mi.commit} exceeds the {self.per_item_cap_bytes}-byte per-item cap; "
                 f"every section below is delivered BY REFERENCE unless marked DELIVERED IN FULL -- read a "
                 f"by-reference section by its exact line range and verify its own sha256 (REPAIR_PLAN.md section "
                 f"3 rule 1: never a silent, unmarked cut)]"]
        delivered_rows: list = []
        if disclosure:
            selected, remaining = overflowmod.select_oversize_facet_sections(disclosure)
            for r in selected:
                text = _read_excerpt(r["path"], r["commit"], r["line_start"], r["line_end"], repo=self.repo,
                                      max_chars=None)
                if text is None:
                    remaining = list(remaining) + [r]  # could not actually be re-read -- falls back, disclosed
                    continue
                lines.append(f"- {r['name']}  lines {r['line_start']}-{r['line_end']}  sha256={r['sha256']}  "
                              f"[DELIVERED IN FULL -- selected by the gather facet vocabulary]")
                lines.append(f"--- {r['name']} ---")
                lines.append(text.rstrip("\n"))
                delivered_rows.append(dict(r))
            for r in sorted(remaining, key=lambda row: (row["line_start"] if row["line_start"] is not None else 0)):
                lines.append(f"- {r['name']}  lines {r['line_start']}-{r['line_end']}  sha256={r['sha256']}")
            undelivered = [dict(r) for r in remaining]
        else:
            lines.append("- (no structural map available for this format; read the whole item by exact reference)")
            undelivered = [{"path": primary["path"], "commit": primary["commit"],
                            "line_start": primary["line_start"], "line_end": primary["line_end"],
                            "name": "(whole item)", "sha256": primary["sha256"], "bytes": primary["bytes"]}]
        # REPAIR_DAG node R1-GA3 real-view finding (CONTROL-A: a 132-section oversize mandatory item): the
        # notice's own "section_map" field this compiler used to carry (every disclosure row a SECOND time, on
        # top of "delivered"/"undelivered_ranges", which already partition that exact same set) is dead weight --
        # `governbridge.compile.validate.verify_declared_and_delivered`'s tiling check reads only "delivered" and
        # "undelivered_ranges" (confirmed by reading it directly, and by grep: nothing anywhere reads
        # notice["section_map"]), and every disclosed name/range/sha256 is ALSO already printed, human-readably,
        # in this item's own rendered body above. A real oversize mandatory item's own J section (PINNED, never
        # budget-dropped) was measured at 76,978 bytes for this ONE notice alone before this fix (CONTROL-A's
        # real contract_v3, 132 structural sections) -- material against "the main packet is within the profile
        # total". Replaced with a compact summary (count + a digest over the sorted names), the same "verification
        # stays possible, the rendered/manifest copy stops being triplicated" discipline BR-AR-0015's own
        # ``budgets.compact_drops`` already established for G's own oversized drop lists.
        section_map_summary = {
            "count": len(disclosure) if disclosure else len(undelivered),
            "names_sha256": sha256_text("\n".join(sorted(r["name"] for r in disclosure))) if disclosure else None,
        }
        self.notices.append({
            "type": "MANDATORY_PARTIAL_DELIVERY", "id": mi.id, "path": mi.path, "commit": mi.commit,
            "section_map_summary": section_map_summary,
            "delivered": delivered_rows, "undelivered_ranges": undelivered,
        })
        # BR-DAG-AMEND-R1-11's newly-delivered sections above are still never HASHED as "the item's delivered
        # body" -- delivered_sha256 stays None so `packet verify` is forced onto the coverage/tiling check (2b),
        # which now legitimately covers a MIX of full-text and by-reference rows, rather than a whole-body hash
        # comparison that could never pass for a partially-delivered item.
        return "\n".join(lines) + "\n", None

    def reference_item(self, source: PacketItem, section: str) -> PacketItem:
        """A cheap D.1 pointer to an item already fully rendered in A (never a second copy of its content --
        ARCHITECTURE.md section 7.2's "if a record is already in A, [it is referenced] by item id rather than
        duplicating it", applied here to D.1 for the same economy)."""
        return PacketItem(unit_kind=source.unit_kind, unit_id=source.unit_id, section=section,
                           delivery=source.delivery, cls=source.cls, lifecycle=source.lifecycle,
                           version_status=source.version_status, ref=source.ref, commit=source.commit,
                           path=source.path, blob=source.blob, line_start=source.line_start,
                           line_end=source.line_end, text=f"[see A: {source.item_id} ({source.unit_id})]",
                           content_sha256=source.content_sha256, by_reference=True, route=source.route,
                           raw_score=None, rank=None, fused_score=None, edge_path=(), reason="already in A",
                           banner=None, source_sha256=source.source_sha256, delivered_sha256=source.delivered_sha256,
                           is_directory=source.is_directory, directory_members=source.directory_members)

    def reference_to_a_item(self, a_item: PacketItem, section: str, query_ids: tuple = (),
                             facet_tags: tuple = ()) -> PacketItem:
        """REPAIR_PLAN.md section 2.8: "content already present is cited by item id". A gather hit whose unit id
        this compile ALREADY placed in section A is never duplicated into B-H a second time -- it is cited here
        instead, by ``a_item.item_id``, so the packet still records that query/facet as having touched it (the
        tag), without a second copy of its body. Deliberately RETRIEVED/UNCLASSIFIED here (never A's own
        MANDATORY/PINNED delivery or class): this pointer is an ordinary, droppable B-H row, not a second
        authoritative entry, so it never inherits A's budget exemption."""
        return PacketItem(unit_kind=a_item.unit_kind, unit_id=a_item.unit_id, section=section,
                           delivery="RETRIEVED", cls=None, lifecycle=classesmod.LIFECYCLE_UNKNOWN,
                           version_status=a_item.version_status, ref=a_item.ref, commit=a_item.commit,
                           path=a_item.path, blob=a_item.blob, line_start=a_item.line_start,
                           line_end=a_item.line_end, text=f"[see A: {a_item.item_id} ({a_item.unit_id})]",
                           content_sha256=a_item.content_sha256, by_reference=True, route="resolver",
                           raw_score=None, rank=None, fused_score=None, edge_path=(),
                           reason="content already delivered in section A", banner=None,
                           source_sha256=a_item.source_sha256, delivered_sha256=a_item.delivered_sha256,
                           query_ids=tuple(sorted(set(query_ids))), facet_tags=tuple(sorted(set(facet_tags))))

    # -- construction from a route hit (delivery RETRIEVED/DERIVED) -------------------------------------------

    def item_from_hit(self, fused: "routermod.FusedHit", section: str, facet_tags: tuple = (),
                       query_ids: tuple = (), top: bool = False) -> PacketItem:
        """``facet_tags``/``query_ids`` (REPAIR_DAG node R1-GA3, REPAIR_PLAN.md section 2.8): "per-item tags: the
        query ids and facets each item serves" -- both default to ``()`` so every pre-existing caller (the seed
        why/history/traverse/code loop, ``_attach_evidence_both_ways``'s pre-gather callers) is unaffected. ``top``
        (REPAIR_PLAN.md section 2.8, RC-5): "a larger slice for the facet's top items" -- doubles this item's own
        content-slice cap.

        RC-5 ("pointer-only delivery"): a code-route hit's own ``text`` is a bare signature or edge label
        (``govbridge.route.real_routes``, not this node's file to edit); a semantic-route hit carries no text at
        all. ``govbridge.compile.overflow.needs_content_slice`` recognises both shapes; when it does, this method
        reads the item's own definition/context body FRESH from Git (``overflow.read_content_slice``) and appends
        it below the original pointer line (kept as a one-line header -- never discarded, since it names the kind/
        qualified name or the edge's own label) -- an honest MISSING (the pointer alone, unchanged) if Git cannot
        supply it."""
        h = fused.hit
        occ = h.occurrences[0] if h.occurrences else None
        lifecycle = h.lifecycle or classesmod.LIFECYCLE_UNKNOWN
        banner = LIFECYCLE_BANNERS.get(lifecycle) if lifecycle != classesmod.LIFECYCLE_ACTIVE else None
        text = h.text or ""
        if occ is not None and overflowmod.needs_content_slice(h.unit_kind, h.route, text):
            pad = 0 if h.unit_kind == "symbol" else 3
            cap = self.max_slice_chars * (2 if top else 1)
            fetched = overflowmod.read_content_slice(occ.path, occ.commit, occ.line_start, occ.line_end,
                                                       self.repo, cap, pad=pad)
            if fetched:
                text = f"{text}\n{fetched}" if text else fetched
        # a RETRIEVED/DERIVED hit has no separate "source" to diverge from -- content_sha256 already hashes
        # exactly the bytes delivered, so source_sha256/delivered_sha256 both mirror it (BR-DAG node R1-RM: the
        # delivered-vs-source distinction only ever BITES for a MANDATORY item; see item_from_mandatory).
        content_sha256 = sha256_text(text) if text else None
        return PacketItem(unit_kind=h.unit_kind, unit_id=h.unit_id, section=section, delivery=h.delivery,
                           cls=h.authority_class, lifecycle=lifecycle,
                           version_status=occ.version_status if occ else None, ref=occ.ref if occ else None,
                           commit=occ.commit if occ else None, path=occ.path if occ else None, blob=None,
                           line_start=occ.line_start if occ else None, line_end=occ.line_end if occ else None,
                           text=text, content_sha256=content_sha256, by_reference=False,
                           route=h.route, raw_score=None, rank=h.rank, fused_score=fused.fused_score,
                           edge_path=tuple(h.edge_path), reason=None, banner=banner,
                           tier=getattr(h, "tier", None), resolution=getattr(h, "resolution", None),
                           source_sha256=content_sha256, delivered_sha256=content_sha256,
                           query_ids=tuple(sorted(set(query_ids))), facet_tags=tuple(sorted(set(facet_tags))))

    # -- construction from a graph.why/history Edge hop (delivery DERIVED) --------------------------------------

    def item_from_edge_hop(self, stage_or_kind: str, edge: dict, section: str) -> PacketItem:
        occ = edge.get("evidence_occurrence") or ""
        path, _, rest = occ.partition("@")
        commit, line = None, edge.get("evidence_line")
        if rest:
            commit = rest.split(":", 1)[0]
        text = _read_excerpt(path, commit, line, line, repo=self.repo) if (path and commit) else None
        unit_id = f"{edge.get('type')}:{edge.get('dst')}"
        body = (text or "")[:2000]
        content_sha256 = sha256_text(body) if body else None
        return PacketItem(unit_kind="occurrence", unit_id=unit_id, section=section, delivery="DERIVED", cls=None,
                           lifecycle=classesmod.LIFECYCLE_UNKNOWN, version_status=None, ref=None, commit=commit,
                           path=path or None, blob=None, line_start=line, line_end=line, text=body,
                           content_sha256=content_sha256, by_reference=False, route="graph",
                           raw_score=None, rank=None, fused_score=None, edge_path=(edge,),
                           reason=f"{stage_or_kind}: {edge.get('derivation')}", banner=None,
                           source_sha256=content_sha256, delivered_sha256=content_sha256)

    # -- placement, with dedup ------------------------------------------------------------------------------------

    def add(self, sections: dict, section: str, item: PacketItem) -> Optional[PacketItem]:
        """Appends ``item`` to ``sections[section]`` unless its unit id is already present there. Section A is
        NEVER accepted here -- ARCHITECTURE.md section 5.3 rule 1 ("Packet.section_a accepts only MandatoryItem,
        checked with isinstance") is enforced by routing every A-bound item through ``add_to_a`` instead, which is
        the only method that ever appends to ``sections["A"]``. Returns the item actually stored, or None if it
        was a duplicate (never stored).

        REPAIR_DAG node R1-GA3: a duplicate is never a pure no-op when it carries a NEW ``query_ids``/
        ``facet_tags`` value -- the already-stored item is replaced IN PLACE (same position, same text/placement/
        score -- ``dataclasses.replace`` touches only these two fields) by the UNION of both tuples, so an item
        two different queries or facets both surface keeps every one of its tags rather than silently keeping only
        whichever query/facet reached this section first."""
        if section == "A":
            raise SectionAViolation(
                f"section A must be filled through Compiler.add_to_a, never Compiler.add -- refused "
                f"{item.unit_kind}:{item.unit_id} (delivery={item.delivery}, route={item.route})")
        seen = self._seen.setdefault(section, set())
        if item.unit_id in seen:
            if item.query_ids or item.facet_tags:
                lst = sections.get(section) or []
                for i, existing in enumerate(lst):
                    if existing.unit_id != item.unit_id:
                        continue
                    merged_q = tuple(sorted(set(existing.query_ids) | set(item.query_ids)))
                    merged_f = tuple(sorted(set(existing.facet_tags) | set(item.facet_tags)))
                    if merged_q != existing.query_ids or merged_f != existing.facet_tags:
                        lst[i] = dataclasses.replace(existing, query_ids=merged_q, facet_tags=merged_f)
                    break
            return None
        seen.add(item.unit_id)
        sections.setdefault(section, []).append(item)
        return item

    def add_to_a(self, sections: dict, mi) -> Optional[PacketItem]:
        """The ONLY function that ever appends to ``sections["A"]``. ``isinstance`` is checked here, exactly as
        ARCHITECTURE.md section 5.3 rule 1 requires -- no PacketItem, RouteHit or graph Edge, however it is
        labelled, can reach A: only a ``govbridge.authority.resolver.MandatoryItem`` can."""
        if not isinstance(mi, resolvermod.MandatoryItem):
            raise SectionAViolation(f"section A accepts only MandatoryItem (isinstance check); got {type(mi)!r}")
        item = self.item_from_mandatory(mi, "A")
        seen = self._seen.setdefault("A", set())
        if item.unit_id in seen:
            return None
        seen.add(item.unit_id)
        sections.setdefault("A", []).append(item)
        return item


def compile_packet(task_spec: dict, routes: Optional[RouteSet] = None, repo: Optional[str] = None,
                    registry_path: Optional[str] = None, budgets_path: Optional[str] = None,
                    facets_path: Optional[str] = None) -> dict:
    """Compiles ``task_spec`` into a packet. Returns a dict with keys ``status``, ``sections`` (post-budget,
    post-sort ``{letter_or_subblock: [PacketItem]}``), ``drops`` (``{letter_or_subblock: [drop dict]}``),
    ``queries_log``, ``notices``, ``resolve_result``, ``manifest``, ``rendered``, ``packet_sha256``,
    ``manifest_sha256``, ``packet_id``, ``gather_results``, ``evidence_notes``, ``supplementary_packets``.

    ``facets_path`` (REPAIR_DAG.yaml node R1-GA3): overrides ``config/facets.yaml`` for every
    ``govbridge.gather``/``govbridge.compile.overflow`` call this compile makes (facet quotas, per-item facet
    tags, D.2's both-ways gather, the oversize-mandatory-item facet vocabulary) -- ``None`` (the default) uses the
    real, versioned registry, exactly as before this node."""
    routes = routes or FAKE_ROUTES
    view_path = _abs_path(task_spec["view"])
    profile = budgetsmod.load_profile(task_spec["budget_profile"], path=budgets_path)

    # BR-DAG-AMEND-R1-23 (ONE RESOLVED VIEW PER OPERATION): this ONE resolution is the whole compile's own view
    # for its entire lifetime -- reusing `routes.resolved_view` (govbridge.route.router.RouteSet, populated by
    # real_routes_for/build_real_routes) when the caller passed real routes, since that is ALREADY the exact
    # resolution those routes' own hits were produced against; a fresh resolution only happens here at all for a
    # `--fake-routes`/FAKE_ROUTES compile, which never had a view of its own to reuse. Previously this function
    # made FOUR-PLUS independent resolutions across one compile (resolver.resolve's own, Compiler.__init__'s own,
    # each per-seed why()/history() call, and each per-query gather_with_followup call) -- a "records" ref that
    # moved between any two of them could make one compile's own section A, its route hits, and its follow-up
    # identifiers disagree about which commit they were even answering from. Threaded into resolver.resolve,
    # Compiler (which threads it into registrymod.load), every why()/history() call, and every per-query
    # gather_with_followup call (via q_routes.resolved_view, below) instead.
    resolved_view = getattr(routes, "resolved_view", None)
    if resolved_view is None:
        resolved_view = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)

    resolve_result = resolvermod.resolve(task_spec, repo=repo, registry_path=registry_path,
                                          resolved_view=resolved_view)
    status = STATUS_OK if resolve_result.status == resolvermod.STATUS_OK else STATUS_BLOCKED

    c = Compiler(task_spec, routes, repo, view_path, registry_path, profile.rrf_k, profile.graph_neighbour_depth,
                 budgets_path=budgets_path, fanout=profile.g_fanout, per_item_cap_bytes=profile.per_item_cap_bytes,
                 max_slice_chars=profile.max_slice_chars, top_n=profile.parent_expansion_top_n,
                 resolved_view=resolved_view,
                 facets_path=facets_path)

    sections: dict = {k: [] for k in ("A", "B", "C", "D.1", "D.2", "D.3", "E", "F", "G", "H")}
    queries_log: dict = {}

    # --- section A (+ D.1 references), from the resolver ALONE. This is the only code path that ever appends to
    # sections["A"]; every entry is, by construction, a PacketItem built from an isinstance-checked MandatoryItem.
    for mi in resolve_result.items:
        if not isinstance(mi, resolvermod.MandatoryItem):  # belt-and-braces: section 5.3 rule 1
            continue
        section, also_d1 = place_item(mi.cls, mi.lifecycle, delivery_for_mandatory(mi.cls), mi.id, c.grammar)
        if section == "A":
            item = c.add_to_a(sections, mi)
        else:
            item = c.add(sections, section, c.item_from_mandatory(mi, section))
        if item is None:
            continue  # a duplicate unit id in this section; nothing further to reference from it
        if also_d1:
            c.add(sections, "D.1", c.reference_item(item, "D.1"))
        ladder_spec = classesmod.ALL_CLASSES.get(mi.cls)
        if section == "A" and mi.lifecycle != classesmod.LIFECYCLE_ACTIVE:
            # BR-ARCH-RULING-1 rule 2: the item stays in A (never moved out, never relabelled ACTIVE), but the
            # gap is made visible in J -- "so the orchestrator sees the classification gap or the stale task
            # spec". Replaces MANDATORY_ITEM_NOT_IN_A for this case, which is no longer reachable here: an
            # A-admissible mandatory item is never placed anywhere but A now, whatever its lifecycle.
            c.notices.append({"type": "MANDATORY_LIFECYCLE_NOT_ACTIVE", "id": mi.id, "class": mi.cls,
                               "lifecycle": mi.lifecycle})
        elif ladder_spec is not None and ladder_spec.ladder and section != "A":
            # a required input whose CLASS is not admissible in A at all (e.g. DERIVED) -- never fabricated as
            # admissible, and never moved there. Made visible in J rather than silently parked wherever
            # place_item's generic fallback put it.
            c.notices.append({"type": "MANDATORY_ITEM_NOT_IN_A", "id": mi.id, "class": mi.cls,
                               "lifecycle": mi.lifecycle, "placed_in": section})
        if section == "D.2":
            _attach_evidence_both_ways(c, sections, queries_log, item, view_path, repo, budgets_path=budgets_path)

    # --- B (why) and F (history), from seeds -- real B5 graph modules, git-backed, outage-proof.
    for seed in task_spec.get("seeds", []) or []:
        try:
            why_result = whymod.why(seed, repo=repo, view_path=view_path, registry_path=c.registry_path,
                                     code_conn=c.code_conn(), resolved_view=c.resolved_view)
        except Exception:
            why_result = {"stages": {}}
        for stage, info in why_result.get("stages", {}).items():
            for hop in info.get("hops", []):
                c.add(sections, "B", c.item_from_edge_hop(f"WHY:{stage}", hop, "B"))

        try:
            hist_result = historymod.history(seed, repo=repo, view_path=view_path, registry_path=c.registry_path,
                                              resolved_view=c.resolved_view)
        except Exception:
            hist_result = {"entries": []}
        for entry in hist_result.get("entries", []):
            edge = entry.get("edge")
            if edge is None:
                continue
            c.add(sections, "F", c.item_from_edge_hop("HISTORY", edge, "F"))

        try:
            conn = storemod.open_db()
            neighbours = traversemod.bfs(conn, [seed], max_depth=c.graph_depth)
        except Exception:
            neighbours = {}
        for unit, edge_list in neighbours.items():
            if unit == seed or not edge_list:
                continue
            c.add(sections, "C", c.item_from_edge_hop("NEIGHBOUR", edge_list[0].to_dict(), "C"))

        # BR-HO-0015 (G row): a record seed (e.g. a review finding id) carries no symbol name of its own, so the
        # code route above would resolve nothing for it. code_seeds_for derives every symbol/occurrence the seed
        # RECORD's own text cites -- path:line, a path-qualified symbol, or a bare backticked symbol -- resolved at
        # the canonical product ref, and hands them to the SAME code route as extra names/occurrences so definitions,
        # callers, callees, TESTS edges and READS_KEY consumers are all expanded uniformly (defect 1 + defect 2). A
        # seed that is already a code symbol keeps working exactly as before (seed_names always starts with seed).
        seed_names, seed_labels, bare_occurrences = c.code_seeds_for(seed)
        # R1-RX (RC-8): this call previously passed no exclude= at all -- the seed code route is one of the two
        # compile call sites CAUSE_ANALYSIS.md named as running without exclusions.
        for hit in c.routes.run("code", seeds=seed_names, seed_labels=seed_labels,
                                 bare_occurrences=bare_occurrences, fanout=c.fanout, exclude=c.exclusions,
                                 exclude_counter=c.exclusion_counter):
            cls_section, _ = place_item(hit.authority_class, hit.lifecycle, hit.delivery, hit.unit_id, c.grammar)
            # BR-HO-0015 defect 3: only a LADDER class may be redirected H -> G (g_admissible); a non-ladder class
            # (UNCLASSIFIED, FIXTURE) has a FIXED allowed_sections that never names G, and redirecting one there
            # would fail validate.py's independent placement re-derivation.
            target = "G" if (cls_section == "H" and g_admissible(hit.authority_class)) else cls_section
            fused = routermod.FusedHit(hit=hit, fused_score=0.0, routes=(hit.route,))
            item = c.item_from_hit(fused, target)
            if item.tier is not None and target != "G":
                # T1/T2 pinning (BR-AR-0015 reopening) only ever means anything INSIDE G. A citation-derived hit
                # whose class is non-ladder (e.g. UNCLASSIFIED -- its own allowed_sections never names G, so
                # g_admissible refused the redirect above) lands in H or E like any other item of that class: it
                # must not carry PINNED there, which would wrongly exempt it from THAT section's own budget and
                # (since item_from_hit's banner is lifecycle-only) fail verify_banners' PINNED-non-ladder check,
                # which expects the class's own mandatory banner, not a lifecycle one.
                item = dataclasses.replace(
                    item, delivery=("RETRIEVED" if item.delivery == "PINNED" else item.delivery), tier=None)
            c.add(sections, target, item)

    # --- queries: govbridge.gather (facets, parallel retrieval, adaptive follow-up), one call per INSTANTIATED
    # task query -- REPAIR_DAG.yaml node R1-GA3 (REPAIR_PLAN.md sections 2.1, 2.8; RC-2, RC-4, RC-5). A query with
    # no executable text is the compile error QUERY_NOT_EXECUTABLE, never a silent skip (RC-2) -- the SAME
    # instantiation govbridge.compile.section_i.instantiated_query_set and govbridge.gather.followup's own CLI
    # already use, never a second, diverging reading of the query-set document.
    all_facets = facetsmod.load_facets(c.facets_path)
    a_by_unit_id = {i.unit_id: i for i in sections.get("A", [])}
    gather_results_by_query: dict = {}
    try:
        raw_queries = task_spec.get("queries")
        query_doc = instantiatemod.load_query_set(raw_queries, repo=repo, base_dir=GOV_BRIDGE_DOMAIN)
        instantiated_queries = instantiatemod.instantiate_all(query_doc)
    except instantiatemod.QueryNotExecutable as exc:
        instantiated_queries = []
        status = STATUS_BLOCKED
        c.notices.append({"type": "QUERY_NOT_EXECUTABLE", **exc.to_dict()})

    for q in instantiated_queries:
        requested_names = facetsmod.facets_for_query(q, c.facets_path)
        requested_facets = {n: all_facets[n] for n in requested_names if n in all_facets}
        target_section = q.get("target_section")

        # ARCHITECTURE.md section 7.2 / govbridge.route.router.select_routes: an explicit `routes` list on the
        # query (or the auto-detected shape of its own text) has ALWAYS decided which routes may run for it --
        # unchanged by this node. A facet may declare a route this ONE query never asked for (e.g. "purpose"
        # declares semantic; a query with `routes: [lexical]` never wants a real embedding call at all) -- rather
        # than widening every query to every facet's own routes, the query's own route selection is honoured by
        # zeroing the disallowed route SLOTS for this one gather call (a facet whose every route is zeroed simply
        # reports MISSING, exactly as it would with genuinely no candidates -- never a crash, never a silent
        # widening of what this query was allowed to touch).
        allowed_routes = set(routermod.select_routes(q, grammar=c.grammar))
        # BR-DAG-AMEND-R1-23: carry c.resolved_view forward on this per-query RouteSet too (see
        # _attach_evidence_both_ways's own identical comment) -- this is the MAIN query loop's own gather call,
        # the one most exposed to a "records" ref moving mid-compile across many queries.
        q_routes = routermod.RouteSet(
            exact=c.routes.exact if "exact" in allowed_routes else routermod.empty_route,
            lexical=c.routes.lexical if "lexical" in allowed_routes else routermod.empty_route,
            semantic=c.routes.semantic if "semantic" in allowed_routes else routermod.empty_route,
            code=c.routes.code if "code" in allowed_routes else routermod.empty_route,
            resolved_view=c.resolved_view,
        )

        gather_result = gather_with_followup(
            q, q_routes, task=c.task_ctx, facet_names=(list(requested_names) if requested_names else None),
            exclude=list(c.exclusions), view_path=view_path, repo=repo, facets_path=c.facets_path,
            budgets_path=budgets_path, resolved_view=c.resolved_view,
        )
        gather_results_by_query[q["id"]] = gather_result
        c.exclusion_counter.bump(gather_result.get("excluded_hits", 0))

        merged = gather_result.get("merged") or []
        touched_sections = set()
        facet_present = {name: False for name in requested_names}
        # REPAIR_PLAN.md section 2.8: "a larger slice for the facet's TOP items" -- a per-FACET rank, never a
        # single rank over the whole merged list (which would only ever mark the first facet in registry order as
        # having "top" items at all). ``merged`` accumulates facet-by-facet within a round (govbridge.gather.
        # engine.gather's own "walk facets in registry order" merge), so counting each facet's own occurrences as
        # they are encountered approximates that facet's own internal rank order closely enough to decide "is this
        # one of this facet's own first c.top_n items."
        facet_rank_counters: dict = {}
        for rank, md in enumerate(merged, start=1):
            tags = overflowmod.facet_tags_for_merged_item(md, requested_facets)
            top = False
            for name in tags:
                if name in facet_present:
                    facet_present[name] = True
                facet_rank_counters[name] = facet_rank_counters.get(name, 0) + 1
                if facet_rank_counters[name] <= c.top_n:
                    top = True

            a_item = a_by_unit_id.get(md.get("unit_id"))
            if a_item is not None:
                # REPAIR_PLAN.md section 2.8: "content already present is cited by item id" -- never a second copy
                # of an item this compile already placed in section A.
                ref = c.reference_to_a_item(a_item, target_section or "H", query_ids=(q["id"],), facet_tags=tags)
                c.add(sections, ref.section, ref)
                touched_sections.add(ref.section)
                continue

            hit = _hit_from_merged(md)
            section, also_d1 = place_item(hit.authority_class, hit.lifecycle, hit.delivery, hit.unit_id, c.grammar)
            if section == "H":
                # BR-HO-0015 defect 3 (G row), unchanged: a RETRIEVED/DERIVED item whose canonical occurrence is a
                # code or test surface goes to G, never H.
                occ_path = hit.occurrences[0].path if hit.occurrences else None
                if (occ_path and g_admissible(hit.authority_class)
                        and codesurfacesmod.is_code_or_test_surface(occ_path, c.code_surface_rules)):
                    section = "G"
                elif target_section:
                    section = target_section
            fused = routermod.FusedHit(hit=hit, fused_score=1.0 / rank, routes=(hit.route,))
            item = c.item_from_hit(fused, section, facet_tags=tags, query_ids=(q["id"],), top=top)
            if section == "G" and item.tier is None:
                item = dataclasses.replace(item, tier="T3")
            elif item.tier is not None and section != "G":
                item = dataclasses.replace(
                    item, delivery=("RETRIEVED" if item.delivery == "PINNED" else item.delivery), tier=None)
            c.add(sections, section, item)
            touched_sections.add(section)
            if also_d1:
                d1_item = c.item_from_hit(fused, "D.1", facet_tags=tags, query_ids=(q["id"],), top=top)
                c.add(sections, "D.1", d1_item)
                touched_sections.add("D.1")

        query_row = {
            "id": q.get("id"), "text": q.get("text"), "facets": list(requested_names),
            "stop_reason": gather_result.get("stop_reason"),
            "followup_rounds": gather_result.get("followup_rounds"), "merged_items": len(merged),
        }
        for sec in (touched_sections or {target_section or "H"}):
            queries_log.setdefault(sec, []).append(query_row)

        # REPAIR_PLAN.md section 2.6/2.8: "every requested facet of every query is present, or disclosed as
        # MISSING". A facet whose own base-round telemetry already reported it MISSING (no candidates anywhere,
        # engine.gather's own disclosed reason) is reported with that reason; one that had candidates but never
        # got a single item PLACED into the compiled packet (dedup/budget) is disclosed generically -- neither
        # case is silently absent.
        per_round = ((gather_result.get("telemetry") or {}).get("per_round")) or []
        for name in requested_names:
            if facet_present.get(name):
                continue
            facet_rounds = [r for r in per_round if r.get("facet") == name]
            reason = next((r.get("missing_reason") for r in facet_rounds if r.get("missing")), None)
            c.notices.append({
                "type": "FACET_MISSING", "query_id": q["id"], "facet": name,
                "reason": reason or "gather found candidates for this facet, but none were placed in the "
                                     "compiled packet (deduplicated away or dropped by budget -- see the BUDGET "
                                     "drop records for this section)",
            })

    # R1-RX (OBS-BR-08): "each output discloses how many hits were excluded" -- one notice, always present (even
    # at 0), summing every c.routes.run(...) call this compile made (the query loop, the seed code route and the
    # D.2 both-ways templates all share c.exclusion_counter).
    c.notices.append({"type": "RETRIEVAL_EXCLUSIONS_APPLIED", "excluded_hits": c.exclusion_counter.count,
                       "retrieval_exclusions": list(c.exclusions)})

    # --- I / J: verbatim task-spec content, never computed.
    c.add(sections, "I", _build_i_item(task_spec))
    j_item, all_notices = _build_j_item(task_spec, resolve_result, c.notices)
    c.notices = all_notices
    c.add(sections, "J", j_item)

    # --- budgets (facet-quota-aware, REPAIR_DAG.yaml node R1-GA3), then final deterministic ordering.
    facet_shares = overflowmod.facet_min_shares(c.facets_path)
    sections, drops_list, blocked_budget, budget_notices = budgetsmod.apply_budgets(
        sections, profile, facet_min_shares=facet_shares)
    if blocked_budget:
        status = STATUS_BLOCKED_BUDGET
    c.notices.extend(budget_notices)  # e.g. G_T1_OVER_BUDGET (BR-AR-0015 reopening defect 2)
    for key in sections:
        sections[key] = sorted(sections[key], key=sort_key)

    # --- overflow: REPAIR_PLAN.md section 2.8 ("if merged evidence exceeds the profile, the compiler emits
    # hierarchical evidence notes and supplementary packets... nothing is silently discarded"). An item this
    # compile's own gather calls retrieved but the budget then dropped (``drops_list``, BEFORE it is compacted
    # below) is never simply lost: it is shaped into an R1-RN evidence note (grounded claims, when a concrete line
    # range is groundable) PLUS an R1-RS supplementary packet (the full remainder, deduplicated against what the
    # main packet already kept) per query. Neither artifact is validated here (a caller runs ``govbridge notes
    # validate`` / ``packet verify`` on them, exactly like every other note/supplementary packet in this domain);
    # this only shapes the data and discloses it in J, in both directions (never a silent overflow).
    from govbridge.compile import supplementary as supplementarymod  # lazy: supplementary.py imports this module

    dropped_keys = {f"{d['unit']['kind']}:{d['unit']['id']}" for d in drops_list}
    already_placed_keys = {f"{i.unit_kind}:{i.unit_id}" for items in sections.values() for i in items}
    evidence_notes: dict = {}
    supplementary_packets: dict = {}
    for qid, g_result in gather_results_by_query.items():
        overflow_items = [md for md in (g_result.get("merged") or [])
                           if f"{md.get('unit_kind')}:{md.get('unit_id')}" in dropped_keys]
        if not overflow_items:
            continue
        note = overflowmod.build_overflow_note(qid, overflow_items, repo=repo)
        if note is not None:
            evidence_notes[qid] = note
        supplementary_built = supplementarymod.build_supplementary_packet(
            "gather", {"merged": overflowmod.merged_items_as_hit_dicts(overflow_items)}, task_spec,
            dedup_ids=already_placed_keys)
        supplementary_packets[qid] = supplementary_built
        c.notices.append({
            "type": "EVIDENCE_OVERFLOW", "query_id": qid, "overflow_item_count": len(overflow_items),
            "note_id": (note or {}).get("note_id"), "note_unresolved_count": len((note or {}).get("unresolved", [])),
            "supplementary_packet_sha256": supplementary_built.get("packet_sha256"),
        })

    # BR-AR-0015 reopening, defect 4: compact, per (section, tier) -- a count, a sha256 over the sorted dropped
    # unit ids, and the first 50 of those ids -- never the raw per-item drop list the manifest used to carry.
    drops_by_section = budgetsmod.compact_drops(drops_list)

    # --- assemble manifest + render.
    task_spec_sha256 = sha256_text(canonical_json(task_spec))
    view_rows = []
    for r in c.resolved_view.config.refs:
        rc = c.resolved_view.named.get(r.name)
        if rc is None:
            continue
        view_rows.append({"name": r.name, "ref": r.ref, "role": r.role, "commit": rc.commit})
    config_sha256 = _config_shas(view_path, c.registry_path, budgets_path)
    manifest = rendermod.build_manifest(
        task_spec_sha256=task_spec_sha256, view_rows=view_rows, build_manifest_sha256=None,
        bridge_code_tree=bridge_code_tree(repo=repo), config_sha256=config_sha256,
        budget_profile=task_spec["budget_profile"],
        retrieval_exclusions=task_spec.get("retrieval_exclusions") or [], status=status, sections=sections,
        queries_log=queries_log, drops_by_section=drops_by_section, notices=c.notices,
    )
    manifest, rendered, packet_id = rendermod.render_packet(manifest, sections, queries_log, drops_by_section)

    return {
        "status": status, "sections": sections, "drops": drops_by_section, "queries_log": queries_log,
        "notices": c.notices, "resolve_result": resolve_result, "manifest": manifest, "rendered": rendered,
        "packet_sha256": manifest["packet_sha256"], "manifest_sha256": manifest["manifest_sha256"],
        "packet_id": packet_id, "view_path": view_path, "registry_path": c.registry_path,
        # R1-RX (OBS-BR-08): the same count as the RETRIEVAL_EXCLUSIONS_APPLIED notice, surfaced at the top level
        # too so a caller (govbridge.cli, a test) never has to scan notices for it.
        "excluded_hits": c.exclusion_counter.count,
        # REPAIR_DAG.yaml node R1-GA3: per-query gather results (telemetry, stop reasons, facets) and this
        # compile's own overflow shaping -- a DERIVED_NOTE dict (unvalidated: run govbridge.notes.validate) and a
        # built (unwritten: run govbridge.compile.supplementary.write_supplementary_packet) supplementary packet
        # per query whose gathered evidence did not entirely fit. Both are `{}` when nothing overflowed. Writing
        # these to disk under `govbridge compile --out DIR` is a govbridge/cli.py change, outside this node's
        # mutation scope this wave (see this node's checkpoint decisions/next_consumer).
        "gather_results": gather_results_by_query,
        "evidence_notes": evidence_notes,
        "supplementary_packets": supplementary_packets,
    }


def _config_shas(view_path: str, registry_path: str, budgets_path: Optional[str]) -> dict:
    """sha256 per config file this compile actually read (``schemas/packet-manifest.yaml``'s ``config_sha256``) --
    labelled generically (never by a content-specific name), read from the WORKING TREE the compiler runs from,
    which is fine here: these are the compiler's OWN inputs (config, not corpus), read the same way B5's registry
    loader reads them."""
    labelled = {
        "canonical_view": view_path,
        "authority_registry": registry_path,
        "id_grammar": recordsmod._default_grammar_path(),
        "budgets": budgets_path or budgetsmod._default_budgets_path(),
    }
    out = {}
    for label, path in labelled.items():
        try:
            with open(path, "rb") as fh:
                out[label] = hashlib.sha256(fh.read()).hexdigest()
        except OSError:
            out[label] = None
    return out


def _build_i_item(task_spec: dict) -> PacketItem:
    body = json.dumps({
        "objective": task_spec.get("objective"),
        "mutation_scope": task_spec.get("mutation_scope"),
        "prohibitions": task_spec.get("prohibitions"),
    }, indent=1, sort_keys=True)
    return PacketItem(unit_kind="section", unit_id="I", section="I", delivery="PINNED", cls=None,
                       lifecycle=classesmod.LIFECYCLE_ACTIVE, version_status=None, ref=None, commit=None, path=None,
                       blob=None, line_start=None, line_end=None, text=body,
                       content_sha256=sha256_text(body), by_reference=False, route="task_spec", raw_score=None,
                       rank=None, fused_score=None, edge_path=(), reason="task_spec, verbatim", banner=None)


def _build_j_item(task_spec: dict, resolve_result: resolvermod.ResolveResult, existing_notices: list) -> tuple:
    all_notices = list(existing_notices)
    if resolve_result.status != resolvermod.STATUS_OK:
        for reason in resolve_result.blocked_reasons:
            all_notices.append({"type": "BLOCKED_INPUT", "detail": reason})
    body = json.dumps({
        "required_checks": task_spec.get("required_checks"),
        "completion_vocabulary": task_spec.get("completion_vocabulary"),
        "receipt_schema": "govbridge-receipt/1",
        "notices": all_notices,
    }, indent=1, sort_keys=True)
    item = PacketItem(unit_kind="section", unit_id="J", section="J", delivery="PINNED", cls=None,
                       lifecycle=classesmod.LIFECYCLE_ACTIVE, version_status=None, ref=None, commit=None, path=None,
                       blob=None, line_start=None, line_end=None, text=body,
                       content_sha256=sha256_text(body), by_reference=False, route="task_spec", raw_score=None,
                       rank=None, fused_score=None, edge_path=(), reason="task_spec, verbatim", banner=None)
    return item, all_notices


def _attach_evidence_both_ways(c: Compiler, sections: dict, queries_log: dict, d2_item: PacketItem,
                                view_path: str, repo: Optional[str], budgets_path: Optional[str] = None) -> None:
    """ARCHITECTURE.md section 7.3: for every OWNER_DIRECTION_TO_TEST item, two symmetric fixed query templates,
    placed side by side, never labelled as supporting. ``d2_item`` is already the list entry ``c.add`` just placed
    in ``sections["D.2"]``; this replaces it IN PLACE with a copy carrying the extra text (same unit id/section/
    delivery, so its ``item_id`` -- and ``c._seen`` membership -- is unchanged).

    REPAIR_PLAN.md section 2.8: "D.2 both-ways evidence is produced by gather with the task context's exclusions"
    (REPAIR_DAG.yaml node R1-GA3) -- each template is now one ``govbridge.gather.followup.gather_with_followup``
    call (facets, parallel retrieval, one bounded round of adaptive follow-up) instead of a single-round ad hoc
    route fuse; the task context's exclusions (``c.task_ctx``, merged with the ambient ``GOVBRIDGE_TASK`` exactly
    as every other gather call in this module already does) are honoured through the same ``task=``/``exclude=``
    plumbing, never a second, diverging exclusion path for D.2 alone. ``max_followup_rounds=1``: bounded, since
    this runs once per OWNER_DIRECTION_TO_TEST item, potentially several per compile."""
    subject = d2_item.unit_id
    templates = [
        ("consumers_and_uses", f"consumers, dependents and uses of {subject}"),
        ("purpose_and_origin", f"purpose, origin and the requirements {subject} was created for"),
    ]
    blocks = []
    for label, text in templates:
        q = {"id": f"{subject}#{label}", "text": text}
        allowed_routes = set(routermod.select_routes(q, grammar=c.grammar))
        # BR-DAG-AMEND-R1-23: this per-query RouteSet used to drop `resolved_view` entirely (the field did not
        # exist before this amendment) -- carrying it forward means gather_with_followup below reuses THIS
        # compile's own one resolved view (c.resolved_view) instead of falling through to its own independent
        # resolution.
        q_routes = routermod.RouteSet(
            exact=c.routes.exact if "exact" in allowed_routes else routermod.empty_route,
            lexical=c.routes.lexical if "lexical" in allowed_routes else routermod.empty_route,
            semantic=c.routes.semantic if "semantic" in allowed_routes else routermod.empty_route,
            code=c.routes.code if "code" in allowed_routes else routermod.empty_route,
            resolved_view=c.resolved_view,
        )
        result = gather_with_followup(q, q_routes, task=c.task_ctx, exclude=list(c.exclusions),
                                       view_path=view_path, repo=repo, facets_path=c.facets_path,
                                       budgets_path=budgets_path, max_followup_rounds=1,
                                       resolved_view=c.resolved_view)
        c.exclusion_counter.bump(result.get("excluded_hits", 0))
        queries_log.setdefault("D.2", []).append({
            "id": q["id"], "text": text, "facets": result.get("facets"), "stop_reason": result.get("stop_reason"),
        })
        items = []
        for md in (result.get("merged") or [])[:5]:
            hit = _hit_from_merged(md)
            fused = routermod.FusedHit(hit=hit, fused_score=1.0, routes=(hit.route,))
            items.append(c.item_from_hit(fused, "D.2", query_ids=(q["id"],)))
        blocks.append((label, items))

    extra = ["", "--- evidence bearing on this direction, both ways (neither side is labelled as supporting) ---"]
    for label, items in blocks:
        extra.append(f"[{label}]")
        if not items:
            extra.append("(none)")
        for it in items:
            extra.append(f"  - {it.unit_kind}:{it.unit_id} ({it.route}, class={it.cls}, lifecycle={it.lifecycle})")
    new_text = (d2_item.text or "") + "\n" + "\n".join(extra) + "\n"
    replaced = dataclasses.replace(d2_item, text=new_text)
    lst = sections["D.2"]
    for i, it in enumerate(lst):
        if it is d2_item:
            lst[i] = replaced
            return


# --------------------------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------------------------

def real_routes_for(task_spec: dict, registry_path: Optional[str] = None, repo: Optional[str] = None) -> RouteSet:
    """The default RouteSet for a real compile: the real B2 (lexical)/B3 (code)/B4 (semantic) adapters
    (``govbridge.route.real_routes``, node I1 -- B6's own open issue "the real B2/B3/B4 routes are not wired").
    Imported lazily so ``govbridge.compile.packet`` itself still never imports ``.lexical``/``.semantic``/``.code``
    at module load time (only when an actual compile asks for real routes)."""
    from govbridge.route import real_routes as real_routesmod
    return real_routesmod.build_real_routes(view_path=_abs_path(task_spec["view"]), repo=repo,
                                             registry_path=registry_path)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.compile.packet")
    p.add_argument("task_spec")
    p.add_argument("--fake-routes", action="store_true",
                    help="use the all-empty RouteSet (lexical/semantic/code return nothing; graph routes -- "
                         "why/history/traverse -- are always real). The DEFAULT is the real B2/B3/B4 routes "
                         "(govbridge.route.real_routes); this flag exists for tests and a corpus-less smoke check.")
    p.add_argument("--registry")
    p.add_argument("--budgets")
    p.add_argument("--json", action="store_true", help="print the manifest instead of the rendered packet")
    args = p.parse_args(argv)

    task_spec = load_yaml_file(args.task_spec)
    routes = FAKE_ROUTES if args.fake_routes else real_routes_for(task_spec, registry_path=args.registry)
    result = compile_packet(task_spec, routes=routes, registry_path=args.registry, budgets_path=args.budgets)
    if args.json:
        print(json.dumps(result["manifest"], indent=1, sort_keys=True))
    else:
        sys.stdout.write(result["rendered"])
    return 0 if result["status"] == STATUS_OK else 1


if __name__ == "__main__":
    sys.exit(main())
