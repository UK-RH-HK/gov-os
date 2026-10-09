"""Exact queries over the store that ``gov.store.load`` wrote (CAP-08.a, CAP-09, CAP-13.a).

Every answer is plain JSON data, in sorted order. A filter left as None is not applied.
"""

from __future__ import annotations

from pathlib import Path

from gov.store import connect

_IS_RECORD = "IN (SELECT id FROM records)"


def _rows(root: Path, sql: str, **filters) -> list[tuple]:
    """The rows of ``sql``, sorted, narrowed to the filters given (column name -> value)."""
    given = {column: value for column, value in filters.items() if value is not None}
    if given:
        sql += (" AND " if " WHERE " in sql else " WHERE ") + " AND ".join(f"{column} = ?" for column in given)
    connection = connect(root)
    try:
        return sorted(connection.execute(sql, tuple(given.values())).fetchall())
    finally:
        connection.close()


def _edges(rows) -> list[dict]:
    return [{"type": edge_type, "source": source, "target": target} for edge_type, source, target in rows]


def records(root: Path, type: str | None = None, status: str | None = None) -> list[dict]:
    """The records whose frontmatter matches every filter given; a register entry with its heading and title."""
    rows = _rows(root, "SELECT records.id, type, status, path, heading, title FROM records"
                       " LEFT JOIN register_entries ON register_entries.id = records.id", type=type, status=status)
    return [dict(zip(("id", "type", "status", "path"), row)) if row[4] is None
            else dict(zip(("id", "type", "status", "path", "heading", "title"), row)) for row in rows]


def active(root: Path, type: str | None = None) -> list[str]:
    """The ids of the ACTIVE set (CAP-08): frontmatter status ACTIVE, and nothing supersedes the record."""
    sql = ("SELECT id FROM records WHERE status = 'ACTIVE'"
           " AND id NOT IN (SELECT target FROM edges WHERE type = 'SUPERSEDES')")
    return [row[0] for row in _rows(root, sql, type=type)]


def edges(root: Path, type: str | None = None, source: str | None = None, target: str | None = None) -> list[dict]:
    """The edges between records that match every filter given, dangling ones included."""
    return _edges(_rows(root, "SELECT type, source, target FROM edges", type=type, source=source, target=target))


def dangling(root: Path) -> list[dict]:
    """Every reference whose target is the id of no record: edges, and trailers (their source is the commit)."""
    return _edges(_rows(root, f"SELECT type, source, target FROM edges WHERE target NOT {_IS_RECORD}"
                              f" UNION SELECT upper(key), commit_id, value FROM trailers WHERE value NOT {_IS_RECORD}"))


def commits(root: Path, path: str | None = None) -> list[dict]:
    """The commits of ``HEAD``'s history, or those that changed ``path``, with their trailer ids."""
    if path is None:
        found = _rows(root, "SELECT id FROM commits")
    else:
        found = _rows(root, "SELECT commit_id FROM commit_paths", path=path)
    answer = {commit: {"commit": commit, "task": [], "implements": []} for commit, in found}
    for commit, key, value in _rows(root, "SELECT commit_id, key, value FROM trailers"):
        if commit in answer:
            answer[commit][key.lower()].append(value)
    return list(answer.values())
