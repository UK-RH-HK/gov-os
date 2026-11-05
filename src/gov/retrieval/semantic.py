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
- A question is embedded by the query embedder at ``ollama.query_host()``, in one request after the bare
  instruction, and the second vector is its vector. It is used only when computed on the GPU (W2-32 S10, DEC-1065
  (1), replacing DEC-1033's "any device"): on the GPU the vector can depend on the prompt computed just before it
  (DEC-773), and the owner accepted that drift on the evidence that it changed no answer of the standing memory
  measure. The vector is used only when that embedder reports the model loaded on the GPU after computing it and the
  two vectors are well-formed (one length above 0, every number finite); a vector computed on the CPU is
  ``EMBEDDER_ON_CPU``, never cached; otherwise the facet is unavailable and the question goes nowhere else.
  The chunks go to the shared runner at ``OLLAMA_HOST``, with no runner option; a batch the runner lists the model
  for with ``size_vram`` 0 is ``EMBEDDER_ON_CPU``, and one whose device cannot be read after the waits of
  ``RETRY_WAITS_S`` is ``EMBEDDER_DEVICE_UNREAD``: either way nothing of it is stored or cached, and the stage is not
  reported built. No embedder is ever started here (``ollama.ensure_*`` check health only): one that
  does not answer is ``EMBEDDER_UNAVAILABLE``.
- That vector is cached in ``QUERY_VECTORS_REL``, the one file a read writes (DEC-782): beside the store and never in
  it, keyed by the model, the revision the model list reports at the time of the search, the device that computed
  it and the sha256 of the exact text, at most ``GOV_QUERY_VECTOR_CACHE_MAX_BYTES`` bytes. Round 3's entries, keyed
  without the device, are never read and are dropped at the next write. The cache only saves a request: a cache that
  cannot be read, written or created is skipped, and deleting it changes no answer.
- Before a chunk or a question is embedded, the machine-wide cache (``vector_cache``, W2-126, DEC-1032) is looked up
  under the model, the revision and the sha256 of the exact text sent; a hit is used and nothing is sent, a miss is
  embedded and stored. ``refresh`` and ``search`` name the run's ``vector_cache`` counts (hits, misses, skipped).
- The embedder is the one ``governance/project/models.yaml`` pins (``gov.config.models``; ``MODEL`` without the file)
  (W2-32 S1, S2; CAP-19.a). A build under another model, revision or cut than the store's manifest and
  ``semantic_pin`` record drops every vector and embeds them all again. A pin without a revision
  (``MODEL_UNPINNED``), an endpoint whose digest is not the pinned one or a question's embedder that reports another
  revision than the vectors' (``MODEL_MISMATCH``), and a pinned model the endpoint does not list
  (``MODEL_NOT_LISTED``) make the facet unavailable, the code first in ``reason`` and named in ``error``: nothing is
  embedded or compared (fail closed). Vectors built under another pin are ``MODEL_MISMATCH``, and a store that
  records no cut, or another one (built before W2-32, W2-L065), is ``stale``; both until a rebuild.
- With ``embed_headers: true`` in ``rebuild.yaml`` (absent: false; DEC-1067 order (5), index-time method 1), each
  chunk is embedded after its contextual header, its path and the headings above it (``chunking.headers``), the
  whole cut to ``EMBED_CHARS``; the keyword chunk, the evidence text and the reranker's input are unchanged. The
  store records the recipe (``HEADERS_KEY``), so switching the setting makes the store ``stale`` and the next build
  a full re-embed, as another cut does.
- With ``file_level_index: true`` in ``rebuild.yaml`` (absent: false; DEC-1068 M1), each embedded file also gets one
  vector, of its path, its headings and its opening (``_FileTexts``), in ``semantic_file_vector``; ``file_search``
  is the file route ``retrieve`` fuses beside the others: the nearest files, each expanded to its best chunks. Off,
  that table and its ``semantic_pin`` row do not exist. Switching it makes the store ``stale``, and the next build
  makes or drops the file vectors alone; the chunk vectors are not touched.
"""

from __future__ import annotations

import contextvars
import hashlib
import http.client
import json
import math
import os
import sqlite3
import struct
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from gov.cli.errors import GovError
from gov.config import models
from gov.config.loader import FILE_LEVEL_INDEX, KNOWN_FILES, PROJECT_DIR, embed_headers, index_flag, load_config
from gov.retrieval import chunking, learning, lexical, ollama, rerank, vector_cache
from gov.secrets import _matches
from gov.store import STORE_REL

FACET = "semantic"
MODEL = models.DEFAULT_MODEL  # the embedder when no models.yaml pins one (W2-32 S1)
EMBEDDED = "embedded"  # the one value of ``embedding_policy`` that embeds (DEC-381)
# A question is embedded with the model's retrieval instruction; a chunk is embedded without one.
INSTRUCTION = "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: "
DEVICES = ("gpu",)  # the one device a vector is used from (W2-32 S10, DEC-1065 (1)); the cache key names it
ON_CPU = "EMBEDDER_ON_CPU"  # a vector computed on the CPU: refused, never cached or stored (W2-32 S10)
DEVICE_UNREAD = "EMBEDDER_DEVICE_UNREAD"  # the device a batch was computed on could not be read: refused (S10)
# A chunk is embedded whole up to this many characters (W2-32 S7, DEC-1066 G1, DEC-1067; was 512, DEC-406). The
# shared embedder's context is 4,096 tokens and cuts a longer input silently (the CTO's measure, 2026-11-04: 3.7 to
# 3.8 characters a token on the register, 24,000 characters read as 4,095 tokens). 10,000 characters is about 2,650
# tokens there, and still fits text as dense as 2.5 characters a token. A chunk above it is embedded from its first
# part and named in the refresh's ``cut`` and on standard error, never silently.
EMBED_LIMIT_CHARS = 10_000
EMBED_CHARS = EMBED_LIMIT_CHARS  # the cut the manifest records (W2-L065)
TOP_K = 30  # the nearest chunks the route returns, as S0b2's R1 takes them (DEC-406)
BATCH = 32
TIMEOUT_S = 120.0  # each try of a request (the first loads the model); unchanged by DEC-1026
RETRY_WAITS_S = (10.0, 30.0)  # the growing waits before a failed chunk batch's 2nd and 3rd try (DEC-1026, W2-126)


class _Transient(dict):
    """``_ask``'s answer to a request that failed in a way a later try may not: empty, so read as none; ``kind``
    names the failure (DEC-1026; W2-126 KPI 7, P-W2-123-4)."""

    def __init__(self, kind: str):
        super().__init__()
        self.kind = kind


class GaveUp(Exception):
    """Every try of a chunk batch's request failed transiently: ``args[0]`` names each try's failure, in order."""


TIMED_OUT = _Transient("timed out")  # a request accepted and not answered within ``TIMEOUT_S``
REFUSED, RESET = _Transient("connection refused"), _Transient("connection reset")
NO_VECTORS = "sqlite_vec cannot be loaded: no vector can be stored or compared"
NO_MODEL = f"{models.NOT_LISTED}: {MODEL} is not in Ollama's model list"
NO_EMBEDDING = f"Ollama did not embed with {MODEL}"
NOT_LOADED = f"the query embedder does not report {MODEL} loaded: its vector is not used"
MALFORMED = f"the query embedder's vectors from {MODEL} are malformed: the question's vector is not used"
QUERY_ON_CPU = f"{ON_CPU}: the query embedder computed the question's vector with {MODEL} on the CPU: it is not used "\
               f"or cached (no CPU fallback, DEC-1065)"
BUILD_ON_CPU = f"{ON_CPU}: the shared embedder computed the chunks' vectors with {MODEL} on the CPU: none is stored "\
               f"or cached, and the stage is not reported built (no CPU fallback, DEC-1065)"
BUILD_DEVICE_UNREAD = f"{DEVICE_UNREAD}: the shared embedder's listing did not say on which device it computed the " \
                      f"chunks' vectors with {MODEL}, after every try: none is stored or cached, and the stage is " \
                      f"not reported built (the GPU is never assumed, DEC-1065)"

SCHEMA = """
CREATE TABLE IF NOT EXISTS semantic_vector (chunk_id TEXT PRIMARY KEY, embedding BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS semantic_manifest (embedder_model TEXT NOT NULL, embedder_revision TEXT NOT NULL,
    reranker_model TEXT NOT NULL, reranker_revision TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS semantic_pin (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""
CUT_KEY = "embed_chars"  # the row of ``semantic_pin`` that records the cut the vectors were made with (W2-L065)
# The row of ``semantic_pin`` that records the embedding recipe: ``true`` when each chunk was embedded after its
# contextual header (``chunking.headers``; DEC-1067 order (5), ``embed_headers`` in ``rebuild.yaml``), ``false``
# without. A store that records none was built without (every store before it), so it stays fresh with the setting off.
HEADERS_KEY = "embed_headers"
# DEC-1068 M1, a file-level index beside the chunk index (``file_level_index`` in ``rebuild.yaml``, absent: off): one
# vector per embedded file, of ``_FileTexts``'s text, in a table of its own made only while the setting is on, and the
# ``semantic_pin`` row ``FILE_KEY`` = ``true``. Off, neither exists, so the store is today's. A search's file route
# takes the ``FILE_TOP`` nearest files and each one's ``FILE_CHUNKS`` nearest chunks (``file_search``).
FILE_KEY = "file_level_index"
FILE_FACET = "file"
FILE_TOP = 10
FILE_CHUNKS = 2
OPENING_CHARS = chunking.MAX_CHARS  # the file's first characters in its vector's text, as much as one chunk holds
FILE_OFF = f"{FILE_LEVEL_INDEX} is off in rebuild.yaml: no file route"
_FILE_TABLE = "CREATE TABLE IF NOT EXISTS semantic_file_vector (path TEXT PRIMARY KEY, text_sha256 TEXT NOT NULL, " \
              "embedding BLOB NOT NULL)"
_MODEL = contextvars.ContextVar("semantic_model", default=None)  # the pinned model for this refresh or search


class Refused(str):
    """A reason the facet is unavailable that carries a named error ``code`` (W2-32 S2)."""

    code: str

    def __new__(cls, code: str, reason: str):
        self = super().__new__(cls, reason)
        self.code = code
        return self


def _model() -> str:
    """The embedder this refresh or search runs under: the pinned one, else ``MODEL``."""
    return _MODEL.get() or MODEL


def _say(message: str) -> str:
    """``message`` naming the embedder in use where it names ``MODEL``."""
    return message if _model() == MODEL else message.replace(MODEL, _model())


def _pin(root: Path) -> tuple[models.Pin | None, Refused | None]:
    """The embedder's pin at ``root``, or why there is none (the configuration's named error)."""
    try:
        return models.embedder(root), None
    except GovError as error:
        return None, Refused(error.code, error.message)


def _mismatch(reason: str) -> Refused:
    return Refused(models.MISMATCH, f"{models.MISMATCH}: {reason}")


def _recipe(root: Path) -> tuple[bool | None, Refused | None]:
    """Whether the chunks are embedded with their headers at ``root`` (``rebuild.yaml``'s ``embed_headers``), or why
    the setting cannot be read (``CONFIG_INVALID``, naming the key)."""
    try:
        return embed_headers(root), None
    except GovError as error:
        return None, Refused(error.code, error.message)


def _file_setting(root: Path) -> tuple[bool | None, Refused | None]:
    """Whether the file-level index is on at ``root`` (``rebuild.yaml``'s ``file_level_index``, DEC-1068 M1), or why
    the setting cannot be read (``CONFIG_INVALID``, naming the key)."""
    try:
        return index_flag(root, FILE_LEVEL_INDEX), None
    except GovError as error:
        return None, Refused(error.code, error.message)


def file_level_on(root: Path) -> bool:
    """Whether a search asks the file route (DEC-1068 M1); raises CONFIG_INVALID for a setting that cannot be read."""
    return index_flag(root, FILE_LEVEL_INDEX)


def _recorded_files(connection: sqlite3.Connection) -> bool | None:
    """Whether the store holds the file-level index (``FILE_KEY``): absent is off; None when it cannot say."""
    try:
        row = connection.execute("SELECT value FROM semantic_pin WHERE key = ?", (FILE_KEY,)).fetchone()
    except sqlite3.Error:
        return None
    return False if row is None else {"true": True}.get(row[0])


class _FileTexts:
    """The text a file's vector is made from (DEC-1068 M1): ``[path: <path>]``, then ``[headings: <a> | <b> | ...]``
    (each Markdown heading the chunker starts a section at, or each Python function it makes a parent, in the file's
    order; the line left out when there is none), then the file's opening: its lines from the first, each once (the
    chunks' overlap read once), up to ``OPENING_CHARS`` characters; the whole cut to ``EMBED_CHARS``."""

    _PARENTS = "SELECT p.kind, p.start_line, f.text FROM lexical_parent p JOIN lexical_chunk c " \
               "ON c.parent_id = p.parent_id AND c.start_line = p.start_line JOIN lexical_fts f ON f.rowid = c.id " \
               "WHERE p.path = ? AND c.path = ? ORDER BY p.start_line"
    _LINES = "SELECT c.start_line, f.text FROM lexical_chunk c JOIN lexical_fts f ON f.rowid = c.id WHERE c.path = ? " \
             "ORDER BY c.start_line, c.end_line"

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def __call__(self, path: str) -> str:
        names = []
        for kind, _, text in self.connection.execute(self._PARENTS, (path, path)):
            line = (text.splitlines() or [""])[0]
            if kind == "section" and (found := chunking._heading(line)):
                names.append(found[1])
            elif kind == "function" and (match := chunking._DEF.match(line)):
                names.append(match.group(1))
        opening, done = "", 0  # the last line read into the opening
        for start, text in self.connection.execute(self._LINES, (path,)):
            if len(opening) >= OPENING_CHARS:
                break
            for number, line in enumerate(text.splitlines(keepends=True), start):
                if number > done:
                    opening, done = opening + line, number
        headings = f"[headings: {' | '.join(names)}]\n" if names else ""
        return (chunking.header(path) + headings + opening[:OPENING_CHARS])[:EMBED_CHARS]


def _recorded_headers(connection: sqlite3.Connection) -> bool | None:
    """The recipe the store's vectors were made with (``HEADERS_KEY``): absent is without headers; None when the
    store cannot say, or records a value of neither kind."""
    try:
        row = connection.execute("SELECT value FROM semantic_pin WHERE key = ?", (HEADERS_KEY,)).fetchone()
    except sqlite3.Error:
        return None
    return False if row is None else {"true": True, "false": False}.get(row[0])


class _Texts:
    """The text each chunk is embedded as: its text, or with headers its parent's header (``chunking.headers``)
    followed by its text; either cut to ``EMBED_CHARS``, so the header counts toward the limit and is kept while the
    text is cut (DEC-1067 order (5)). Off, the text is the chunk's alone, byte for byte as before the setting."""

    _PARENTS = "SELECT p.parent_id, p.kind, p.start_line, f.text FROM lexical_parent p JOIN lexical_chunk c " \
               "ON c.parent_id = p.parent_id AND c.start_line = p.start_line JOIN lexical_fts f ON f.rowid = c.id " \
               "WHERE p.path = ? AND c.path = ?"  # the chunk's path bound too: planned through lexical_chunk_by_path,
    # not a scan of the whole keyword table per file (review F2; the same rows, as a chunk lies in its parent's file)
    _CHUNK = "SELECT c.path, c.parent_id, f.text FROM lexical_chunk c JOIN lexical_fts f ON f.rowid = c.id " \
             "WHERE c.chunk_id = ?"

    def __init__(self, connection: sqlite3.Connection, headers: bool):
        self.connection, self.headers, self._by_path = connection, headers, {}

    def header(self, path: str, parent_id: str) -> str:
        if not self.headers:
            return ""
        if path not in self._by_path:
            firsts = [(parent, kind, start, (text.splitlines() or [""])[0])
                      for parent, kind, start, text in self.connection.execute(self._PARENTS, (path, path))]
            self._by_path = {path: chunking.headers(path, firsts)}  # one file at a time: chunks come in path order
        return self._by_path[path].get(parent_id) or chunking.header(path)

    def __call__(self, chunk_id: str) -> str:
        path, parent_id, text = self.connection.execute(self._CHUNK, (chunk_id,)).fetchone()
        return (self.header(path, parent_id) + text)[:EMBED_CHARS]

    def over_limit(self, wanted: list[str]) -> list[str]:
        """The paths of the embedded chunks longer than ``EMBED_LIMIT_CHARS`` with their headers, once each, in order."""
        keep = set(wanted)
        if not self.headers:
            return _over_limit(self.connection, wanted)
        rows = self.connection.execute("SELECT c.chunk_id, c.path, c.parent_id, length(f.text) FROM lexical_chunk c "
                                       "JOIN lexical_fts f ON f.rowid = c.id ORDER BY c.path, c.start_line").fetchall()
        return list(dict.fromkeys(path for chunk_id, path, parent_id, size in rows if chunk_id in keep
                                  and size + len(self.header(path, parent_id)) > EMBED_LIMIT_CHARS))
_NEAREST = "SELECT c.chunk_id, c.path, c.start_line, c.end_line, c.parent_id, " \
           "vec_distance_cosine(v.embedding, ?) AS distance FROM semantic_vector v " \
           "JOIN lexical_chunk c ON c.chunk_id = v.chunk_id ORDER BY distance, c.chunk_id LIMIT ?"
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
_STATUS: dict = {}  # resolved root -> (key, status): the vectors' status worked out last in this process (W2-108)


def _report(reason: str | None, **more) -> dict:
    named = {"error": reason.code} if isinstance(reason, Refused) else {}
    return {"available": reason is None, "facet": FACET, "state": "FACET_UNAVAILABLE" if reason else "AVAILABLE",
            "reason": None if reason is None else str(reason), **named, **more}


def _ask(path: str, body: dict | None = None, host: str | None = None):
    """The JSON answer to ``path`` of the Ollama endpoint at ``host`` (default: the shared one at ``OLLAMA_HOST``);
    None when it gives none; a transient failure's answer (empty, read as none) when it accepted the request and gave
    no answer within ``TIMEOUT_S`` (``TIMED_OUT``), answered with a server error (HTTP 5xx), or the connection was
    refused or reset (``REFUSED``, ``RESET``)."""
    host = host or os.environ.get("OLLAMA_HOST") or ollama.DEFAULT_HOST
    request = urllib.request.Request((host if "://" in host else f"http://{host}").rstrip("/") + path,
                                     data=None if body is None else json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
    try:
        with _OPENER.open(request, timeout=TIMEOUT_S) as reply:
            return json.load(reply)
    except TimeoutError:  # the socket's own time-out once connected; a refusal comes wrapped in a URLError
        return TIMED_OUT
    except urllib.error.HTTPError as error:  # an answer with an error status: only a server error is transient
        return _Transient(f"HTTP {error.code}") if 500 <= error.code < 600 else None
    except urllib.error.URLError as error:  # raised before an answer: a refusal or a reset is transient
        failure = error.reason
        return REFUSED if isinstance(failure, ConnectionRefusedError) else \
            RESET if isinstance(failure, ConnectionResetError) else None
    except ConnectionResetError:  # reset (or closed with no answer) while the answer was awaited or read
        return RESET
    except (OSError, http.client.HTTPException, ValueError):
        return None


def _embed(texts: list[str], host: str | None = None, retries: list | None = None) -> list[bytes] | None:
    """One float32 BLOB per text, embedded at ``host`` (default: the shared runner) with no runner option; None unless
    the endpoint returned a vector for each. With ``retries`` (a rebuild's chunks), a try that failed transiently
    (timed out, a server error, a refused or reset connection) is tried again after each wait of ``RETRY_WAITS_S`` in
    turn, a request with such a try is recorded in ``retries``, and ``GaveUp`` (naming each try's failure) is raised
    when every try failed so (DEC-1026; W2-126 KPI 7). Any other failure ends at once."""
    waits: list[float] = []
    failures: list[str] = []
    while isinstance(answer := _ask("/api/embed", {"model": _model(), "input": texts}, host), _Transient) \
            and retries is not None and len(waits) < len(RETRY_WAITS_S):
        failures.append(answer.kind)
        waits.append(RETRY_WAITS_S[len(waits)])
        time.sleep(waits[-1])
    vectors = (answer or {}).get("embeddings") or []
    if retries is not None and (waits or isinstance(answer, _Transient)):
        retries.append({"tries": len(waits) + 1, "waits_s": waits, "embedded": len(vectors) == len(texts)})
        if isinstance(answer, _Transient):
            raise GaveUp([*failures, answer.kind])
    if len(vectors) != len(texts):
        return None
    return [struct.pack(f"{len(vector)}f", *vector) for vector in vectors]


def _revision(host: str | None = None) -> str | None:
    """The digest the model list at ``host`` (default: the shared runner) reports for the embedder (DEC-374)."""
    for model in (_ask("/api/tags", host=host) or {}).get("models") or []:
        if _model() in (model.get("name"), model.get("model")):
            return model.get("digest") or None
    return None


def _device(host: str) -> str | None:
    """Where the embedder at ``host`` reports, at ``/api/ps``, the model loaded: ``"cpu"`` with ``size_vram`` 0,
    ``"gpu"`` with ``size_vram`` above 0 (wholly or partly in GPU memory), each with ``size`` above 0 (DEC-1033). None
    when the listing cannot be read, lacks the model or reports it without those two whole numbers."""
    listing = _ask("/api/ps", host=host)
    for model in (listing.get("models") or [] if isinstance(listing, dict) else []):
        if isinstance(model, dict) and _model() in (model.get("name"), model.get("model")):
            size, vram = model.get("size"), model.get("size_vram")
            if not all(isinstance(n, int) and not isinstance(n, bool) for n in (size, vram)) or size <= 0 or vram < 0:
                return None
            return "gpu" if vram > 0 else "cpu"
    return None


def _well_formed(vectors: list[bytes]) -> bool:
    """True when the vectors are of one length above 0 and every number of the question's is finite."""
    if len({len(vector) for vector in vectors}) != 1 or not vectors[-1]:
        return False
    return all(math.isfinite(number) for number in struct.unpack(f"{len(vectors[-1]) // 4}f", vectors[-1]))


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


def query_vector(root: Path, query: str, counts: dict | None = None,
                 expect: str | None = None) -> tuple[bytes | None, str | None]:
    """The vector a search compares with for ``query``, and why there is none: the one cached under its key for
    the GPU, else the one the query embedder gives the question, sent right after the bare instruction in one
    request, if the vectors are well-formed and that embedder then reports the model loaded on the GPU (W2-32 S10,
    DEC-1065; cached then, under that device). When the embedder gives no vector, malformed vectors, does not report
    the model loaded, or computed it on the CPU (``EMBEDDER_ON_CPU``), there is no vector and nothing is cached.
    Without a revision in the model list there is no key and nothing is cached. The machine-wide cache is looked up first, and given the vector whenever the tree's cache is.

    With ``expect`` (the revision the vectors were built with), a query embedder whose model list reports another
    revision, or none, gives no vector: ``MODEL_MISMATCH``, before any cache is read or anything is sent."""
    host = ollama.query_host()
    text, revision, path = INSTRUCTION + query, _revision(host), Path(root) / QUERY_VECTORS_REL
    if expect is not None and revision != expect:
        return None, _mismatch(f"the query embedder reports {_model()} at revision {revision!r}, but the vectors "
                               f"were built at {expect!r}: the question's vector is not compared")
    digest = hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()
    keys = {device: (_model(), revision, device, digest) for device in DEVICES} if revision else {}
    machine = vector_cache.Cache(_model(), revision, counts)
    cached = machine.get([text])[0]
    if cached:
        return cached, None
    for key in keys.values():
        cached = _cached(path, key)
        if cached:
            machine.put([text], [cached])
            return cached, None
    try:
        vectors = _embed([INSTRUCTION, text], host)
    except (struct.error, TypeError):  # an answer whose vectors are not lists of numbers
        return None, _say(MALFORMED)
    if vectors is None:
        return None, _say(NO_EMBEDDING)
    if not _well_formed(vectors):
        return None, _say(MALFORMED)
    device = _device(host)  # read after the computation: a fresh embedder lists nothing until a request loads it
    if device is None:
        return None, _say(NOT_LOADED)
    if device not in DEVICES:  # W2-32 S10: a CPU vector is refused, never cached
        return None, Refused(ON_CPU, _say(QUERY_ON_CPU))
    if device in keys:
        _cache(path, keys[device], vectors[1])
        machine.put([text], [vectors[1]])
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
            held_out = rel.startswith(learning.LEARNING_REL + "/")  # W2-32 S3: the learning loop's, held out
            verdicts[rel] = not held_out and bool(policies) and all(policy == EMBEDDED for policy in policies)
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


def _over_limit(connection: sqlite3.Connection, wanted: list[str]) -> list[str]:
    """The paths of the embedded chunks longer than ``EMBED_LIMIT_CHARS``, once each, in order."""
    over = connection.execute(f"SELECT c.chunk_id, c.path FROM lexical_chunk c JOIN lexical_fts f ON f.rowid = c.id "
                              f"WHERE length(f.text) > {EMBED_LIMIT_CHARS} ORDER BY c.path, c.start_line").fetchall()
    keep = set(wanted)
    return list(dict.fromkeys(path for chunk_id, path in over if chunk_id in keep))


def _build(root: Path, counts: dict, retries: list, cut: dict | None = None) -> str | None:
    """Bring the lexical index up to date, then embed the chunks that have no vector, each whole (up to
    ``EMBED_CHARS``, W2-32 S7), those the machine-wide cache holds taken from it (counted in ``counts``) and the rest
    embedded, recording timed-out requests in ``retries``; why it cannot be done, or None.

    Under the pin of ``models.yaml`` (W2-32 S1, S2): an unpinned configuration, or an endpoint that reports another
    revision than the pinned one, stops it before anything is sent or stored. Vectors built under another model,
    revision or cut are all dropped first, so every chunk is embedded again (a full re-embed)."""
    lexical.refresh(root)
    pin, refused = _pin(root)
    headers, unread = _recipe(root)
    files_on, unread_files = _file_setting(root)
    if refused or unread or unread_files:
        return refused or unread or unread_files  # nothing was sent to be embedded, the store's vectors as they are
    connection = sqlite3.connect(root / STORE_REL)
    try:
        reason = _ready(connection)
        revision = None if reason else _revision()
        if revision is None:
            return reason or Refused(models.NOT_LISTED, _say(NO_MODEL))  # nothing was sent to be embedded
        if not pin.matches(revision):
            return _mismatch(f"the endpoint reports {pin.model} at revision {revision}, but {pin.source} pins "
                             f"{pin.revision}: nothing is embedded")
        connection.executescript(SCHEMA)
        wanted = _wanted(root, connection)
        text_of = _Texts(connection, headers)
        if cut is not None:  # the chunks above the embedder's limit, named (DEC-1067; review F-4)
            over = text_of.over_limit(wanted)
            cut.update(limit=EMBED_LIMIT_CHARS, count=len(over), paths=over)
            if over:
                print(f"semantic: {len(over)} file(s) hold a chunk over {EMBED_LIMIT_CHARS} characters, embedded "
                      f"from its first {EMBED_LIMIT_CHARS}: {', '.join(over)}", file=sys.stderr, flush=True)
        with connection:
            built_by = connection.execute("SELECT embedder_model, embedder_revision FROM semantic_manifest").fetchone()
            other_pin = built_by != (pin.model, revision) or _cut(connection) != EMBED_CHARS
            if other_pin or _recorded_headers(connection) is not headers:
                connection.execute("DELETE FROM semantic_vector")  # another pin, cut or recipe: a full re-embed
            connection.execute("DELETE FROM semantic_manifest")
            connection.execute("INSERT INTO semantic_manifest VALUES (?, ?, ?, ?)",
                               (pin.model, revision, rerank.MODEL, rerank.REVISION))
            connection.execute("INSERT OR REPLACE INTO semantic_pin VALUES (?, ?)", (CUT_KEY, str(EMBED_CHARS)))
            connection.execute("INSERT OR REPLACE INTO semantic_pin VALUES (?, ?)",
                               (HEADERS_KEY, "true" if headers else "false"))
            have = {chunk_id for (chunk_id,) in connection.execute("SELECT chunk_id FROM semantic_vector")}
            connection.executemany("DELETE FROM semantic_vector WHERE chunk_id = ?",
                                   [(chunk_id,) for chunk_id in have - set(wanted)])
            missing = [chunk_id for chunk_id in wanted if chunk_id not in have]
            machine = vector_cache.Cache(pin.model, revision, counts)
            for start in range(0, len(missing), BATCH):
                batch = missing[start:start + BATCH]
                vectors, failed = _embedded([text_of(chunk_id) for chunk_id in batch], machine, retries)
                if failed:
                    return failed
                connection.executemany("INSERT INTO semantic_vector VALUES (?, ?)", zip(batch, vectors))
            return _build_files(connection, wanted, files_on, other_pin, machine, retries)
    finally:
        connection.close()


def _embedded(texts: list[str], machine, retries: list) -> tuple[list[bytes] | None, str | None]:
    """A vector for each text, those the machine-wide cache holds taken from it and the rest embedded on the GPU (W2-32
    S10), or why none is kept (the request gave up or gave nothing, or the device was the CPU or could not be read)."""
    vectors = machine.get(texts)  # no cache connection stays open while the misses are embedded
    todo = [i for i, vector in enumerate(vectors) if vector is None]
    if todo:
        try:
            embedded = _embed([texts[i] for i in todo], retries=retries)
        except GaveUp as gave_up:  # the vectors made so far stay; the store is not reported built
            return None, _gave_up(gave_up.args[0])
        if embedded is None:
            return None, _say(NO_EMBEDDING)
        device = _batch_device()  # W2-32 S10: read after the request, which loads the model
        if device is None:  # never assumed the GPU: nothing of this batch is kept (review F-2)
            return None, Refused(DEVICE_UNREAD, _say(BUILD_DEVICE_UNREAD))
        if device not in DEVICES:  # listed on the CPU (size_vram 0): nothing of this batch is kept
            return None, Refused(ON_CPU, _say(BUILD_ON_CPU))
        machine.put([texts[i] for i in todo], embedded)
        for i, vector in zip(todo, embedded):
            vectors[i] = vector
    return vectors, None


def _build_files(connection: sqlite3.Connection, wanted: list[str], on: bool, other_pin: bool, machine,
                 retries: list) -> str | None:
    """The file-level index brought to the setting (DEC-1068 M1). Off: its table and its ``semantic_pin`` row
    dropped, so the store is today's. On: one vector per file of the embedded chunks, of ``_FileTexts``'s text; a
    file whose text changed, or every file under another pin or cut, embedded again, and a file no longer embedded
    dropped. The chunk vectors are never touched here, so switching the setting rebuilds the file vectors alone."""
    if not on:
        connection.execute("DROP TABLE IF EXISTS semantic_file_vector")
        connection.execute("DELETE FROM semantic_pin WHERE key = ?", (FILE_KEY,))
        return None
    connection.execute(_FILE_TABLE)
    if other_pin:
        connection.execute("DELETE FROM semantic_file_vector")
    keep = set(wanted)
    paths = list(dict.fromkeys(path for chunk_id, path in connection.execute(
        "SELECT chunk_id, path FROM lexical_chunk ORDER BY path, start_line") if chunk_id in keep))
    file_text = _FileTexts(connection)
    texts = {path: file_text(path) for path in paths}
    digests = {path: hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest() for path, text in texts.items()}
    have = dict(connection.execute("SELECT path, text_sha256 FROM semantic_file_vector"))
    connection.executemany("DELETE FROM semantic_file_vector WHERE path = ?",
                           [(path,) for path, digest in have.items() if digests.get(path) != digest])
    connection.execute("INSERT OR REPLACE INTO semantic_pin VALUES (?, ?)", (FILE_KEY, "true"))
    missing = [path for path in paths if have.get(path) != digests[path]]
    for start in range(0, len(missing), BATCH):
        batch = missing[start:start + BATCH]
        vectors, failed = _embedded([texts[path] for path in batch], machine, retries)
        if failed:
            return failed
        connection.executemany("INSERT INTO semantic_file_vector VALUES (?, ?, ?)",
                               [(path, digests[path], vector) for path, vector in zip(batch, vectors)])
    return None


def _batch_device() -> str | None:
    """The device the shared embedder reports the model on, read after a chunk batch (W2-32 S10). A listing that
    cannot be read, or lacks the model, is transient, as a failed request is (DEC-1026): read again after each wait
    of ``RETRY_WAITS_S`` in turn. None after the last try; ``"cpu"`` only for the model listed with ``size_vram`` 0."""
    device = _device(None)
    for wait in RETRY_WAITS_S:
        if device is not None:
            break
        time.sleep(wait)
        device = _device(None)
    return device


def _gave_up(failures: list[str]) -> str:
    """Why the stage stopped after the last try: W2-123's words when every try timed out, else each try's failure."""
    tail = f"each under {TIMEOUT_S:g} s; waits {', '.join(f'{w:g} s' for w in RETRY_WAITS_S)}"
    if all(failure == TIMED_OUT.kind for failure in failures):
        return f"{_say(NO_EMBEDDING)}: the request timed out at all {len(failures)} tries ({tail})"
    return f"{_say(NO_EMBEDDING)}: the request failed at all {len(failures)} tries ({', '.join(failures)}; {tail})"


def _cut(connection: sqlite3.Connection) -> int | None:
    """The cut the store's vectors were made with, from ``semantic_pin``; None for a store built before it was
    recorded (W2-L065), or one that cannot say."""
    try:
        row = connection.execute("SELECT value FROM semantic_pin WHERE key = ?", (CUT_KEY,)).fetchone()
    except sqlite3.Error:
        return None
    try:
        return int(row[0]) if row else None
    except ValueError:
        return None


def _built_at(connection: sqlite3.Connection) -> str | None:
    """The revision the store's vectors were built at; None when the store records none."""
    try:
        row = connection.execute("SELECT embedder_revision FROM semantic_manifest").fetchone()
    except sqlite3.Error:
        return None
    return row[0] if row else None


def _status(root: Path) -> str | None:
    """Why the vectors cannot be answered from as they stand (missing, empty or stale), or None. Writes nothing.
    Worked out once per store, tree and configuration in a process, keyed by their fingerprints, and again whenever a
    fingerprint changes or cannot be read (W2-108); the lexical index's freshness is kept the same way."""
    tree, status, _ = lexical._checked(root)  # the store's and the tree's key, taken with the lexical answer
    if status != "fresh":
        return status
    config = lexical._stamps(Path(root) / PROJECT_DIR / name  # what ``_wanted``, ``_pin`` and ``_recipe`` read
                             for name in [*KNOWN_FILES, models.MODELS_FILE])  # rebuild.yaml among the known
    key, place = None if tree is None or config is None else (tree, config), Path(root).resolve()
    if key is None or _STATUS.get(place, (None,))[0] != key:
        _STATUS[place] = (key, _vectors(root))
    return _STATUS[place][1]


def _vectors(root: Path) -> str | None:
    """The status of the vectors, worked out from the store, the path map and the pin as they stand: a pin that
    cannot be had, or vectors built under another model or revision, refuse them by name; another cut, or another
    recipe than ``rebuild.yaml``'s ``embed_headers`` (DEC-1067 order (5)), is stale. A setting that cannot be read is
    refused by name (``CONFIG_INVALID``)."""
    pin, refused = _pin(root)
    headers, unread = _recipe(root)
    files_on, unread_files = _file_setting(root)
    if refused or unread or unread_files:
        return refused or unread or unread_files
    connection = _open(root)
    if connection is None:
        return "missing"
    try:
        have = {chunk_id for (chunk_id,) in connection.execute("SELECT chunk_id FROM semantic_vector")}
        built_by = connection.execute("SELECT embedder_model, embedder_revision FROM semantic_manifest").fetchone()
        if built_by is None:
            return "missing"
        if built_by[0] != pin.model or not pin.matches(built_by[1]):
            return _mismatch(f"the vectors were built with {built_by[0]} at revision {built_by[1]}, but {pin.source} "
                             f"pins {pin.model} at {pin.revision}: they are not compared until a rebuild embeds "
                             f"them all again")
        if _cut(connection) != EMBED_CHARS:  # W2-L065: built before the cut was recorded, or under another cut
            return "stale"
        if _recorded_headers(connection) is not headers:  # the setting switched since the vectors were made
            return "stale"
        if _recorded_files(connection) is not files_on:  # DEC-1068 M1: the file index built otherwise than set
            return "stale"
        wanted = _wanted(root, connection)
        if files_on and _file_paths(connection) != set(_paths_of(connection, wanted)):
            return "stale"  # a file of the embedded chunks without its vector, or one no longer embedded
        return "stale" if have != set(wanted) else None if have else "empty"
    finally:
        connection.close()


def _file_paths(connection: sqlite3.Connection) -> set[str] | None:
    """The files the file-level index holds a vector of; None when it has no table."""
    try:
        return {path for (path,) in connection.execute("SELECT path FROM semantic_file_vector")}
    except sqlite3.Error:
        return None


def _paths_of(connection: sqlite3.Connection, chunk_ids: list[str]) -> list[str]:
    """The files of ``chunk_ids``, once each."""
    keep = set(chunk_ids)
    return list(dict.fromkeys(path for chunk_id, path in connection.execute("SELECT chunk_id, path FROM lexical_chunk")
                              if chunk_id in keep))


def _pinned(work):
    """``work(pin)`` run with the pinned model as the one every request names (``_model``)."""
    def run(root, *args, **kwargs):
        pin, _ = _pin(Path(root))
        token = _MODEL.set(pin.model if pin else None)
        try:
            return work(root, *args, **kwargs)
        finally:
            _MODEL.reset(token)
    run.__doc__, run.__name__, run.__wrapped__ = work.__doc__, work.__name__, work
    return run


@_pinned
def refresh(root: Path) -> dict:
    """Bring the lexical index up to date, then embed the chunks that have no vector. ``retries`` lists, in order,
    each chunk batch request that failed transiently at least once (timed out, a server error, a refused or reset
    connection): its tries, the waits taken and whether it embedded. Under another pin than the store's, every
    chunk is embedded again; an unpinned or mismatched pin embeds nothing (``error`` names which)."""
    counts, retries, cut = vector_cache.zero(), [], {}
    return _report(_build(Path(root), counts, retries, cut), retries=retries, vector_cache=counts,
                   cut=cut or {"limit": EMBED_LIMIT_CHARS, "count": 0, "paths": []})


@_pinned
def search(root: Path, query: str, refresh: bool = True, top_k: int | None = None) -> dict:
    """The ``TOP_K`` chunks nearest to ``query``, nearest first, as the chunk records of the lexical index; ``top_k``
    is this search's depth in place of ``TOP_K`` (W2-32 S11's ``pool.route_depth``; None or 0: ``TOP_K``).

    With ``refresh`` the vectors are brought up to date first. Without, the store is not written, and missing, empty
    or stale vectors are reported as ``FACET_UNAVAILABLE`` with the reason and no hit (DEC-342). Either way, the
    question is embedded by the query embedder alone (never started here, and used only from the GPU: W2-32 S10,
    DEC-1065) and its vector is cached beside the store once the vectors can be answered from (DEC-782).

    Under the pin (W2-32 S2): an unpinned configuration, vectors built under another pin, or a query embedder that
    reports another revision than the vectors were built with give no hit, with ``error`` naming the refusal.
    """
    root, counts = Path(root), vector_cache.zero()
    reason = (_build(root, counts, []) if refresh else None) or _status(root)
    if reason:
        return _report(reason, hits=[], vector_cache=counts)
    connection = _open(root)
    try:
        reason = _ready(connection, ollama.ensure_query_available)
        built_at = None if reason else _built_at(connection)
        if not reason and built_at is None:
            reason = "missing"
        vector, reason = (None, reason) if reason else query_vector(root, query, counts, expect=built_at)
        if vector is None:
            return _report(reason, hits=[], vector_cache=counts)
        keys = ("chunk_id", "path", "start_line", "end_line", "parent_id", "distance")
        return _report(None, hits=[dict(zip(keys, row)) for row in connection.execute(_NEAREST, (vector, top_k or TOP_K))],
                       vector_cache=counts)
    finally:
        connection.close()


_NEAREST_FILES = "SELECT path, vec_distance_cosine(embedding, ?) AS distance FROM semantic_file_vector " \
                 "ORDER BY distance, path LIMIT ?"
_BEST_OF_FILE = "SELECT c.chunk_id, c.path, c.start_line, c.end_line, c.parent_id, " \
                "vec_distance_cosine(v.embedding, ?) AS distance FROM semantic_vector v " \
                "JOIN lexical_chunk c ON c.chunk_id = v.chunk_id WHERE c.path = ? ORDER BY distance, c.chunk_id LIMIT ?"


@_pinned
def file_search(root: Path, query: str, refresh: bool = False) -> dict:
    """The file route (DEC-1068 M1): the ``FILE_TOP`` files whose file vectors are nearest the question, each
    expanded to its ``FILE_CHUNKS`` chunks nearest the question by their own vectors; ``hits`` are those chunks as
    the chunk records ``search`` gives (with ``file_distance`` beside the chunk's ``distance``), file by file, nearest
    first. Unavailable, with the reason and no hit, when the setting is off (``FILE_OFF``), the vectors cannot be
    answered from as they stand (as ``search``: missing, empty, stale or refused) or no question vector can be had.
    Reads only: ``refresh`` is accepted for the routes' call and never builds anything."""
    root, counts = Path(root), vector_cache.zero()
    on, unread = _file_setting(root)
    reason = unread or (None if on else FILE_OFF) or _status(root)
    if reason:
        return _report(reason, hits=[], vector_cache=counts)
    connection = _open(root)
    try:
        reason = _ready(connection, ollama.ensure_query_available)
        built_at = None if reason else _built_at(connection)
        if not reason and built_at is None:
            reason = "missing"
        vector, reason = (None, reason) if reason else query_vector(root, query, counts, expect=built_at)
        if vector is None:
            return _report(reason, hits=[], vector_cache=counts)
        keys = ("chunk_id", "path", "start_line", "end_line", "parent_id", "distance")
        hits = []
        for path, file_distance in connection.execute(_NEAREST_FILES, (vector, FILE_TOP)).fetchall():
            hits += [{**dict(zip(keys, row)), "file_distance": file_distance}
                     for row in connection.execute(_BEST_OF_FILE, (vector, path, FILE_CHUNKS))]
        return _report(None, hits=hits, vector_cache=counts)
    finally:
        connection.close()


@_pinned
def distances(root: Path, query: str, chunk_ids: list[str]) -> dict[str, float] | None:
    """Each chunk's cosine distance from its stored vector to the question's (W2-32 S8: the code route ranked); a
    chunk with no vector is left out. None when no vector can be compared (vectors missing, stale or of another pin,
    or no question vector), so the caller keeps its own order. Reads only, and the question's vector is the one a
    search uses (cached, from the GPU, never an embedder started)."""
    root = Path(root)
    if not chunk_ids or _status(root):
        return None
    connection = _open(root)
    if connection is None:
        return None
    try:
        built_at = _built_at(connection)
        if built_at is None or not ollama.ensure_query_available()["available"]:
            return None
        vector, _ = query_vector(root, query, None, expect=built_at)
        if vector is None:
            return None
        question = struct.unpack(f"{len(vector) // 4}f", vector)
        q_norm = math.sqrt(sum(x * x for x in question)) or 1.0
        found: dict[str, float] = {}
        ids = list(dict.fromkeys(chunk_ids))
        for start in range(0, len(ids), 500):
            part = ids[start:start + 500]
            rows = connection.execute(f"SELECT chunk_id, embedding FROM semantic_vector "
                                      f"WHERE chunk_id IN ({','.join('?' * len(part))})", part)
            for chunk_id, blob in rows:
                stored = struct.unpack(f"{len(blob) // 4}f", blob)
                if len(stored) != len(question):
                    continue
                norm = math.sqrt(sum(x * x for x in stored)) or 1.0
                found[chunk_id] = 1.0 - sum(a * b for a, b in zip(question, stored)) / (q_norm * norm)
        return found
    finally:
        connection.close()


def manifest(root: Path) -> dict | None:
    """The models the vectors were built with and the reranker's pin, each with its revision; None when there is no
    vector index. Read from the store alone: writes nothing and asks Ollama nothing (DEC-374). ``embed_chars`` is the
    cut the vectors were made with (W2-L065), None for a store built before it was recorded. ``embed_headers`` is the
    recipe: whether each chunk was embedded after its contextual header (DEC-1067 order (5)); false for a store built
    before it was recorded."""
    connection = _open(root)
    if connection is None:
        return None
    try:
        row = connection.execute("SELECT * FROM semantic_manifest").fetchone()
        cut, headers, files = _cut(connection), _recorded_headers(connection), _recorded_files(connection)
    finally:
        connection.close()
    return row and {"embedder": {"model": row[0], "revision": row[1]},
                    "reranker": {"model": row[2], "revision": row[3]}, CUT_KEY: cut, HEADERS_KEY: headers,
                    FILE_KEY: files}
