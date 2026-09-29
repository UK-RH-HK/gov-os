"""The build manifest (ARCHITECTURE.md section 8.1, schemas/build-manifest.yaml): the deterministic identity of one
index build. No timestamps live here (those go to telemetry); two from-clean builds at the same view must produce
the same ``manifest_sha256``.

Layer-registration API. B1 owns two layers directly (``occurrence``, ``chunk``) and registers their digest
functions below. Every later node (B2 lexical, B3 code, B4 semantic, B5 authority/graph) adds its OWN tables to the
same store and makes them visible to the manifest the same way, from its OWN package, without editing this file:

    from govbridge.core.manifest import register_layer, LayerDigest

    def my_layer_digest(conn) -> LayerDigest:
        rows = conn.execute("SELECT ... ORDER BY ...").fetchall()
        ...
        return LayerDigest(rows=len(rows), digest=the_sha256_hex)

    register_layer("my_layer_name", my_layer_digest)

Call this once, at import time of the layer's own package (its ``__init__.py``), the same pattern core uses for
its own two layers at the bottom of this file. ``build_manifest()`` then includes every registered layer without
knowing anything about it beyond its name and the ``LayerDigest`` it returns.
"""
from __future__ import annotations

import dataclasses
import hashlib
import os
import sqlite3
from typing import Callable, Optional

from govbridge import GOV_BRIDGE_DOMAIN
from govbridge.core import gitobj
from govbridge.core.chunking import CHUNKER_VERSION
from govbridge.core.yamlutil import canonical_json, sha256_text

FIELD_SEP = "\x1f"
ROW_SEP = "\x1e"


@dataclasses.dataclass(frozen=True)
class LayerDigest:
    rows: int
    digest: str
    extra: Optional[dict] = None

    def to_dict(self) -> dict:
        d = {"rows": self.rows, "digest": self.digest}
        if self.extra:
            d.update(self.extra)
        return d


LayerFn = Callable[[sqlite3.Connection], LayerDigest]
_LAYER_REGISTRY: dict[str, LayerFn] = {}


def register_layer(name: str, fn: LayerFn) -> None:
    """Register a digest function for build-manifest layer ``name``. Idempotent: re-registering the same name
    replaces the previous function (a module reload re-registers cleanly)."""
    _LAYER_REGISTRY[name] = fn


def get_registered_layers() -> dict[str, LayerFn]:
    return dict(_LAYER_REGISTRY)


# --- pins: the same extension-point pattern as `register_layer`, for schemas/build-manifest.yaml's `pins.<name>`
# block (routed issue B4/BR-AR-0006 OI-2: "the semantic pins sit at layers.vector.extra.semantic_block, not
# pins.semantic ... add a per-layer pins hook in core"). `run()`'s own `pins = {"chunker_version": ...}` dict is
# built inline with no extension point; a layer registers HERE instead, at import time of its own package, exactly
# like `register_layer` -- never by editing this dict-construction site in freshness.py. ------------------------

PinsFn = Callable[[sqlite3.Connection], dict]
_PINS_REGISTRY: dict[str, PinsFn] = {}


def register_pins(name: str, fn: PinsFn) -> None:
    """Register an extra ``pins.<name>`` block provider (schemas/build-manifest.yaml: ``pins: {chunker_version,
    fts_tokenizer, code_adapters, semantic}``). ``fn(conn)`` returns the block's dict; called once per
    ``build_manifest()`` call, alongside the fixed pins already passed in."""
    _PINS_REGISTRY[name] = fn


def get_registered_pins() -> dict[str, PinsFn]:
    return dict(_PINS_REGISTRY)


def _rows_digest(rows: list[tuple]) -> str:
    h = hashlib.sha256()
    for row in rows:
        h.update(FIELD_SEP.join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(ROW_SEP.encode())
    return h.hexdigest()


def occurrence_layer_digest(conn: sqlite3.Connection) -> LayerDigest:
    rows = conn.execute(
        "SELECT ref_name, commit_id, path, blob_id, mode FROM occurrence ORDER BY ref_name, commit_id, path"
    ).fetchall()
    return LayerDigest(rows=len(rows), digest=_rows_digest(rows))


def chunk_layer_digest(conn: sqlite3.Connection) -> LayerDigest:
    rows = conn.execute(
        "SELECT chunk_id, blob_id, chunker_version, start_line, end_line, text_sha256 "
        "FROM chunk ORDER BY chunk_id"
    ).fetchall()
    return LayerDigest(rows=len(rows), digest=_rows_digest(rows), extra={"chunker_version": CHUNKER_VERSION})


def blob_layer_digest(conn: sqlite3.Connection) -> LayerDigest:
    rows = conn.execute(
        "SELECT blob_id, sha256, size, is_text, corpus_rule, corpus_effect FROM blob ORDER BY blob_id"
    ).fetchall()
    return LayerDigest(rows=len(rows), digest=_rows_digest(rows))


register_layer("occurrence", occurrence_layer_digest)
register_layer("chunk", chunk_layer_digest)
register_layer("blob", blob_layer_digest)


def bridge_code_tree(repo: Optional[str] = None) -> Optional[str]:
    """The git tree id of govbridge/ at HEAD (ARCHITECTURE.md section 3). None if govbridge/ is not yet committed
    at HEAD (a fresh checkout mid-development); callers treat that as 'always rebuild'."""
    root = repo or gitobj.repo_root()
    rel = os.path.relpath(os.path.join(GOV_BRIDGE_DOMAIN, "govbridge"), root)
    rel = rel.replace(os.sep, "/")
    return gitobj.rev_parse(f"HEAD:{rel}", repo=root)


def build_manifest(conn: sqlite3.Connection, view: list[dict], config_sha256: dict, pins: dict,
                    coverage: dict, repo: Optional[str] = None) -> dict:
    # B2 OI-4 ("build_manifest calls every registered digest unconditionally"): every layer already self-defends
    # (ensure_schema()-first) against a connection it never touched, but this try/except is the CENTRAL backstop --
    # one layer's digest computation failing (a future layer that forgets to self-defend, or a genuine runtime
    # error) must never take the whole manifest build down. The manifest still records the failure, visibly,
    # rather than silently omitting the layer.
    layers: dict = {}
    for name, fn in get_registered_layers().items():
        try:
            layers[name] = fn(conn).to_dict()
        except Exception as exc:  # noqa: BLE001 -- see comment above
            layers[name] = {"rows": 0, "digest": None, "error": f"{type(exc).__name__}: {exc}"}

    merged_pins = dict(pins)
    for name, fn in get_registered_pins().items():
        try:
            merged_pins[name] = fn(conn)
        except Exception as exc:  # noqa: BLE001 -- same central backstop, for a pins provider
            merged_pins[name] = {"status": "UNAVAILABLE", "error": f"{type(exc).__name__}: {exc}"}

    manifest = {
        "view": view,
        "config_sha256": config_sha256,
        "bridge_code_tree": bridge_code_tree(repo=repo),
        "pins": merged_pins,
        "coverage": coverage,
        "layers": layers,
        "manifest_sha256": None,
    }
    manifest["manifest_sha256"] = manifest_sha256(manifest)
    return manifest


def manifest_sha256(manifest: dict) -> str:
    """sha256 of the manifest with manifest_sha256 (and packet_sha256, if present) set to null."""
    m = dict(manifest)
    m["manifest_sha256"] = None
    if "packet_sha256" in m:
        m["packet_sha256"] = None
    return sha256_text(canonical_json(m))
