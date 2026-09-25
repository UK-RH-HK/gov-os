"""Generic graph traversal over persisted authority_edge rows (govbridge.authority.layer) plus on-demand edges
(govbridge.graph.derive). Bounded: every call takes a depth/limit; nothing here walks the whole graph.
"""
from __future__ import annotations

import sqlite3
from typing import Optional

from govbridge.graph import edges as E


def persisted_edges_from(conn: Optional[sqlite3.Connection], unit: str) -> list:
    """Every persisted edge whose dst == unit (i.e. "what points at this unit"), or [] if no store is available
    (ARCHITECTURE.md section 5.3 item 6: an absent index is never an error, only fewer derived hops)."""
    if conn is None:
        return []
    from govbridge.authority import layer as authlayer
    authlayer.ensure_schema(conn)
    rows = conn.execute(
        "SELECT src, type, dst, derivation, evidence_occurrence, evidence_line, note FROM authority_edge WHERE dst = ?",
        (unit,),
    ).fetchall()
    return [E.Edge(src=r[0], type=r[1], dst=r[2], derivation=r[3], evidence_occurrence=r[4], evidence_line=r[5],
                    note=r[6]) for r in rows]


def persisted_edges_to(conn: Optional[sqlite3.Connection], unit: str) -> list:
    """Every persisted edge whose src == unit."""
    if conn is None:
        return []
    from govbridge.authority import layer as authlayer
    authlayer.ensure_schema(conn)
    rows = conn.execute(
        "SELECT src, type, dst, derivation, evidence_occurrence, evidence_line, note FROM authority_edge WHERE src = ?",
        (unit,),
    ).fetchall()
    return [E.Edge(src=r[0], type=r[1], dst=r[2], derivation=r[3], evidence_occurrence=r[4], evidence_line=r[5],
                    note=r[6]) for r in rows]


def neighbours(conn: Optional[sqlite3.Connection], unit: str, edge_types: Optional[tuple] = None) -> list:
    """Every persisted edge touching ``unit`` in EITHER direction, optionally filtered to ``edge_types``."""
    out = persisted_edges_from(conn, unit) + persisted_edges_to(conn, unit)
    if edge_types:
        out = [e for e in out if e.type in edge_types]
    return out


def bfs(conn: Optional[sqlite3.Connection], seeds: list, max_depth: int = 2,
        edge_types: Optional[tuple] = None) -> dict:
    """A bounded breadth-first walk over persisted edges from ``seeds``, at most ``max_depth`` hops. Returns
    {unit: [Edge, ...]} -- the edge(s) that first reached each unit (never a whole-graph walk; ``max_depth`` and the
    seed set bound the work)."""
    visited: dict = {}
    frontier = list(seeds)
    for s in frontier:
        visited.setdefault(s, [])
    depth = 0
    while frontier and depth < max_depth:
        next_frontier = []
        for unit in frontier:
            for e in neighbours(conn, unit, edge_types=edge_types):
                other = e.dst if e.src == unit else e.src
                if other not in visited:
                    visited[other] = [e]
                    next_frontier.append(other)
        frontier = next_frontier
        depth += 1
    return visited
