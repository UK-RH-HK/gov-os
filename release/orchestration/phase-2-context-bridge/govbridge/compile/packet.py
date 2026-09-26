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
from govbridge.compile import render as rendermod
from govbridge.core import gitobj, store as storemod, view as viewmod
from govbridge.core import taskctx as taskctxmod
from govbridge.core.manifest import bridge_code_tree
from govbridge.core.yamlutil import canonical_json, load_yaml_file, sha256_text
from govbridge.graph import history as historymod
from govbridge.graph import traverse as traversemod
from govbridge.graph import why as whymod
from govbridge.route import router as routermod
from govbridge.route.router import FAKE_ROUTES, RouteSet

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


def _load_queries(task_spec: dict, repo: Optional[str] = None) -> list:
    """``schemas/task-spec.yaml``: ``queries: 'path | list'``, ``[{id, text, routes?, target_section?}]`` or a
    queries file. A file (like ``ARCHITECTURE/demonstration-queries.yaml``) that is a query-DESIGN document rather
    than a flat executable list yields no mechanically-run queries here -- generic, never an error: the sections
    such a task still gets (A from the resolver, B/F from the seeds) are honestly complete on their own, and the
    worker issues further live ``govbridge`` queries during the task itself."""
    raw = task_spec.get("queries")
    if raw is None:
        return []
    if isinstance(raw, list):
        candidates = raw
    elif isinstance(raw, str):
        doc = load_yaml_file(_abs_path(raw))
        if isinstance(doc, list):
            candidates = doc
        elif isinstance(doc, dict) and isinstance(doc.get("queries"), list):
            candidates = doc["queries"]
        else:
            candidates = []
    else:
        candidates = []
    return [q for q in candidates if isinstance(q, dict) and isinstance(q.get("text"), str)]


def _read_excerpt(path: str, commit: str, l1: Optional[int], l2: Optional[int],
                   repo: Optional[str] = None, max_chars: int = 4000) -> Optional[str]:
    """The text of ``path``@``commit`` (or lines ``l1``-``l2`` of it), or None if there is nothing to read -- a
    directory entry (a MandatoryItem's ``path`` may be a directory: resolver.py's own is_directory case carries
    no text), a missing object, or a decode failure. None is the honest, generic "no excerpt" result; the caller
    falls back to a reference note, never a crash."""
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
    return text[:max_chars]


