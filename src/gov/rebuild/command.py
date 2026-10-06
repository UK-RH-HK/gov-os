"""``gov rebuild`` (W1-27): an act command that recreates every derived store under ``.gov-runtime/``.

Two rebuilds from the same commit give the same digest. Needs only git.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

ACT_PATHS = (".gov-runtime/**",)
CLASS = "act"
HELP = "rebuild derived state"
EXIT_CODES = {}

_LEXICAL_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS lexical_file "
    "(path TEXT PRIMARY KEY, blob TEXT NOT NULL, indexed INTEGER NOT NULL)",
    "CREATE TABLE IF NOT EXISTS lexical_parent "
    "(parent_id TEXT PRIMARY KEY, path TEXT NOT NULL, kind TEXT NOT NULL, "
    "start_line INTEGER NOT NULL, end_line INTEGER NOT NULL)",
    "CREATE TABLE IF NOT EXISTS lexical_chunk "
    "(id INTEGER PRIMARY KEY, chunk_id TEXT NOT NULL UNIQUE, path TEXT NOT NULL, "
    "start_line INTEGER NOT NULL, end_line INTEGER NOT NULL, parent_id TEXT NOT NULL)",
)


def run(root: Path, args, config: dict) -> dict:
    from gov.store import load as store_load

    store_result = store_load(root)

    store_path = root / ".gov-runtime" / "store.db"
    conn = sqlite3.connect(str(store_path))
    try:
        for ddl in _LEXICAL_SCHEMA:
            conn.execute(ddl)
        conn.commit()
    finally:
        conn.close()

    skipped = []
    skipped.append({"name": "semantic", "reason": "requires ollama and qwen3-embedding model"})
    skipped.append({"name": "codeintel", "reason": "requires code intelligence tool"})

    return {
        "digest": store_result["digest"],
        "store": store_result,
        "skipped": skipped,
    }
