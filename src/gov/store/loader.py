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
- Each entry of the register file that the path map of ``HEAD`` names under ``decision_register`` is a record of
  type ``decision`` (DEC-521, DEC-473, DEC-479): its id is the heading's, its status the word after
  ``**Status:**`` on its first line that is not blank, its path the register file. Its heading and title are kept
  in ``register_entries``. A named register that ``HEAD`` does not hold as a file of text refuses the load
  (DEC-579: one that is not in the commit too).
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
PATH_MAP_REL = "governance/project/path-map.yaml"
REGISTER_KEY = "decision_register"  # DEC-479
REGISTER_TABLE = "register_entries"

# DEC-473: a level-3 heading at the start of a line, the id, a space, a colon or a dash, and the title
_ENTRY = re.compile(r"### (DEC-[0-9]+)(?=[ :\-–—])[ \t:\-–—]*([^\s:\-–—].*)")
_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
_STATUS = re.compile(r"\s*(?:[-*+]\s+)?\*\*Status:\*\*\s*([A-Za-z][A-Za-z_-]*)")
_SUPERSEDES = re.compile(r"\*\*Supersedes:\*\*([^·]*)")
_IDS_ALONE = re.compile(r"DEC-[0-9]+(?:(?:\s*,\s*|\s+and\s+)DEC-[0-9]+)*")

