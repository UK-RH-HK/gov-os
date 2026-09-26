#!/usr/bin/env python3
"""``govbridge impact <seed>``: the direct-dependency/impact traversal ARCHITECTURE.md section 7.2 names for
packet section C (``graph neighbours of seeds``), exposed as its own CLI/library entry point. Combines the
PERSISTED authority-graph BFS (``govbridge.graph.traverse.bfs``, over ``authority_edge`` -- DEFINES/SUPERSESSIONS)
with the real code route's CALLS/callees (``govbridge.graph.code_bridge`` + ``govbridge.graph.derive``, routed
issue B5/BR-AR-0007: "wire [CALLS/READS_KEY/TESTS] against the real B3 tables, so why/impact reach code"), at the
canonical product ref (resolved by ROLE, never a hard-coded ref name -- OC-BR-02).
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from govbridge.core import store, view as viewmod
from govbridge.core import taskctx as taskctxmod
from govbridge.graph import code_bridge
from govbridge.graph import derive as D
from govbridge.graph import traverse as T


def _resolved_view(view_path: Optional[str] = None, repo: Optional[str] = None) -> "viewmod.ResolvedView":
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    view_path = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    vc = viewmod.load_view(view_path)
    return viewmod.resolve_view(vc, repo=repo)


def _product_commit(resolved_view: "viewmod.ResolvedView") -> Optional[str]:
    for r in resolved_view.config.refs:
        if r.role == "product" and r.name in resolved_view.named:
            return resolved_view.named[r.name].commit
    return None


def impact(seed: str, repo: Optional[str] = None, view_path: Optional[str] = None, max_depth: int = 2,
           task: Optional[taskctxmod.TaskContext] = None) -> dict:
    resolved_view = _resolved_view(view_path, repo)

    try:
        conn = store.open_db()
        graph_hops = T.bfs(conn, [seed], max_depth=max_depth)
    except Exception:
        graph_hops = {}

    product_commit = _product_commit(resolved_view)
    code_conn = code_bridge.build_shaped_code_connection(product_commit, repo=repo) if product_commit else None
    code_edges = D.callers_of(code_conn, seed) + D.callees_of(code_conn, seed) + D.tests_of(code_conn, seed)

    # R1-RX (OBS-BR-08): filtered generically by evidence-occurrence path, the same predicate every route/command
    # uses. A code-route edge's own evidence_occurrence is "blob:line" (govbridge.graph.code_bridge's shaped
    # connection), not path-shaped, so it is honestly left unfiltered here -- the same MISSING-not-guessed
    # discipline govbridge.core.taskctx.occurrence_path already documents.
    task = task or taskctxmod.current()
    excluded_hits = 0
    filtered_graph = {}
    for unit, edges in graph_hops.items():
        if unit == seed:
            continue
        kept, dropped = taskctxmod.filter_edges(edges, task)
        filtered_graph[unit] = [e.to_dict() for e in kept]
        excluded_hits += dropped

    return {
        "seed": seed,
        "max_depth": max_depth,
        "graph": filtered_graph,
        "code": [e.to_dict() for e in code_edges],
        "excluded_hits": excluded_hits,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.graph.impact")
    p.add_argument("seed")
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--view")
    p.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    taskctxmod.add_cli_arg(p)
    args = p.parse_args(argv)
    ctx = taskctxmod.from_args(args)
    result = impact(args.seed, view_path=args.view, max_depth=args.depth, task=ctx)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
