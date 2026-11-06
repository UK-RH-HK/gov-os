"""The register's tags, relations and what is in force (W2-55; DEC-791 item 1, DEC-825 items 2 and 4, DEC-866).

The register is the file the path map of ``HEAD`` names under ``decision_register``, read as the store reads it
(``gov.store.loader``): its entries are the live entries of W2-03's grammar, in the register's order. A named
register that ``HEAD`` does not hold refuses (``STORE_REGISTER_UNREADABLE``), never an empty register.

- An entry's tags are one line ``- **Tags:** domain: <d> · scope: <s> · lands in: <paths>``, with an optional
  final `` · done`` (a one-off whose action is finished: it is not in force).
- Its relations are read from status lines: another entry's ``**Supersedes:**`` naming ids alone supersedes them; a
  ``**Supersedes:**`` naming a part (``the last point of DEC-526``) changes it, as the register's own convention
  has it (DEC-825 item 4: a partial supersession is a "Changed by" note) and as the store reads it. ``**Changes:**``,
  ``**Settles:**``, ``**Corrects:**``, ``**Reverses:**`` and ``**Withdraws:**`` change; so does the entry's own
  ``**Changed by:**`` note. A changed entry is still in force for its other parts.
- An old entry records the literal values that state its rule (``- **Values:** "300000"``), and an old or new
  entry the files kept with a reason (``- **Kept:** <path> — <reason>``); the propagation check reads both.
"""

from __future__ import annotations

import re
from pathlib import Path

DOMAINS = ("guard", "close", "retrieval", "context", "adopt", "launch", "checks", "plan", "roles", "records",
           "release")  # DEC-791 item 1: the closed list
SCOPES = {"repository": "governance/project/", "kernel": "template/governance/kernel/"}  # where each scope lands
CHANGING = ("Changes", "Settles", "Corrects", "Reverses", "Withdraws")
TAG_PARTS = ("domain", "scope", "lands in")
MARK = ("entry", "status", "changed_by", "in_force", "not_in_force")  # an item's entry mark (W2-92 S9, DEC-1073 (2))

_ID = re.compile(r"(?<![A-Za-z0-9_])DEC-[0-9]+(?![A-Za-z0-9_])")
_FIELD = re.compile(r"\*\*([A-Za-z][A-Za-z ]*):\*\*([^·]*)")
_IDS_ALONE = re.compile(r"DEC-[0-9]+(?:(?:\s*,\s*|\s+and\s+)DEC-[0-9]+)*")
_SUCCESSOR = re.compile(r"\s*SUPERSEDED\s+by\s+(DEC-[0-9]+)")
_LINE = re.compile(r"\s*[-*+]\s+\*\*(Tags|Values|Kept):\*\*\s*(.*)")
_DASH = re.compile(r"\s+(?:—|–|--?)\s+")


def ids(text: str) -> list[str]:
    """The decision ids ``text`` cites as whole words, in order, each once."""
    return list(dict.fromkeys(_ID.findall(text)))


def _tags(value: str) -> dict:
    parts = [part.strip() for part in value.split("·")]
    tags = {"done": bool(parts) and parts[-1] == "done"}
    for part in parts[:-1] if tags["done"] else parts:
        key, colon, rest = part.partition(":")
        if colon and key.strip() in TAG_PARTS:
            tags[key.strip()] = rest.strip()
    if "lands in" in tags:
        tags["places"] = [place.strip().strip("`") for place in tags["lands in"].split(",") if place.strip()]
    return tags


