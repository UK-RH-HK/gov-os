"""The memory-use log (W2-197 S8, S9, F2; EMERGENCY-2 5.6): one JSON line per ``gov retrieve`` call and per
``gov brief`` memory retrieval, and the reader the digest counts it with.

The log is ``GOV_MEMORY_LOG`` when set, else ``<main worktree>/.gov-runtime/memory-use.jsonl``: the main worktree of
the caller's tree is the parent of ``git rev-parse --git-common-dir``; a tree outside git is its own. A record holds
``ts`` (UTC, ISO 8601), ``command`` (``retrieve`` or ``brief``), ``role``, ``ticket``, ``session``, ``query_sha256``
(the first 16 hex digits of the query's sha256; the query itself is never logged), ``stop_reason``, ``items``,
``characters``, ``latency_ms``, ``refusal`` (the error code, else null), ``store_commit``, ``reranked`` and
``search_number`` (this session's calls of the command in the log, this one included; null with no session).

``append`` never raises: a log that cannot be written changes nothing a search or a brief prints or exits with (F2).
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path

ENV = "GOV_MEMORY_LOG"
LOG_REL = ".gov-runtime/memory-use.jsonl"
FIELDS = ("ts", "command", "role", "ticket", "session", "query_sha256", "stop_reason", "items", "characters",
          "latency_ms", "refusal", "store_commit", "reranked", "search_number")


def query_hash(query: str) -> str:
    """The first 16 hex digits of the query's sha256."""
    return hashlib.sha256(str(query).encode("utf-8")).hexdigest()[:16]


def log_path(root=None) -> Path:
    """``GOV_MEMORY_LOG``, else the log in the main worktree of ``root`` (the working folder when None)."""
    named = os.environ.get(ENV)
    if named:
        return Path(named)
    from gov.util.role_paths import main_tree

    tree = Path(root) if root is not None else Path.cwd()
    if not tree.is_dir():  # a folder named that does not exist (a missing store): the caller's own folder
        tree = Path.cwd()
    return Path(main_tree(tree)) / LOG_REL


def _records(path: Path):
    """(records, skipped) of the log at ``path``; a missing log has none."""
    records, skipped = [], 0
    try:
        text = path.read_bytes().decode("utf-8", errors="replace")
    except OSError:
        return records, skipped
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except ValueError:
            item = None
        if isinstance(item, dict):
            records.append(item)
        else:
            skipped += 1
    return records, skipped


def append(record: dict, root=None) -> None:
    """Appends ``record`` as one line, with ``ts`` and ``search_number`` set; never raises (F2)."""
    try:
        path = log_path(root)
        line = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds"), **record}
        session = line.get("session") or None
        line["session"] = session
        if session is None:
            line["search_number"] = None
        else:
            earlier = _records(path)[0]
            line["search_number"] = 1 + sum(1 for item in earlier if item.get("session") == session
                                            and item.get("command") == line.get("command"))
        text = json.dumps(line) + "\n"
        if os.environ.get(ENV):
            path.parent.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(exist_ok=True)  # .gov-runtime in an existing tree; never a tree made up
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(text)
    except Exception:  # noqa: BLE001 - F2: the log never fails or changes a search or a brief
        return


class Records(list):
    """The log's records, read in order; ``skipped`` counts the lines that are no JSON object."""

    skipped: int = 0
    path: str | None = None


def read(path=None, root=None, since: str | None = None) -> Records:
    """The log's records (``path``, else ``GOV_MEMORY_LOG``, else the log of ``root``'s main worktree), those of days
    from ``since`` (``YYYY-MM-DD``) on when given; unreadable lines skipped and counted in ``.skipped``."""
    where = Path(path) if path is not None else log_path(root)
    found, skipped = _records(where)
    out = Records(item for item in found if since is None or str(item.get("ts", ""))[:10] >= since)
    out.skipped, out.path = skipped, str(where)
    return out


def per_role_day(records) -> dict:
    """``{(day, role): {retrieves, briefs, refused}}``, in day and role order; a record with no role is role
    ``none``."""
    counts: dict[tuple[str, str], dict] = {}
    for item in records:
        key = (str(item.get("ts", ""))[:10], str(item.get("role") or "none"))
        row = counts.setdefault(key, {"retrieves": 0, "briefs": 0, "refused": 0})
        if item.get("command") == "retrieve":
            row["retrieves"] += 1
        elif item.get("command") == "brief":
            row["briefs"] += 1
        if item.get("refusal"):
            row["refused"] += 1
    return {key: counts[key] for key in sorted(counts)}
