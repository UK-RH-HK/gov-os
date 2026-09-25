"""govbridge.code -- the code/symbol/reference route (ARCHITECTURE.md section 4.6, DAG node B3): a tree-sitter Rust
adapter (BUILD) plus the existing Python AST plugin (REUSE, run from its blob, unmodified), symbol/call/literal
tables, labelled resolution and lazy per-commit symbol history.

Importing this package registers the code layer's digest with the shared build manifest (govbridge.core.manifest),
the same pattern govbridge.core itself uses for its own two layers -- see manifest.py's module docstring. The code
layer is *lazy*: unlike the occurrence/chunk layers, it does not walk every ref in the canonical view up front; it
parses and caches Rust blobs the first time a query needs them (ARCHITECTURE.md section 4.6, "Symbol history"). The
manifest digest therefore reports whatever has been indexed so far, not a claim of whole-view coverage -- callers
that need guaranteed coverage of one commit call ``govbridge.code.symbols.ensure_indexed`` first, exactly as the
CLI commands below do.
"""
from __future__ import annotations

import sqlite3

from govbridge.core.manifest import LayerDigest, register_layer


def _code_layer_digest(conn: sqlite3.Connection) -> LayerDigest:
    from govbridge.code import store as codestore

    codestore.ensure_schema(conn)
    rows = conn.execute(
        "SELECT symbol_id, blob_id, kind, name, qualified_name, module_path, start_line, end_line, is_test, "
        "derivation FROM code_symbol ORDER BY symbol_id"
    ).fetchall()
    import hashlib

    h = hashlib.sha256()
    for row in rows:
        h.update("\x1f".join("" if v is None else str(v) for v in row).encode("utf-8"))
        h.update(b"\x1e")
    blobs_parsed = conn.execute("SELECT COUNT(*) FROM code_blob").fetchone()[0]
    return LayerDigest(rows=len(rows), digest=h.hexdigest(), extra={"blobs_parsed": blobs_parsed})


register_layer("code", _code_layer_digest)