def _entry(live: dict) -> dict:
    status_line = live["first"]
    fields = [(name.strip(), text) for name, text in _FIELD.findall(status_line)]
    successor = _SUCCESSOR.match(status_line.split("**Status:**", 1)[-1])
    entry = {"id": live["id"], "title": live["title"], "line": live["line"], "status": live["status"],
             "status_line": status_line, "span": live["span"], "tags": None, "values": [], "kept": {},
             "successor": successor.group(1) if successor else None, "supersedes": [], "changes": [],
             "named": ids(status_line.split("**Status:**", 1)[-1].split("·", 1)[0]),  # the ids its status word names
             "changed_by": [i for name, text in fields if name == "Changed by" for i in ids(text)]}
    for name, text in fields:
        if name == "Supersedes" and _IDS_ALONE.fullmatch(text.strip().rstrip(".;")):
            entry["supersedes"] += ids(text)
        elif name == "Supersedes" or name in CHANGING:
            entry["changes"] += ids(text)
    for line in live["span"].split("\n")[1:]:
        found = _LINE.match(line)
        if not found:
            continue
        kind, value = found.groups()
        if kind == "Tags" and entry["tags"] is None:
            entry["tags"] = _tags(value)
        elif kind == "Values":
            entry["values"] += [text for text in re.findall(r'"([^"]*)"', value) if text]
        elif kind == "Kept":  # a file kept without a reason is not kept
            path, *reason = _DASH.split(value.strip(), 1)
            if reason and reason[0].strip():
                entry["kept"][path.strip().strip("`")] = reason[0].strip()
    return entry


_READ: dict[str, tuple[bytes, dict | None]] = {}  # resolved root -> (HEAD's commit, its register), one per root


def read(root: Path) -> dict | None:
    """``{"path", "entries", "superseded", "changed", "done"}`` of the register ``HEAD`` holds; None where the path
    map names none. ``superseded`` and ``changed`` map an old id to the ids that superseded or changed it.

    The register is parsed once per process for one root and one ``HEAD`` commit, which fixes the path map and the
    register file: a new commit or another root reads afresh, a refusal is never kept, and each caller is given its
    own copy."""
    import copy

    from gov.cli.errors import GovError
    from gov.store.loader import _git

    key = str(Path(root).resolve())
    try:
        head = _git(Path(root), "rev-parse", "--verify", "HEAD^{commit}").strip()
    except GovError:  # no commit to key on: the read refuses or answers as it always has
        return _read(root)
    if key not in _READ or _READ[key][0] != head:
        _READ[key] = (head, _read(root))
    return copy.deepcopy(_READ[key][1])


def _read(root: Path) -> dict | None:
    from gov.store.loader import _register, _tree, register_entries

    named = _register(Path(root), _tree(Path(root)))
    if named is None:
        return None
    entries = [_entry(live) for live in register_entries(named[1])[0]]
    held = {entry["id"] for entry in entries}
    superseded: dict[str, list] = {}
    changed: dict[str, list] = {}
    for entry in entries:
        if entry["status"] == "SUPERSEDED":
            superseded.setdefault(entry["id"], [])
            if entry["successor"]:
                superseded[entry["id"]].append(entry["successor"])
        for old in entry["supersedes"]:
            if old in held and old != entry["id"]:
                superseded.setdefault(old, []).append(entry["id"])
        for old in entry["changes"]:
            if old in held and old != entry["id"]:
                changed.setdefault(old, []).append(entry["id"])
        if entry["changed_by"]:
            changed.setdefault(entry["id"], []).extend(entry["changed_by"])
    unique = {old: list(dict.fromkeys(new)) for old, new in superseded.items()}
    return {"path": named[0], "entries": entries, "superseded": unique,
            "changed": {old: list(dict.fromkeys(new)) for old, new in changed.items() if old not in unique},
            "done": {entry["id"] for entry in entries if entry["tags"] and entry["tags"]["done"]}}


def left_out_record(register: dict, left: set) -> dict:
    """``{"count", "superseded", "done"}`` of the entries ``left`` out, sorted, each id once."""
    return {"count": len(left), "superseded": sorted(left & register["superseded"].keys()),
            "done": sorted(left & register["done"])}


