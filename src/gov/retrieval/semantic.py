"""The semantic route: a vector for each chunk of the lexical index, in the shared store (W1-19; DEC-379, DEC-374,
DEC-381).

- The corpus is the lexical index's chunks, so every text was let through by ``gov.secrets.indexable`` before it
  was chunked. Of those, only the files whose namespace says ``embedding_policy: embedded`` reach the vectors.
- A vector is a float32 BLOB in a plain table, compared with ``sqlite_vec``'s ``vec_distance_cosine``. There is no
  virtual table, so the store stays readable by a connection that has not loaded the extension.
- The manifest names the embedder and the reranker, each with its revision. The embedder's is the digest Ollama's
  model list reported when the vectors were built (DEC-374). Vectors of another embedder are dropped and built again.
- ``search(..., refresh=False)`` and ``manifest`` open the store read-only and never write it (DEC-322). Missing, empty
  or stale vectors, an absent ``sqlite_vec`` and an absent Ollama make the facet unavailable; none raises.
- On the GPU the embedder gives a text a vector that depends on the prompt the runner computed just before it, by
  this or any other client (DEC-773; W2-54's change record §5.5). On the CPU it gives one vector whatever came
  before, whatever the request's shape and whoever else asks at the same time. So a question is embedded by the
  CPU-only embedder at ``ollama.query_host()`` (DEC-798), in one request after the bare instruction, and the second
  vector is its vector. It is used only when that embedder reports the model wholly on the CPU after computing it;
  otherwise the facet is unavailable and the question goes nowhere else. The chunks go to the shared runner at
  ``OLLAMA_HOST``, with no runner option.
- That vector is cached in ``QUERY_VECTORS_REL``, the one file a read writes (DEC-782): beside the store and never in
  it, keyed by the model, the revision the model list reports at the time of the search, the device that computed
  it and the sha256 of the exact text, at most ``GOV_QUERY_VECTOR_CACHE_MAX_BYTES`` bytes. Round 3's entries, keyed
  without the device, are never read and are dropped at the next write. The cache only saves a request: a cache that
  cannot be read, written or created is skipped, and deleting it changes no answer.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import sqlite3
import struct
import urllib.request
from pathlib import Path

from gov.config.loader import load_config
from gov.retrieval import lexical, ollama, rerank
from gov.secrets import _matches
from gov.store import STORE_REL

FACET = "semantic"
MODEL = "qwen3-embedding:0.6b"
EMBEDDED = "embedded"  # the one value of ``embedding_policy`` that embeds (DEC-381)
# A question is embedded with the model's retrieval instruction; a chunk is embedded without one.
INSTRUCTION = "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: "
DEVICE = "cpu"  # the one device a question's vector is used from: on the CPU its vector is one vector
EMBED_CHARS = 512  # a chunk is embedded as its first characters, this many, as S0b2's R1 does (DEC-406)
TOP_K = 30  # the nearest chunks the route returns, as S0b2's R1 takes them (DEC-406)
BATCH = 32
TIMEOUT_S = 120.0  # the first request loads the model
NO_VECTORS = "sqlite_vec cannot be loaded: no vector can be stored or compared"
NO_MODEL = f"{MODEL} is not in Ollama's model list"
NO_EMBEDDING = f"Ollama did not embed with {MODEL}"
NOT_ON_CPU = f"the query embedder does not report {MODEL} wholly on the CPU: its vector is not used"

SCHEMA = """
CREATE TABLE IF NOT EXISTS semantic_vector (chunk_id TEXT PRIMARY KEY, embedding BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS semantic_manifest (embedder_model TEXT NOT NULL, embedder_revision TEXT NOT NULL,
    reranker_model TEXT NOT NULL, reranker_revision TEXT NOT NULL);
"""
_NEAREST = "SELECT c.chunk_id, c.path, c.start_line, c.end_line, c.parent_id, " \
           "vec_distance_cosine(v.embedding, ?) AS distance FROM semantic_vector v " \
           "JOIN lexical_chunk c ON c.chunk_id = v.chunk_id ORDER BY distance, c.chunk_id LIMIT ?"
_TEXT = "SELECT f.text FROM lexical_chunk c JOIN lexical_fts f ON f.rowid = c.id WHERE c.chunk_id = ?"
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # the endpoint is local: no proxy
QUERY_VECTORS_REL = ".gov-runtime/query-vector-cache.db"  # a file of its own: store.db is not written by a search
CACHE_BOUND_SETTING = "GOV_QUERY_VECTOR_CACHE_MAX_BYTES"
CACHE_BOUND = 64 * 1024 * 1024  # the default bound on the cache file, in bytes
_QUERY_SCHEMA = "CREATE TABLE IF NOT EXISTS device_query_vector (model TEXT NOT NULL, revision TEXT NOT NULL, " \
                "device TEXT NOT NULL, text_sha256 TEXT NOT NULL, embedding BLOB NOT NULL, " \
                "PRIMARY KEY (model, revision, device, text_sha256))"
_ROUND_3_TABLE = "DROP TABLE IF EXISTS query_vector"  # round 3's entries: keyed without the device, never served
_QUERY_VECTOR = "SELECT embedding FROM device_query_vector " \
                "WHERE model = ? AND revision = ? AND device = ? AND text_sha256 = ?"
_OLDER_HALF = "DELETE FROM device_query_vector " \
              "WHERE rowid <= (SELECT (min(rowid) + max(rowid)) / 2 FROM device_query_vector)"


def _report(reason: str | None, **more) -> dict:
    return {"available": reason is None, "facet": FACET, "state": "FACET_UNAVAILABLE" if reason else "AVAILABLE",
            "reason": reason, **more}


def _ask(path: str, body: dict | None = None, host: str | None = None):
    """The JSON answer to ``path`` of the Ollama endpoint at ``host`` (default: the shared one at ``OLLAMA_HOST``);
    None when it gives none."""
    host = host or os.environ.get("OLLAMA_HOST") or ollama.DEFAULT_HOST
    request = urllib.request.Request((host if "://" in host else f"http://{host}").rstrip("/") + path,
                                     data=None if body is None else json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
    try:
        with _OPENER.open(request, timeout=TIMEOUT_S) as reply:
            return json.load(reply)
    except (OSError, http.client.HTTPException, ValueError):
        return None


def _embed(texts: list[str], host: str | None = None) -> list[bytes] | None:
    """One float32 BLOB per text, embedded at ``host`` (default: the shared runner) with no runner option; None unless
    the endpoint returned a vector for each."""
    vectors = (_ask("/api/embed", {"model": MODEL, "input": texts}, host) or {}).get("embeddings") or []
    if len(vectors) != len(texts):
        return None
    return [struct.pack(f"{len(vector)}f", *vector) for vector in vectors]


def _revision(host: str | None = None) -> str | None:
    """The digest the model list at ``host`` (default: the shared runner) reports for the embedder (DEC-374)."""
    for model in (_ask("/api/tags", host=host) or {}).get("models") or []:
        if MODEL in (model.get("name"), model.get("model")):
            return model.get("digest") or None
    return None


def _on_cpu(host: str) -> bool:
    """True when the embedder at ``host`` reports, at ``/api/ps``, the model loaded wholly on the CPU: ``size_vram`` 0
    and ``size`` above 0. A listing without the model, or one that cannot be read, is not the CPU."""
    for model in (_ask("/api/ps", host=host) or {}).get("models") or []:
        if MODEL in (model.get("name"), model.get("model")):
            return model.get("size_vram") == 0 and (model.get("size") or 0) > 0
    return False


def _bound() -> int:
    """The cache's bound in bytes: ``GOV_QUERY_VECTOR_CACHE_MAX_BYTES``, else ``CACHE_BOUND``."""
    try:
        return int(os.environ.get(CACHE_BOUND_SETTING) or CACHE_BOUND)
    except ValueError:
        return CACHE_BOUND


def _cached(path: Path, key: tuple) -> bytes | None:
    """The vector cached under ``key`` at ``path``, opened read-only; None when there is none or none can be read."""
    try:
        connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30.0)
        try:
            row = connection.execute(_QUERY_VECTOR, key).fetchone()
        finally:
            connection.close()
    except sqlite3.Error:
        return None
    return row and row[0]


