"""The content-addressed index store: where it lives, its schema, and the two tables B1 owns directly
(``blob``, ``occurrence``, ``chunk``). One store, one SQLite database (``store.db``); later layers (lexical FTS5,
semantic vectors, code symbol tables, authority/graph tables) add their own tables to the same file, so a query can
join across layers without a second connection.

Store isolation (orchestrator amendment BR-DAG-AMEND-1): every module that needs the store root MUST go through
``store_root()``. Nothing else may compute or hard-code a path under ``$HOME/.cache/gov-bridge``. This is what lets
several parallel builders each build into their own store via ``GOVBRIDGE_STORE`` without colliding.
"""
from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 1


def gov_bridge_home() -> Path:
    """The shared root for the venv, the model cache and (by default) telemetry and the store. Overridable with
    GOV_BRIDGE_HOME; defaults to ~/.cache/gov-bridge, the path every other bridge document names."""
    env = os.environ.get("GOV_BRIDGE_HOME")
    if env:
        return Path(env)
    return Path.home() / ".cache" / "gov-bridge"


def store_root(view_id: Optional[str] = None) -> Path:
    """The index store root. GOVBRIDGE_STORE, if set, wins outright (BR-DAG-AMEND-1: each parallel builder gets its
    own store this way). Otherwise the default is ``$HOME/.cache/gov-bridge/store/<view_id>``. Every module that
    needs the store location -- store, freshness, manifest, every CLI in govbridge.core -- MUST call this function
    rather than compute a path itself."""
    env = os.environ.get("GOVBRIDGE_STORE")
    if env:
        return Path(env)
    vid = view_id or "default"
    return gov_bridge_home() / "store" / vid


def db_path(root: Optional[Path] = None, view_id: Optional[str] = None) -> Path:
    return (root or store_root(view_id)) / "store.db"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS store_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS blob (
    blob_id TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL,
    size INTEGER NOT NULL,
    is_text INTEGER NOT NULL,
    corpus_rule TEXT NOT NULL,
    corpus_effect TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS occurrence (
    ref_name TEXT NOT NULL,
    commit_id TEXT NOT NULL,
    path TEXT NOT NULL,
    blob_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    PRIMARY KEY (ref_name, commit_id, path)
);
CREATE INDEX IF NOT EXISTS occurrence_by_blob ON occurrence(blob_id);
CREATE INDEX IF NOT EXISTS occurrence_by_path ON occurrence(path);

-- REPAIR_DAG.yaml node R1-GA1 (second reopening): a DEDUPLICATED (blob_id, path) view of `occurrence`, built and
-- maintained HERE, at BUILD time, by put_occurrence/clear_layer_tables/prune_stale_distinct_paths below -- never
-- created or populated by a query path (govbridge.lexical.query, govbridge.semantic.vectors). `occurrence` itself
-- is keyed by (ref_name, commit_id, path): on a real corpus the SAME (blob_id, path) pair repeats once per
-- historical ref/commit that ever carried it, sometimes hundreds of times (measured: ~500k occurrence rows for
-- ~8k distinct pairs on the CONTROL-A corpus). A query that needs "does blob B ever occur at a path matching this
-- glob" (the authority-class scope filter's Tier B, govbridge.route.real_routes) would otherwise have to walk
-- every one of those repeats; this table holds each pair exactly once. Content is a PURE, deterministic function
-- of `occurrence`'s own rows, so the ALREADY-registered `occurrence` layer digest (govbridge.core.manifest.
-- occurrence_layer_digest) is a faithful proxy for this table's own determinism too -- two from-clean builds with
-- the same occurrence digest necessarily produce the same occurrence_distinct_path content, and
-- tests/core/test_scope_path_cache.py verifies this directly rather than only by that argument.
CREATE TABLE IF NOT EXISTS occurrence_distinct_path (
    blob_id TEXT NOT NULL,
    path TEXT NOT NULL,
    PRIMARY KEY (blob_id, path)
);