_TRAILER = re.compile(r"^(Task|Implements):[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
_LOG_FORMAT = "--format=%x1e%H%x1f%cs%x1f%(trailers:key=Task,key=Implements,unfold)%x1f%B%x1f"
_TABLES = {
    "records": "path TEXT, id TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, PRIMARY KEY (path, id)",
    "edges": "type TEXT, source TEXT, target TEXT, PRIMARY KEY (type, source, target)",
    "commits": "id TEXT PRIMARY KEY",
    "trailers": "commit_id TEXT, key TEXT, value TEXT, PRIMARY KEY (commit_id, key, value)",
    "commit_paths": "commit_id TEXT, path TEXT, PRIMARY KEY (commit_id, path)",
    REGISTER_TABLE: "id TEXT PRIMARY KEY, heading TEXT NOT NULL, title TEXT NOT NULL",
}


def _git(root: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        return subprocess.run(["git", "-C", str(root), *args], input=stdin, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        reason = " ".join(getattr(exc, "stderr", b"").decode("utf-8", "replace").split()) or str(exc)
        raise GovError("STORE_GIT_FAILED", f"git {args[0]} failed in {root}: {reason}", {"root": str(root)}) from None


def _tree(root: Path) -> dict[str, tuple[str, str, str]]:
    """``path -> (mode, type, object id)`` of every entry of ``HEAD``."""
    entries = {}
    for entry in _git(root, "ls-tree", "-r", "-z", "HEAD").decode("utf-8", "replace").split("\0"):
        meta, _, path = entry.partition("\t")
        if path:
            entries[path] = tuple(meta.split())
    return entries


def _file(root: Path, tree: dict, path: str) -> str | None:
    """The text ``HEAD`` holds at ``path``; None where it holds no file of UTF-8 text there (a link is no file)."""
    mode, kind, sha = tree.get(path, ("", "", ""))
    if kind != "blob" or mode == "120000":
        return None
    try:
        text = _git(root, "cat-file", "blob", sha).decode("utf-8")
    except UnicodeDecodeError:
        return None
    return None if "\0" in text else text


def _register(root: Path, tree: dict) -> tuple[str, str] | None:
    """``(path, text)`` of the register file the path map of ``HEAD`` names; None where it names none."""
    import yaml

    def unreadable(named: str, why: str) -> GovError:
        return GovError("STORE_REGISTER_UNREADABLE", f"{named}: {why}; the decisions of the register are not loaded",
                        {"root": str(root), "named": named})

    if PATH_MAP_REL not in tree:
        return None
    try:
        path_map = yaml.safe_load(_file(root, tree, PATH_MAP_REL) or "")
    except yaml.YAMLError:
        path_map = None
    if not isinstance(path_map, dict):
        raise unreadable(REGISTER_KEY, f"{PATH_MAP_REL} cannot be read as a mapping, so whether it names a register "
                                       "is not known")
    if REGISTER_KEY not in path_map:
        return None
    path = path_map[REGISTER_KEY]
    if not isinstance(path, str) or not path.strip():
        raise unreadable(REGISTER_KEY, f"the key of {PATH_MAP_REL} is not a path")
    text = _file(root, tree, path)  # a named register that is not in the commit is refused, never no register (DEC-579)
    if text is None:
        raise unreadable(path, f"HEAD does not hold the register named under '{REGISTER_KEY}' as a file of text")
    return path, text


def _read_register(path: str, text: str, recorded: dict[str, str]):
    """The decision records, the SUPERSEDES edges, the headings and the entries that are no records of a register.

    ``recorded`` is ``id -> path`` of the records of the files: an id a file records is the file's, never two.
    """
    entries, fence, lines = {}, None, text.split("\n")
    for number, line in enumerate(lines):
        mark, entry = _FENCE.match(line), _ENTRY.match(line)
        if fence is None:
            if mark:
                fence = mark.group(1)
            elif entry:
                first = next((lines[at] for at in range(number + 1, len(lines)) if lines[at].strip()), "")
                entries.setdefault(entry.group(1), []).append((line.rstrip(), entry.group(2).strip(), first))
        elif mark and mark.group(1).startswith(fence) and not line[mark.end():].strip():
            fence = None  # closed by a fence of the same mark, at least as long, with nothing after it
    records, edges, headings, invalid = [], set(), [], []
    for record_id, found in entries.items():
        (heading, title, first), status = found[0], _STATUS.match(found[0][2])
        if len(found) > 1:
            reason = f"{record_id} stands under {len(found)} headings of the register: none of them is a record"
        elif record_id in recorded:
            reason = f"{record_id} is recorded by the decision file {recorded[record_id]}: the entry is no record"
        elif not status:
            reason = f"{record_id} has no status line (`**Status:**` and a word, first under its heading)"
        else:
            records.append((path, record_id, "decision", status.group(1)))
            headings.append((record_id, heading, title))
            superseded = _SUPERSEDES.search(first)
            if superseded and _IDS_ALONE.fullmatch(superseded.group(1).strip()):  # a part of a decision gives none
                edges.update(("SUPERSEDES", record_id, target)
                             for target in re.findall(r"DEC-[0-9]+", superseded.group(1)))
            continue
        invalid.append({"path": path, "reason": reason})
    return records, edges, headings, invalid


def _markdown(root: Path, tree: dict) -> list[tuple[str, str]]:
    """``(path, text)`` of every Markdown file of ``HEAD``."""
    blobs = [(path, sha) for path, (_, kind, sha) in tree.items() if path.endswith(".md") and kind == "blob"]
    out =_git(root, "cat-file", "--batch", stdin="".join(f"{sha}\n" for _, sha in blobs).encode())
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


def frontmatters(root: Path, but: frozenset[str] = frozenset()) -> list[tuple[str, object, str | None]]:
    """``(path, frontmatter, why it cannot be read)`` of every Markdown file of ``HEAD`` whose path is not in ``but``."""
    found = []
    for path, text in _markdown(root, {path: entry for path, entry in _tree(root).items() if path not in but}):
        try:
            found.append((path, _frontmatter(text), None))
        except ValueError as exc:
            found.append((path, None, str(exc)))
    return found


def _ids(value) -> list[str]:
    if value is None:
        return []
    return [str(item) for item in (value if isinstance(value, list) else [value])]


def _read_records(root: Path):
    records, edges, invalid = [], set(), []
    tree = _tree(root)
    register = _register(root, tree)
    for path, text in _markdown(root, tree):
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
    headings = []
    if register:
        of_files = {record_id: path for path, record_id, _, _ in reversed(records)}
        entries, supersedes, headings, no_records = _read_register(*register, of_files)
        records += entries
        edges |= supersedes
        invalid += no_records
    return records, edges, invalid, headings


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
    if not content[-1][1]:  # no register entry: the digest is the one of a store without that table
        del content[-1]
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
    records, edges, invalid, headings = _read_records(root)
    commits, trailers, paths = _read_commits(root)
    rows = dict(zip(_TABLES, (records, edges, commits, trailers, paths, headings)))
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
