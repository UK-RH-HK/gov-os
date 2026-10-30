"""Where a source stands in retrieval (W2-87; DEC-952, DEC-423, DEC-866).

A chunk of the register is the entry whose span holds it, never the register as a whole: every decision of the
register is its own record (W2-03), and all share the register's path. ``register_entries_of`` gives the mapping;
W2-55 reuses it for what the bundle leaves out (DEC-791 item 1).

The authority order is configuration (DEC-952 item 1): the path map's ``retrieval_authority`` block gives ordered
tiers, by path pattern and by the store's record type and status, and the lift per tier step. ``order`` reads it;
the fused list is lifted before the first call's cut and the reranked list after the rerank. No path, record type
or tier is named here; without the block nothing is re-sorted.
"""

from __future__ import annotations

import math
import re
from bisect import bisect_right
from collections.abc import Callable
from pathlib import Path

from gov.cli.errors import GovError
from gov.config.loader import PROJECT_DIR, read_yaml

SUPERSEDES = "SUPERSEDES"
BLOCK = "retrieval_authority"
PATH_MAP_REL = f"{PROJECT_DIR}/path-map.yaml"
_BLOCK_KEYS, _LIFT_KEYS = ("lift", "default", "tiers"), ("fused", "rerank")
_TIER_KEYS, _RULE_KEYS = frozenset({"name", "paths", "records"}), frozenset({"type", "status"})
_WORD = re.compile(r"[A-Za-z0-9_-]+")


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


def _invalid(key: str | None, reason: str) -> GovError:
    where = f"{PATH_MAP_REL}: key '{key}'" if key else PATH_MAP_REL
    return GovError("CONFIG_INVALID", f"{where}: {reason}", {"file": PATH_MAP_REL, "key": key})


def _keys(value, key: str, allowed, required) -> None:
    """``value`` is a mapping whose keys are among ``allowed`` and hold every one of ``required``."""
    if not isinstance(value, dict):
        raise _invalid(key, "must be a map")
    for name in value:
        if name not in allowed:
            raise _invalid(f"{key}.{name}", "unknown key")
    for name in required:
        if name not in value:
            raise _invalid(f"{key}.{name}", "required key is missing")


def _strings(value, key: str) -> list[str]:
    if not isinstance(value, list):
        raise _invalid(key, "must be a list")
    for item in value:
        if not isinstance(item, str) or not item:
            raise _invalid(key, "each item must be a non-empty string")
    return value


def _pattern(text: str) -> re.Pattern:
    """A path pattern matched against a repository-relative path whole: ``**`` crosses folders (``**/`` matches zero
    or more of them), ``*`` stays inside one name, every other character is itself."""
    parts, at = [], 0
    while at < len(text):
        if text.startswith("**/", at):
            parts, at = parts + ["(?:[^/]+/)*"], at + 3
        elif text.startswith("**", at):
            parts, at = parts + [".*"], at + 2
        elif text[at] == "*":
            parts, at = parts + ["[^/]*"], at + 1
        else:
            parts, at = parts + [re.escape(text[at])], at + 1
    return re.compile("".join(parts), re.DOTALL)


