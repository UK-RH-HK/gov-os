"""The deterministic closure over referenced ids, with no model (W1-20; DEC-033, DEC-080, DEC-391).

``closure(root, ids, depth)`` follows the start ids through the record graph of the store (the eight typed
edges, both ways) and through the code index (a symbol's callers and callees), ``depth`` hops far. An id that
is a record's id is a record; a start id that is none, and a name reached from a symbol, is asked of the code
index; a record's edge to no record is unresolved without asking. Everything is sorted: the same store, index
and working tree give the same result. It only reads: it builds neither the store nor the code index.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

COMPLETE, DEPTH_LIMIT, FACET_UNAVAILABLE, UNRESOLVED = \
    "CLOSURE_COMPLETE", "DEPTH_LIMIT_REACHED", "FACET_UNAVAILABLE", "UNRESOLVED"
# The stopping reason when unresolved ids are the only gaps: with the owner (DEC-391, DP-5). Only this line names it.
UNRESOLVED_ALONE = "UNRESOLVED_IDS"
# Hops for an impact radius: R0 and R1, R2, R3 and above (DEC-035's placeholders, to tune from telemetry).
DEPTH_R1, DEPTH_R2, DEPTH_R3 = 1, 3, 8

__all__ = ["closure", "depth_of_radius"]


def depth_of_radius(radius: int) -> int:
    return DEPTH_R1 if radius <= 1 else DEPTH_R2 if radius == 2 else DEPTH_R3


def _symbol(root: Path, name: str) -> set | None:
    """The names of the callers and callees of the symbol ``name``; None when the index has no such symbol."""
    from gov import codeintel

    if not codeintel.definitions(root, name):
        return None
    return {entry["name"] for entry in codeintel.callers(root, name) + codeintel.callees(root, name)}


def closure(root: Path, ids: list[str], depth: int) -> dict:
    """The result of ``gov closure``: what is at most ``depth`` hops from ``ids``, and the gaps."""
    from gov import store
    from gov.cli.errors import GovError

    if depth < 0:
        raise GovError("CLOSURE_DEPTH_INVALID", f"the depth is {depth}: it is a number of hops, 0 or more")
    root, near = Path(root), {}
    connection = store.connect(root)
    try:
        records = {row[0] for row in connection.execute("SELECT id FROM records")}
        for source, target in connection.execute("SELECT source, target FROM edges"):
            near.setdefault(source, set()).add(target)
            near.setdefault(target, set()).add(source)
    finally:
        connection.close()
    status = subprocess.run(["git", "--no-optional-locks", "-C", str(root), "-c", "core.quotePath=false", "status",
                             "--porcelain"], capture_output=True, text=True, check=True).stdout
    kinds, gaps, code, front, askable = {}, {}, "not_asked", set(ids), set(ids)
    for _ in range(depth + 1):
        named = set()
        for item in sorted(front):
            if item in records:
                kinds[item], found = "record", near.get(item, set())
            elif item not in askable:
                gaps[item], found = UNRESOLVED, set()
            else:
                try:
                    if code == "unavailable":  # it could not answer once: it is not asked again
                        raise RuntimeError
                    found, code = _symbol(root, item), "available"
                except (RuntimeError, OSError):
                    found, code = set(), "unavailable"
                    gaps[item] = FACET_UNAVAILABLE
                else:
                    if found is None:
                        gaps[item], found = UNRESOLVED, set()
                    else:
                        kinds[item] = "symbol"
                        askable |= found
            named |= found
        front = named - kinds.keys() - gaps.keys()
    gaps.update(dict.fromkeys(front, DEPTH_LIMIT))  # named at the depth and not looked up
    reasons = set(gaps.values())
    stopping = next((reason for reason in (FACET_UNAVAILABLE, DEPTH_LIMIT) if reason in reasons),
                    UNRESOLVED_ALONE if reasons else COMPLETE)
    return {"start": sorted(set(ids)), "depth": depth, "stopping_reason": stopping,
            "closure": [{"id": item, "kind": kinds[item]} for item in sorted(kinds)],
            "gaps": [{"id": item, "reason": gaps[item]} for item in sorted(gaps)],
            "facets": {"code": code}, "uncommitted": sorted(line[3:] for line in status.splitlines())}