def _cache(path: Path, key: tuple, vector: bytes) -> None:
    """Cache ``vector`` under ``key`` at ``path`` in one transaction, unless an entry is there already. Past the bound
    the transaction is undone, and tried once more after the older half of the entries is deleted; an entry that
    still does not fit is not kept. A cache that cannot be written raises nothing."""
    try:
        connection = sqlite3.connect(path, timeout=30.0, isolation_level=None)
        try:
            for evict in (False, True):
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(_ROUND_3_TABLE)
                connection.execute(_QUERY_SCHEMA)
                if evict:
                    connection.execute(_OLDER_HALF)
                connection.execute("INSERT OR IGNORE INTO device_query_vector VALUES (?, ?, ?, ?, ?)", (*key, vector))
                pages = connection.execute("PRAGMA page_count").fetchone()[0]
                if pages * connection.execute("PRAGMA page_size").fetchone()[0] <= _bound():
                    connection.execute("COMMIT")
                    return
                connection.execute("ROLLBACK")
        finally:
            connection.close()
    except sqlite3.Error:
        return


def query_vector(root: Path, query: str) -> tuple[bytes | None, str | None]:
    """The vector a search compares with for ``query``, and why there is none: the one cached under its key, else the
    one the CPU-only embedder gives the question, sent right after the bare instruction in one request, if that
    embedder then reports the model wholly on the CPU (cached then). When the embedder gives no vector, or does not
    report the CPU, there is no vector and nothing is cached. Without a revision in the model list there is no key and
    nothing is cached."""
    host = ollama.query_host()
    text, revision, path = INSTRUCTION + query, _revision(host), Path(root) / QUERY_VECTORS_REL
    key = revision and (MODEL, revision, DEVICE, hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest())
    cached = key and _cached(path, key)
    if cached:
        return cached, None
    vectors = _embed([INSTRUCTION, text], host)
    if vectors is None:
        return None, NO_EMBEDDING
    if not _on_cpu(host):  # read after the computation: a fresh embedder lists nothing until a request loads it
        return None, NOT_ON_CPU
    if key:
        _cache(path, key, vectors[1])
    return vectors[1], None