def in_force(root: Path) -> dict:
    """The digest of the decisions in force (DEC-953 item 7): one line per entry neither superseded nor done, in the
    register's order, a changed entry naming what changed it; what was left out and why; the register's path."""
    register = read(root)
    if register is None:
        return {"lines": [], "left_out": {"count": 0, "superseded": [], "done": []}, "register": None}
    out = register["superseded"].keys() | register["done"]
    lines = []
    for entry in register["entries"]:
        if entry["id"] in out:
            continue
        changers = register["changed"].get(entry["id"])
        lines.append(f"{entry['id']} — {entry['title']}" + (f" (changed by {', '.join(changers)})" if changers else ""))
    return {"lines": lines, "left_out": left_out_record(register, out), "register": register["path"]}


def leave_out(root: Path, evidence: list[dict]) -> tuple[list[dict], dict | None]:
    """``evidence`` without the register's superseded and done entries, and the ``left_out`` record (None where
    nothing was left out). An item is the entries whose spans its lines touch: one that touches a left-out entry is
    narrowed to its own chunk where that chunk touches none (an expanded parent), and left out otherwise."""
    import hashlib

    from gov import records
    from gov.retrieval import authority, lexical

    if not any("start_line" in item for item in evidence):  # an item without lines is no entry's span
        return evidence, None
    register = read(root)
    if register is None:
        return evidence, None
    out = register["superseded"].keys() | register["done"]
    entry_of = authority.register_entries_of(records.records(root), records.edges(root, type=authority.SUPERSEDES),
                                             root)

    def entries_in(first: int, last: int) -> list:
        """The entries whose spans the lines ``first`` to ``last`` touch, in order, each once."""
        return list(dict.fromkeys(entry["id"] for line in range(first, last + 1)
                                  if (entry := entry_of(register["path"], line)) is not None))

    def touched(first: int, last: int) -> set:
        return set(entries_in(first, last))

    def narrowed(item: dict, chunk: dict, body: bytes) -> dict:
        """W2-133 (DEC-1083): the item narrowed to its own chunk, labelled from the chunk's own lines as ``retrieve``
        labels an item (W2-131): its id the entry holding its first line (the chunk id in the preface or a gap), with
        that entry's mark, and each other entry it touches in ``also``. The marks are the parent's own, per entry; the
        parent's id, entry, status and ``also`` are never kept."""
        marks = {mark["entry"]: mark for mark in [{key: item[key] for key in MARK if key in item},
                                                    *item.get("also", ())] if "entry" in mark}
        new = {key: value for key, value in item.items() if key not in MARK + ("also",)}  # ``id`` keeps its place
        new.update({"start_line": chunk["start_line"], "end_line": chunk["end_line"],
                    "sha256": hashlib.sha256(body).hexdigest(), "text": body.decode("utf-8", "replace")})
        holder = (entry_of(register["path"], chunk["start_line"]) or {}).get("id")
        new["id"] = holder or chunk["chunk_id"]
        new.update(marks.get(holder, {}))
        others = [marks[rid] for rid in entries_in(chunk["start_line"], chunk["end_line"])
                  if rid != holder and rid in marks]
        if others:
            new["also"] = others
        return new

    kept, left, own, lines = [], set(), None, None
    for item in evidence:
        if item.get("path") != register["path"]:
            kept.append(item)
            continue
        hit = touched(item["start_line"], item["end_line"]) & out
        if not hit:
            kept.append(item)
            continue
        left |= hit
        if own is None:
            own = {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root, register["path"])}
            lines = (Path(root) / register["path"]).read_bytes().splitlines(keepends=True)
        chunk = own.get(item.get("chunk_id"))
        if chunk and (chunk["start_line"], chunk["end_line"]) != (item["start_line"], item["end_line"]) \
                and not touched(chunk["start_line"], chunk["end_line"]) & out:
            kept.append(narrowed(item, chunk, b"".join(lines[chunk["start_line"] - 1:chunk["end_line"]])))
    return kept, (left_out_record(register, left) if left else None)
