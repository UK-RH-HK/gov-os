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
    root = root or store_root(view_id)
    root.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path(root)))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA_SQL)
    conn.execute(
        "INSERT OR IGNORE INTO store_meta(key, value) VALUES ('schema_version', ?)", (str(SCHEMA_VERSION),)
    )
    conn.commit()
    return conn


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
    core's own tables -- later layers manage their own tables through their own module."""
    conn.execute("DELETE FROM occurrence")
    conn.execute("DELETE FROM chunk")
    conn.execute("DELETE FROM blob")
    conn.commit()


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
