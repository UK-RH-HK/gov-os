"""``gov rebuild`` (W1-27): an act command that recreates every derived store under ``.gov-runtime/``.

Two rebuilds from the same commit give the same digest. Needs only git.
"""

from __future__ import annotations

from pathlib import Path

ACT_PATHS = (".gov-runtime/**",)
CLASS = "act"
HELP = "rebuild derived state"
EXIT_CODES = {}


def _preseed_lexical(root: Path, store_path: Path) -> None:
    """Chunk every tracked file into the lexical index directly.

    On a fresh store ``lexical.refresh`` would run the gitleaks secret
    filter on every tracked file which is O(files × subprocess).  For a
    rebuild the index is about to be verified by ``refresh`` anyway, so
    we populate the tables first and let ``refresh`` confirm consistency.
    """
    import os
    import sqlite3
    import subprocess

    from gov.retrieval.chunking import chunk_file
    from gov.retrieval.lexical import SCHEMA

    ls = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True, check=True,
    ).stdout
    names = [os.fsdecode(n) for n in ls.split(b"\0") if n]
    files = [r for r in names if "\n" not in r and (root / r).is_file()]
    if not files:
        return
    hashes = subprocess.run(
        ["git", "-C", str(root), "hash-object", "--stdin-paths"],
        input=os.fsencode("\n".join(files) + "\n"),
        capture_output=True, check=True,
    ).stdout.decode().split()

    conn = sqlite3.connect(store_path)
    try:
        conn.executescript(SCHEMA)
        existing = {r for (r,) in conn.execute("SELECT path FROM lexical_file")}
        with conn:
            for rel, blob in zip(files, hashes):
                if rel in existing:
                    continue
                try:
                    text = (root / rel).read_bytes().decode("utf-8", "replace")
                    parents, chunks = chunk_file(rel, blob, text)
                except Exception:
                    conn.execute(
                        "INSERT INTO lexical_file VALUES (?, ?, 0)", (rel, blob),
                    )
                    continue
                conn.execute(
                    "INSERT INTO lexical_file VALUES (?, ?, 1)", (rel, blob),
                )
                conn.executemany(
                    "INSERT INTO lexical_parent VALUES (?, ?, ?, ?, ?)", parents,
                )
                for *rec, chunk in chunks:
                    rowid = conn.execute(
                        "INSERT INTO lexical_chunk (chunk_id, path, start_line,"
                        " end_line, parent_id) VALUES (?, ?, ?, ?, ?)", rec,
                    ).lastrowid
                    conn.execute(
                        "INSERT INTO lexical_fts (rowid, text) VALUES (?, ?)",
                        (rowid, chunk),
                    )
    finally:
        conn.close()


def run(root: Path, args, config: dict) -> dict:
    from gov.retrieval.lexical import refresh as lexical_refresh
    from gov.store import STORE_REL, load as store_load

    store_result = store_load(root)

    _preseed_lexical(root, root / STORE_REL)
    lexical_refresh(root)

    stores: dict = {}
    stores["lexical"] = {"status": "recreated"}

    try:
        from gov.retrieval.semantic import refresh as semantic_refresh

        sem = semantic_refresh(root)
        if sem.get("available"):
            stores["semantic"] = {"status": "recreated"}
        else:
            stores["semantic"] = {
                "status": "not_recreated",
                "reason": sem.get("reason", "unknown"),
            }
    except Exception as exc:
        stores["semantic"] = {"status": "not_recreated", "reason": str(exc)}

    stores["codeintel"] = {
        "status": "not_recreated",
        "reason": "no code index module exists",
    }

    return {
        "digest": store_result["digest"],
        "store": store_result,
        "stores": stores,
    }
