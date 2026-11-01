"""The lexical index: an FTS5 table over line-aligned chunks, in the shared store (W1-17; DEC-340 to DEC-344).

Ported from ``cli/govbridge/lexical/fts.py`` (the FTS5 table, its tokenizer and the row digest) and
``cli/govbridge/core/chunking.py`` (see ``gov.retrieval.chunking``).

- The corpus is ``git ls-files`` passed through ``gov.secrets.indexable``; there is no include list. A file is
  read as it stands in the working tree (DEC-344), and only after the filter has let it through.
- The index is incremental by blob hash: ``lexical_file`` holds the blob of every tracked file that was judged,
  indexed or not, and a refresh judges and chunks only the paths whose blob differs. When the path map or the
  gitleaks rules change, every tracked file is judged again.
- ``search(..., refresh=False)``, ``freshness``, ``digest``, ``chunks`` and ``parent`` open the store read-only
  and never write (DEC-322). A missing, empty or stale index makes the facet unavailable (DEC-342).

``python3 -m gov.retrieval.lexical`` in a project root is the index-freshness check: exit 0 when the index is fresh.
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

from gov.cli.errors import GovError
from gov.config.loader import PROJECT_DIR
from gov.retrieval.chunking import chunk_file
from gov.secrets import CONFIG_REL, indexable
from gov.store import STORE_REL
from gov.util.gitenv import git_env

FACET = "lexical"
# Carried: porter unicode61, with '_' a token character so a snake_case identifier stays one token.
TOKENIZE = "porter unicode61 tokenchars '_'"
# What the filter's verdict on a file depends on besides the file: when one changes, every file is judged again.
JUDGES = (f"{PROJECT_DIR}/path-map.yaml", CONFIG_REL)
FIELD_SEP, ROW_SEP = "\x1f", "\x1e"

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS lexical_file (path TEXT PRIMARY KEY, blob TEXT NOT NULL, indexed INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS lexical_parent (parent_id TEXT PRIMARY KEY, path TEXT NOT NULL, kind TEXT NOT NULL,
    start_line INTEGER NOT NULL, end_line INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT NOT NULL UNIQUE, path TEXT NOT NULL,
    start_line INTEGER NOT NULL, end_line INTEGER NOT NULL, parent_id TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS lexical_chunk_by_path ON lexical_chunk (path);
CREATE INDEX IF NOT EXISTS lexical_parent_by_path ON lexical_parent (path);
CREATE VIRTUAL TABLE IF NOT EXISTS lexical_fts USING fts5(text, tokenize = "{TOKENIZE}");
"""
_CHUNKS = "SELECT chunk_id, path, start_line, end_line, parent_id FROM lexical_chunk"
_DIGESTED = (
    "SELECT path, blob, indexed FROM lexical_file ORDER BY path",
    "SELECT parent_id, path, kind, start_line, end_line FROM lexical_parent ORDER BY parent_id",
    "SELECT c.chunk_id, c.path, c.start_line, c.end_line, c.parent_id, f.text FROM lexical_chunk c "
    "JOIN lexical_fts f ON f.rowid = c.id ORDER BY c.chunk_id",
)
RACY_NS = 10_000_000  # a file changed this recently (a coarse clock's tick) may not yet tell a later write apart
_FRESHNESS: dict = {}  # resolved root -> (key, answer): the freshness worked out last in this process (W2-108)
_LISTED: dict = {}  # resolved root -> ((head, index stamp), ``ls-files -z``): the tracked paths listed last (W2-108)


