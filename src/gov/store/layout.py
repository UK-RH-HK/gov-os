"""The store layout, stated once (W2-88 S4, F3; DEC-957, CAP-20, DEC-016).

Each store, the file it lives in, its tables and their columns, and the layout version the code reads. A store of
another version is never read as current: ``check`` refuses it with ``STORE_LAYOUT_STALE`` naming both versions, and
``gov rebuild`` replaces it. ``loader.load`` stamps the store; ``loader.connect`` checks it after its ``STORE_MISSING``
check, so a stale store never reports a missing one.

An **unstamped** store (one built before this layout was stamped) is stale, ``found: 0``, only when a table that
``STORES`` names is present without one of its columns (the planted case: a store from before W2-03's
``register_entries.span``); otherwise it is read as current.
"""

from __future__ import annotations

import sqlite3

from gov.cli.errors import GovError

LAYOUT_VERSION = 2
STAMP_TABLE = "store_layout"
STORE_FILE = ".gov-runtime/store.db"

STORES = {
    "record": {
        "file": STORE_FILE,
        "tables": {
            "records": ("path", "id", "type", "status"),
            "edges": ("type", "source", "target"),
            "commits": ("id",),
            "trailers": ("commit_id", "key", "value"),
            "commit_paths": ("commit_id", "path"),
            "register_entries": ("id", "heading", "title", "span", "content_hash"),
            "record_titles": ("path", "id", "title"),
            "stated_links": ("type", "source", "target", "via"),
            "fingerprints": ("head", "code", "records", "kind"),
        },
    },
    "lexical": {
        "file": STORE_FILE,
        "tables": {
            "lexical_file": ("path", "blob", "indexed"),
            "lexical_parent": ("parent_id", "path", "kind", "start_line", "end_line"),
            "lexical_chunk": ("id", "chunk_id", "path", "start_line", "end_line", "parent_id"),
        },
    },
    "vectors": {
        "file": STORE_FILE,
        "tables": {
            "semantic_vector": ("chunk_id", "embedding"),
            "semantic_manifest": ("embedder_model", "embedder_revision", "reranker_model", "reranker_revision"),
            "semantic_pin": ("key", "value"),
        },
    },
    "codegraph": {"file": ".gov-runtime/codeintel/", "tables": ()},
}


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {name for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def stamp(conn: sqlite3.Connection, commit: bool = True) -> None:
    """Write ``LAYOUT_VERSION`` into the store, replacing any stamp (the connection must be writable). A caller inside
    its own transaction passes ``commit=False``: the stamp then stands or falls with that transaction."""
    conn.execute(f"CREATE TABLE IF NOT EXISTS {STAMP_TABLE} (version INTEGER NOT NULL)")
    conn.execute(f"DELETE FROM {STAMP_TABLE}")
    conn.execute(f"INSERT INTO {STAMP_TABLE} VALUES (?)", (LAYOUT_VERSION,))
    if commit and conn.in_transaction:
        conn.commit()


def version_of(conn: sqlite3.Connection) -> int | None:
    """The stamped layout version of the store; None where the store holds no stamp."""
    if STAMP_TABLE not in _tables(conn):
        return None
    rows = conn.execute(f"SELECT version FROM {STAMP_TABLE}").fetchall()
    return int(rows[0][0]) if len(rows) == 1 and isinstance(rows[0][0], int) else 0


def _lacking(conn: sqlite3.Connection) -> list[str]:
    """The ``table.column`` names ``STORES`` states that a table present in the store lacks."""
    lacking = []
    present = _tables(conn)
    for store in STORES.values():
        for table, columns in dict(store["tables"]).items():
            if table not in present:
                continue
            held = {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}
            lacking += [f"{table}.{column}" for column in columns if column not in held]
    return lacking


def found_of(conn: sqlite3.Connection) -> int | None:
    """The version the store is read at, or None where it is current: the stamp when it differs from this layout's;
    ``0`` for an unstamped store that lacks a column ``STORES`` names; None for a current store (stamped as
    ``LAYOUT_VERSION``, or unstamped and whole)."""
    version = version_of(conn)
    if version is None:
        return 0 if _lacking(conn) else None
    return None if version == LAYOUT_VERSION else version


def check(conn: sqlite3.Connection, path) -> None:
    """Raise ``STORE_LAYOUT_STALE`` (naming the version found and the one this gov reads) unless the store is current."""
    found = found_of(conn)
    if found is not None:
        raise GovError("STORE_LAYOUT_STALE",
                       f"{path}: store layout {found}, this gov reads {LAYOUT_VERSION}; run gov rebuild",
                       {"found": found, "expected": LAYOUT_VERSION})
