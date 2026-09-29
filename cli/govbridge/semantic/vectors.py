"""The vector store (ARCHITECTURE.md section 4.5/9, SEMANTIC_ROUTE.md section 4): ``vector(chunk_id TEXT PRIMARY
KEY, text_sha256 TEXT, pin_id TEXT, dim INT, vec BLOB)`` in the same ``store.db`` every other layer shares
(``govbridge.core.store``), plus brute-force cosine search and the CLI this node's determinism acceptance check
runs (``python -m govbridge.semantic.vectors determinism``).

Nothing here is specific to the pinned model: every function takes ``pin_id``/``dim`` as data, so a Phase-3
replacement model builds a parallel vector set under its own pin id (SEMANTIC_ROUTE.md section 5, "Replacement")
without touching this module.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Iterable, Optional

from govbridge.core import store
from govbridge.core.manifest import FIELD_SEP, ROW_SEP
from govbridge.core.yamlutil import sha256_bytes
from govbridge.semantic import modelpin, runner

DIM_BYTES = 4  # float32


def create_table(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS vector (
            chunk_id TEXT PRIMARY KEY,
            text_sha256 TEXT NOT NULL,
            pin_id TEXT NOT NULL,
            dim INTEGER NOT NULL,
            vec BLOB NOT NULL
        );
        CREATE INDEX IF NOT EXISTS vector_by_text_pin ON vector(text_sha256, pin_id);
        CREATE INDEX IF NOT EXISTS vector_by_pin ON vector(pin_id);
        """
    )
    conn.commit()


def vec_to_bytes(values: Iterable[float]) -> bytes:
    import numpy as np

    return np.asarray(list(values), dtype="<f4").tobytes()


def bytes_to_vec(data: bytes):
    import numpy as np

    return np.frombuffer(data, dtype="<f4")


def put_vector(conn: sqlite3.Connection, chunk_id: str, text_sha256: str, pin_id: str, dim: int,
                vec_bytes: bytes) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO vector(chunk_id, text_sha256, pin_id, dim, vec) VALUES (?,?,?,?,?)",
        (chunk_id, text_sha256, pin_id, dim, vec_bytes),
    )


def reuse_vector(conn: sqlite3.Connection, text_sha256: str, pin_id: str) -> Optional[bytes]:
    row = conn.execute(
        "SELECT vec FROM vector WHERE text_sha256=? AND pin_id=? LIMIT 1", (text_sha256, pin_id)
    ).fetchone()
    return row[0] if row else None


