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
from typing import Optional

from govbridge.authority import layer as authoritylayer
from govbridge.authority import lifecycle as lifecyclemod
from govbridge.authority import registry as registrymod
from govbridge.code import symbols as codesymbols
from govbridge.core import exact as exactmod
from govbridge.core import pathrules
from govbridge.core import store as storemod
from govbridge.core import view as viewmod
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
    conn = storemod.open_db()
    product_commit = _product_commit(resolved_view)

    def classify_occ(path: Optional[str], commit: Optional[str], line_start=None, line_end=None) -> tuple:
        if not path:
            return UNCLASSIFIED
        try:
            c = authoritylayer.classify_hit(conn, path, commit, line_start, line_end, reg=reg,
                                             mandatory_items=mandatory_items, repo=repo, view_path=view_path)
            return (c.cls or "UNCLASSIFIED"), (c.lifecycle or "UNKNOWN")
        except Exception:
            return UNCLASSIFIED

    # --- lexical -------------------------------------------------------------------------------------------

    def _lexical_classify(item: "lexicalquery.RetrievedItem") -> tuple:
        occ0 = item.occurrences[0] if item.occurrences else None
        if occ0 is None:
            return UNCLASSIFIED
        return classify_occ(occ0.path, occ0.commit, item.start_line, item.end_line)

    def lexical_route(text: Optional[str] = None, seeds=None, k: int = 8, exclude=None, **_kw) -> list:
        if not text:
            return []
        result = lexicalquery.query(_safe_fts_query(text), k=k, exclude=exclude, view_path=view_path, repo=repo,
                                     classify=_lexical_classify)
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
        return hits

    # --- semantic --------------------------------------------------------------------------------------------

    def _semantic_classify(blob_id: str) -> tuple:
        row = conn.execute("SELECT path, commit_id FROM occurrence WHERE blob_id=? LIMIT 1", (blob_id,)).fetchone()
        if row is None:
            return UNCLASSIFIED
        return classify_occ(row[0], row[1])

    def semantic_route(text: Optional[str] = None, seeds=None, k: int = 8, exclude=None, **_kw) -> list:
        if not text:
            return []
        result = semanticsearch.search(text, k=k, view_path=view_path, repo=repo, classify=_semantic_classify)
        hits = []
        for r in result["results"]:
            occ_d = r.get("occurrence")
            if occ_d is None:
                continue
            if exclude and pathrules.any_glob_match(occ_d["path"], exclude) is not None:
                continue
            occs = (RouteOccurrence(ref=occ_d["ref"], commit=occ_d["commit"], path=occ_d["path"],
                                     version_status=r.get("version_status") or "ABSENT",
                                     canonical_ref=r.get("canonical_ref"), canonical_commit=r.get("canonical_commit"),
                                     line_start=occ_d.get("line_start"), line_end=occ_d.get("line_end")),)
            hits.append(RouteHit(unit_id=r["id"], unit_kind="chunk", route="semantic", rank=r["rank"],
                                  occurrences=occs, text=None, authority_class=r.get("authority_class"),
                                  lifecycle=r.get("lifecycle")))
        return hits

    # --- code ------------------------------------------------------------------------------------------------

    def _code_hit_from_definition(d: dict, rank: int) -> RouteHit:
        cls, lifecycle = classify_occ(d["path"], product_commit, d["start_line"], d["end_line"])
        vstatus = resolved_view.classify_occurrence(d["path"], product_commit).status
        occs = (RouteOccurrence(ref="product", commit=product_commit, path=d["path"], version_status=vstatus,
                                 line_start=d["start_line"], line_end=d["end_line"]),)
        return RouteHit(unit_id=d["symbol_id"], unit_kind="symbol", route="code", rank=rank, occurrences=occs,
                         text=f"{d['kind']} {d['qualified_name']}", authority_class=cls, lifecycle=lifecycle)

    def _code_hit_from_caller(row: dict, rank: int) -> RouteHit:
        path, _, line = row["at"].partition(":")
        line_i = int(line) if line.isdigit() else None
        cls, lifecycle = classify_occ(path, product_commit, line_i, line_i)
        vstatus = resolved_view.classify_occurrence(path, product_commit).status if path else "ABSENT"
        occs = (RouteOccurrence(ref="product", commit=product_commit, path=path, version_status=vstatus,
                                 line_start=line_i, line_end=line_i),)
        return RouteHit(unit_id=f"CALLS:{row['at']}", unit_kind="occurrence", route="code", rank=rank,
                         occurrences=occs, text=f"{row['callee_text']} [{row['label']}]", authority_class=cls,
                         lifecycle=lifecycle)

    def code_route(text: Optional[str] = None, seeds=None, k: int = 8, exclude=None, **_kw) -> list:
        if not product_commit:
            return []
        names = list(seeds or []) or _extract_symbol_names(text)
        hits: list = []
        for name in names:
            try:
                defs_out = codesymbols.definitions(name, product_commit, repo=repo)
            except Exception:
                defs_out = {"definitions": []}
            for d in defs_out.get("definitions", []):
                if exclude and pathrules.any_glob_match(d["path"], exclude) is not None:
                    continue
                hits.append(_code_hit_from_definition(d, len(hits) + 1))
            try:
                callers_out = codesymbols.callers(name, product_commit, repo=repo)
            except Exception:
                callers_out = {"callers": []}
            for row in callers_out.get("callers", []):
                path = row["at"].split(":", 1)[0]
                if exclude and pathrules.any_glob_match(path, exclude) is not None:
                    continue
                hits.append(_code_hit_from_caller(row, len(hits) + 1))
        return hits[:k] if (text and not seeds) else hits

    # --- exact -----------------------------------------------------------------------------------------------

    def exact_route(text: Optional[str] = None, seeds=None, k: int = 8, exclude=None, **_kw) -> list:
        if not text:
            return []
        try:
            result = exactmod.id_lookup(text, view_path=view_path, repo=repo)
        except Exception:
            return []
        hits = []
        commit = result.get("commit")
        for m in result.get("mention_sites", []):
            path, line = m.get("path"), m.get("line")
            if exclude and path and pathrules.any_glob_match(path, exclude) is not None:
                continue
            cls, lifecycle = classify_occ(path, commit, line, line)
            vstatus = resolved_view.classify_occurrence(path, commit).status if path and commit else "ABSENT"
            occs = (RouteOccurrence(ref=result.get("ref") or "?", commit=commit, path=path, version_status=vstatus,
                                     line_start=line, line_end=line),)
            hits.append(RouteHit(unit_id=f"{path}:{line}", unit_kind="occurrence", route="exact",
                                  rank=len(hits) + 1, occurrences=occs, text=m.get("text"), authority_class=cls,
                                  lifecycle=lifecycle))
            if len(hits) >= k:
                break
        return hits

    return RouteSet(exact=exact_route, lexical=lexical_route, semantic=semantic_route, code=code_route)
