"""The store files of a project, hashed (S5's "byte-identical before and after" the stage's proposal step).

What is compared, exactly: the sha256 of the bytes of ``.gov-runtime/store.db`` (the record graph, the lexical index and the
vectors: ``store.layout.STORES`` puts the three in that one file) and of every file under ``.gov-runtime/codeintel/`` (the
code graph), each under its path relative to the project. SQLite's side files (``-wal``, ``-shm``, ``-journal``) are not
compared: a reader may create and remove them without touching the store's bytes. Used by the child program
``a9_hash_stores.py`` (taken the moment ``gov.rebuild.command.run`` returns, the build being done) and by the case (taken
after the stage's process has ended).
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def store_files(root) -> list:
    base = Path(root) / ".gov-runtime"
    files = []
    database = base / "store.db"
    if database.is_file():
        files.append(database)
    codeintel = base / "codeintel"
    if codeintel.is_dir():
        files.extend(sorted(p for p in codeintel.rglob("*") if p.is_file()))
    return files


def digest(root) -> dict:
    """``{relative path: sha256 of the file's bytes}`` of every store file."""
    root = Path(root)
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in store_files(root)}