def count_for_pin(conn: sqlite3.Connection, pin_id: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM vector WHERE pin_id=?", (pin_id,)).fetchone()[0]


def digest_for_pin(conn: sqlite3.Connection, pin_id: str) -> str:
    """sha256 over sorted (chunk_id, sha256(vec)) -- schemas/build-manifest.yaml's ``vector`` layer field,
    verbatim. Row-hashed the same way govbridge.core.manifest's own layer digests are (FIELD_SEP/ROW_SEP), so all
    layer digests in one manifest are built the same way."""
    rows = conn.execute(
        "SELECT chunk_id, vec FROM vector WHERE pin_id=? ORDER BY chunk_id", (pin_id,)
    ).fetchall()
    h = hashlib.sha256()
    for chunk_id, vec_bytes in rows:
        h.update(FIELD_SEP.join([chunk_id, sha256_bytes(vec_bytes)]).encode("utf-8"))
        h.update(ROW_SEP.encode())
    return h.hexdigest()


#: the BUILD-time deduplicated (blob_id, path) table (REPAIR_DAG.yaml node R1-GA1, second reopening) -- shared with
#: govbridge.lexical.query (same store.db, same name, same shape). Created and maintained ONLY by
#: govbridge.core.store/.freshness; this module only ever READS it.
SCOPE_PATH_CACHE_TABLE = "occurrence_distinct_path"
#: the BUILD-time index (govbridge.authority.layer's own SCHEMA_SQL) this module's Tier A relies on.
_RECORD_DEF_PATH_INDEX = "record_def_by_path"


class StoreNeedsRebuild(RuntimeError):
    """The semantic-route twin of ``govbridge.lexical.query.StoreNeedsRebuild`` -- see its docstring. A separate
    class (never imported from govbridge.lexical) so this module stays independent of the lexical package."""
    CODE = "STORE_NEEDS_REBUILD"

    def __init__(self, missing: str):
        self.missing = missing
        super().__init__(
            f"{self.CODE}: {missing} is missing from this store -- rebuild it (e.g. "
            f"`python -m govbridge index rebuild`) before running a scoped query against it; a query path never "
            f"builds this itself"
        )


def _sqlite_object_exists(conn: sqlite3.Connection, kind: str, name: str) -> bool:
    row = conn.execute("SELECT name FROM sqlite_master WHERE type=? AND name=?", (kind, name)).fetchone()
    return row is not None


def _check_scope_structures(conn: sqlite3.Connection, needs_cache_table: bool, needs_record_def_index: bool) -> None:
    """READ-ONLY (sqlite_master lookups only) -- see govbridge.lexical.query._check_scope_structures's docstring
    for the full rationale. Checked lazily, only for whichever tier(s) a call's scope_classes/scope_path_globs
    combination will actually use."""
    if needs_cache_table and not _sqlite_object_exists(conn, "table", SCOPE_PATH_CACHE_TABLE):
        raise StoreNeedsRebuild(f"table {SCOPE_PATH_CACHE_TABLE!r} (govbridge.core.store)")
    if needs_record_def_index and not _sqlite_object_exists(conn, "index", _RECORD_DEF_PATH_INDEX):
        raise StoreNeedsRebuild(f"index {_RECORD_DEF_PATH_INDEX!r} (govbridge.authority.layer)")


def _scope_sql(scope_classes: Optional[tuple], lifecycle_scope: Optional[tuple],
               scope_path_globs: Optional[tuple]) -> tuple:
    """The semantic-route twin of ``govbridge.lexical.query._scope_sql`` (REPAIR_DAG.yaml node R1-GA1 reopening):
    a SQL fragment (``''`` or ``' AND (...)'``) plus its bound params, joined against ``chunk``/``occurrence``/
    ``record_def``/``class_lifecycle`` (all pre-existing store tables; no new schema, no ``govbridge.authority``
    import) so a SCOPED facet's candidate set is restricted BEFORE the top-k cosine ranking runs, never after.
    Duplicated rather than imported from ``govbridge.lexical.query`` on purpose: this module stays independent of
    the lexical package (SEMANTIC_ROUTE.md's own "B2/B4 are siblings, neither depends on the other")."""
    if not scope_classes and not scope_path_globs:
        return "", []
    clauses: list = []
    params: list = []
    if scope_classes:
        cls_placeholders = ",".join("?" for _ in scope_classes)
        # occurrence_distinct_path (built at BUILD time, see govbridge.core.store), never the raw occurrence
        # table: the SAME blob/path pair repeats once per historical (ref, commit) on occurrence (hundreds of
        # times for a popular blob on this corpus), so matching against the deduplicated table is the difference
        # between a handful of row checks and hundreds -- measured directly as the actual cost behind a
        # corpus-scale timeout.
        tier_a = (
            f"EXISTS (SELECT 1 FROM {SCOPE_PATH_CACHE_TABLE} rdo "
            "JOIN record_def rd ON rd.path = rdo.path AND rd.line_start <= c.end_line AND rd.line_end >= c.start_line "
            "JOIN class_lifecycle cl ON cl.unit = rd.id "
            f"WHERE rdo.blob_id = c.blob_id AND cl.cls IN ({cls_placeholders})"
        )
        params.extend(scope_classes)
        if lifecycle_scope:
            lc_placeholders = ",".join("?" for _ in lifecycle_scope)
            tier_a += f" AND cl.lifecycle IN ({lc_placeholders})"
            params.extend(lifecycle_scope)
        tier_a += ")"
        clauses.append(tier_a)
    if scope_path_globs and not lifecycle_scope:
        glob_or = " OR ".join("occ2.path GLOB ?" for _ in scope_path_globs)
        clauses.append(f"EXISTS (SELECT 1 FROM {SCOPE_PATH_CACHE_TABLE} occ2 WHERE occ2.blob_id = c.blob_id "
                        f"AND ({glob_or}))")
        params.extend(scope_path_globs)
    if not clauses:
        return "", []
    return " AND (" + " OR ".join(clauses) + ")", params


def search(conn: sqlite3.Connection, qvec, k: int, pin_id: str, offset: int = 0,
           scope_classes: Optional[tuple] = None, lifecycle_scope: Optional[tuple] = None,
           scope_path_globs: Optional[tuple] = None):
    """Brute-force cosine search (vectors are already L2-normalised at embed time, so dot product == cosine).
    Returns [(chunk_id, score)], highest score first, ties broken by ``chunk_id`` ASC for full determinism (two
    vectors can legitimately tie on score, especially in small/synthetic corpora; a fixed tiebreaker is what makes
    the same query byte-identical across thread counts and repeated runs -- REPAIR_DAG.yaml node R1-GA1). O(n) over
    the pin's vectors -- fine at this corpus's scale (SEMANTIC_ROUTE.md section 3: ~40k x 384 floats, ~61 MB);
    ARCHITECTURE.md section 9 names the replacement path (e.g. HNSW) once the corpus outgrows brute force.

    ``offset`` (REPAIR_PLAN.md section 2.4, "lexical and semantic take an offset"): pages through the SAME full,
    deterministic ranking -- ``search(..., k=k, offset=0)`` then ``search(..., k=k, offset=k)`` etc. returns exactly
    the same union, one page at a time, as a single unbounded call would.

    ``scope_classes``/``lifecycle_scope``/``scope_path_globs`` (REPAIR_DAG.yaml node R1-GA1 reopening): restricts
    the candidate SET before ranking (:func:`_scope_sql`), so a scoped facet's top-k is already in scope. This
    function is READ-ONLY with respect to scope filtering: it never creates or populates the structures Tier A/B
    rely on (built at BUILD time -- see govbridge.core.store/.freshness and govbridge.authority.layer) -- if scope
    filtering is requested and the store does not have them yet, :class:`StoreNeedsRebuild` is raised (never a
    silent, slower fallback to an unscoped candidate set, and never a write)."""
    import numpy as np

    scope_sql, scope_params = _scope_sql(scope_classes, lifecycle_scope, scope_path_globs)
    if scope_sql:
        _check_scope_structures(conn, needs_cache_table=True, needs_record_def_index=bool(scope_classes))
        # The `chunk` JOIN is needed ONLY here: _scope_sql's own fragments reference c.blob_id/c.start_line/
        # c.end_line. An unscoped call (the overwhelming common case, and every pre-existing caller/test) never
        # joins `chunk` at all -- this table belongs to govbridge.core.store, not to this module's own schema
        # (vectors.create_table only creates `vector`), so a caller testing `vector` in isolation must not be
        # required to have a `chunk` table just to run an UNSCOPED search.
        rows = conn.execute(
            "SELECT v.chunk_id, v.dim, v.vec FROM vector v JOIN chunk c ON c.chunk_id = v.chunk_id "
            "WHERE v.pin_id=?" + scope_sql,
            (pin_id, *scope_params),
        ).fetchall()
    else:
        rows = conn.execute("SELECT chunk_id, dim, vec FROM vector WHERE pin_id=?", (pin_id,)).fetchall()
    if not rows:
        return []
    dim = rows[0][1]
    ids = [r[0] for r in rows]
    mat = np.frombuffer(b"".join(r[2] for r in rows), dtype="<f4").reshape(len(rows), dim)
    q = np.asarray(qvec, dtype="<f4")
    scores = mat @ q
    order = sorted(range(len(ids)), key=lambda i: (-scores[i], ids[i]))
    page = order[offset:offset + k]
    return [(ids[i], float(scores[i])) for i in page]


# ---------------------------------------------------------------------------------------------------------------
# Embedding + storage, shared by the freshness layer builder and the CLI below.
# ---------------------------------------------------------------------------------------------------------------

def embed_and_store(conn: sqlite3.Connection, chunk_rows, pin: "modelpin.ModelPin", pin_id: str,
                     threads: int = 4, batch_size: int = 1, adapter_path: Optional[str] = None,
                     adapter_args: Optional[list] = None, batch_texts: int = 2000) -> dict:
    """``chunk_rows``: iterable of (chunk_id, text_sha256, text). Groups rows by ``text_sha256`` first, so every
    distinct text is embedded (or reused from a previous run's stored vector, SEMANTIC_ROUTE.md section 5.3) at
    most once, however many chunk rows share it -- one chunk per unique group is credited ``chunks_embedded``
    (or, if a prior vector already exists under this ``pin_id``, none are); every other chunk sharing that text
    is credited ``chunks_reused`` and gets a byte-identical copy of the same vector, never a second model call.
    Returns stats: {chunks_seen, chunks_embedded, chunks_reused, wall_seconds, throughput_chunks_per_s}."""
    extra_args = ["--threads", str(threads), "--batch-size", str(batch_size)]
    if adapter_args:
        extra_args += adapter_args
    kw = {"adapter_path": adapter_path} if adapter_path else {}

    t0 = time.monotonic()
    groups: dict = {}  # text_sha256 -> {"text": str, "chunk_ids": [chunk_id, ...]}
    seen = 0
    for chunk_id, text_sha256, text in chunk_rows:
        seen += 1
        g = groups.get(text_sha256)
        if g is None:
            groups[text_sha256] = {"text": text, "chunk_ids": [chunk_id]}
        else:
            g["chunk_ids"].append(chunk_id)

    embedded = 0
    reused = 0
    need_embed: list = []  # (text_sha256, text)
    for text_sha256, g in groups.items():
        existing = reuse_vector(conn, text_sha256, pin_id)
        if existing is not None:
            dim = len(existing) // DIM_BYTES
            for cid in g["chunk_ids"]:
                put_vector(conn, cid, text_sha256, pin_id, dim, existing)
            reused += len(g["chunk_ids"])
        else:
            need_embed.append((text_sha256, g["text"]))
    # B4 OI-5 ("embed_and_store commits once, at the end"): commit the reuse pass now, before any embedding call,
    # so a kill during the (much longer) embedding loop below never loses rows this pass already resolved for
    # free from a previous run's stored vectors.
    conn.commit()

    for i in range(0, len(need_embed), batch_texts):
        batch = need_embed[i:i + batch_texts]
        outputs = runner.embed([t for _, t in batch], mode="passage", dimensions=pin.dimensions, pin_id=pin_id,
                                extra_args=extra_args, **kw)
        dim = outputs["dim"]
        for (text_sha256, _text), vec in zip(batch, outputs["vectors"]):
            vb = vec_to_bytes(vec)
            chunk_ids = groups[text_sha256]["chunk_ids"]
            put_vector(conn, chunk_ids[0], text_sha256, pin_id, dim, vb)
            embedded += 1
            for cid in chunk_ids[1:]:
                put_vector(conn, cid, text_sha256, pin_id, dim, vb)
                reused += 1
        # B4 OI-5: commit PER BATCH, not once at the end. A killed rebuild resumes: every already-committed batch's
        # text_sha256 group is found by `reuse_vector` above on the next call (whether that next call is a fresh
        # `embed_and_store` over the SAME uncompleted chunk_rows, or the same store simply reopened), so it is
        # never re-embedded -- only the remaining, not-yet-committed batches call the model again. This is proven
        # equal to an uninterrupted build by digest (tests/semantic/test_vectors_resumability.py::
        # test_resumed_build_equals_uninterrupted_build, a NEW test file -- this function's existing tests are
        # unmodified).
        conn.commit()
    wall = time.monotonic() - t0
    return {
        "chunks_seen": seen, "chunks_embedded": embedded, "chunks_reused": reused,
        "wall_seconds": round(wall, 3),
        "throughput_chunks_per_s": round(embedded / wall, 2) if wall > 0 and embedded else 0.0,
    }


# ---------------------------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------------------------

def _sample_chunks(conn: sqlite3.Connection, n: int):
    return conn.execute("SELECT chunk_id, text_sha256, text FROM chunk ORDER BY chunk_id LIMIT ?", (n,)).fetchall()


def cmd_determinism(args) -> int:
    root = Path(args.store) if args.store else store.store_root()
    conn = store.open_db(root=root)
    create_table(conn)
    rows = _sample_chunks(conn, args.sample)
    if not rows:
        print(json.dumps({"error": "NO_CHUNKS", "message": f"no chunks in {root}/store.db; run the core layer first"}))
        return 1
    pin_path = args.pin or modelpin.default_pin_path()
    pin = modelpin.load_model_pin(pin_path)
    texts = [r[2] for r in rows]

    adapter_kw = {"adapter_path": args.adapter} if args.adapter else {}
    extra1 = ["--threads", str(args.threads), "--batch-size", "1"]
    extra32 = ["--threads", str(args.threads), "--batch-size", "32"]
    if args.model_dir:
        extra1 += ["--model-dir", args.model_dir]
        extra32 += ["--model-dir", args.model_dir]

    t0 = time.monotonic()
    out1 = runner.embed(texts, mode="passage", dimensions=pin.dimensions, extra_args=extra1, **adapter_kw)
    t1 = time.monotonic()
    out32 = runner.embed(texts, mode="passage", dimensions=pin.dimensions, extra_args=extra32, **adapter_kw)
    t2 = time.monotonic()

    def digest_of(vectors):
        h = hashlib.sha256()
        for cid, v in zip((r[0] for r in rows), vectors):
            h.update(FIELD_SEP.join([cid, sha256_bytes(vec_to_bytes(v))]).encode("utf-8"))
            h.update(ROW_SEP.encode())
        return h.hexdigest()

    d1 = digest_of(out1["vectors"])
    d32 = digest_of(out32["vectors"])
    result = {
        "sample": len(rows), "threads": args.threads,
        "batch1_digest": d1, "batch32_digest": d32, "batch1_eq_batch32": d1 == d32,
        "batch1_seconds": round(t1 - t0, 3), "batch32_seconds": round(t2 - t1, 3),
        "pin_id": out1.get("pin_id"),
    }
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if d1 == d32 else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.semantic.vectors")
    sub = p.add_subparsers(dest="cmd", required=True)

    det = sub.add_parser("determinism")
    det.add_argument("--sample", type=int, default=50)
    det.add_argument("--threads", type=int, default=4)
    det.add_argument("--store")
    det.add_argument("--pin")
    det.add_argument("--adapter")
    det.add_argument("--model-dir")

    args = p.parse_args(argv)
    if args.cmd == "determinism":
        return cmd_determinism(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