def _ready(connection: sqlite3.Connection, ensure=None) -> str | None:
    """Load ``sqlite_vec`` into ``connection`` and make the Ollama ``ensure`` names answer (the shared runner by
    default); why a vector cannot be made, or None."""
    try:
        import sqlite_vec  # imported here: absent, the facet is unavailable and the other routes are not affected
        connection.enable_load_extension(True)
        sqlite_vec.load(connection)
        connection.enable_load_extension(False)
    except (ImportError, AttributeError, sqlite3.Error):
        return NO_VECTORS
    return None if (ensure or ollama.ensure_available)()["available"] else ollama.WARNING


def _wanted(root: Path, connection: sqlite3.Connection) -> list[str]:
    """The chunks that are embedded: those of a file whose every namespace says ``embedded`` (DEC-381). Any other
    value, a namespace without the field and a file without a namespace are not embedded."""
    namespaces = load_config(root).get("path-map.yaml", {}).get("namespaces", {})
    verdicts: dict[str, bool] = {}

    def embedded(rel: str) -> bool:
        if rel not in verdicts:
            policies = [entry.get("embedding_policy") for entry in namespaces.values()
                        if any(_matches(rel, pattern) for pattern in entry["paths"])]
            verdicts[rel] = bool(policies) and all(policy == EMBEDDED for policy in policies)
        return verdicts[rel]

    return [chunk_id for chunk_id, rel in connection.execute("SELECT chunk_id, path FROM lexical_chunk ORDER BY id")
            if embedded(rel)]


def _open(root: Path) -> sqlite3.Connection | None:
    """The store at ``root``, read-only; None when there is no store or it holds no vector index."""
    path = Path(root) / STORE_REL
    if not path.is_file():
        return None
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    if connection.execute("SELECT 1 FROM sqlite_master WHERE name = 'semantic_manifest'").fetchone() is None:
        connection.close()
        return None
    return connection


