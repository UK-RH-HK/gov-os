"""The machine-wide vector cache: each text embedded once on the machine, whatever tree, clone or code asks (W2-126;
DEC-1032 levers b.1 and b.6, DEC-1039).

- A vector depends only on the model, its revision and the exact text sent, so an entry is keyed by those three: the
  model's name, the digest its model list reports (DEC-374) and the sha256 of the text's UTF-8 bytes. Another model or
  revision is another key space; nothing is ever served across them.
- One SQLite file, ``vectors.db``, in ``GOV_VECTOR_CACHE_DIR`` (default ``$XDG_CACHE_HOME/gov-os/vector-cache``, else
  ``~/.cache/gov-os/vector-cache``), created with mode 0600 in a folder of mode 0700. WAL mode, so readers never wait
  for a writer; each write is one short transaction with a busy timeout, and no connection is held across an embedding
  request: a run looks up, closes, embeds the misses, then stores them.
- An entry holds the vector's bytes exactly as the embedder returned them and their sha256. An entry whose bytes do not
  match it, or are not whole float32 numbers, is a miss, and the next store replaces it.
- ``GOV_VECTOR_CACHE_MAX_BYTES`` bounds the file (its pages in use, in bytes); past it the least recently used entries
  are deleted in the same transaction and the freed pages returned to the file system.
- The cache only saves requests. A cache that cannot be opened, read or written (unreadable, locked past the busy
  timeout, not a database) is skipped for the rest of the run, and nothing raises. A run's counts: ``hits`` (texts
  served from the cache), ``misses`` (texts sent to the embedder) and ``skipped`` (None, or why the cache was skipped).
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
import time
from pathlib import Path

DIR_SETTING = "GOV_VECTOR_CACHE_DIR"
BOUND_SETTING = "GOV_VECTOR_CACHE_MAX_BYTES"
FILE = "vectors.db"
BOUND = 512 * 1024 * 1024  # about two corpora: 2 x 54,000 texts of 1,024 float32 numbers, measured 4,841 B each
BUSY_S = 2.0  # the longest a lookup or a store waits for another writer before the cache is skipped
SCHEMA = """
CREATE TABLE IF NOT EXISTS vector (id INTEGER PRIMARY KEY, model TEXT NOT NULL, revision TEXT NOT NULL,
    text_sha256 TEXT NOT NULL, checksum BLOB NOT NULL, embedding BLOB NOT NULL, UNIQUE (model, revision, text_sha256));