def _git(root: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        return subprocess.run(["git", "-C", str(root), *args], input=stdin, capture_output=True, check=True,
                              env=git_env(root)).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        reason = " ".join(getattr(exc, "stderr", b"").decode("utf-8", "replace").split()) or str(exc)
        raise GovError("INDEX_GIT_FAILED", f"git {args[0]} failed in {root}: {reason}", {"root": str(root)}) from None


def _tracked(root: Path) -> dict[str, str]:
    """``path -> blob hash`` of every tracked file, as it stands in the working tree (DEC-344)."""
    names = dict.fromkeys(os.fsdecode(name) for name in _git(root, "ls-files", "-z").split(b"\0") if name)
    files = [rel for rel in names if "\n" not in rel and (root / rel).is_file()]
    if not files:
        return {}
    hashes = _git(root, "hash-object", "--stdin-paths", stdin=os.fsencode("\n".join(files) + "\n")).decode().split()
    return dict(zip(files, hashes, strict=True))


def _open(root: Path) -> sqlite3.Connection | None:
    """The store at ``root``, read-only; None when there is no store or it holds no index."""
    path = Path(root) / STORE_REL
    if not path.is_file():
        return None
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    if connection.execute("SELECT 1 FROM sqlite_master WHERE name = 'lexical_file'").fetchone() is None:
        connection.close()
        return None
    return connection


def _digest(connection: sqlite3.Connection) -> str:
    """sha256 of the index's logical content: its files, parents and chunks with their text, in sorted order."""
    digest = hashlib.sha256()
    for query in _DIGESTED:
        for row in connection.execute(query):
            digest.update(FIELD_SEP.join(str(value) for value in row).encode("utf-8", "replace"))
            digest.update(ROW_SEP.encode())
        digest.update(ROW_SEP.encode())
    return digest.hexdigest()


def _drop(connection: sqlite3.Connection, rel: str) -> None:
    connection.execute("DELETE FROM lexical_fts WHERE rowid IN (SELECT id FROM lexical_chunk WHERE path = ?)", (rel,))
    for table in ("lexical_chunk", "lexical_parent", "lexical_file"):
        connection.execute(f"DELETE FROM {table} WHERE path = ?", (rel,))


def _update(root: Path) -> tuple[sqlite3.Connection, list[str]]:
    """Bring the index up to date; the open store and the paths chunked in this call."""
    current = _tracked(root)
    (root / STORE_REL).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(root / STORE_REL)
    try:
        connection.executescript(SCHEMA)
        stored = {rel: (blob, indexed) for rel, blob, indexed in connection.execute("SELECT * FROM lexical_file")}
        judge_all = any(stored.get(rel, (None,))[0] != current.get(rel) for rel in JUDGES)
        asked = [rel for rel in current if judge_all or stored.get(rel, (None,))[0] != current[rel]]
        allowed = set(indexable(root, asked)) if asked else set()
        indexed = []
        with connection:
            for rel in stored.keys() - current.keys():
                _drop(connection, rel)
            for rel in asked:
                state = (current[rel], int(rel in allowed))
                if stored.get(rel) == state:
                    continue  # judged again and nothing changed: the chunks stand
                _drop(connection, rel)
                connection.execute("INSERT INTO lexical_file VALUES (?, ?, ?)", (rel, *state))
                if rel not in allowed:
                    continue
                text = (root / rel).read_bytes().decode("utf-8", "replace")  # only after the filter let it through
                parent_rows, chunk_rows = chunk_file(rel, current[rel], text)
                connection.executemany("INSERT INTO lexical_parent VALUES (?, ?, ?, ?, ?)", parent_rows)
                for *record, chunk in chunk_rows:
                    rowid = connection.execute("INSERT INTO lexical_chunk (chunk_id, path, start_line, end_line, "
                                               "parent_id) VALUES (?, ?, ?, ?, ?)", record).lastrowid
                    connection.execute("INSERT INTO lexical_fts (rowid, text) VALUES (?, ?)", (rowid, chunk))
                indexed.append(rel)
        return connection, indexed
    except BaseException:
        connection.close()
        raise


def _empty(connection: sqlite3.Connection) -> bool:
    return connection.execute("SELECT 1 FROM lexical_chunk LIMIT 1").fetchone() is None


def refresh(root: Path) -> dict:
    """Bring the index up to date with the tracked files; its digest and the paths chunked in this call."""
    connection, indexed = _update(Path(root))
    try:
        return {"digest": _digest(connection), "indexed": indexed}
    finally:
        connection.close()


def _stamps(paths) -> tuple | None:
    """Each path's device, inode, size and change times, which any write or replacement changes (None for one that is
    absent); None for all when one cannot be read, or changed less than ``RACY_NS`` ago or later than now."""
    now, stamps = time.time_ns(), []
    for path in paths:
        try:
            st = os.stat(path)
        except FileNotFoundError:
            stamps.append(None)
            continue
        except OSError:
            return None
        if now - max(st.st_mtime_ns, st.st_ctime_ns) < RACY_NS:
            return None
        stamps.append((st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns))
    return tuple(stamps)


def _store_stamp(root: Path) -> tuple | None:
    """The store's fingerprint: the stamps of its file, its write-ahead log and its journal."""
    path = Path(root) / STORE_REL
    return _stamps(path.with_name(path.name + suffix) for suffix in ("", "-wal", "-journal"))


def _tree(root: Path, place: Path) -> tuple | None:
    """What ``_tracked`` depends on: ``HEAD``, the git index's stamp, the tracked paths and each one's stamps; None when
    one cannot be read. The paths are listed again only when the head or the index changed."""
    try:
        head, index = _git(root, "rev-parse", "HEAD", "--git-path", "index").splitlines()
    except (GovError, ValueError):
        return None
    index_stamp = _stamps([os.path.join(os.fsencode(root), index)])
    if index_stamp is None:
        return None
    listed = (head, index_stamp)
    if _LISTED.get(place, (None,))[0] != listed:
        try:
            _LISTED[place] = (listed, _git(root, "ls-files", "-z"))
        except GovError:
            return None
    names = _LISTED[place][1]
    top = os.fsencode(root)  # joined as bytes: a Path for each of thousands of files costs more than its stat
    stamps = _stamps(os.path.join(top, name) for name in names.split(b"\0") if name)
    return None if stamps is None else (listed, names, stamps)


def _checked(root: Path) -> tuple[tuple | None, str, list[str]]:
    """The key of the store and the tree as they stand (None when one cannot be read), the status and the stale paths:
    worked out once per key in a process, and on every call when there is no key (W2-108)."""
    root = Path(root)
    place = root.resolve()
    store, tree = _store_stamp(root), _tree(root, place)
    key = None if store is None or tree is None else (store, tree)
    if key is None or _FRESHNESS.get(place, (None,))[0] != key:
        _FRESHNESS[place] = (key, _freshness(root))
    status, stale = _FRESHNESS[place][1]
    return key, status, list(stale)


def freshness(root: Path) -> dict:
    """``status`` (fresh, stale, empty or missing) and the ``stale`` paths. Writes nothing. Worked out once per store
    and tree in a process, keyed by their fingerprints, and again whenever a fingerprint changes or cannot be read
    (W2-108)."""
    _, status, stale = _checked(root)
    return {"status": status, "stale": stale}


def _freshness(root: Path) -> tuple[str, list[str]]:
    """The status and the stale paths, worked out from the store and the tracked files as they stand."""
    connection = _open(root)
    if connection is None:
        return "missing", []
    try:
        stored = dict(connection.execute("SELECT path, blob FROM lexical_file"))
        current = _tracked(Path(root))
        stale = sorted(rel for rel in stored.keys() | current.keys() if stored.get(rel) != current.get(rel))
        return "stale" if stale else "empty" if _empty(connection) else "fresh", stale
    finally:
        connection.close()


def digest(root: Path) -> str:
    """The digest of the index as it stands. Writes nothing; ``INDEX_MISSING`` when there is no index."""
    connection = _open(root)
    if connection is None:
        raise GovError("INDEX_MISSING", f"{STORE_REL}: no lexical index at {root}", {"root": str(root)})
    try:
        return _digest(connection)
    finally:
        connection.close()


def search(root: Path, query: str, refresh: bool = True) -> dict:
    """Every line of the corpus that holds the exact string ``query``, with its path, line, chunk and parent.

    With ``refresh`` the index is brought up to date first. Without, nothing is written, and a missing, empty or
    stale index is reported as ``FACET_UNAVAILABLE`` with its reason and no hit (DEC-342).
    """
    if refresh:
        connection, status = _update(Path(root))[0], "fresh"
    else:
        connection, status = _open(root), freshness(root)["status"]
    try:
        if status == "fresh" and _empty(connection):
            status = "empty"
        if status != "fresh":
            return {"available": False, "facet": FACET, "state": "FACET_UNAVAILABLE", "reason": status, "hits": []}
        # FTS5 finds the chunks that hold the query's tokens as a phrase; the lines are then matched exactly.
        sql = f"SELECT c.chunk_id, c.path, c.start_line, c.parent_id, f.text FROM lexical_chunk c " \
              f"JOIN lexical_fts f ON f.rowid = c.id {{}} ORDER BY c.path, c.start_line"
        if any(char.isalnum() or char == "_" for char in query):
            rows = connection.execute(sql.format("WHERE lexical_fts MATCH ?"), ('"' + query.replace('"', '""') + '"',))
        else:  # no token to match by: every chunk is read
            rows = connection.execute(sql.format(""))
        hits, seen = [], set()
        for chunk_id, path, start_line, parent_id, text in rows:
            for line, content in enumerate(text.splitlines(), start_line):
                if query in content and (path, line) not in seen:
                    seen.add((path, line))
                    hits.append({"path": path, "line": line, "text": content, "chunk_id": chunk_id,
                                 "parent_id": parent_id})
        return {"available": True, "facet": FACET, "state": "AVAILABLE", "reason": None, "hits": hits}
    finally:
        if connection is not None:
            connection.close()


def chunks(root: Path, path: str | None = None) -> list[dict]:
    """The chunk records, all or one file's, by path and line. Writes nothing."""
    connection = _open(root)
    if connection is None:
        return []
    try:
        where, values = (" WHERE path = ?", (path,)) if path is not None else ("", ())
        rows = connection.execute(f"{_CHUNKS}{where} ORDER BY path, start_line, end_line", values)
        return [dict(zip(("chunk_id", "path", "start_line", "end_line", "parent_id"), row)) for row in rows]
    finally:
        connection.close()


def parent(root: Path, parent_id: str) -> dict | None:
    """The parent ``parent_id``: its file, kind and span of lines; None when the index holds no such parent."""
    connection = _open(root)
    if connection is None:
        return None
    try:
        row = connection.execute("SELECT * FROM lexical_parent WHERE parent_id = ?", (parent_id,)).fetchone()
        return row and dict(zip(("parent_id", "path", "kind", "start_line", "end_line"), row))
    finally:
        connection.close()


def main() -> int:
    """The index-freshness check. Green only on a fresh index; prints each stale path; never writes."""
    try:
        state = freshness(Path.cwd())
    except GovError as error:
        print(f"index freshness cannot be decided: {error.message}")
        return 1
    for rel in state["stale"]:
        print(f"stale in the lexical index: {rel}")
    if state["status"] != "fresh":
        print(f"the lexical index is {state['status']}")
    return 0 if state["status"] == "fresh" else 1


if __name__ == "__main__":
    sys.exit(main())
