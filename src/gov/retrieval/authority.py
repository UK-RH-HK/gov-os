"""Where a source stands in retrieval (W2-87; DEC-952, DEC-423, DEC-866).

A chunk of the register is the entry whose span holds it, never the register as a whole: every decision of the
register is its own record (W2-03), and all share the register's path. ``register_entries_of`` gives the mapping;
W2-55 reuses it for what the bundle leaves out (DEC-791 item 1).
"""

from __future__ import annotations

from bisect import bisect_right
from collections.abc import Callable
from pathlib import Path

SUPERSEDES = "SUPERSEDES"


def register_path(known: list[dict]) -> str | None:
    """The path of the register the store's records were loaded from: the one path its entries carry with a span
    (the file the path map's ``decision_register`` names); None where the store holds no register entry."""
    return next((record["path"] for record in known if record.get("span") is not None), None)


def register_entries_of(known: list[dict], edges: list[dict], root: Path) -> Callable[[str, int], dict | None]:
    """The mapping of a register chunk to its entry, built once over the store's records.

    ``known`` is the store's records (``gov.records.records``), ``edges`` its edges (only SUPERSEDES edges are
    read), ``root`` the project root the register file is read from. The returned function takes a chunk's ``path``
    and ``start_line`` (1-based) and gives the entry whose span holds that line, as ``{"id", "type", "status",
    "current", "reason", "start_line", "end_line"}``, or None: for a line before the first entry or between two
    entries' spans, and for a file that is not the register.

    An entry's lines are where its stored span stands in the register file read from ``root``: its heading line
    and as many lines as its span has. An entry is not current (``current`` False, ``reason`` given) when its status
    is SUPERSEDED or it is the target of a SUPERSEDES edge (``reason`` SUPERSEDED), or its status is must-not-cite
    (``reason`` the status; DEC-423). Deterministic: the same records, edges and file give the same answers.
    """
    from gov.retrieval.retrieve import MUST_NOT_CITE_STATUSES, SUPERSEDED  # retrieve imports this module

    path = register_path(known)
    if path is None:
        return lambda chunk_path, start_line: None
    superseded = {edge["target"] for edge in edges if edge["type"] == SUPERSEDES}
    try:
        lines = (Path(root) / path).read_text(encoding="utf-8", errors="replace").split("\n")
    except OSError:
        lines = []
    entries = sorted((record for record in known if record["path"] == path and record.get("span") is not None),
                     key=lambda record: record["id"])
    spans = {record["id"]: record["span"].split("\n") for record in entries}
    at: dict[str, list[int]] = {own[0]: [] for own in spans.values()}
    for number, line in enumerate(lines):
        if line in at:
            at[line].append(number)

    located = []
    for record in entries:
        own = spans[record["id"]]
        first = next((number for number in at[own[0]] if lines[number:number + len(own)] == own), None)
        if first is None:  # the file no longer holds the span the store loaded
            continue
        if record["status"] == SUPERSEDED or record["id"] in superseded:
            reason = SUPERSEDED
        elif record["status"] in MUST_NOT_CITE_STATUSES:
            reason = record["status"]
        else:
            reason = None
        located.append({"id": record["id"], "type": record["type"], "status": record["status"],
                        "current": reason is None, "reason": reason,
                        "start_line": first + 1, "end_line": first + len(own)})
    located.sort(key=lambda entry: (entry["start_line"], entry["id"]))
    starts = [entry["start_line"] for entry in located]

    def entry_of(chunk_path: str, start_line: int) -> dict | None:
        if chunk_path != path:
            return None
        index = bisect_right(starts, start_line) - 1
        if index < 0 or start_line > located[index]["end_line"]:
            return None
        return dict(located[index])

    return entry_of