CREATE TABLE IF NOT EXISTS vector_use (id INTEGER PRIMARY KEY, used INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS vector_use_used ON vector_use (used);
"""
_GET = "SELECT id, checksum, embedding FROM vector WHERE model = ? AND revision = ? AND text_sha256 = ?"


def location() -> Path:
    """The cache's file: in ``GOV_VECTOR_CACHE_DIR``, else in the user's own cache folder."""
    folder = os.environ.get(DIR_SETTING)
    if not folder:
        folder = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "gov-os" / "vector-cache"
    return Path(folder) / FILE


def bound() -> int:
    """The bound in bytes: ``GOV_VECTOR_CACHE_MAX_BYTES``, else ``BOUND``."""
    try:
        return int(os.environ.get(BOUND_SETTING) or BOUND)
    except ValueError:
        return BOUND


def zero() -> dict:
    """A run's counts before it looks anything up."""
    return {"hits": 0, "misses": 0, "skipped": None}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()


def _connect(path: Path) -> sqlite3.Connection:
    """The cache at ``path``, created (0600, WAL, its schema) when absent. Raises ``OSError`` or ``sqlite3.Error``."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.close(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
    except FileExistsError:
        pass
    connection = sqlite3.connect(path, timeout=BUSY_S, isolation_level=None)
    try:
        if connection.execute("SELECT 1 FROM sqlite_master WHERE name = 'vector_use_used'").fetchone() is None:
            connection.execute("PRAGMA auto_vacuum = INCREMENTAL")  # set before the first table, or a no-op
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(SCHEMA)
        connection.execute("PRAGMA journal_size_limit = 4194304")
        return connection
    except BaseException:
        connection.close()
        raise


def _bytes(connection: sqlite3.Connection) -> int:
    pages, size = (connection.execute(f"PRAGMA {name}").fetchone()[0] for name in ("page_count", "page_size"))
    return pages * size


class Cache:
    """One run's use of the cache for ``model`` at ``revision`` (no revision: no key, the cache skipped)."""

    def __init__(self, model: str, revision: str | None, counts: dict | None = None):
        self.model, self.revision, self.path = model, revision, location()
        self.counts = counts if counts is not None else zero()
        self.usable, self._touch, self._pending, self._bad = True, True, set(), set()
        if revision is None:
            self._skip("the model list reports no revision of the model: there is no key")

    def _skip(self, reason: str) -> None:
        self.usable = False
        self.counts["skipped"] = self.counts.get("skipped") or reason

    def get(self, texts: list[str]) -> list[bytes | None]:
        """The cached vector of each text, None for each one to embed. Writes nothing but each hit's last use."""
        found: list[bytes | None] = [None] * len(texts)
        if not self.usable:
            self.counts["misses"] += len(texts)
            return found
        keys = [digest(text) for text in texts]
        hit_ids = []
        try:
            connection = _connect(self.path)
            try:
                for i, key in enumerate(keys):
                    row = connection.execute(_GET, (self.model, self.revision, key)).fetchone()
                    if row is None:
                        continue
                    blob = bytes(row[2])
                    if blob and len(blob) % 4 == 0 and hashlib.sha256(blob).digest() == bytes(row[1]):
                        found[i] = blob
                        hit_ids.append(row[0])
                    else:
                        self._bad.add(key)
                try:  # the last use, for the eviction order; a busy cache keeps the hits, untouched for the run
                    if hit_ids and self._touch:
                        now = time.time_ns()
                        connection.execute("BEGIN IMMEDIATE")
                        connection.executemany("INSERT OR REPLACE INTO vector_use VALUES (?, ?)",
                                               [(i, now) for i in hit_ids])
                        connection.execute("COMMIT")
                except sqlite3.Error:
                    self._touch = False
            finally:
                connection.close()
        except (OSError, sqlite3.Error) as error:
            self._skip(f"the vector cache {self.path} could not be read: {error}")
            self.counts["misses"] += len(texts)
            return [None] * len(texts)
        hits = sum(blob is not None for blob in found)
        self.counts["hits"] += hits
        self.counts["misses"] += len(texts) - hits
        self._pending.update(key for key, blob in zip(keys, found) if blob is None)
        return found

    def put(self, texts: list[str], vectors: list[bytes]) -> None:
        """Store the embedder's vectors of texts ``get`` missed, in one transaction, then evict past the bound."""
        rows = [(text_key, bytes(vector)) for text_key, vector in ((digest(t), v) for t, v in zip(texts, vectors))
                if text_key in self._pending]
        if not rows or not self.usable:
            return
        self._pending.difference_update(key for key, _ in rows)
        try:
            connection = _connect(self.path)
            try:
                now = time.time_ns()
                connection.execute("BEGIN IMMEDIATE")
                for key, blob in rows:
                    verb = "INSERT OR REPLACE" if key in self._bad else "INSERT OR IGNORE"
                    cursor = connection.execute(f"{verb} INTO vector (model, revision, text_sha256, checksum, "
                                                "embedding) VALUES (?, ?, ?, ?, ?)",
                                                (self.model, self.revision, key, hashlib.sha256(blob).digest(), blob))
                    if cursor.rowcount:
                        connection.execute("INSERT OR REPLACE INTO vector_use VALUES (?, ?)", (cursor.lastrowid, now))
                self._evict(connection)
                connection.execute("COMMIT")
            finally:
                connection.close()
        except (OSError, sqlite3.Error) as error:
            self._skip(f"the vector cache {self.path} could not be written: {error}")

    @staticmethod
    def _evict(connection: sqlite3.Connection) -> None:
        """Delete the least recently used entries until the file's pages fit the bound (or none is left)."""
        limit = bound()
        while (size := _bytes(connection)) > limit:
            count = connection.execute("SELECT count(*) FROM vector").fetchone()[0]
            if not count:
                return
            n = max(1, min(count, -(-(size - limit) * count // size)))
            ids = [(i,) for (i,) in connection.execute(
                "SELECT v.id FROM vector v LEFT JOIN vector_use u ON u.id = v.id "
                "ORDER BY coalesce(u.used, 0), v.id LIMIT ?", (n,))]
            connection.executemany("DELETE FROM vector WHERE id = ?", ids)
            connection.executemany("DELETE FROM vector_use WHERE id = ?", ids)
            connection.execute("PRAGMA incremental_vacuum").fetchall()
