"""The readings of ``gov impact`` that are still with the owner, each in one place (W2-37 packages P-2 to P-6).

The test designer took these readings where no source spells the answer. A different answer from the owner is a
change in this file and nowhere else.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

# P-6, the output's form: the five kinds of CAP-33's acceptance line, the two graphs, and the state of a graph read in
# full and current. Any other state is a word and a reason ("stale: ...", "missing: ...", "unavailable: ...").
KINDS = ("specifications", "decisions", "tickets", "tests", "code")
RECORD, CODE = "record", "code"
OK = "ok"

# P-6, reading R2: the kind of a record. None is no kind: the record is named as a gap, never dropped.
SPECIFICATION_TYPES = ("specification", "capability")


def record_kind(record: dict, testers: set) -> str | None:
    """``testers``: the records that name a record by a ``tests`` edge."""
    if record["type"] in SPECIFICATION_TYPES:
        return "specifications"
    if record["type"] == "decision":
        return "decisions"
    if record["type"] == "task" or record["path"].startswith(".tickets/"):
        return "tickets"
    return "tests" if record["id"] in testers else None


def symbol_kind(paths: list[str]) -> str:
    """Reading R2: a symbol defined only in test files (under a ``tests`` folder) is a test; any other is code."""
    in_tests = [path for path in paths if "tests" in PurePosixPath(path).parts[:-1]]
    return "tests" if paths and len(in_tests) == len(paths) else "code"


# P-3, reading R8 (G-24, the deletable-class join): deletable only when neither graph has anything that depends on
# the item: no record edge names it and, for a symbol, the code index answers it as dead code (W1-16). What the item
# depends on itself does not count. A graph that is not read in full and current never makes an item deletable.
def deletable(named_by_records: bool, dead_in_code: bool, graphs_current: bool) -> bool:
    return graphs_current and not named_by_records and dead_in_code


# P-3 and W2-L319: the radius. R0: the whole change is deletable. Otherwise the number of the five kinds one hop
# reaches: one or none R1, two or three R2, four or five R3 (DEC-035 names the radii, not how one is found).
def radius(all_deletable: bool, kinds_at_one_hop: set) -> int:
    if all_deletable:
        return 0
    return 1 if len(kinds_at_one_hop) <= 1 else 2 if len(kinds_at_one_hop) <= 3 else 3


# P-2, W2-L319: where the depth of a radius comes from. gov.closure.depth_of_radius holds DEC-035's placeholders, read
# as hops by DEC-391 DP-3; no owner decision or measurement sets them yet. This names that source, as it is.
DEPTH_SOURCE = "DEC-035"

# P-5, reading R9: a closed specification is a ``specification`` record whose status is CLOSED.
CLOSED = "CLOSED"


def closed_specification(record: dict) -> bool:
    return record["type"] == "specification" and record["status"] == CLOSED


# Reading R10 (W2-M150): a path is governance when a namespace of the path map that matches it is governance memory.
# Without a path map, or a namespace that matches, it counts as governance: the stricter side.
def governance(namespaces: dict | None, rel: str | None) -> bool:
    if not namespaces or rel is None:
        return True
    classes = [entry.get("memory_class") for entry in namespaces.values()
               if any(_matches(rel, pattern) for pattern in entry.get("paths", []))]
    return not classes or "governance" in classes


def _matches(rel: str, pattern: str) -> bool:
    """``*`` stays inside one folder, ``**`` crosses folders (the language of the path map)."""
    parts = [re.escape(part).replace(r"\*", "[^/]*") for part in pattern.split("**")]
    return re.fullmatch(".*".join(parts), rel) is not None
