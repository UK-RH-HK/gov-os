#!/usr/bin/env python3
"""Real B2 (lexical)/B3 (code)/B4 (semantic) route adapters, translating each route's own output into
``govbridge.route.router.RouteHit`` -- B6's own open issue ("the real B2/B3/B4 routes are not wired: B6 used
--fake-routes, by design. I1 must write the adapter functions... and wire them into a RouteSet"). This module
never edits ``govbridge/route/router.py`` or ``govbridge/compile/**``; it only builds a ``RouteSet`` those modules
already know how to consume.

Every adapter also wires the REAL authority classifier into its hits (``govbridge.authority.layer.classify_hit``)
-- routed issue B4/BR-AR-0006 OI-3 ("retrieved results carry placeholder UNCLASSIFIED/UNKNOWN... wire B5's
classifier into every route's results"). A retrieved item's delivery stays RETRIEVED always: these adapters build
only ``RouteHit``, never ``MandatoryItem`` -- no conversion function exists between them (ARCHITECTURE.md section
5.3 rule 1), so a real class label here can never be a promotion into section A.

Generic, not bespoke (OC-BR-02): nothing here names Review 8, F1-F6, Phase 2 or a particular id/file. The "product"
ref is resolved by its ``role`` in ``config/canonical-view.yaml``, exactly as ``govbridge.compile.packet.Compiler.
code_conn`` and ``govbridge.graph.impact`` already do.
"""
from __future__ import annotations

import re
import threading
from typing import Optional

from govbridge.authority import layer as authoritylayer
from govbridge.authority import lifecycle as lifecyclemod
from govbridge.authority import registry as registrymod
from govbridge.code import symbols as codesymbols
from govbridge.core import exact as exactmod
from govbridge.core import pathrules
from govbridge.core import store as storemod
from govbridge.core import taskctx as taskctxmod
from govbridge.core import view as viewmod
from govbridge.graph import derive as derivemod
from govbridge.lexical import query as lexicalquery
from govbridge.route import router as routermod
from govbridge.route.router import RouteHit, RouteOccurrence, RouteSet
from govbridge.semantic import search as semanticsearch

UNCLASSIFIED = ("UNCLASSIFIED", "UNKNOWN")

_FTS_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
_FTS_QUOTED_RE = re.compile(r'^\s*"[^"]*"\s*$')


def _safe_fts_query(text: Optional[str]) -> str:
    """Free natural-language text (a task-spec query, a section 7.3 "evidence both ways" template, ...) is not
    guaranteed to be valid FTS5 MATCH syntax -- a comma or colon in ordinary prose is a syntax error to SQLite's
    FTS5 parser (``govbridge.lexical.query`` documents itself as taking "an FTS5 MATCH expression", which is a
    fair contract for a caller who already builds one, but every generic caller here -- task-spec query text,
    section 7.3's templates -- hands over plain prose). Already-valid FTS5 syntax (a caller's own single quoted
    phrase, e.g. ``'"exact_symbol_name"'``, the shape B2's own examples use) is passed through unchanged. Anything
    else is tokenised (the same word-shape the tokenizer itself keeps whole -- alphanumeric plus ``_``) and OR'd
    together: a safe, syntactically valid, recall-favouring lexical query that can never raise fts5's own syntax
    error, whatever punctuation the source text contains."""
    text = text or ""
    if _FTS_QUOTED_RE.match(text):
        return text
    tokens = _FTS_TOKEN_RE.findall(text)
    if not tokens:
        return '""'
    return " OR ".join(f'"{t}"' for t in tokens)


def _product_commit(resolved_view: "viewmod.ResolvedView") -> Optional[str]:
    for r in resolved_view.config.refs:
        if r.role == "product" and r.name in resolved_view.named:
            return resolved_view.named[r.name].commit
    return None


def _extract_symbol_names(text: Optional[str]) -> list:
    """Candidate code-route names out of free text, using the SAME symbol-shaped-token pattern
    ``govbridge.route.router.select_routes`` already uses to decide whether the code route should run at all --
    never a new, separate notion of "looks like a symbol"."""
    if not text:
        return []
    out: list = []
    for m in routermod._SYMBOL_TOKEN_RE.finditer(text):
        tok = m.group(0).rstrip("()")
        if tok and tok not in out:
            out.append(tok)
    return out


