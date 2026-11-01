"""``gov rebuild --seed`` (W2-122; DEC-1014 items 4 and 6): a tree's stores seeded from a warm base, so its rebuild
re-embeds only the files whose content differs from the base's.

- **The base** is the root of another tree that holds a ``.gov-runtime/store.db``: the folder given to ``--seed``, or,
  with none, the absolute path ``integration_store`` of the tree's ``governance/project/rebuild.yaml``. A link is
  followed once, and the resolved path is the one read. The base is only read, never written.
- **The base's record:** ``RECORD_REL``, which every full rebuild removes at its start and writes only after its
  stores are complete: the fingerprint of the code that built them, the embedder its semantic store records, and the
  stores' schema version. A base is used only where all three equal the tree's own build: the running code, the
  embedder the endpoint reports now (not asked under ``--no-embeddings``, whose seed keeps no vector) and the running
  code's schema. A base without a readable record, or one that differs, is refused, named, and nothing of it is
  copied: the rebuild runs cold (fail closed: never a store of two embedders).
- **The code fingerprint** is the program that turns files into store entries, never the repository's content: every
  file of the running ``gov`` package, the gitleaks the pre-index filter runs (which decides which files enter), and
  the versions of the interpreter and SQLite that read and store them.
- **The copy:** the record store (with the lexical and semantic stores in it) through SQLite's own backup, so a base
  in use is read as one consistent state; the code-graph tool's home file by file, its SQLite files the same way,
  into the tree's own home (re-homed, never shared). It is made beside the tree's stores first and kept only where
  the base's record is unchanged after it; any fault removes what was copied. The secrets record (W2-107) is one file
  of the machine, outside every tree: the base's verdicts are the tree's already, and nothing is copied for it.
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

RECORD_REL = ".gov-runtime/rebuild/stores.json"
KEY = "integration_store"
CONFIGURED = ""  # ``--seed`` given no folder: the configured base
SEEDED, REFUSED, NONE = "seeded", "refused", "none"
_STAGING_REL = ".gov-runtime/rebuild/seed.tmp"
_SIDECARS = ("-wal", "-shm", "-journal")


@functools.cache
def code_fingerprint() -> str:
    """``sha256:`` over every file of the running ``gov`` package, the gitleaks ``PATH`` finds, and the versions of
    Python and SQLite."""
    import gov

    digest = hashlib.sha256()
    package = Path(gov.__file__).resolve().parent
    for path in sorted(package.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            digest.update(path.relative_to(package).as_posix().encode() + b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    gitleaks = shutil.which("gitleaks")
    digest.update(hashlib.sha256(Path(gitleaks).read_bytes()).digest() if gitleaks else b"no gitleaks")
    digest.update(f"\0{sys.version}\0{sqlite3.sqlite_version}".encode())
    return "sha256:" + digest.hexdigest()


def schema_version() -> str:
    """``sha256:`` over the tables the record, lexical and semantic stores are made of."""
    from gov.retrieval import lexical, semantic
    from gov.store import loader

    text = json.dumps([loader._TABLES, loader._FINGERPRINTS, lexical.SCHEMA, semantic.SCHEMA])
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


def _read(path: Path) -> dict | None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return record if isinstance(record, dict) else None


def forget(root: Path) -> None:
    """The tree's record removed: its stores are no base until a full rebuild completes them again."""
    (Path(root) / RECORD_REL).unlink(missing_ok=True)


