"""The audit's ledger, ``runs/<audit>/ledger.jsonl`` (Interface section 2): one JSON object per line, in order, each
``{"seq": n, "at": <ISO UTC>, "event": <word>, ...}`` with numbers and codes only. This ticket writes ``preflight``,
``drop``, ``void``, ``declaration`` and ``used``; W2-171 appends ``search`` and ``spend`` after ``used``."""

from __future__ import annotations

import json
import os
from pathlib import Path

from gov.memaudit.common import utc_iso

NAME = "ledger.jsonl"


def _file(where) -> Path:
    where = Path(where)
    return where / NAME if where.is_dir() else where


def read(where) -> list[dict]:
    """The ledger's objects in order; a line that is not a JSON object is skipped."""
    try:
        with open(_file(where), encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def append(where, event: str, **fields) -> dict:
    """Append one event to the ledger (``where`` is the run folder or the ledger file); the object written."""
    path = _file(where)
    seq = 1 + max((o.get("seq", 0) for o in read(path) if isinstance(o.get("seq"), int)), default=0)
    obj = {"seq": seq, "at": utc_iso(), "event": event, **fields}
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, (json.dumps(obj, sort_keys=True) + "\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    return obj
