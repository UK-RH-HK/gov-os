"""The machine-wide record of clean gitleaks verdicts, by the digest of what was judged (W2-107; DEC-966 item 4).

The pre-index filter judges a file's content and a path's names. A verdict of no finding at all, by every rule set,
is remembered here under the sha256 of the bytes judged, the kind (``content`` or ``path``) and the engine's
fingerprint, so the same bytes judged again by the same engine are answered without starting gitleaks. A finding is
never remembered. The record is one SQLite file outside every repository, ``~/.cache/gov-os/secrets-scan.sqlite``,
shared by worktrees, close clones and the nightly; ``GOV_SECRETS_CACHE`` names another file, or none when empty.
It holds digests, kinds, fingerprints and verdicts only: never content, a path or a match.

Whatever goes wrong with the record is a miss: the text is scanned. A write that fails is left out. The file is never
deleted or replaced here; a damaged one stays a miss until someone removes it.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import shutil
import sqlite3
import threading
from pathlib import Path

FORMAT = 1  # the form of the record and of the fingerprint; another form is never read
DEFAULT_REL = ".cache/gov-os/secrets-scan.sqlite"  # under the home folder
_WAIT_S = 2.0  # how long a lock held by another writer is waited out before the text is scanned instead
_SCHEMA = ("CREATE TABLE engine (one INTEGER PRIMARY KEY CHECK (one = 1), fingerprint TEXT NOT NULL)",
           "CREATE TABLE verdict (digest TEXT NOT NULL, kind TEXT NOT NULL, fingerprint TEXT NOT NULL,"
           " verdict TEXT NOT NULL CHECK (verdict = 'clean'), PRIMARY KEY (digest, kind, fingerprint)) WITHOUT ROWID")

_lock = threading.Lock()
_binaries: dict[tuple, str] = {}  # the digest of each gitleaks binary, by its path and what its status says of it
_ready: set[tuple[str, str]] = set()  # the records whose engine this process has checked, by file and fingerprint


def location() -> Path | None:
    """The record's file, or None when no record is used: ``GOV_SECRETS_CACHE`` empty, or a pytest test running
    without it set (so a suite never reads the machine's record), or no home folder."""
    named = os.environ.get("GOV_SECRETS_CACHE")
    if named is not None:
        return Path(named) if named else None
    home = os.environ.get("HOME")
    if "PYTEST_CURRENT_TEST" in os.environ or not home:
        return None
    return Path(home) / DEFAULT_REL


def full_scan() -> bool:
    """Whether ``GOV_SECRETS_FULL_SCAN`` asks for every text to be scanned: nothing is read, clean verdicts are written."""
    return os.environ.get("GOV_SECRETS_FULL_SCAN", "") not in ("", "0")


def fingerprint(rules: tuple[str, ...]) -> str | None:
    """The engine that decides a verdict: the record's form, the sha256 of each rule set and of the gitleaks binary
    ``PATH`` finds. None when no gitleaks is found or it cannot be read; the scan then raises, and nothing is kept.

    The binary is read once per process for each binary, known by its path and status: another build, another file
    first on ``PATH`` or new bytes give another fingerprint.
    """
    found = shutil.which("gitleaks")
    if found is None:
        return None
    try:
        status = os.stat(found)
        known = (found, status.st_dev, status.st_ino, status.st_size, status.st_mtime_ns, status.st_ctime_ns)
        with _lock:
            binary = _binaries.get(known)
        if binary is None:
            with open(found, "rb") as handle:
                binary = hashlib.file_digest(handle, "sha256").hexdigest()
            with _lock:
                _binaries[known] = binary
    except OSError:
        return None
    sets = [hashlib.sha256(each.encode()).hexdigest() for each in rules]
    return hashlib.sha256(json.dumps([FORMAT, sets, binary]).encode()).hexdigest()


def _open(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    return sqlite3.connect(path, timeout=_WAIT_S, isolation_level=None)


def _prepare(connection: sqlite3.Connection, path: Path, engine: str) -> None:
    """Makes the record's tables where the file is new, and forgets every verdict of another engine: once per process
    for each file and engine, in one write transaction. Raises ``sqlite3.Error`` on a file of any other form."""
    key = (str(path), engine)
    with _lock:
        if key in _ready:
            return
    connection.execute("BEGIN IMMEDIATE")
    try:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if version == 0 and connection.execute("SELECT count(*) FROM sqlite_master").fetchone()[0] == 0:
            for statement in _SCHEMA:
                connection.execute(statement)
            connection.execute(f"PRAGMA user_version = {FORMAT}")
        elif version != FORMAT:
            raise sqlite3.DatabaseError("not a record of this form")
        held = connection.execute("SELECT fingerprint FROM engine").fetchall()
        if held != [(engine,)]:  # a changed engine forgets everything, before the first read
            connection.execute("DELETE FROM verdict")
            connection.execute("INSERT OR REPLACE INTO engine VALUES (1, ?)", (engine,))
        connection.execute("COMMIT")
    except BaseException:
        with contextlib.suppress(sqlite3.Error):
            connection.execute("ROLLBACK")
        raise
    with contextlib.suppress(sqlite3.Error):  # readers and writers at once; only a record of this form is changed
        connection.execute("PRAGMA journal_mode=WAL")
    with _lock:
        _ready.add(key)


def _use(kind: str, digest: str, rules: tuple[str, ...], step) -> bool:
    """``step(connection, row)`` on the record, prepared for the current engine; False on any doubt."""
    path = location()
    engine = fingerprint(rules) if path is not None else None
    if engine is None:
        return False
    try:
        with contextlib.closing(_open(path)) as connection:
            _prepare(connection, path, engine)
            return step(connection, (digest, kind, engine))
    except (OSError, sqlite3.Error):  # cannot be opened or made, damaged, of another form, or locked: a miss
        with _lock:
            _ready.discard((str(path), engine))  # checked again next time, once it may be usable
        return False


def remembered(kind: str, digest: str, rules: tuple[str, ...]) -> bool:
    """Whether the bytes of sha256 ``digest``, of ``kind``, were judged clean before by the engine of ``rules``.

    Only a verdict of the current engine answers. False under a full scan, without a record, or on any doubt.
    """
    if full_scan():
        return False
    return _use(kind, digest, rules, lambda connection, row: connection.execute(
        "SELECT 1 FROM verdict WHERE digest = ? AND kind = ? AND fingerprint = ? AND verdict = 'clean'",
        row).fetchone() is not None)


def remember(kind: str, digest: str, rules: tuple[str, ...]) -> None:
    """Keeps a clean verdict on the bytes of sha256 ``digest``, of ``kind``, by the engine of ``rules``. A write that
    fails is left out: the next run scans again."""
    _use(kind, digest, rules, lambda connection, row: connection.execute(
        "INSERT OR REPLACE INTO verdict VALUES (?, ?, ?, 'clean')", row) and True)