def read_block(root: Path) -> dict | None:
    """The path map's ``retrieval_authority`` block, validated: ``{"lift": {"fused", "rerank"}, "default": index,
    "tiers": [{"name", "paths": [pattern], "records": [(type, statuses or None)]}]}``; None when the path map or
    the block is absent. Anything else that cannot be read as an order refuses with CONFIG_INVALID (fail closed)."""
    path = Path(root) / PATH_MAP_REL
    if not path.is_file():
        return None
    document = read_yaml(path, "CONFIG_INVALID", PATH_MAP_REL)
    if not isinstance(document, dict):
        raise _invalid(None, "the top level must be a map")
    if BLOCK not in document:
        return None
    block = document[BLOCK]
    _keys(block, BLOCK, _BLOCK_KEYS, _BLOCK_KEYS)
    _keys(block["lift"], f"{BLOCK}.lift", _LIFT_KEYS, _LIFT_KEYS)
    lift = {}
    for name in _LIFT_KEYS:
        value = block["lift"][name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise _invalid(f"{BLOCK}.lift.{name}", "must be a non-negative number")
        lift[name] = float(value)
    if not isinstance(block["tiers"], list) or not block["tiers"]:
        raise _invalid(f"{BLOCK}.tiers", "must be a non-empty list")
    tiers = []
    for number, tier in enumerate(block["tiers"]):
        key = f"{BLOCK}.tiers[{number}]"
        _keys(tier, key, _TIER_KEYS, ("name",))
        if not isinstance(tier["name"], str) or not tier["name"]:
            raise _invalid(f"{key}.name", "must be a non-empty string")
        if any(tier["name"] == other["name"] for other in tiers):
            raise _invalid(f"{key}.name", f"tier '{tier['name']}' is named twice")
        rules = []
        records = tier.get("records", [])
        if not isinstance(records, list):
            raise _invalid(f"{key}.records", "must be a list")
        for place, rule in enumerate(records):
            where = f"{key}.records[{place}]"
            _keys(rule, where, _RULE_KEYS, ("type",))
            if not isinstance(rule["type"], str) or not rule["type"]:
                raise _invalid(f"{where}.type", "must be a non-empty string")
            statuses = None
            if "status" in rule:
                statuses = rule["status"] if isinstance(rule["status"], list) else [rule["status"]]
                if not statuses or not all(isinstance(status, str) and _WORD.fullmatch(status) for status in statuses):
                    raise _invalid(f"{where}.status", "each status must be a single word (letters, digits, _, -)")
                statuses = frozenset(statuses)
            rules.append((rule["type"], statuses))
        patterns = [_pattern(text) for text in _strings(tier.get("paths", []), f"{key}.paths")]
        tiers.append({"name": tier["name"], "paths": patterns, "records": rules})
    names = [tier["name"] for tier in tiers]
    if not isinstance(block["default"], str) or block["default"] not in names:
        raise _invalid(f"{BLOCK}.default", f"must name one of the tiers {names}")
    return {"lift": lift, "default": names.index(block["default"]), "tiers": tiers}


class Order:
    """The authority order of one retrieval: the block read once, and each chunk's tier steps above the default.

    A chunk's tier is the lowest (least authority) of the tiers it matches, by its path or by its record: a
    register chunk's own entry, any other file's store record. A chunk with no match is in the default tier; one
    whose record is not current (DEC-423) is never above it. Without the block every list is returned as given.
    """

    def __init__(self, block: dict | None, known: list[dict], edges: list[dict],
                 entry_of: Callable[[str, int], dict | None]):
        from gov.retrieval.retrieve import MUST_NOT_CITE_STATUSES, SUPERSEDED  # retrieve imports this module

        self.block, self.entry_of, self.register = block, entry_of, register_path(known)
        superseded = {edge["target"] for edge in edges if edge["type"] == SUPERSEDES}
        self.record_at = {}
        for record in known:
            current = (record["status"] != SUPERSEDED and record["id"] not in superseded
                       and record["status"] not in MUST_NOT_CITE_STATUSES)
            self.record_at[record["path"]] = {"type": record["type"], "status": record["status"], "current": current}
        self.steps_of: dict[tuple[str, int | None], int] = {}

    def steps(self, path: str, start_line: int | None) -> int:
        """The tier steps of a chunk above the default: positive above it, 0 at it, negative below."""
        if (path, start_line) not in self.steps_of:
            if path != self.register:
                record = self.record_at.get(path)
            else:
                record = None if start_line is None else self.entry_of(path, start_line)
            matched = [index for index, tier in enumerate(self.block["tiers"])
                       if any(pattern.fullmatch(path) for pattern in tier["paths"])
                       or (record is not None and any(kind == record["type"] and (statuses is None
                                                                                  or record["status"] in statuses)
                                                      for kind, statuses in tier["records"]))]
            default = self.block["default"]
            index = max(matched) if matched else default
            if record is not None and not record["current"]:
                index = max(index, default)
            self.steps_of[(path, start_line)] = default - index
        return self.steps_of[(path, start_line)]

    def _sorted(self, hits: list[dict], score: str, lift: float, chunks: dict) -> list[dict]:
        def adjusted(hit):
            where = chunks.get(hit["chunk_id"], hit)
            return hit[score] + lift * self.steps(where["path"], where.get("start_line"))

        return sorted(hits, key=lambda hit: -adjusted(hit))

    def fused(self, fused: list[dict], chunks: dict) -> list[dict]:
        """The fused (RRF) list on its score lifted by the ``fused`` lift, before the first call's cut; ties keep the
        fused order. ``chunks`` (``chunk_id`` -> chunk) gives a hit's start line where the hit carries none."""
        if self.block is None:
            return fused
        return self._sorted(fused, "score", self.block["lift"]["fused"], chunks)

    def reranked(self, ranked: list[dict]) -> list[dict]:
        """The reranked candidates on ``rerank_score`` lifted by the ``rerank`` lift; ties keep the rerank's order.
        Without scores the gathered (already lifted) order stands."""
        if self.block is None or not all("rerank_score" in candidate for candidate in ranked):
            return ranked
        return self._sorted(ranked, "rerank_score", self.block["lift"]["rerank"], {})


def order(root: Path, known: list[dict], edges: list[dict], entry_of: Callable[[str, int], dict | None]) -> Order:
    """The authority order of one retrieval over the store's records and edges, the block read once."""
    return Order(read_block(root), known, edges, entry_of)
