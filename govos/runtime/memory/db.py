"""Derived runtime store (SQLite + FTS5). Never authoritative; always rebuildable."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id TEXT PRIMARY KEY, path TEXT UNIQUE NOT NULL, record_type TEXT, title TEXT, status TEXT, state_class TEXT,
  namespace TEXT, sensitivity TEXT, path_class TEXT, content_hash TEXT, repo_commit TEXT, index_version TEXT,
  size INTEGER, indexed_at TEXT, data_json TEXT, semantic INTEGER, lexical INTEGER, graph INTEGER, code INTEGER,
  default_retrieval INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS chunks (
  chunk_id TEXT PRIMARY KEY, artifact_id TEXT NOT NULL, parent_chunk_id TEXT, level TEXT, section TEXT, ordinal INTEGER,
  content_hash TEXT, text TEXT, chars INTEGER, lexical INTEGER DEFAULT 1, semantic INTEGER DEFAULT 1);
CREATE INDEX IF NOT EXISTS idx_chunks_artifact ON chunks(artifact_id);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, chunk_id UNINDEXED, artifact_id UNINDEXED, tokenize='unicode61');
CREATE TABLE IF NOT EXISTS vectors (chunk_id TEXT PRIMARY KEY, artifact_id TEXT, embedder TEXT, dim INTEGER, vec TEXT);
CREATE TABLE IF NOT EXISTS edges (src TEXT, type TEXT, dst TEXT, source_artifact TEXT, provenance TEXT,
  PRIMARY KEY (src, type, dst, source_artifact));
CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst);
CREATE TABLE IF NOT EXISTS symbols (symbol_id TEXT PRIMARY KEY, artifact_id TEXT, path TEXT, name TEXT, qualname TEXT, kind TEXT,
  lineno INTEGER, end_lineno INTEGER, parent TEXT, signature TEXT);
CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
CREATE TABLE IF NOT EXISTS symbol_refs (path TEXT, name TEXT, kind TEXT, lineno INTEGER, target TEXT);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS claims (task_id TEXT PRIMARY KEY, session_id TEXT, role TEXT, claimed_at TEXT, expires_at TEXT);
CREATE TABLE IF NOT EXISTS retrieval_log (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, query TEXT, routes TEXT, hits TEXT, latency_ms REAL);
CREATE TABLE IF NOT EXISTS excluded (path TEXT PRIMARY KEY, reason TEXT, detail TEXT);
CREATE TABLE IF NOT EXISTS capability (key TEXT PRIMARY KEY, value TEXT, updated_at TEXT);
"""


class RuntimeDB:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")

    def init_schema(self) -> None:
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    # --- generic helpers ---
    def execute(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, tuple(params))

    def executemany(self, sql: str, rows: Iterable[Iterable[Any]]) -> None:
        self.conn.executemany(sql, [tuple(r) for r in rows])

    def commit(self) -> None:
        self.conn.commit()

    def fetchall(self, sql: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute(sql, tuple(params)).fetchall()]

    def fetchone(self, sql: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
        r = self.conn.execute(sql, tuple(params)).fetchone()
        return dict(r) if r else None

    def get_meta(self, key: str, default: Any = None) -> Any:
        r = self.fetchone("SELECT value FROM meta WHERE key=?", (key,))
        return json.loads(r["value"]) if r else default

    def set_meta(self, key: str, value: Any) -> None:
        self.execute("INSERT OR REPLACE INTO meta(key,value) VALUES (?,?)", (key, json.dumps(value)))
        self.commit()

    def integrity_ok(self) -> bool:
        try:
            r = self.conn.execute("PRAGMA integrity_check").fetchone()
            return bool(r and r[0] == "ok")
        except sqlite3.DatabaseError:
            return False

    # --- artifact-level deletes (used by incremental indexing) ---
    def delete_artifact(self, artifact_id: str) -> None:
        self.execute("DELETE FROM chunks_fts WHERE artifact_id=?", (artifact_id,))
        self.execute("DELETE FROM vectors WHERE artifact_id=?", (artifact_id,))
        self.execute("DELETE FROM chunks WHERE artifact_id=?", (artifact_id,))
        self.execute("DELETE FROM edges WHERE source_artifact=?", (artifact_id,))
        row = self.fetchone("SELECT path FROM artifacts WHERE artifact_id=?", (artifact_id,))
        if row:
            self.execute("DELETE FROM symbols WHERE path=?", (row["path"],))
            self.execute("DELETE FROM symbol_refs WHERE path=?", (row["path"],))
        self.execute("DELETE FROM artifacts WHERE artifact_id=?", (artifact_id,))

    def artifact_by_path(self, path: str) -> dict[str, Any] | None:
        return self.fetchone("SELECT * FROM artifacts WHERE path=?", (path,))

    def artifact(self, artifact_id: str) -> dict[str, Any] | None:
        return self.fetchone("SELECT * FROM artifacts WHERE artifact_id=?", (artifact_id,))

    def counts(self) -> dict[str, int]:
        out = {}
        for t in ("artifacts", "chunks", "vectors", "edges", "symbols", "symbol_refs", "excluded"):
            out[t] = self.fetchone(f"SELECT COUNT(*) AS c FROM {t}")["c"]  # type: ignore[index]
        return out
