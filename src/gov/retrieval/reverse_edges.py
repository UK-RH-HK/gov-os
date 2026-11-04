"""DEC-1068 M3: the reverse ``depends_on`` edge in the closure, behind ``closure_reverse_depends_on`` in
``governance/project/rebuild.yaml`` (absent: off, today's index and answers).

The meaning (the CTO's ruling P-W2-32-10): a question naming a record reaches the records that depend on it **beyond
one hop** (C depends on B, which depends on the named A). ``gov.closure`` already follows every edge both ways, so a
plain question (depth 1, R0 or R1) reaches A's direct dependents today, and no further; off stays exactly that.

- **The bound:** ``DEPTH`` = 3 ``DEPENDS_ON`` hops back from each start record (hop 1 is today's), and at most
  ``CAP`` = 50 dependents added beyond hop 1, the nearest hop first and then by id. On this repository's store
  (720 edges, 213 records with dependents) a record reaches 11.8 dependents within 3 hops on average and one reaches
  289, so the cap cuts only such roots, and says so in the closure facet (``reverse_depends_on``: ``capped``). A
  larger radius's own closure (R2: 3 hops, R3: 8, both ways) still reaches what it reaches today.
- **The index** (``refresh``, at ``gov rebuild`` after the record store): for each ``DEPENDS_ON`` edge, the line of
  the source record's file that states it: the first line of its front matter's ``depends_on`` value that names the
  target as a whole id (an inline list's own line, or a list item under the key). It is kept in
  ``closure_reverse_edge (target, source, path, line)`` with the store's recipe row
  ``index_recipe.closure_reverse_depends_on = true``. An edge whose line cannot be found has no row (its dependent is
  still reached). Off, the table and the row are dropped, so the store is today's.
- **The closure** (``walk``, ``retrieve``): the dependents reached join the closure, so all their chunks join the
  closure route, and the chunk holding each stating line on the way comes first (hop by hop, then by the dependent's
  id; a dependent of two records on the way has both its lines, in the order of the records); the route's other
  chunks follow in today's order. With the setting on
  and no index built under it, the closure is today's and the facet says ``reverse_depends_on: stale`` until a
  rebuild.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from gov.config.loader import CLOSURE_REVERSE_DEPENDS_ON, index_flag
from gov.store import STORE_REL

EDGE = "DEPENDS_ON"
KEY = "depends_on"  # the front-matter key whose edges the store makes DEPENDS_ON
RECIPE_KEY = CLOSURE_REVERSE_DEPENDS_ON
STALE = "stale"
CAPPED = "capped"
FACET_KEY = "reverse_depends_on"
DEPTH = 3  # DEPENDS_ON hops back from a start record (hop 1 is today's closure at depth 1)
CAP = 50  # dependents added beyond hop 1, at most
_SCHEMA = "CREATE TABLE closure_reverse_edge (target TEXT NOT NULL, source TEXT NOT NULL, path TEXT NOT NULL, " \
          "line INTEGER NOT NULL, PRIMARY KEY (target, source))"
_RECIPE = "CREATE TABLE IF NOT EXISTS index_recipe (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
_EDGES = "SELECT e.source, e.target, r.path FROM edges e JOIN records r ON r.id = e.source WHERE e.type = ? " \
         "ORDER BY e.target, e.source"
_KEY_LINE = re.compile(r"^(?P<key>[A-Za-z_][\w-]*):(?P<value>.*)$")


def on(root: Path) -> bool:
    """Whether the setting is on; CONFIG_INVALID (naming the key) for a value that cannot be read."""
    return index_flag(root, CLOSURE_REVERSE_DEPENDS_ON)


def _named(target: str, line: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(target)}(?![\w-])", line) is not None


def stating_line(text: str, target: str) -> int | None:
    """The 1-based line of ``text``'s front matter whose ``depends_on`` value names ``target`` as a whole id: the key's
    own line when its value is inline, else the first item under it; None when there is none."""
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        return None
    under = False
    for number, line in enumerate(lines[1:], 2):
        if line.rstrip() == "---":
            return None
        match = _KEY_LINE.match(line)
        if match:  # a key at the left edge ends the one before it
            under = match["key"] == KEY
            if under and _named(target, match["value"]):
                return number
        elif under and _named(target, line):
            return number
    return None


def refresh(root: Path) -> dict | None:
    """The index brought to the setting; with it on, the rebuild's part of the result: ``status: recreated``,
    ``edges`` (the store's ``DEPENDS_ON`` edges) and ``stated`` (those with a stating line). Off: the table and the
    recipe row dropped, and None (the rebuild's result is today's)."""
    root = Path(root)
    if not on(root):
        _drop(root)
        return None
    connection = sqlite3.connect(root / STORE_REL)
    try:
        with connection:
            connection.execute("DROP TABLE IF EXISTS closure_reverse_edge")
            connection.execute(_SCHEMA)
            connection.execute(_RECIPE)
            edges = connection.execute(_EDGES, (EDGE,)).fetchall()
            texts: dict[str, str] = {}
            rows = []
            for source, target, path in edges:
                if path not in texts:
                    try:
                        texts[path] = (root / path).read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        texts[path] = ""
                line = stating_line(texts[path], target)
                if line is not None:
                    rows.append((target, source, path, line))
            connection.executemany("INSERT OR IGNORE INTO closure_reverse_edge VALUES (?, ?, ?, ?)", rows)
            connection.execute("INSERT OR REPLACE INTO index_recipe VALUES (?, 'true')", (RECIPE_KEY,))
        return {"status": "recreated", "edges": len(edges), "stated": len(rows)}
    finally:
        connection.close()


def _drop(root: Path) -> None:
    """Off: the index's table and recipe row dropped where a store holds them. No store, or one that cannot be read
    (the rebuild's compaction names it), is left as it is: off, the rebuild touches nothing of today's."""
    path = Path(root) / STORE_REL
    if not path.is_file():
        return
    try:
        connection = sqlite3.connect(path)
        try:
            names = {name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            with connection:
                if "closure_reverse_edge" in names:
                    connection.execute("DROP TABLE closure_reverse_edge")
                if "index_recipe" in names:
                    connection.execute("DELETE FROM index_recipe WHERE key = ?", (RECIPE_KEY,))
        finally:
            connection.close()
    except sqlite3.Error:
        return


class Walk:
    """What the walk back along ``DEPENDS_ON`` from the start records found: ``dependents`` (id -> hop, at most
    ``DEPTH``; hop 1 always whole, beyond it at most ``CAP``), ``stating`` (the (source, path, line) of each edge
    walked whose line is known, hop by hop) and ``capped`` (dependents left out by ``CAP``)."""

    def __init__(self, dependents: dict[str, int], stating: list[tuple[str, str, int]], capped: int):
        self.dependents, self.stating, self.capped = dependents, stating, capped

    def first(self, chunks: dict[str, dict]) -> list[dict]:
        """The closure route's first chunks, each once, in order: the chunk holding each stating line (the first of
        its file, by its first line, whose lines hold it), from ``chunks`` (the keyword index's, ``chunk_id -> record``)."""
        by_path: dict[str, list[dict]] = {}
        for chunk in chunks.values():
            by_path.setdefault(chunk["path"], []).append(chunk)
        ordered, seen = [], set()
        for _, path, line in self.stating:
            holding = sorted((c for c in by_path.get(path, []) if c["start_line"] <= line <= c["end_line"]),
                             key=lambda c: (c["start_line"], c["end_line"]))
            if holding and holding[0]["chunk_id"] not in seen:
                seen.add(holding[0]["chunk_id"])
                ordered.append(holding[0])
        return ordered


def walk(root: Path, starts: list[str]) -> Walk | None:
    """The bounded walk back along ``DEPENDS_ON`` from ``starts`` (in the order given): hop by hop up to ``DEPTH``,
    each hop's new dependents by id, the start records and those already found never again; beyond hop 1 at most
    ``CAP`` dependents in all, the rest counted in ``capped``. Reads the store only; None when it holds no index built
    under the setting (``STALE``)."""
    path = Path(root) / STORE_REL
    if not path.is_file():
        return None
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        built = connection.execute("SELECT value FROM index_recipe WHERE key = ?", (RECIPE_KEY,)).fetchone()
        if not built or built[0] != "true":
            return None
        back: dict[str, list[str]] = {}
        for source, target in connection.execute("SELECT source, target FROM edges WHERE type = ? "
                                                 "ORDER BY target, source", (EDGE,)):
            back.setdefault(target, []).append(source)
        lines = {(target, source): (path, line) for target, source, path, line in
                 connection.execute("SELECT target, source, path, line FROM closure_reverse_edge")}
    except sqlite3.Error:
        return None
    finally:
        connection.close()
    front, found, stating, added, capped = list(dict.fromkeys(starts)), {}, [], 0, 0
    known = set(front)
    for hop in range(1, DEPTH + 1):
        new: list[tuple[str, str]] = []  # (dependent, the record it depends on) of this hop, by dependent
        for target in front:
            new += [(source, target) for source in back.get(target, []) if source not in known]
        reached: list[str] = []
        for source, target in sorted(new, key=lambda pair: pair[0]):
            if source not in known:
                if hop > 1 and added >= CAP:
                    capped += 1
                    known.add(source)
                    continue
                known.add(source)
                found[source] = hop
                reached.append(source)
                added += hop > 1
            if found.get(source) == hop and (target, source) in lines:
                stating.append((source, *lines[(target, source)]))
        front = reached
        if not front:
            break
    return Walk(found, stating, capped)
