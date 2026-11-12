"""The state folder ``<root>/.gov-runtime/dispatch/`` and the files in it (the ticket's Interface section).

``ready.txt`` (the orchestrator's list), ``started.txt`` (one line a start: ``<log name> <time> <W2> <ticket id>``),
``never-ran.txt``, ``items-written.txt`` (every inbox item ever written: it outlives the item), ``escalated.txt`` (the
escalations sent), ``escalate-failed.txt`` (the failed attempts of the notifier), ``land.txt`` and ``land-done.txt`` (the landing step's, part b; shown here only),
``inbox/`` and ``inbox/read/`` (one text item per event), ``logs/<log name>`` and ``logs/<log name>.exit`` (a session's
output and, when it ends, its exit code), ``status.json``, ``status.txt``, ``peaks.json``, ``OFF``, ``tick.lock``.
"""

from __future__ import annotations

import datetime
import fcntl
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

FOLDER = Path(".gov-runtime") / "dispatch"
ITEM_SUFFIXES = (".return.txt", ".never-ran.txt", ".owner.txt")  # the inbox items a pass writes
WRITTEN = "items-written.txt"  # one line per inbox item ever written: ``<item name> <time>``
SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._=+-]*$")


def now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def stamp(moment: datetime.datetime | None = None) -> str:
    return (moment or now()).isoformat(timespec="seconds")


def parse_time(text: str) -> datetime.datetime | None:
    try:
        moment = datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=datetime.timezone.utc)