def build_real_routes(view_path: Optional[str] = None, repo: Optional[str] = None,
                       registry_path: Optional[str] = None) -> RouteSet:
    """One ``RouteSet`` whose four slots call the real lexical/semantic/code/exact routes, each hit carrying real
    authority classification. Every piece of shared state (the resolved view, the registry, the mandatory-items
    index, the store connection) is built ONCE here and closed over by the four route functions, never reloaded
    per query or per hit."""
    from govbridge import GOV_BRIDGE_DOMAIN
    import os

    view_path = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    resolved_view = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)
    reg = registrymod.load(registry_path or registrymod._default_registry_path(), verify_commit="records",
                            view_path=view_path, repo=repo)
    mandatory_items = lifecyclemod._load_mandatory_items(repo=repo, view_path=view_path)
    product_commit = _product_commit(resolved_view)

    # REPAIR_DAG.yaml node R1-GA1 (OD-BR-05 section 2: "independent facets MAY be retrieved concurrently"): a
    # sqlite3.Connection may only be used by the thread that created it (this surfaced as a real
    # "SQLite objects created in a thread can only be used in that same thread" failure once govbridge.gather.engine
    # started running facets on a thread pool). The single connection this function used to build ONCE and share
    # across every call is now built ONCE PER THREAD instead -- still never reopened per query or per hit WITHIN one
    # thread, and every single-threaded caller (govbridge search, govbridge.compile.packet, every existing test)
    # sees exactly one connection for the RouteSet's whole lifetime, unchanged.
    _local = threading.local()

    def _conn():
        # REPAIR_DAG.yaml node R1-GA1 (second reopening, coordinator addendum): this connection's own two uses
        # (_semantic_classify's SELECT, and classify_occ -> authoritylayer.classify_hit) are both queries, never a
        # build -- but classify_hit itself still calls authoritylayer.ensure_schema(conn) on every call, a
        # pre-existing lazy-schema-creation pattern in a module this node is authorized to touch for exactly one
        # purpose (the record_def_by_path index, not this). Switching this connection to
        # store.open_db_readonly() breaks that ensure_schema call -- and therefore classification itself -- on any
        # store whose authority-layer schema was never separately built (this file's OWN pre-existing tests build
        # a bare git repo and never run govbridge.authority.layer's builder, exactly this situation), which is why
        # this stays on store.open_db() rather than the stricter read-only connection lexical/semantic queries now
        # use: it already tolerates a read-only STORE FILE (every write it attempts is wrapped, see its own
        # docstring), which is what this node's own required tests exercise, without this out-of-scope regression.
        # Named here, not silently patched: govbridge.authority.layer's own schema lifecycle -- ensure_schema
        # called from a query path at all -- is unresolved, for whoever owns that module next.
        c = getattr(_local, "conn", None)
        if c is None:
            c = storemod.open_db()
            _local.conn = c
        return c

    def classify_occ(path: Optional[str], commit: Optional[str], line_start=None, line_end=None) -> tuple:
        if not path:
            return UNCLASSIFIED
        try:
            c = authoritylayer.classify_hit(_conn(), path, commit, line_start, line_end, reg=reg,
                                             mandatory_items=mandatory_items, repo=repo, view_path=view_path)
            return (c.cls or "UNCLASSIFIED"), (c.lifecycle or "UNKNOWN")
        except Exception:
            return UNCLASSIFIED

    # REPAIR_DAG.yaml node R1-GA1 reopening, defect 1: a scoped facet's SQL-level pre-filter needs plain PATH GLOBS,
    # not a class name -- this is the ONE place that translates "these authority classes" into "these globs",
    # reusing the registry's OWN class_rules (``govbridge.authority.registry.Registry.class_rules``, already loaded
    # above) rather than a second, hand-maintained list (OC-BR-02: generic, config-driven, never a hard-coded path).
    # Cached per distinct ``scope_classes`` tuple -- the registry itself never changes within one RouteSet's life.
    _path_globs_cache: dict = {}

    def _path_globs_for_classes(scope_classes: Optional[tuple]) -> tuple:
        if not scope_classes:
            return ()
        key = tuple(sorted(scope_classes))
        cached = _path_globs_cache.get(key)
        if cached is None:
            cached = tuple(rule.glob for rule in reg.class_rules if rule.cls in scope_classes)
            _path_globs_cache[key] = cached
        return cached

    def _apply_scope_assertion(hits: list, scope_classes: Optional[tuple], lifecycle_scope: Optional[tuple]) -> tuple:
        """The shared "keep the post-filter only as an assertion" step every route applies to its ALREADY-classified
        hits (REPAIR_DAG.yaml node R1-GA1 reopening, defect 1). For code/exact this is the PRIMARY scope mechanism
        (their result sets are already small and bounded by fanout/id-lookup, so there is no large corpus-wide
        ranking to push a SQL filter into); for lexical/semantic it is the secondary check behind the SQL
        pre-filter. Returns ``(kept, dropped_count)``."""
        if scope_classes is None and lifecycle_scope is None:
            return hits, 0
        kept: list = []
        dropped = 0
        for h in hits:
            if scope_classes is not None and h.authority_class not in scope_classes:
                dropped += 1
                continue
            if lifecycle_scope is not None and h.lifecycle not in lifecycle_scope:
                dropped += 1
                continue
            kept.append(h)
        return kept, dropped

    # --- lexical -------------------------------------------------------------------------------------------

    def _lexical_classify(item: "lexicalquery.RetrievedItem") -> tuple:
        occ0 = item.occurrences[0] if item.occurrences else None
        if occ0 is None:
            return UNCLASSIFIED
        return classify_occ(occ0.path, occ0.commit, item.start_line, item.end_line)

    def lexical_route(text: Optional[str] = None, seeds=None, k: Optional[int] = None, exclude=None,
                       exclude_counter=None, offset: int = 0, page_info_out: Optional[dict] = None,
                       scope_classes: Optional[tuple] = None, lifecycle_scope: Optional[tuple] = None,
                       **_kw) -> list:
        if not text:
            return []
        k = lexicalquery.DEFAULT_K if k is None else k
        # R1-RX (OBS-BR-08): the ambient task context's own exclusions are merged in HERE, so this route excludes
        # them even for a caller that passes exclude=None (the CLI default before this repair) -- see
        # govbridge.core.taskctx's module docstring.
        exclude = taskctxmod.current().merge_exclude(exclude)
        # REPAIR_DAG.yaml node R1-GA1 reopening, defect 1: scope is pushed DOWN into the SQL itself
        # (lexicalquery.query's own scope_classes/lifecycle_scope/scope_path_globs params) so a scoped facet's page
        # is already in scope, rather than filtered client-side after paging through a corpus-wide ranking.
        scope_path_globs = _path_globs_for_classes(scope_classes)
        result = lexicalquery.query(_safe_fts_query(text), k=k, exclude=exclude, offset=offset, view_path=view_path,
                                     repo=repo, classify=_lexical_classify, scope_classes=scope_classes,
                                     lifecycle_scope=lifecycle_scope, scope_path_globs=scope_path_globs)
        # REPAIR_PLAN.md section 2.4 ("lexical and semantic take an offset"): the paging metadata lexicalquery.query
        # already computes (govbridge.gather.engine's own per-facet cursor) -- an out-param, the SAME idiom
        # exclude_counter already uses here, since RouteFn's own contract returns a plain list of RouteHit.
        if page_info_out is not None:
            page_info_out["next_offset"] = result.get("next_offset")
            page_info_out["total_matching_chunks"] = result.get("total_matching_chunks")
        if exclude and exclude_counter is not None:
            # govbridge.lexical.query already filtered internally (out of this node's mutation scope, so it
            # exposes no count of its own) -- a second, exclude=None call over the SAME query measures how many
            # candidates would have leaked through by default, the same double-run technique
            # ARCHITECTURE/REPAIR-1/evidence/tools/exclusion_probe.py itself used to first diagnose RC-8. Its
            # result is used only to count; it is never returned or delivered as a hit.
            raw = lexicalquery.query(_safe_fts_query(text), k=k, exclude=None, offset=offset, view_path=view_path,
                                      repo=repo, classify=_lexical_classify, scope_classes=scope_classes,
                                      lifecycle_scope=lifecycle_scope, scope_path_globs=scope_path_globs)
            exclude_counter.bump(sum(
                1 for h in raw["hits"]
                if any(pathrules.any_glob_match(o["path"], exclude) is not None for o in h["occurrences"])
            ))
        hits = []
        for h in result["hits"]:
            occs = tuple(
                RouteOccurrence(ref=o["ref"], commit=o["commit"], path=o["path"], version_status=o["version_status"],
                                 canonical_ref=o.get("canonical_ref"), canonical_commit=o.get("canonical_commit"),
                                 line_start=h["start_line"], line_end=h["end_line"])
                for o in h["occurrences"]
            )
            hits.append(RouteHit(unit_id=h["item_id"], unit_kind="chunk", route="lexical", rank=h["rank"],
                                  occurrences=occs, text=h["text"], authority_class=h.get("authority_class"),
                                  lifecycle=h.get("lifecycle")))
        # The SQL-level pre-filter above is a PRE-filter, not the final word (its Tier B path-glob half, and a
        # stale/partial authority layer, can both let an out-of-scope hit through); the REAL classification this
        # route already computed for every hit is the final, asserted check -- REPAIR_DAG.yaml node R1-GA1
        # reopening: "keep the post-filter only as an assertion." A drop here means the SQL pre-filter itself was
        # imperfect for this hit, never that scoped paging is silently degrading to corpus-wide paging.
        hits, scope_dropped = _apply_scope_assertion(hits, scope_classes, lifecycle_scope)
        if page_info_out is not None:
            page_info_out["scope_assertion_dropped"] = scope_dropped
        return hits

    # --- semantic --------------------------------------------------------------------------------------------

    def _semantic_classify(blob_id: str) -> tuple:
        row = _conn().execute("SELECT path, commit_id FROM occurrence WHERE blob_id=? LIMIT 1", (blob_id,)).fetchone()
        if row is None:
            return UNCLASSIFIED
        return classify_occ(row[0], row[1])

    def semantic_route(text: Optional[str] = None, seeds=None, k: Optional[int] = None, exclude=None,
                        exclude_counter=None, offset: int = 0, page_info_out: Optional[dict] = None,
                        scope_classes: Optional[tuple] = None, lifecycle_scope: Optional[tuple] = None,
                        **_kw) -> list:
        if not text:
            return []
        k = lexicalquery.DEFAULT_K if k is None else k
        exclude = taskctxmod.current().merge_exclude(exclude)
        # REPAIR_DAG.yaml node R1-GA1 reopening, defect 1: restrict the candidate set by class BEFORE top-k, never
        # after (semanticsearch.search -> vectors.search's own scope_classes/lifecycle_scope/scope_path_globs).
        scope_path_globs = _path_globs_for_classes(scope_classes)
        result = semanticsearch.search(text, k=k, view_path=view_path, repo=repo, classify=_semantic_classify,
                                        offset=offset, scope_classes=scope_classes, lifecycle_scope=lifecycle_scope,
                                        scope_path_globs=scope_path_globs)
        if page_info_out is not None:
            page_info_out["next_offset"] = result.get("next_offset")
        hits = []
        for r in result["results"]:
            occ_d = r.get("occurrence")
            if occ_d is None:
                continue
            if exclude and pathrules.any_glob_match(occ_d["path"], exclude) is not None:
                if exclude_counter is not None:
                    exclude_counter.bump()
                continue
            occs = (RouteOccurrence(ref=occ_d["ref"], commit=occ_d["commit"], path=occ_d["path"],
                                     version_status=r.get("version_status") or "ABSENT",
                                     canonical_ref=r.get("canonical_ref"), canonical_commit=r.get("canonical_commit"),
                                     line_start=occ_d.get("line_start"), line_end=occ_d.get("line_end")),)
            hits.append(RouteHit(unit_id=r["id"], unit_kind="chunk", route="semantic", rank=r["rank"],
                                  occurrences=occs, text=None, authority_class=r.get("authority_class"),
                                  lifecycle=r.get("lifecycle")))
        # The SQL pre-filter's assertion (kept only as an assertion -- see lexical_route's own comment).
        hits, scope_dropped = _apply_scope_assertion(hits, scope_classes, lifecycle_scope)
        if page_info_out is not None:
            page_info_out["scope_assertion_dropped"] = scope_dropped
        return hits

    # --- code ------------------------------------------------------------------------------------------------

    # The shaped code_conn (govbridge.graph.code_bridge) wires CALLEES/TESTS/READS_KEY against the real B3 tables,
    # exactly the way govbridge.compile.packet.Compiler.code_conn already does for why/impact (routed issue
    # B5/BR-AR-0007). ``blob_to_path`` is plain, read-only-after-construction Python data, safe to build once and
    # share; the sqlite3 connection itself is NOT (same thread-affinity issue as ``_conn()`` above), so it is built
    # once PER THREAD instead -- "shared state built once" now means "once per thread that ever calls the code
    # route," never reopened per query or per hit within one thread.
    _blob_to_path_state = {"attempted": False, "map": {}}
    _code_local = threading.local()

    def _shaped_code_conn() -> tuple:
        if not _blob_to_path_state["attempted"]:
            _blob_to_path_state["attempted"] = True
            if product_commit:
                try:
                    raw_conn = codesymbols._open_conn()
                    entries = codesymbols.ensure_indexed(raw_conn, product_commit, repo=repo)
                    _blob_to_path_state["map"] = {blob_id: p for p, blob_id in entries}
                except Exception:
                    _blob_to_path_state["map"] = {}
        if not hasattr(_code_local, "conn"):
            code_conn = None
            if product_commit:
                try:
                    from govbridge.graph import code_bridge
                    code_conn = code_bridge.build_shaped_code_connection(product_commit, repo=repo)
                except Exception:
                    code_conn = None
            _code_local.conn = code_conn
        return _code_local.conn, _blob_to_path_state["map"]

    # BR-AR-0015 reopening, defect 2: a fixed, generous fallback when a caller does not pass its own profile
    # fan-out -- used by the query-mode (T3) path, which is not bounded per symbol the way a T1 seed's own
    # expansion is, and by any caller (e.g. tests/route/test_real_routes.py) that predates this reopening.
    _DEFAULT_FANOUT = {"max_callers": 8, "max_callees": 8, "max_tests": 8, "max_reads_key_values": 8,
                        "max_reads_key_consumers": 8}

    def _code_hit_from_definition(d: dict, rank: int, tier: str, citation_label: Optional[str] = None) -> RouteHit:
        cls, lifecycle = classify_occ(d["path"], product_commit, d["start_line"], d["end_line"])
        vstatus = resolved_view.classify_occurrence(d["path"], product_commit).status
        occs = (RouteOccurrence(ref="product", commit=product_commit, path=d["path"], version_status=vstatus,
                                 line_start=d["start_line"], line_end=d["end_line"]),)
        # T1 (pinned, ARCHITECTURE.md section 7.2's G row) is specifically "a citation FOUND IN THE SEED
        # RECORDS" -- a definition resolved from a genuine record citation (``citation_label`` set, by
        # ``govbridge.compile.codeseeds``). A seed that is ALREADY a bare symbol name, with no citation to speak
        # of (the task named the symbol directly, not a record that cites it), keeps its pre-reopening behaviour
        # exactly: an ordinary RETRIEVED code-route hit, no tier -- there is no "citation" here to pin.
        is_t1 = tier == "T1" and citation_label is not None
        resolution = citation_label
        text = f"{d['kind']} {d['qualified_name']}"
        if resolution:
            text += f" [citation:{resolution}]"
        delivery = "PINNED" if is_t1 else "RETRIEVED"
        effective_tier = None if (tier == "T1" and not is_t1) else tier
        return RouteHit(unit_id=d["symbol_id"], unit_kind="symbol", route="code", rank=rank, occurrences=occs,
                         text=text, authority_class=cls, lifecycle=lifecycle, delivery=delivery,
                         tier=effective_tier, resolution=resolution)

    def _code_hit_from_caller(row: dict, rank: int, tier: str) -> RouteHit:
        path, _, line = row["at"].partition(":")
        line_i = int(line) if line.isdigit() else None
        cls, lifecycle = classify_occ(path, product_commit, line_i, line_i)
        vstatus = resolved_view.classify_occurrence(path, product_commit).status if path else "ABSENT"
        occs = (RouteOccurrence(ref="product", commit=product_commit, path=path, version_status=vstatus,
                                 line_start=line_i, line_end=line_i),)
        return RouteHit(unit_id=f"CALLS:{row['at']}", unit_kind="occurrence", route="code", rank=rank,
                         occurrences=occs, text=f"{row['callee_text']} [{row['label']}]", authority_class=cls,
                         lifecycle=lifecycle, tier=tier, resolution=row["label"])

    def _code_hit_from_edge(edge, blob_to_path: dict, rank: int, tier: str) -> Optional[RouteHit]:
        """A CALLEES/TESTS/READS_KEY edge from ``govbridge.graph.derive`` (its ``evidence_occurrence`` is
        ``blob_id:line`` against the SHAPED connection's own schema -- never a path, so it is mapped back through
        ``blob_to_path`` here, the one place code_route does that translation)."""
        blob_id, _, line_s = (edge.evidence_occurrence or "").partition(":")
        path = blob_to_path.get(blob_id)
        if path is None:
            return None
        line_i = int(line_s) if line_s.isdigit() else edge.evidence_line
        cls, lifecycle = classify_occ(path, product_commit, line_i, line_i)
        vstatus = resolved_view.classify_occurrence(path, product_commit).status
        occs = (RouteOccurrence(ref="product", commit=product_commit, path=path, version_status=vstatus,
                                 line_start=line_i, line_end=line_i),)
        return RouteHit(unit_id=f"{edge.type}:{path}:{line_i}:{edge.dst}", unit_kind="occurrence", route="code",
                         rank=rank, occurrences=occs, text=f"{edge.type} {edge.src} -> {edge.dst} [{edge.derivation}]",
                         authority_class=cls, lifecycle=lifecycle, tier=tier, resolution=edge.derivation)

    def _edge_sort_key(edge) -> tuple:
        return (edge.evidence_occurrence or "", edge.dst or "")

    def _expand_symbol(qname: str, conn, blob_to_path: dict, hits: list, exclude, fanout: dict,
                        exclude_counter=None, include_callees: bool = True, include_tests: bool = True,
                        include_reads_key: bool = True, page_size: Optional[int] = None,
                        cursor_in: Optional[dict] = None, cursor_out: Optional[dict] = None,
                        seed_key: Optional[str] = None) -> None:
        """T2 (ARCHITECTURE.md section 7.2's G row, BR-HO-0015 defect 2): direct callees, TESTS edges, and the
        READS_KEY consumers of any literal key read AT this T1 symbol -- callers are covered by ``codesymbols.
        callers`` in the caller loop below. Every list is sorted into a STABLE, deterministic order (B3's own
        SQL carries no ORDER BY) and then capped to the profile's fan-out limit BEFORE any RouteHit is built --
        "bound candidate generation per symbol", never just the rendered output after the fact.

        ``include_callees``/``include_tests``/``include_reads_key`` (REPAIR_DAG.yaml node R1-GA1's ``dependencies``
        vs ``dependents`` vs ``tests`` facets, ``config/facets.yaml``): every caller that omits them keeps getting
        ALL THREE, byte-for-byte as before. ``page_size``/``cursor_in``/``cursor_out`` page the TESTS edges through
        R1-RL's own ``derivemod.tests_of`` cursor (never re-implemented here); omitted, that edge type keeps its
        pre-existing fanout-capped, unpaged behaviour too. READS_KEY consumers stay fanout-capped either way (R1-RL
        did not add paging to the "which keys does this symbol read" half, only to "who else reads key K")."""
        if conn is None:
            return
        if include_callees:
            callees = sorted(derivemod.callees_of(conn, qname), key=_edge_sort_key)[:fanout.get("max_callees", 8)]
            for edge in callees:
                h = _code_hit_from_edge(edge, blob_to_path, len(hits) + 1, "T2")
                if h is None:
                    continue
                if exclude and pathrules.any_glob_match(h.occurrences[0].path, exclude) is not None:
                    if exclude_counter is not None:
                        exclude_counter.bump()
                    continue
                hits.append(h)
        if include_tests:
            cursor_key = (seed_key or qname, "tests")
            cur = (cursor_in or {}).get(cursor_key)
            if page_size is not None:
                page = derivemod.tests_of(conn, qname, page_size=page_size, cursor=cur)
                tests = sorted(page["items"], key=_edge_sort_key)
                if cursor_out is not None:
                    cursor_out[cursor_key] = page["next_cursor"]
            else:
                tests = sorted(derivemod.tests_of(conn, qname), key=_edge_sort_key)[:fanout.get("max_tests", 8)]
            for edge in tests:
                h = _code_hit_from_edge(edge, blob_to_path, len(hits) + 1, "T2")
                if h is None:
                    continue
                if exclude and pathrules.any_glob_match(h.occurrences[0].path, exclude) is not None:
                    if exclude_counter is not None:
                        exclude_counter.bump()
                    continue
                hits.append(h)
        if include_reads_key:
            try:
                key_rows = conn.execute(
                    "SELECT DISTINCT value FROM literal WHERE enclosing_symbol=?", (qname,)).fetchall()
            except Exception:
                key_rows = []
            key_values = sorted((v for (v,) in key_rows))[:fanout.get("max_reads_key_values", 8)]
            for key_value in key_values:
                consumers = sorted(derivemod.reads_key_of(conn, key_value),
                                    key=_edge_sort_key)[:fanout.get("max_reads_key_consumers", 8)]
                for edge in consumers:
                    h = _code_hit_from_edge(edge, blob_to_path, len(hits) + 1, "T2")
                    if h is None:
                        continue
                    if exclude and pathrules.any_glob_match(h.occurrences[0].path, exclude) is not None:
                        if exclude_counter is not None:
                            exclude_counter.bump()
                        continue
                    hits.append(h)

    def _code_hit_from_bare_occurrence(occ: dict, rank: int) -> Optional[RouteHit]:
        """T1 (ARCHITECTURE.md section 7.2's G row, BR-HO-0015 defect 3): the CITED LINE ITSELF, always emitted
        for a path:line citation -- whether or not an enclosing symbol was ALSO found (that is a separate,
        additional T1 definition hit, never a substitute). This is also how a cited evidence probe surfaces,
        generically, since a non-code path never resolves to a symbol."""
        path, line_i, label = occ.get("path"), occ.get("line"), occ.get("label")
        if not path:
            return None
        cls, lifecycle = classify_occ(path, product_commit, line_i, line_i)
        vstatus = resolved_view.classify_occurrence(path, product_commit).status
        occs = (RouteOccurrence(ref="product", commit=product_commit, path=path, version_status=vstatus,
                                 line_start=line_i, line_end=line_i),)
        return RouteHit(unit_id=f"CITED:{path}:{line_i}", unit_kind="occurrence", route="code", rank=rank,
                         occurrences=occs, text=f"[cited line] [{label}]", authority_class=cls, lifecycle=lifecycle,
                         delivery="PINNED", tier="T1", resolution=label)

    def code_route(text: Optional[str] = None, seeds=None, k: Optional[int] = None, exclude=None, seed_labels=None,
                   bare_occurrences=None, fanout=None, exclude_counter=None, include_callers: bool = True,
                   include_callees: bool = True, include_tests: bool = True, include_reads_key: bool = True,
                   page_size: Optional[int] = None, cursor_in: Optional[dict] = None,
                   cursor_out: Optional[dict] = None, scope_classes: Optional[tuple] = None,
                   lifecycle_scope: Optional[tuple] = None, scope_info_out: Optional[dict] = None,
                   **_kw) -> list:
        """``include_callers``/``include_callees``/``include_tests``/``include_reads_key`` and
        ``page_size``/``cursor_in``/``cursor_out`` (REPAIR_DAG.yaml node R1-GA1): every existing caller (``govbridge
        search``, ``govbridge.compile.packet``) passes none of these, so it sees EXACTLY the pre-existing behaviour
        -- all four edge kinds, fanout-capped, unpaged. ``govbridge.gather.engine`` is the one caller that narrows
        the edge kinds per facet (``dependencies`` vs ``dependents`` vs ``tests``, ``config/facets.yaml``'s
        ``code_mode``) and pages ``callers``/``tests`` round over round through R1-RL's own cursor, keyed by
        ``(seed name, edge type)`` in ``cursor_in``/``cursor_out`` so a multi-seed call pages every seed
        independently.

        ``scope_classes``/``lifecycle_scope`` (REPAIR_DAG.yaml node R1-GA1 reopening, defect 1): applied as the
        SAME post-hoc assertion every route uses (``_apply_scope_assertion``) -- this route's own result sets are
        already small and bounded (one symbol's definitions/callers/callees, or a fanout-capped query-mode top-k),
        so there is no large corpus-wide ranking to push a SQL pre-filter into; a post-filter here has no
        "advances the cursor without advancing the count" failure mode to guard against the way lexical/semantic
        did. ``scope_info_out``, filled with ``{"dropped": n}`` when given, discloses how many hits this call
        itself dropped, so a caller (govbridge.gather.engine) can tell scoped code-route filtering apart from a
        genuinely empty result."""
        if not product_commit:
            return []
        exclude = taskctxmod.current().merge_exclude(exclude)
        k = lexicalquery.DEFAULT_K if k is None else k
        is_seeded = seeds is not None  # T1/T2 (a task seed's own citations) vs T3 (free-text query retrieval)
        names = list(seeds or []) or _extract_symbol_names(text)
        seed_labels = seed_labels or {}
        fanout = fanout or _DEFAULT_FANOUT
        conn, blob_to_path = _shaped_code_conn()
        hits: list = []
        expanded: set = set()
        def_tier = "T1" if is_seeded else "T3"
        caller_tier = "T2" if is_seeded else "T3"
        for name in names:
            try:
                defs_out = codesymbols.definitions(name, product_commit, repo=repo)
            except Exception:
                defs_out = {"definitions": []}
            for d in defs_out.get("definitions", []):
                if exclude and pathrules.any_glob_match(d["path"], exclude) is not None:
                    if exclude_counter is not None:
                        exclude_counter.bump()
                    continue
                hits.append(_code_hit_from_definition(d, len(hits) + 1, def_tier,
                                                        citation_label=seed_labels.get(name)))
                qname = d["qualified_name"]
                # T2 expansion only ever runs from a T1 (seeded) definition -- a query-mode (T3) hit's own
                # callers/callees are themselves at most T3, never T2, so query mode never expands here.
                if is_seeded and qname not in expanded:
                    expanded.add(qname)
                    _expand_symbol(qname, conn, blob_to_path, hits, exclude, fanout, exclude_counter=exclude_counter,
                                    include_callees=include_callees, include_tests=include_tests,
                                    include_reads_key=include_reads_key, page_size=page_size, cursor_in=cursor_in,
                                    cursor_out=cursor_out, seed_key=name)
            if include_callers:
                cursor_key = (name, "callers")
                cur = (cursor_in or {}).get(cursor_key)
                try:
                    if page_size is not None:
                        callers_out = codesymbols.callers(name, product_commit, repo=repo, page_size=page_size,
                                                           cursor=cur)
                    else:
                        callers_out = codesymbols.callers(name, product_commit, repo=repo)
                except Exception:
                    callers_out = {"callers": []}
                caller_rows = callers_out.get("callers", [])
                if page_size is not None:
                    if cursor_out is not None:
                        cursor_out[cursor_key] = callers_out.get("next_cursor")
                elif is_seeded:
                    caller_rows = caller_rows[:fanout.get("max_callers", 8)]
                for row in caller_rows:
                    path = row["at"].split(":", 1)[0]
                    if exclude and pathrules.any_glob_match(path, exclude) is not None:
                        if exclude_counter is not None:
                            exclude_counter.bump()
                        continue
                    hits.append(_code_hit_from_caller(row, len(hits) + 1, caller_tier))
        for occ in (bare_occurrences or []):
            if exclude and occ.get("path") and pathrules.any_glob_match(occ["path"], exclude) is not None:
                if exclude_counter is not None:
                    exclude_counter.bump()
                continue
            h = _code_hit_from_bare_occurrence(occ, len(hits) + 1)
            if h is not None:
                hits.append(h)
        hits, scope_dropped = _apply_scope_assertion(hits, scope_classes, lifecycle_scope)
        if scope_info_out is not None:
            scope_info_out["dropped"] = scope_dropped
        return hits[:k] if (text and not seeds and not bare_occurrences) else hits

    # --- exact -----------------------------------------------------------------------------------------------

    def exact_route(text: Optional[str] = None, seeds=None, k: Optional[int] = None, exclude=None,
                     exclude_counter=None, scope_classes: Optional[tuple] = None,
                     lifecycle_scope: Optional[tuple] = None, scope_info_out: Optional[dict] = None,
                     **_kw) -> list:
        """``scope_classes``/``lifecycle_scope`` (REPAIR_DAG.yaml node R1-GA1 reopening, defect 1): applied as a
        post-hoc assertion (``_apply_scope_assertion``), same rationale as ``code_route``'s own docstring -- an id
        lookup's mention sites are already a small, bounded set. Truncation to ``k`` happens AFTER the scope
        filter, not before, so a scoped caller gets up to ``k`` IN-SCOPE mentions rather than up to ``k`` raw ones
        that scope then thins out further."""
        if not text:
            return []
        k = lexicalquery.DEFAULT_K if k is None else k
        exclude = taskctxmod.current().merge_exclude(exclude)
        try:
            result = exactmod.id_lookup(text, view_path=view_path, repo=repo)
        except Exception:
            return []
        hits = []
        commit = result.get("commit")
        for m in result.get("mention_sites", []):
            path, line = m.get("path"), m.get("line")
            if exclude and path and pathrules.any_glob_match(path, exclude) is not None:
                if exclude_counter is not None:
                    exclude_counter.bump()
                continue
            cls, lifecycle = classify_occ(path, commit, line, line)
            vstatus = resolved_view.classify_occurrence(path, commit).status if path and commit else "ABSENT"
            occs = (RouteOccurrence(ref=result.get("ref") or "?", commit=commit, path=path, version_status=vstatus,
                                     line_start=line, line_end=line),)
            hits.append(RouteHit(unit_id=f"{path}:{line}", unit_kind="occurrence", route="exact",
                                  rank=len(hits) + 1, occurrences=occs, text=m.get("text"), authority_class=cls,
                                  lifecycle=lifecycle))
        hits, scope_dropped = _apply_scope_assertion(hits, scope_classes, lifecycle_scope)
        if scope_info_out is not None:
            scope_info_out["dropped"] = scope_dropped
        return hits[:k]

    return RouteSet(exact=exact_route, lexical=lexical_route, semantic=semantic_route, code=code_route)
