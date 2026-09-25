"""The "semantic" freshness layer builder and the "vector" build-manifest layer digest (node B4).

Registered generically, the same pattern ``govbridge.core.freshness``'s own docstring documents for B2-B5: calling
``register_layer_builder``/``register_layer`` at import time of this package, never by editing
``govbridge/core/freshness.py`` or ``govbridge/core/manifest.py``. See ``govbridge/semantic/__init__.py`` for the
one place those calls happen, and ``open_issues`` in this run's typed report for the one gap this exposed: nothing
in ``govbridge.core`` imports sibling layer packages, so a bare ``python -m govbridge.core.freshness`` does not
know about the "semantic" layer until something imports ``govbridge.semantic`` first (worked around, in-scope,
below and in this node's checkpoint -- never by editing core).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

from govbridge import GOV_BRIDGE_DOMAIN
from govbridge.core import gitobj, manifest as manifestmod, store, telemetry
from govbridge.core.freshness import register_layer_builder
from govbridge.core.manifest import LayerDigest, register_layer
from govbridge.core.view import ResolvedView
from govbridge.core.yamlutil import canonical_json, sha256_text
from govbridge.semantic import modelpin, profile as profilemod, vectors

_ADAPTER_REL_PATH = "govbridge/semantic/adapters/onnx_embed.py"


def _adapter_blob(repo) -> Optional[str]:
    """The git blob id of the adapter FILE itself at HEAD (SEMANTIC_ROUTE.md section 4: ``plugin_blob: <git blob
    id at the build commit>``) -- not ``manifest.bridge_code_tree()``, which returns the TREE id of the whole
    ``govbridge/`` directory and is the wrong object kind for a single plugin file. None if the adapter is not
    yet committed at HEAD (uncommitted working-tree state); callers treat that as 'not yet resolvable', the same
    convention ``bridge_code_tree()`` documents for itself."""
    import os

    root = repo or gitobj.repo_root()
    rel = os.path.relpath(os.path.join(GOV_BRIDGE_DOMAIN, _ADAPTER_REL_PATH), root).replace(os.sep, "/")
    return gitobj.rev_parse(f"HEAD:{rel}", repo=root)

STATUS_BUILT = "BUILT"
STATUS_UNAVAILABLE = "UNAVAILABLE"

_META_STATUS = "semantic_status"
_META_PIN_ID = "semantic_pin_id"
_META_BLOCK = "semantic_manifest_block"
_META_ERROR = "semantic_last_error"


def _profile_path() -> str:
    return str(Path(GOV_BRIDGE_DOMAIN) / "config" / "embed-profile.yaml")


def _set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute("INSERT OR REPLACE INTO store_meta(key, value) VALUES (?, ?)", (key, value))
    conn.commit()


def _get_meta(conn: sqlite3.Connection, key: str) -> Optional[str]:
    row = conn.execute("SELECT value FROM store_meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def _eligible_chunk_rows(conn: sqlite3.Connection, resolved: ResolvedView, prof: "profilemod.EmbedProfile"):
    """(chunk_id, text_sha256, text) for every chunk of every blob admitted by BOTH gates of
    govbridge.semantic.profile: kind admission and ref-layer eligibility (profile.py's module docstring)."""
    ref_names = profilemod.eligible_ref_names(resolved, prof)
    if not ref_names:
        return []
    conn.execute("CREATE TEMP TABLE IF NOT EXISTS semantic_eligible_ref(ref_name TEXT PRIMARY KEY)")
    conn.execute("DELETE FROM semantic_eligible_ref")
    conn.executemany("INSERT INTO semantic_eligible_ref(ref_name) VALUES (?)", [(r,) for r in ref_names])

    rep_paths = conn.execute(
        """
        SELECT o.blob_id, MIN(o.path)
        FROM occurrence o
        JOIN semantic_eligible_ref e ON e.ref_name = o.ref_name
        GROUP BY o.blob_id
        """
    ).fetchall()

    conn.execute("CREATE TEMP TABLE IF NOT EXISTS semantic_eligible_blob(blob_id TEXT PRIMARY KEY)")
    conn.execute("DELETE FROM semantic_eligible_blob")
    eligible = []
    for blob_id, rep_path in rep_paths:
        brow = conn.execute("SELECT size, corpus_effect FROM blob WHERE blob_id=?", (blob_id,)).fetchone()
        if brow is None:
            continue
        size, corpus_effect = brow
        if corpus_effect in ("EXCLUDE", "LEXICAL_ONLY"):
            continue
        if not profilemod.kind_admitted(prof, rep_path, size):
            continue
        eligible.append((blob_id,))
    if not eligible:
        return []
    conn.executemany("INSERT INTO semantic_eligible_blob(blob_id) VALUES (?)", eligible)

    return list(conn.execute(
        """
        SELECT c.chunk_id, c.text_sha256, c.text
        FROM chunk c
        JOIN semantic_eligible_blob b ON b.blob_id = c.blob_id
        ORDER BY c.chunk_id
        """
    ).fetchall())


def semantic_layer_builder(conn: sqlite3.Connection, resolved: ResolvedView, rules, repo,
                            from_clean: bool, changed_refs=None) -> dict:
    vectors.create_table(conn)
    prof = profilemod.load_profile(_profile_path())

    try:
        pin = modelpin.load_model_pin(modelpin.default_pin_path())
        pin_id = modelpin.compute_pin_id(pin)
        modelpin.resolve_and_verify(pin, modelpin.default_models_root())
    except (modelpin.ModelUnavailable, modelpin.PinMismatch, OSError, KeyError) as exc:
        _set_meta(conn, _META_STATUS, STATUS_UNAVAILABLE)
        _set_meta(conn, _META_ERROR, f"{type(exc).__name__}: {exc}")
        return {"blobs": 0, "occurrences": 0, "chunks": 0, "status": STATUS_UNAVAILABLE, "error": str(exc)}

    rows = _eligible_chunk_rows(conn, resolved, prof)
    try:
        stats = vectors.embed_and_store(conn, rows, pin, pin_id, threads=4, batch_size=1)
    except Exception as exc:  # noqa: BLE001 -- a layer builder must never crash the whole freshness run
        _set_meta(conn, _META_STATUS, STATUS_UNAVAILABLE)
        _set_meta(conn, _META_ERROR, f"{type(exc).__name__}: {exc}")
        return {"blobs": 0, "occurrences": 0, "chunks": 0, "status": STATUS_UNAVAILABLE, "error": str(exc)}

    block = {
        "adapter": {"protocol": "gov-capability/1", "capability": "embed",
                    "plugin_path": _ADAPTER_REL_PATH,
                    "plugin_blob": _adapter_blob(repo)},
        "model": {"id": pin.model_id, "revision": pin.revision,
                  "artefacts": {a.local_name: a.sha256 for a in pin.artefacts}},
        "runtime": pin.runtime,
        "encoding": {"pooling": pin.pooling, "normalize": pin.normalize, "max_tokens": pin.max_tokens,
                     "query_prefix": pin.query_prefix},
        "embed_profile_sha256": sha256_text(canonical_json(prof.raw)),
        "pin_id": pin_id,
    }
    _set_meta(conn, _META_STATUS, STATUS_BUILT)
    _set_meta(conn, _META_PIN_ID, pin_id)
    _set_meta(conn, _META_BLOCK, manifestmod.canonical_json(block))
    _set_meta(conn, _META_ERROR, "")

    telemetry.write_row("builds", {
        "build_id": telemetry.build_id(pin_id, "semantic"),
        "layer": "semantic",
        "trigger": "full" if from_clean else "incremental",
        "pin_id": pin_id,
        "chunks_seen": stats["chunks_seen"],
        "chunks_embedded": stats["chunks_embedded"],
        "chunks_reused": stats["chunks_reused"],
        "wall_seconds": stats["wall_seconds"],
        "throughput_chunks_per_s": stats["throughput_chunks_per_s"],
        "llm_invocations": 0,
    })

    return {"blobs": 0, "occurrences": 0, "chunks": stats["chunks_embedded"], "status": STATUS_BUILT,
            "eligible_chunks": len(rows), **stats}


def vector_layer_digest(conn: sqlite3.Connection) -> LayerDigest:
    """``layers.vector`` in the build manifest (schemas/build-manifest.yaml): rows/digest over the CURRENT pin's
    vectors, plus the semantic manifest block (SEMANTIC_ROUTE.md section 4) and status, both read back from
    ``store_meta`` where the layer builder above left them (a generic key-value table ``govbridge.core.store``
    already defines for exactly this purpose -- see this run's open_issues for why the block lands under
    ``layers.vector.extra`` rather than a top-level ``pins.semantic``, which ``govbridge.core.freshness`` has no
    hook for without editing it).

    Ensures its own schema first (``vectors.create_table``, idempotent): ``build_manifest()`` calls every
    registered layer digest unconditionally, including a caller that opened a bare connection and never ran this
    node's layer builder at all (for example another node's own manifest-assembly test) -- this must not raise
    just because the ``vector`` table happens not to exist yet on that connection (orchestrator advisory,
    BR-AR-0004/B2 precedent: ``lexical_layer_digest()`` calls ``ensure_schema()`` first the same way)."""
    vectors.create_table(conn)
    try:
        pin = modelpin.load_model_pin(modelpin.default_pin_path())
        pin_id = modelpin.compute_pin_id(pin)
    except Exception:  # noqa: BLE001 -- the manifest must still build if model-pin.yaml is unreadable
        return LayerDigest(rows=0, digest="", extra={"status": STATUS_UNAVAILABLE})

    rows = vectors.count_for_pin(conn, pin_id)
    digest = vectors.digest_for_pin(conn, pin_id)
    status = _get_meta(conn, _META_STATUS) or STATUS_UNAVAILABLE
    if rows == 0:
        status = STATUS_UNAVAILABLE
    extra = {"status": status, "pin_id": pin_id}
    block_json = _get_meta(conn, _META_BLOCK)
    if block_json:
        extra["semantic_block"] = json.loads(block_json)
    return LayerDigest(rows=rows, digest=digest, extra=extra)


register_layer_builder("semantic", semantic_layer_builder)
register_layer("vector", vector_layer_digest)