class State:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.dir = self.root / FOLDER
        self.inbox = self.dir / "inbox"
        self.read = self.inbox / "read"
        self.logs = self.dir / "logs"

    def file(self, name: str) -> Path:
        return self.dir / name

    def make(self) -> None:
        for folder in (self.dir, self.inbox, self.read, self.logs):
            folder.mkdir(parents=True, exist_ok=True)

    def text(self, name: str) -> str:
        try:
            return self.file(name).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def lines(self, name: str) -> list[str]:
        """The file's lines, blank ones and ``#`` comments left out."""
        return [line.strip() for line in self.text(name).splitlines() if line.strip() and not line.lstrip().startswith("#")]

    def append(self, name: str, line: str) -> None:
        with open(self.file(name), "a", encoding="utf-8") as handle:
            handle.write(line.rstrip("\n") + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def write_whole(self, path: Path, text: str) -> None:
        """A temporary file beside it, then a rename: a reader never sees half a file."""
        handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                stream.write(text)
            os.replace(temporary, path)
        except BaseException:
            try:
                os.unlink(temporary)
            except OSError:
                pass
            raise

    def exit_file(self, log: str) -> Path:
        return self.logs / f"{log}.exit"

    # --- the start records -------------------------------------------------------------------------------------

    def started(self) -> list["Start"]:
        out = []
        path = self.file("started.txt")
        try:
            fallback = datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc)
        except OSError:
            return out
        for line in self.lines("started.txt"):
            parts = line.split()
            moment = parse_time(parts[1]) if len(parts) > 1 and "T" in parts[1] else None
            rest = parts[2:] if moment else parts[1:]
            out.append(Start(parts[0], moment or fallback, rest[0] if rest else "", rest[1] if len(rest) > 1 else ""))
        return out

    def record_start(self, log: str, w2: str, ticket: str) -> None:
        self.append("started.txt", f"{log} {stamp()} {w2} {ticket}")

    # --- the inbox -----------------------------------------------------------------------------------------------

    def items(self, folder: Path | None = None) -> list["Item"]:
        folder = folder or self.inbox
        out = []
        try:
            paths = sorted(p for p in folder.iterdir() if p.is_file() and not p.name.startswith("."))
        except OSError:
            return out
        for path in paths:
            fields = {}
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
                age = now().timestamp() - path.stat().st_mtime
            except OSError:
                continue
            for line in lines:
                name, _, value = line.partition(":")
                if name in ("log", "W2", "status", "kind") and name not in fields:
                    fields[name] = value.strip()
            out.append(Item(path, fields.get("W2", ""), fields.get("log", ""), fields.get("status", ""),
                            fields.get("kind", ""), age))
        return out

    def all_items(self) -> list["Item"]:
        return self.items(self.inbox) + self.items(self.read)

    def written(self, name: str) -> bool:
        """Whether the item was ever written: the record ``items-written.txt`` (it outlives the item, deleted from
        ``inbox/`` or ``inbox/read/``), or the item itself in either folder (a state from before the record), or, for a
        never-ran item, its line in ``never-ran.txt``."""
        if (self.inbox / name).exists() or (self.read / name).exists():
            return True
        if name in {line.split()[0] for line in self.lines(WRITTEN)}:
            return True
        suffix = ".never-ran.txt"
        return name.endswith(suffix) and name[:-len(suffix)] in {line.split()[0] for line in self.lines("never-ran.txt")}

    def record_seen(self) -> list[str]:
        """Record as written every item found in ``inbox/`` or ``inbox/read/`` that ``items-written.txt`` does not hold
        (F-1): one the dispatcher did not write itself (a state folder from before the record) counts as written the
        pass that sees it, so deleting it later does not make a pass write it again. The names newly recorded."""
        known = {line.split()[0] for line in self.lines(WRITTEN)}
        added = []
        for folder in (self.inbox, self.read):
            try:
                names = sorted(p.name for p in folder.iterdir() if p.is_file() and p.name.endswith(ITEM_SUFFIXES))
            except OSError:
                continue
            for name in names:
                if name not in known and not name.startswith("."):
                    self.append(WRITTEN, f"{name} {stamp()}")
                    known.add(name)
                    added.append(name)
        return added

    def write_item(self, name: str, lines: list[str]) -> Path | None:
        """The item ``inbox/<name>``, whole, never twice, ever (F-1): None when it was written before, whether it is
        still there (unread or read) or was deleted since. The record is appended after the item is in place."""
        if self.written(name):
            return None
        path = self.inbox / name
        self.write_whole(path, "\n".join(lines) + "\n")
        self.append(WRITTEN, f"{name} {stamp()}")
        return path

    # --- the lock --------------------------------------------------------------------------------------------------

    def lock(self):
        """The pass's lock, or None when another pass holds it. Released with the file (also when the process dies)."""
        # The folder is made only when it is not there, and then no other pass can hold a lock in it: a pass that loses
        # the lock has created nothing. The lock file is opened without a write (append, no data).
        self.dir.mkdir(parents=True, exist_ok=True)
        handle = open(self.file("tick.lock"), "a")
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            return None
        return handle


@dataclass(frozen=True)
class Start:
    log: str
    at: datetime.datetime
    w2: str
    ticket: str


@dataclass(frozen=True)
class Item:
    path: Path
    w2: str
    log: str
    status: str
    kind: str
    age_s: float


@dataclass(frozen=True)
class Entry:
    """A line of the ready list: ``<W2> <ticket id> <brief> <log name>``, or a ``problem`` when malformed."""
    line: str
    w2: str = ""
    ticket: str = ""
    brief: str = ""
    log: str = ""
    problem: str = ""


def read_ready(state: State) -> list[Entry]:
    out = []
    for line in state.lines("ready.txt"):
        parts = line.split()
        if len(parts) != 4:
            out.append(Entry(line, problem=f"malformed: {len(parts)} fields, 4 are needed "
                                           "(<W2> <ticket id> <brief> <log name>)"))
            continue
        w2, ticket, brief, log = parts
        bad = next((n for n, v in (("W2", w2), ("ticket id", ticket), ("log name", log)) if not SAFE.match(v)
                    or ".." in v), None)
        if bad is None and (brief.startswith("-") or ".." in Path(brief).parts):
            bad = "brief"
        out.append(Entry(line, problem=f"malformed: the {bad} is not a plain name") if bad else
                   Entry(line, w2, ticket, brief, log))
    return out