def remember(root: Path, embedder: dict) -> None:
    """The tree's record, written whole once its stores are complete."""
    path = Path(root) / RECORD_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps({"code": code_fingerprint(), "embedder": embedder, "schema": schema_version(),
                                     "written_at": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def _answer(status: str, base: Path | None, reason: str | None, **more) -> dict:
    return {"status": status, "base": None if base is None else str(base), "reason": reason, **more}


def _configured(root: Path) -> tuple[str | None, dict | None]:
    """The configured base's path, or the answer where there is none to read."""
    from gov.config.loader import read_yaml
    from gov.rebuild.watch import SETTINGS_REL

    path = Path(root) / SETTINGS_REL
    document = read_yaml(path, "REBUILD_FAILED", SETTINGS_REL) if path.is_file() else None
    if not isinstance(document, dict) or KEY not in document:
        return None, _answer(NONE, None, f"{SETTINGS_REL} names no {KEY}: no warm base is configured")
    value = document[KEY]
    if not isinstance(value, str) or not os.path.isabs(value):
        return None, _answer(REFUSED, None, f"{SETTINGS_REL}: {KEY} must be an absolute path, not {value!r}")
    return value, None


def _differences(record: dict, embeddings: bool) -> list[str]:
    """What of the base's record differs from the tree's own build, each named."""
    said = []
    if record.get("code") != code_fingerprint():
        said.append(f"the code fingerprint differs: base {record.get('code')!r}, this tree {code_fingerprint()!r}")
    if record.get("schema") != schema_version():
        said.append(f"the schema differs: base {record.get('schema')!r}, this tree {schema_version()!r}")
    if embeddings:
        from gov.retrieval import ollama, semantic

        ollama.ensure_available()
        ours = {"model": semantic.MODEL, "revision": semantic._revision()}
        theirs = record.get("embedder")
        if ours["revision"] is None:
            said.append(f"the embedder model's revision cannot be read from the endpoint (base {theirs!r})")
        elif not isinstance(theirs, dict) or {key: theirs.get(key) for key in ours} != ours:
            said.append(f"the embedder model differs: base {theirs!r}, the endpoint now {ours!r}")
    return said


def _backup(source: Path, target: Path) -> None:
    """The SQLite file ``source``, read as one consistent state, into ``target`` (replaced whole)."""
    reading = sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True, timeout=30.0)
    try:
        writing = sqlite3.connect(target, timeout=30.0)
        try:
            reading.backup(writing)
        finally:
            writing.close()
    finally:
        reading.close()


def _copy_home(source: Path, target: Path) -> None:
    """The code-graph tool's home, regular files only: SQLite files through their backup, the rest as bytes."""
    for path in sorted(source.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.name.endswith(_SIDECARS):
            continue
        copy = target / path.relative_to(source)
        copy.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "rb") as handle:
            sqlite = handle.read(16) == b"SQLite format 3\0"
        if sqlite:
            _backup(path, copy)
        else:
            shutil.copyfile(path, copy)


def _remove(store: Path, home: Path) -> None:
    for path in (store, *(store.with_name(store.name + suffix) for suffix in _SIDECARS)):
        path.unlink(missing_ok=True)
    shutil.rmtree(home, ignore_errors=True)


def seed(root: Path, given: str, embeddings: bool) -> dict:
    """The tree at ``root`` seeded from the base ``given`` (``CONFIGURED``: the configured one), under the tree's
    rebuild lock and before any stage; the answer the result carries as ``seed``."""
    from gov.codeintel import BASE_REL
    from gov.store import STORE_REL

    root = Path(root)
    if given == CONFIGURED:
        given, answer = _configured(root)
        if answer:
            return answer
    base = Path(given).resolve()  # the link followed once; only the resolved path is read from here on
    named = given if Path(given) == base else f"{given} (resolved to {base})"
    if base == root.resolve():
        return _answer(NONE, base, f"the base {named} is this tree itself")
    if not (base / STORE_REL).is_file():
        return _answer(NONE, base, f"no warm base at {named}: it holds no {STORE_REL}")
    record = _read(base / RECORD_REL)
    if record is None:
        return _answer(REFUSED, base, f"the base {named} has no readable record of its stores ({RECORD_REL})")
    said = _differences(record, embeddings)
    if said:
        return _answer(REFUSED, base, "; ".join(said))

    staging, home = root / _STAGING_REL, f"{BASE_REL}/home"
    store, tree_home = root / STORE_REL, root / home
    shutil.rmtree(staging, ignore_errors=True)
    installed = False
    try:
        staging.mkdir(parents=True)
        _backup(base / STORE_REL, staging / "store.db")
        if (base / home).is_dir():
            _copy_home(base / home, staging / "home")
        if _read(base / RECORD_REL) != record:
            return _answer(REFUSED, base, "the base was rebuilt while it was copied: its record changed")
        copied = sqlite3.connect(staging / "store.db", isolation_level=None)
        try:
            has_vectors = copied.execute("SELECT 1 FROM sqlite_master WHERE name = 'semantic_manifest'").fetchone()
            if embeddings and has_vectors:
                built_by = set(copied.execute("SELECT embedder_model, embedder_revision FROM semantic_manifest"))
                if built_by - {(record["embedder"]["model"], record["embedder"]["revision"])}:
                    return _answer(REFUSED, base, f"the base's store holds vectors of another embedder model than "
                                                  f"its record names: {sorted(built_by)!r}")
            elif not embeddings:  # no vector is asked for: none is kept, as a rebuild without embeddings has none
                copied.executescript("DROP TABLE IF EXISTS semantic_vector; DROP TABLE IF EXISTS semantic_manifest;")
        finally:
            copied.close()
        installed = True
        store.parent.mkdir(parents=True, exist_ok=True)
        _backup(staging / "store.db", store)
        shutil.rmtree(tree_home, ignore_errors=True)
        if (staging / "home").is_dir():
            tree_home.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging / "home", tree_home)
    except (OSError, sqlite3.Error) as exc:
        if installed:
            _remove(store, tree_home)
        return _answer(REFUSED, base, f"the base could not be copied: {exc}")
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return _answer(SEEDED, base, None, copied=[STORE_REL] + ([home] if tree_home.is_dir() else []))
