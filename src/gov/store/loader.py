"""Build ``.gov-runtime/store.db``: the record graph, derived from git alone (DEC-012).

Everything is read from ``HEAD``, never from the working tree, so the same
commit gives the same store wherever and whenever it is loaded.

- A record is a Markdown file whose YAML frontmatter carries an ``id``. ``id``,
  ``type`` and ``status`` are required (DEC-239); the path is derived, not
  stored. A record that cannot be loaded is returned in ``invalid`` by its path
  and stops no other record.
- An edge's frontmatter key is its type in lower case, from the record that
  carries the key to each id listed. ``superseded_by`` gives the SUPERSEDES edge
  from the successor. A dangling edge is stored like any other.
- ``Task:`` and ``Implements:`` trailers are read from the final trailer block;
  a commit made before 2026-10-03 is read from the whole message (DEC-182).
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
from pathlib import Path

from gov.cli.errors import GovError

STORE_REL = ".gov-runtime/store.db"
EDGE_TYPES = ("EVIDENCE_FOR", "CONSTRAINS", "IMPLEMENTS", "TESTS", "GENERATES", "VALIDATES", "SUPERSEDES",
              "DEPENDS_ON")
REQUIRED = ("id", "type", "status")
TRAILER_RULE_DATE = "2026-10-03"  # DEC-182; compared with the committer date, in the commit's own time zone

_TRAILER = re.compile(r"^(Task|Implements):[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
_LOG_FORMAT = "--format=%x1e%H%x1f%cs%x1f%(trailers:key=Task,key=Implements,unfold)%x1f%B%x1f"
_TABLES = {
    "records": "path TEXT PRIMARY KEY, id TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL",
    "edges": "type TEXT, source TEXT, target TEXT, PRIMARY KEY (type, source, target)",
    "commits": "id TEXT PRIMARY KEY",
    "trailers": "commit_id TEXT, key TEXT, value TEXT, PRIMARY KEY (commit_id, key, value)",
    "commit_paths": "commit_id TEXT, path TEXT, PRIMARY KEY (commit_id, path)",
}


def _git(root: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        return subprocess.run(["git", "-C", str(root), *args], input=stdin, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        reason = " ".join(getattr(exc, "stderr", b"").decode("utf-8", "replace").split()) or str(exc)
        raise GovError("STORE_GIT_FAILED", f"git {args[0]} failed in {root}: {reason}", {"root": str(root)}) from None


def _markdown(root: Path) -> list[tuple[str, str]]:
    """``(path, text)`` of every Markdown file of ``HEAD``."""
    blobs = []
    for entry in _git(root, "ls-tree", "-r", "-z", "HEAD").decode("utf-8", "replace").split("\0"):
        meta, _, path = entry.partition("\t")
        if path.endswith(".md") and meta.split()[1] == "blob":
            blobs.append((path, meta.split()[2]))
    out = _git(root, "cat-file", "--batch", stdin="".join(f"{sha}\n" for _, sha in blobs).encode())
    files, position = [], 0
    for path, _ in blobs:
        header_end = out.index(b"\n", position)
        size = int(out[position:header_end].split()[2])
        files.append((path, out[header_end + 1:header_end + 1 + size].decode("utf-8", "replace")))
        position = header_end + size + 2
    return files


def _frontmatter(text: str):
    """The frontmatter document of ``text``, None when it has none; ValueError when it cannot be read."""
    import yaml

    lines = [line.rstrip() for line in text.split("\n")]
    if lines[0] != "---":
        return None
    if "---" not in lines[1:]:
        raise ValueError("the frontmatter is not closed")
    try:
        return yaml.safe_load("\n".join(lines[1:lines.index("---", 1)]))
    except (yaml.YAMLError, ValueError) as exc:
        raise ValueError("the frontmatter is not valid YAML: " + " ".join(str(exc).split())) from None


def _ids(value) -> list[str]:
    if value is None:
        return []
    return [str(item) for item in (value if isinstance(value, list) else [value])]


def _read_records(root: Path):
    records, edges, invalid = [], set(), []
    for path, text in _markdown(root):
        try:
            front = _frontmatter(text)
        except ValueError as exc:
            invalid.append({"path": path, "reason": str(exc)})
            continue
        if not isinstance(front, dict) or "id" not in front:
            continue
        missing = [key for key in REQUIRED if not isinstance(front.get(key), str) or not front[key]]
        if missing:
            invalid.append({"path": path, "reason": f"required key missing or not a string: {', '.join(missing)}"})
            continue
        records.append((path, front["id"], front["type"], front["status"]))
        for edge_type in EDGE_TYPES:
            edges.update((edge_type, front["id"], target) for target in _ids(front.get(edge_type.lower())))
        edges.update(("SUPERSEDES", successor, front["id"]) for successor in _ids(front.get("superseded_by")))
    return records, edges, invalid


def _read_commits(root: Path):
    commits, trailers, paths = [], set(), set()
    log = _git(root, "-c", "core.quotePath=false", "log", "--name-only", _LOG_FORMAT, "HEAD")
    for entry in log.decode("utf-8", "replace").split("\x1e")[1:]:
        commit, date, final_block, message, names = entry.split("\x1f")
        commits.append((commit,))
        paths.update((commit, name) for name in names.split("\n") if name)
        for key, value in _TRAILER.findall(message if date < TRAILER_RULE_DATE else final_block):
            trailers.update((commit, key.capitalize(), item) for item in re.split(r"[,\s]+", value) if item)
    return commits, trailers, paths


def _digest(connection: sqlite3.Connection) -> str:
    """sha256 of the store's logical content: every row of every table of the graph, in sorted order."""
    content = [[table, sorted(connection.execute(f"SELECT * FROM {table}").fetchall())] for table in _TABLES]
    return hashlib.sha256(json.dumps(content).encode("utf-8")).hexdigest()


def connect(root: Path) -> sqlite3.Connection:
    """The store at ``root``, read-only. ``STORE_MISSING`` when no load has built it."""
    path = Path(root) / STORE_REL
    if not path.is_file():
        raise GovError("STORE_MISSING", f"{STORE_REL}: no store at {root}; load it first", {"root": str(root)})
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)


def load(root: Path) -> dict:
    """Build the store at ``root`` from its git repository, replacing what an earlier load left."""
    root = Path(root)
    records, edges, invalid = _read_records(root)
    commits, trailers, paths = _read_commits(root)
    rows = dict(zip(_TABLES, (records, edges, commits, trailers, paths)))
    (root / STORE_REL).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(root / STORE_REL, isolation_level=None)
    try:
        connection.execute("BEGIN")
        for table, columns in _TABLES.items():
            connection.execute(f"DROP TABLE IF EXISTS {table}")
            connection.execute(f"CREATE TABLE {table} ({columns})")
            for row in sorted(rows[table]):
                connection.execute(f"INSERT INTO {table} VALUES ({', '.join('?' * len(row))})", row)
        connection.execute("COMMIT")
        return {"digest": _digest(connection), "invalid": sorted(invalid, key=lambda entry: entry["path"])}
    finally:
        connection.close()


def digest(root: Path) -> str:
    """The digest of the store at ``root``."""
    connection = connect(root)
    try:
        return _digest(connection)
    finally:
        connection.close()