def _build(root: Path) -> str | None:
    """Bring the lexical index up to date, then embed the chunks that have no vector, each as its first
    ``EMBED_CHARS`` characters; why it cannot be done, or None."""
    lexical.refresh(root)
    connection = sqlite3.connect(root / STORE_REL)
    try:
        reason = _ready(connection)
        revision = None if reason else _revision()
        if revision is None:
            return reason or NO_MODEL  # nothing was sent to be embedded
        connection.executescript(SCHEMA)
        wanted = _wanted(root, connection)
        with connection:
            built_by = connection.execute("SELECT embedder_model, embedder_revision FROM semantic_manifest").fetchone()
            if built_by != (MODEL, revision):
                connection.execute("DELETE FROM semantic_vector")
            connection.execute("DELETE FROM semantic_manifest")
            connection.execute("INSERT INTO semantic_manifest VALUES (?, ?, ?, ?)",
                               (MODEL, revision, rerank.MODEL, rerank.REVISION))
            have = {chunk_id for (chunk_id,) in connection.execute("SELECT chunk_id FROM semantic_vector")}
            connection.executemany("DELETE FROM semantic_vector WHERE chunk_id = ?",
                                   [(chunk_id,) for chunk_id in have - set(wanted)])
            missing = [chunk_id for chunk_id in wanted if chunk_id not in have]
            for start in range(0, len(missing), BATCH):
                batch = missing[start:start + BATCH]
                vectors = _embed([connection.execute(_TEXT, (chunk_id,)).fetchone()[0][:EMBED_CHARS]
                                  for chunk_id in batch])
                if vectors is None:
                    return NO_EMBEDDING
                connection.executemany("INSERT INTO semantic_vector VALUES (?, ?)", zip(batch, vectors))
        return None
    finally:
        connection.close()


def _status(root: Path) -> str | None:
    """Why the vectors cannot be answered from as they stand (missing, empty or stale), or None. Writes nothing."""
    status = lexical.freshness(root)["status"]
    if status != "fresh":
        return status
    connection = _open(root)
    if connection is None:
        return "missing"
    try:
        have = {chunk_id for (chunk_id,) in connection.execute("SELECT chunk_id FROM semantic_vector")}
        if connection.execute("SELECT 1 FROM semantic_manifest").fetchone() is None:
            return "missing"
        return "stale" if have != set(_wanted(root, connection)) else None if have else "empty"
    finally:
        connection.close()


def refresh(root: Path) -> dict:
    """Bring the lexical index up to date, then embed the chunks that have no vector."""
    return _report(_build(Path(root)))


def search(root: Path, query: str, refresh: bool = True) -> dict:
    """The ``TOP_K`` chunks nearest to ``query``, nearest first, as the chunk records of the lexical index.

    With ``refresh`` the vectors are brought up to date first. Without, the store is not written, and missing, empty
    or stale vectors are reported as ``FACET_UNAVAILABLE`` with the reason and no hit (DEC-342). Either way, the
    question is embedded by the CPU-only embedder alone (started if needed) and its vector is cached beside the store
    once the vectors can be answered from (DEC-782, DEC-798).
    """
    root = Path(root)
    reason = (_build(root) if refresh else None) or _status(root)
    if reason:
        return _report(reason, hits=[])
    connection = _open(root)
    try:
        reason = _ready(connection, ollama.ensure_query_available)
        vector, reason = (None, reason) if reason else query_vector(root, query)
        if vector is None:
            return _report(reason, hits=[])
        keys = ("chunk_id", "path", "start_line", "end_line", "parent_id", "distance")
        return _report(None, hits=[dict(zip(keys, row)) for row in connection.execute(_NEAREST, (vector, TOP_K))])
    finally:
        connection.close()


def manifest(root: Path) -> dict | None:
    """The models the vectors were built with and the reranker's pin, each with its revision; None when there is no
    vector index. Read from the store alone: writes nothing and asks Ollama nothing (DEC-374)."""
    connection = _open(root)
    if connection is None:
        return None
    try:
        row = connection.execute("SELECT * FROM semantic_manifest").fetchone()
    finally:
        connection.close()
    return row and {"embedder": {"model": row[0], "revision": row[1]},
                    "reranker": {"model": row[2], "revision": row[3]}}