CREATE TABLE IF NOT EXISTS chunk (
    chunk_id TEXT PRIMARY KEY,
    blob_id TEXT NOT NULL,
    chunker_version TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    text_sha256 TEXT NOT NULL,
    text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS chunk_by_blob ON chunk(blob_id);
"""


def open_db(root: Optional[Path] = None, view_id: Optional[str] = None) -> sqlite3.Connection:
    """REPAIR_DAG.yaml node R1-GA1 (second reopening): "query commands must never write to the store." Every
    statement below is already the same idempotent, CREATE/INSERT-IF-NOT-EXISTS shape it always was (never a
    schema or data CHANGE on a store that has already been built once) -- the ONE genuine write is the
    ``schema_version`` marker row, and even that is wrapped so a store opened from a read-only FILE (chmod'd
    read-only, e.g. the frozen run-2 demonstration store R1-D2 builds) degrades to "skip the marker, keep going"
    rather than raising. ``root.mkdir(..., exist_ok=True)`` and ``PRAGMA journal_mode=WAL`` (a no-op once the file
    is already in WAL mode -- confirmed empirically: SQLite answers a PRAGMA that changes nothing without
    attempting a write, even over a read-only connection) never fail on an existing, already-built store either."""
    root = root or store_root(view_id)
    root.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path(root)))
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        pass  # a read-only store file: already in WAL mode from when it was built; nothing to change
    try:
        conn.executescript(SCHEMA_SQL)  # CREATE ... IF NOT EXISTS: a no-op once every table already exists
    except sqlite3.OperationalError:
        # A read-only store file built before this table existed: cannot create it here (by design -- query paths
        # never write). Left for the caller's own explicit structure check (e.g. govbridge.lexical.query's
        # STORE_NEEDS_REBUILD) to name clearly; every table this schema declares besides the new one already
        # exists on any store old enough to predate it, so this can only ever be about the new addition.
        conn.rollback()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO store_meta(key, value) VALUES ('schema_version', ?)", (str(SCHEMA_VERSION),)
        )
        conn.commit()
    except sqlite3.OperationalError:
        conn.rollback()  # read-only store file: the schema_version marker is already there from the real build
    return conn


def open_db_readonly(root: Optional[Path] = None, view_id: Optional[str] = None) -> sqlite3.Connection:
    """REPAIR_DAG.yaml node R1-GA1 (second reopening, coordinator addendum): ``open_db()`` above tolerates a
    read-only store FILE (every write it attempts is wrapped so it degrades to a no-op rather than raising), but
    that is "attempt a write, catch the failure" -- a connection that COULD still try to write, relying on every
    write-shaped statement everywhere being individually wrapped in try/except to notice it can't. This function
    is the stronger guarantee instead: a connection opened `file:<path>?mode=ro&immutable=1`, which cannot write at
    all, by construction -- no PRAGMA, no ``executescript``, no ``INSERT`` is even attempted (there is nothing here
    for a write-shaped statement to accidentally slip past). Every QUERY path (``govbridge.lexical.query``,
    ``govbridge.semantic.search``, ``govbridge.route.real_routes``'s own connection) opens the store THIS way;
    every BUILD path (``govbridge.core.freshness`` and everything it drives) keeps calling ``open_db()`` above,
    unchanged -- builds still need read-write, and still own creating the file/schema in the first place.

    ``mode=ro`` alone is not enough on a WAL-mode database (``SCHEMA_VERSION``'s own ``PRAGMA journal_mode=WAL``):
    a plain read-only open still needs to consult (and, if absent, CREATE) the ``-shm``/``-wal`` companion files to
    know which WAL frames apply -- verified directly, empirically, against this exact store shape: with the store
    file AND its directory both read-only, a bare ``mode=ro`` connection raised "attempt to write a readonly
    database" on its very first SELECT, while ``mode=ro&immutable=1`` read it successfully. ``immutable=1`` is
    SQLite's own documented answer for exactly this ("the database file is stored on read-only media... this also
    disables the checks... whether a hot rollback journal or WAL file needs to be rolled back"): it tells SQLite to
    trust the main file's content as fixed and skip the WAL/locking machinery entirely, which is also why this
    connection is only ever handed to a query that is happy to see the store as it stood at BUILD time -- a build
    that commits and then does not fully close/checkpoint before the store is (re)opened this way could leave
    recent writes sitting in an un-merged ``-wal`` file that this connection will never look at. Every build path
    already closes its one connection at the end of a run (Python's own ``sqlite3.Connection.close()``, which
    SQLite auto-checkpoints on if it is the last connection open), so this is not a hazard for the ordinary
    build-then-query sequence this repair's own tests exercise -- but it is a real constraint, named here rather
    than left implicit, for whoever next changes how a build finishes.

    Unlike ``open_db()``, this never creates the root directory or the file: a query against a store that has
    never been built at all is already an error one layer up in a query's own logic (or, failing that, a clear,
    unambiguous "unable to open database file" from SQLite itself) -- never something a query path should
    silently fix by building the store out from under itself."""
    root = root or store_root(view_id)
    uri = f"file:{db_path(root)}?mode=ro&immutable=1"
    return sqlite3.connect(uri, uri=True)


def move_store_aside(root: Optional[Path] = None, view_id: Optional[str] = None) -> Optional[Path]:
    """Move an existing store directory aside (never delete in place -- ARCHITECTURE.md section 8.1, and `rm` is
    denied to every bridge role). Returns the new path, or None if there was nothing to move."""
    root = root or store_root(view_id)
    if not root.exists():
        return None
    dest = root.parent / f"{root.name}.trashed-{int(time.time())}"
    root.rename(dest)
    return dest


def clear_layer_tables(conn: sqlite3.Connection) -> None:
    """Used by a FULL rebuild: empty the tables this module owns, in a fresh (already schema'd) database. Only
    core's own tables -- later layers manage their own tables through their own module. occurrence_distinct_path
    is core's own derived table (see SCHEMA_SQL's own comment) and is cleared here too, so a from-clean rebuild's
    later put_occurrence() calls repopulate it from nothing, exactly like occurrence itself."""
    conn.execute("DELETE FROM occurrence")
    conn.execute("DELETE FROM occurrence_distinct_path")
    conn.execute("DELETE FROM chunk")
    conn.execute("DELETE FROM blob")
    conn.commit()


def prune_stale_distinct_paths(conn: sqlite3.Connection) -> int:
    """Removes every ``occurrence_distinct_path`` row no longer backed by ANY surviving ``occurrence`` row --
    REPAIR_DAG.yaml node R1-GA1 (second reopening): "INSERT OR IGNORE never removes a stale (blob, path) pair...
    Tier B could admit a blob on a path it no longer occupies." Called by ``govbridge.core.freshness`` right after
    each of its three incremental ``DELETE FROM occurrence`` sites, in the SAME transaction (never committed here
    -- the caller commits once, after its own occurrence delete and this prune both land). A blanket
    "keep only what's still referenced" sweep rather than tracking exactly which pairs a given delete orphaned:
    simpler, still correct (a pair that is NOT stale is left untouched either way), and cheap relative to a full
    rebuild since it only runs on the INCREMENTAL delete paths, never on every put_occurrence() call. Returns how
    many rows were removed, for the caller's own stats."""
    cur = conn.execute(
        "DELETE FROM occurrence_distinct_path WHERE NOT EXISTS ("
        "SELECT 1 FROM occurrence o WHERE o.blob_id = occurrence_distinct_path.blob_id "
        "AND o.path = occurrence_distinct_path.path)"
    )
    return cur.rowcount if cur.rowcount is not None and cur.rowcount >= 0 else 0


def put_blob(conn: sqlite3.Connection, blob_id: str, sha256: str, size: int, is_text: bool,
             corpus_rule: str, corpus_effect: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO blob(blob_id, sha256, size, is_text, corpus_rule, corpus_effect) "
        "VALUES (?,?,?,?,?,?)",
        (blob_id, sha256, size, 1 if is_text else 0, corpus_rule, corpus_effect),
    )


def put_occurrence(conn: sqlite3.Connection, ref_name: str, commit_id: str, path: str, blob_id: str,
                    mode: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO occurrence(ref_name, commit_id, path, blob_id, mode) VALUES (?,?,?,?,?)",
        (ref_name, commit_id, path, blob_id, mode),
    )
    # occurrence_distinct_path is maintained IN LOCKSTEP with occurrence itself, at BUILD time, from this single
    # call site -- a from-clean rebuild calls this once per occurrence row (after clear_layer_tables emptied both
    # tables), so it ends up fully, deterministically repopulated; an incremental build adds any genuinely NEW
    # (blob_id, path) pair the same way. Never removes a pair (a DELETE FROM occurrence elsewhere can orphan one --
    # see prune_stale_distinct_paths, called by govbridge.core.freshness right after its own occurrence deletes).
    conn.execute(
        "INSERT OR IGNORE INTO occurrence_distinct_path(blob_id, path) VALUES (?,?)", (blob_id, path)
    )


def put_chunk(conn: sqlite3.Connection, chunk_id: str, blob_id: str, chunker_version: str, start_line: int,
              end_line: int, text_sha256: str, text: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO chunk(chunk_id, blob_id, chunker_version, start_line, end_line, text_sha256, text) "
        "VALUES (?,?,?,?,?,?,?)",
        (chunk_id, blob_id, chunker_version, start_line, end_line, text_sha256, text),
    )


def has_blob(conn: sqlite3.Connection, blob_id: str) -> bool:
    row = conn.execute("SELECT 1 FROM blob WHERE blob_id=?", (blob_id,)).fetchone()
    return row is not None


def chunks_exist_for_blob(conn: sqlite3.Connection, blob_id: str, chunker_version: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM chunk WHERE blob_id=? AND chunker_version=? LIMIT 1", (blob_id, chunker_version)
    ).fetchone()
    return row is not None


def counts(conn: sqlite3.Connection) -> dict:
    out = {}
    for table in ("blob", "occurrence", "chunk"):
        out[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return out
