"""DEC-1068 M3: the reverse ``depends_on`` edge in the closure, behind ``closure_reverse_depends_on`` in
``governance/project/rebuild.yaml`` (absent: off, today's index and answers).

The record store already holds each ``DEPENDS_ON`` edge, and ``gov.closure`` follows every edge both ways, so a
question naming a record already reaches the records that depend on it; but the closure route hands over every chunk
of every record it reaches, unranked, so the line where a dependent names the record is lost among them (W2-15a's
Q14, "Which tickets depend on W2-03?": DAEO-ym8a's closure at depth 1 holds 16 records).

- **The index** (``refresh``, at ``gov rebuild`` after the record store): for each ``DEPENDS_ON`` edge, the line of
  the source record's file that states it: the first line of its front matter's ``depends_on`` value that names the
  target as a whole id (an inline list's own line, or a list item under the key). It is kept in
  ``closure_reverse_edge (target, source, path, line)`` with the store's recipe row
  ``index_recipe.closure_reverse_depends_on = true``. An edge whose line cannot be found has no row. Off, the table
  and the row are dropped, so the store is today's.
- **The closure route** (``first``, ``retrieve``): for each start record (the question's ``--ticket``, ``--id``s and
  the records the record route finds, in that order), the chunk holding each line that states a record depends on
  it, by the dependent's id, comes first; the closure route's other chunks follow as today. A dependent not reached
  is reached now. With the setting on and no index built under it, the route is today's and the closure facet says
  ``reverse_depends_on: stale`` until a rebuild.
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
FACET_KEY = "reverse_depends_on"
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


def _rows(root: Path, starts: list[str]) -> list[tuple] | None:
    """The index's rows for ``starts`` (target, source, path, line), the starts in order and each one's dependents by
    id; None when the store holds no index built under the setting."""
    path = Path(root) / STORE_REL
    if not path.is_file():
        return None
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        built = connection.execute("SELECT value FROM index_recipe WHERE key = ?", (RECIPE_KEY,)).fetchone()
        if not built or built[0] != "true":
            return None
        rows = []
        for target in dict.fromkeys(starts):
            rows += connection.execute("SELECT target, source, path, line FROM closure_reverse_edge WHERE target = ? "
                                       "ORDER BY source", (target,)).fetchall()
        return rows
    except sqlite3.Error:
        return None
    finally:
        connection.close()


def first(root: Path, starts: list[str], chunks: dict[str, dict]) -> tuple[list[dict], set[str]] | None:
    """The closure route's first chunks (each chunk once, in order) and the dependents they belong to; None when the
    index is not built under the setting (``STALE``). ``chunks`` are the keyword index's (``chunk_id -> record``): the
    chunk holding a stating line is the first of its file, by its first line, whose lines hold it."""
    rows = _rows(root, starts)
    if rows is None:
        return None
    by_path: dict[str, list[dict]] = {}
    for chunk in chunks.values():
        by_path.setdefault(chunk["path"], []).append(chunk)
    ordered, sources, seen = [], set(), set()
    for _, source, path, line in rows:
        holding = sorted((c for c in by_path.get(path, []) if c["start_line"] <= line <= c["end_line"]),
                         key=lambda c: (c["start_line"], c["end_line"]))
        if holding and holding[0]["chunk_id"] not in seen:
            seen.add(holding[0]["chunk_id"])
            ordered.append(holding[0])
            sources.add(source)
    return ordered, sources