class Compiler:
    """Holds the per-compile context (repo, view, registry, grammar) so every ``_item_from_*`` helper can stay a
    short, testable method instead of a closure threading five arguments through."""

    def __init__(self, task_spec: dict, routes: RouteSet, repo: Optional[str], view_path: str,
                 registry_path: Optional[str], rrf_k: int, graph_depth: int, budgets_path: Optional[str] = None,
                 fanout: Optional[dict] = None):
        self.task_spec = task_spec
        self.routes = routes or FAKE_ROUTES
        self.repo = repo
        self.view_path = view_path
        self.resolved_view = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)
        self.registry_path = registry_path or registrymod._default_registry_path()
        self.reg = registrymod.load(self.registry_path, verify_commit="records", view_path=view_path, repo=repo)
        self.grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
        self.rrf_k = rrf_k
        self.graph_depth = graph_depth
        # BR-AR-0015 reopening, defect 2: per-symbol fan-out caps for G's T2 expansion (callers/callees/TESTS/
        # READS_KEY), read from the budget profile ("fan-out caps from the profile") -- defaults to the real
        # code_route adapter's own generous fallback when the caller gives none (e.g. an existing test that
        # predates this reopening).
        self.fanout = fanout or {}
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
        text = None
        if mi.path is not None and mi.commit is not None:
            text = _read_excerpt(mi.path, mi.commit, mi.line_start, mi.line_end, repo=self.repo)
        if text is None:
            loc = f"{mi.path}@{mi.commit}"
            if mi.line_start is not None:
                loc += f":{mi.line_start}-{mi.line_end}"
            text = f"[reference only: {loc}]"
        # content_sha256 is the resolver's OWN recorded hash, verbatim -- never a hash of this module's placeholder
        # text (a directory-form item legitimately carries sha256=None; validate.py's independent re-derivation
        # compares this field against the freshly recomputed MandatoryItem field-for-field, so it must never diverge
        # from what the resolver itself reported).
        content_sha256 = mi.sha256
        return PacketItem(unit_kind="record", unit_id=mi.id, section=section, delivery=delivery, cls=mi.cls,
                           lifecycle=mi.lifecycle, version_status=None, ref=None, commit=mi.commit, path=mi.path,
                           blob=mi.blob, line_start=mi.line_start, line_end=mi.line_end, text=text,
                           content_sha256=content_sha256, by_reference=False, route="resolver", raw_score=None,
                           rank=None, fused_score=None, edge_path=(), reason=mi.reason, banner=banner)

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
                           banner=None)

    # -- construction from a route hit (delivery RETRIEVED/DERIVED) -------------------------------------------

    def item_from_hit(self, fused: "routermod.FusedHit", section: str) -> PacketItem:
        h = fused.hit
        occ = h.occurrences[0] if h.occurrences else None
        lifecycle = h.lifecycle or classesmod.LIFECYCLE_UNKNOWN
        banner = LIFECYCLE_BANNERS.get(lifecycle) if lifecycle != classesmod.LIFECYCLE_ACTIVE else None
        text = h.text or ""
        return PacketItem(unit_kind=h.unit_kind, unit_id=h.unit_id, section=section, delivery=h.delivery,
                           cls=h.authority_class, lifecycle=lifecycle,
                           version_status=occ.version_status if occ else None, ref=occ.ref if occ else None,
                           commit=occ.commit if occ else None, path=occ.path if occ else None, blob=None,
                           line_start=occ.line_start if occ else None, line_end=occ.line_end if occ else None,
                           text=text, content_sha256=(sha256_text(text) if text else None), by_reference=False,
                           route=h.route, raw_score=None, rank=h.rank, fused_score=fused.fused_score,
                           edge_path=tuple(h.edge_path), reason=None, banner=banner,
                           tier=getattr(h, "tier", None), resolution=getattr(h, "resolution", None))

    # -- construction from a graph.why/history Edge hop (delivery DERIVED) --------------------------------------

    def item_from_edge_hop(self, stage_or_kind: str, edge: dict, section: str) -> PacketItem:
        occ = edge.get("evidence_occurrence") or ""
        path, _, rest = occ.partition("@")
        commit, line = None, edge.get("evidence_line")
        if rest:
            commit = rest.split(":", 1)[0]
        text = _read_excerpt(path, commit, line, line, repo=self.repo) if (path and commit) else None
        unit_id = f"{edge.get('type')}:{edge.get('dst')}"
        return PacketItem(unit_kind="occurrence", unit_id=unit_id, section=section, delivery="DERIVED", cls=None,
                           lifecycle=classesmod.LIFECYCLE_UNKNOWN, version_status=None, ref=None, commit=commit,
                           path=path or None, blob=None, line_start=line, line_end=line, text=(text or "")[:2000],
                           content_sha256=(sha256_text(text) if text else None), by_reference=False, route="graph",
                           raw_score=None, rank=None, fused_score=None, edge_path=(edge,),
                           reason=f"{stage_or_kind}: {edge.get('derivation')}", banner=None)

    # -- placement, with dedup ------------------------------------------------------------------------------------

    def add(self, sections: dict, section: str, item: PacketItem) -> Optional[PacketItem]:
        """Appends ``item`` to ``sections[section]`` unless its unit id is already present there. Section A is
        NEVER accepted here -- ARCHITECTURE.md section 5.3 rule 1 ("Packet.section_a accepts only MandatoryItem,
        checked with isinstance") is enforced by routing every A-bound item through ``add_to_a`` instead, which is
        the only method that ever appends to ``sections["A"]``. Returns the item actually stored, or None if it
        was a duplicate (never stored)."""
        if section == "A":
            raise SectionAViolation(
                f"section A must be filled through Compiler.add_to_a, never Compiler.add -- refused "
                f"{item.unit_kind}:{item.unit_id} (delivery={item.delivery}, route={item.route})")
        seen = self._seen.setdefault(section, set())
        if item.unit_id in seen:
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
                    registry_path: Optional[str] = None, budgets_path: Optional[str] = None) -> dict:
    """Compiles ``task_spec`` into a packet. Returns a dict with keys ``status``, ``sections`` (post-budget,
    post-sort ``{letter_or_subblock: [PacketItem]}``), ``drops`` (``{letter_or_subblock: [drop dict]}``),
    ``queries_log``, ``notices``, ``resolve_result``, ``manifest``, ``rendered``, ``packet_sha256``,
    ``manifest_sha256``, ``packet_id``."""
    routes = routes or FAKE_ROUTES
    view_path = _abs_path(task_spec["view"])
    profile = budgetsmod.load_profile(task_spec["budget_profile"], path=budgets_path)

    resolve_result = resolvermod.resolve(task_spec, repo=repo, registry_path=registry_path)
    status = STATUS_OK if resolve_result.status == resolvermod.STATUS_OK else STATUS_BLOCKED

    c = Compiler(task_spec, routes, repo, view_path, registry_path, profile.rrf_k, profile.graph_neighbour_depth,
                 budgets_path=budgets_path, fanout=profile.g_fanout)

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
            _attach_evidence_both_ways(c, sections, queries_log, item)

    # --- B (why) and F (history), from seeds -- real B5 graph modules, git-backed, outage-proof.
    for seed in task_spec.get("seeds", []) or []:
        try:
            why_result = whymod.why(seed, repo=repo, view_path=view_path, registry_path=c.registry_path,
                                     code_conn=c.code_conn())
        except Exception:
            why_result = {"stages": {}}
        for stage, info in why_result.get("stages", {}).items():
            for hop in info.get("hops", []):
                c.add(sections, "B", c.item_from_edge_hop(f"WHY:{stage}", hop, "B"))

        try:
            hist_result = historymod.history(seed, repo=repo, view_path=view_path, registry_path=c.registry_path)
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

    # --- queries: exact/lexical/semantic/code routes, fused, placed by (class, lifecycle) alone.
    for q in _load_queries(task_spec, repo=repo):
        route_names = routermod.select_routes(q, grammar=c.grammar)
        hits_by_route = {
            rn: c.routes.run(rn, text=q.get("text"), k=q.get("k", 8), exclude=c.exclusions,
                              exclude_counter=c.exclusion_counter)
            for rn in route_names if rn in ("exact", "lexical", "semantic", "code")
        }
        fused = routermod.fuse(hits_by_route, rrf_k=c.rrf_k)
        target_section = q.get("target_section")
        query_row = {"id": q.get("id"), "text": q.get("text"), "routes": list(route_names), "k": q.get("k", 8)}
        touched_sections = set()
        for f in fused:
            section, also_d1 = place_item(f.hit.authority_class, f.hit.lifecycle, f.hit.delivery, f.hit.unit_id,
                                           c.grammar)
            if section == "H":
                # BR-HO-0015 defect 3 (G row): a RETRIEVED/DERIVED item (here, a lexical/semantic query hit -- the
                # code route's own hits are already redirected in the seed loop above) whose canonical occurrence
                # is a code or test surface goes to G, never H; D.1/D.2/D.3/E/F placements above are unaffected
                # (this branch only ever runs on the section == "H" fallback). Only a LADDER class may move to G
                # (g_admissible) -- a non-ladder class (UNCLASSIFIED, FIXTURE) is H-only by its fixed
                # allowed_sections, whatever its occurrence path looks like.
                occ_path = f.hit.occurrences[0].path if f.hit.occurrences else None
                if (occ_path and g_admissible(f.hit.authority_class)
                        and codesurfacesmod.is_code_or_test_surface(occ_path, c.code_surface_rules)):
                    section = "G"
                elif target_section:
                    section = target_section
            item = c.item_from_hit(f, section)
            if section == "G" and item.tier is None:
                # a lexical/semantic hit redirected into G carries no tier of its own (only the code route's hits
                # set one) -- it is T3 ("code or test hits from lexical, semantic or code retrieval") by
                # construction, since this whole branch only runs for a query hit whose occurrence is a code/test
                # surface (defect 2's tier order).
                item = dataclasses.replace(item, tier="T3")
            c.add(sections, section, item)
            touched_sections.add(section)
            if also_d1:
                c.add(sections, "D.1", c.item_from_hit(f, "D.1"))
                touched_sections.add("D.1")
        # a query with no hits still records itself, under its target_section (or H, its generic default landing
        # spot) -- "every section records its queries" holds even when a query returns nothing.
        for sec in (touched_sections or {target_section or "H"}):
            queries_log.setdefault(sec, []).append(query_row)

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

    # --- budgets, then final deterministic ordering.
    sections, drops_list, blocked_budget, budget_notices = budgetsmod.apply_budgets(sections, profile)
    if blocked_budget:
        status = STATUS_BLOCKED_BUDGET
    c.notices.extend(budget_notices)  # e.g. G_T1_OVER_BUDGET (BR-AR-0015 reopening defect 2)
    for key in sections:
        sections[key] = sorted(sections[key], key=sort_key)
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


