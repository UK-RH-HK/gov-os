"""The machine-wide record of clean gitleaks verdicts, by the digest of what was judged (W2-107; DEC-966 item 4).

The pre-index filter judges a file's content and a path's names. A verdict of no finding at all, by every rule set,
is remembered here under the sha256 of the bytes judged, the kind (``content`` or ``path``) and the engine's
fingerprint, so the same bytes judged again by the same engine are answered without starting gitleaks. A finding is
never remembered. The record is one SQLite file outside every repository, ``~/.cache/gov-os/secrets-scan.sqlite``,
shared by worktrees, close clones and the nightly; ``GOV_SECRETS_CACHE`` names another file, or none when empty.
It holds digests, kinds, fingerprints and verdicts only: never content, a path or a match.

Whatever goes wrong with the record is a miss: the text is scanned. A write that fails is left out. The file is never
deleted or replaced here; a damaged one stays a miss until someone removes it. A record that can be read but not
written still answers the current engine's verdicts, and only those: every row carries the fingerprint it was judged
under.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import threading
from pathlib import Path
from typing import NamedTuple

FORMAT = 1  # the form of the record and of the fingerprint; another form is never read
DEFAULT_REL = ".cache/gov-os/secrets-scan.sqlite"  # under the home folder
_WAIT_S = 2.0  # how long a lock held by another writer is waited out before the text is scanned instead
_VERSION_S = 10  # how long gitleaks may take to say its version; without an answer, no record is used
_SCHEMA = ("CREATE TABLE engine (one INTEGER PRIMARY KEY CHECK (one = 1), fingerprint TEXT NOT NULL)",
           "CREATE TABLE verdict (digest TEXT NOT NULL, kind TEXT NOT NULL, fingerprint TEXT NOT NULL,"
           " verdict TEXT NOT NULL CHECK (verdict = 'clean'), PRIMARY KEY (digest, kind, fingerprint)) WITHOUT ROWID")
_ANSWER = "SELECT 1 FROM verdict WHERE digest = ? AND kind = ? AND fingerprint = ? AND verdict = 'clean'"

_lock = threading.Lock()
_asking = threading.Lock()  # one thread at a time reads a binary and asks its version, so each is asked once
_binaries: dict[tuple, list | None] = {}  # each gitleaks' digest and version, by path and status; None: in doubt
_ready: set[tuple[str, str]] = set()  # the records whose engine this process has checked, by file and fingerprint


class Engine(NamedTuple):
    """What one judgement is made by, taken once before its scan: the record, the fingerprint, and the gitleaks
    ``PATH`` found, by its path and status."""

    path: Path
    fingerprint: str
    binary: tuple


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


def _binary() -> tuple | None:
    """The gitleaks ``PATH`` finds, by its path and status (device, inode, size, modification and change times)."""
    found = shutil.which("gitleaks")
    if found is None:
        return None
    try:
        status = os.stat(found)
    except OSError:
        return None
    return found, status.st_dev, status.st_ino, status.st_size, status.st_mtime_ns, status.st_ctime_ns


def _identity(found: str) -> list | None:
    """The sha256 of the bytes of the gitleaks at ``found`` and the version it says, run there; None in any doubt."""
    try:
        with open(found, "rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        done = subprocess.run([found, "version"], stdin=subprocess.DEVNULL, capture_output=True, timeout=_VERSION_S)
    except (OSError, subprocess.SubprocessError):  # unreadable, cannot run, or no answer in time
        return None
    version = done.stdout.decode("utf-8", "replace").strip()
    return [digest, version] if done.returncode == 0 and version else None


def engine(rules: tuple[str, ...], form: int) -> Engine | None:
    """The engine a judgement is made by, taken once before its scan: the record's form, the filter's reading
    ``form``, the sha256 of each rule set, and the identity of the gitleaks ``PATH`` finds (the sha256 of its bytes and
    the version it says, so a release changed behind a shim of the same bytes is another engine).

    None when no record is used, or no gitleaks is found, or its bytes or version cannot be read: the text is then
    scanned as if there were no record, and nothing is kept. Each binary, known by its path and status, is read and
    asked its version once per process.
    """
    path = location()
    binary = _binary() if path is not None else None
    if binary is None:
        return None
    with _asking:
        if binary not in _binaries:
            _binaries[binary] = _identity(binary[0])
        identity = _binaries[binary]
    if identity is None:
        return None
    sets = [hashlib.sha256(each.encode()).hexdigest() for each in rules]
    return Engine(path, hashlib.sha256(json.dumps([FORMAT, form, sets, identity]).encode()).hexdigest(), binary)


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


def _use(kind: str, digest: str, engine: Engine, step) -> bool | None:
    """``step(connection, row)`` on the record, prepared for ``engine``; None on any doubt."""
    try:
        with contextlib.closing(_open(engine.path)) as connection:
            _prepare(connection, engine.path, engine.fingerprint)
            return step(connection, (digest, kind, engine.fingerprint))
    except (OSError, sqlite3.Error):  # cannot be opened or made, damaged, of another form, read-only or locked
        with _lock:
            _ready.discard((str(engine.path), engine.fingerprint))  # checked again next time, once it may be usable
        return None


def _read(path: Path, row: tuple, immutable: bool = False) -> bool:
    """Whether the record at ``path``, opened only to read, holds ``row`` as clean: it is neither prepared nor cleared,
    so only its form is checked and only a row of the fingerprint asked answers."""
    uri = f"{path.resolve().as_uri()}?mode=ro" + ("&immutable=1" if immutable else "")
    with contextlib.closing(sqlite3.connect(uri, uri=True, timeout=_WAIT_S, isolation_level=None)) as connection:
        if connection.execute("PRAGMA user_version").fetchone()[0] != FORMAT:
            return False
        return connection.execute(_ANSWER, row).fetchone() is not None


def remembered(kind: str, digest: str, engine: Engine | None) -> bool:
    """Whether the bytes of sha256 ``digest``, of ``kind``, were judged clean before by ``engine``.

    Only a verdict of that engine answers. A record that cannot be written (a read-only file or folder, a write lock
    that cannot be had) is read as it is; one whose folder lets no reader's mark be made is read as unchanging, but not
    one that a writer holds against readers. False under a full scan, without an engine, or on any doubt.
    """
    if full_scan() or engine is None:
        return False
    answer = _use(kind, digest, engine, lambda connection, row: connection.execute(_ANSWER, row).fetchone() is not None)
    if answer is not None:
        return answer
    row = (digest, kind, engine.fingerprint)
    try:
        return _read(engine.path, row)
    except sqlite3.Error as error:
        if not getattr(error, "sqlite_errorname", "").startswith("SQLITE_READONLY"):
            return False  # damaged, of another form, missing, or locked: a miss
    except OSError:
        return False
    try:
        return _read(engine.path, row, immutable=True)
    except (OSError, sqlite3.Error):
        return False


def remember(kind: str, digest: str, engine: Engine | None) -> None:
    """Keeps a clean verdict on the bytes of sha256 ``digest``, of ``kind``, by ``engine``, if the gitleaks ``PATH``
    finds is still the file it was before the scan: one replaced meanwhile is never credited with an older one's
    verdict. A write that fails is left out: the next run scans again."""
    if engine is None or _binary() != engine.binary:
        return
    _use(kind, digest, engine, lambda connection, row: connection.execute(
        "INSERT OR REPLACE INTO verdict VALUES (?, ?, ?, 'clean')", row) and True)