def _attach_evidence_both_ways(c: Compiler, sections: dict, queries_log: dict, d2_item: PacketItem) -> None:
    """ARCHITECTURE.md section 7.3: for every OWNER_DIRECTION_TO_TEST item, two symmetric fixed query templates,
    placed side by side, never labelled as supporting. ``d2_item`` is already the list entry ``c.add`` just placed
    in ``sections["D.2"]``; this replaces it IN PLACE with a copy carrying the extra text (same unit id/section/
    delivery, so its ``item_id`` -- and ``c._seen`` membership -- is unchanged)."""
    subject = d2_item.unit_id
    templates = [
        ("consumers_and_uses", f"consumers, dependents and uses of {subject}"),
        ("purpose_and_origin", f"purpose, origin and the requirements {subject} was created for"),
    ]
    blocks = []
    for label, text in templates:
        q = {"id": f"{subject}#{label}", "text": text}
        route_names = routermod.select_routes(q, grammar=c.grammar)
        # R1-RX (RC-8): the other of the two compile call sites CAUSE_ANALYSIS.md named as running without
        # exclusions -- the D.2 "evidence both ways" templates.
        hits_by_route = {rn: c.routes.run(rn, text=text, k=5, exclude=c.exclusions,
                                           exclude_counter=c.exclusion_counter)
                          for rn in route_names if rn in ("exact", "lexical", "semantic", "code")}
        fused = routermod.fuse(hits_by_route, rrf_k=c.rrf_k)
        queries_log.setdefault("D.2", []).append({"id": q["id"], "text": text, "routes": list(route_names)})
        blocks.append((label, [c.item_from_hit(f, "D.2") for f in fused[:5]]))

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
