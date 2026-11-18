"""Per-session inbox files with a read mark, machine-wide (the run-time tool, slice 1: RT-6, RT-7; audit 3 D6, D7).

``$HOME/.gov-os/inbox/<address>/`` holds ``messages.jsonl`` (one JSON object a line) and ``mark`` (the decimal byte
offset of the first unread byte; absent or empty means 0). The inbox never depends on a project root, so two sessions
in two repositories exchange messages with no one relaying them.

- An append holds an exclusive ``flock`` on ``messages.jsonl`` and, under the same lock, refuses an id the inbox
  already holds: a send with an id is idempotent (F1).
- A read that moves the mark holds a ``flock`` on ``mark`` and writes it whole (a temporary file and a rename). It
  reads only whole lines: a line still being written is left for the next read.
- One wake rule (RT-7): a session is woken when its inbox holds an unread ``wake`` message past its mark.
"""

from __future__ import annotations

import datetime
import fcntl
import json
import os
import re
import tempfile
import time
import uuid
from pathlib import Path

ADDRESS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@+-]{0,127}$")
KINDS = ("wake", "notice")
RUNTIME = "runtime"           # the watch pass's own inbox; the only one that takes "watch" messages
MESSAGES, MARK = "messages.jsonl", "mark"
WAIT_DEFAULT_S, WAIT_MAX_S, POLL_S = 540, 570, 1.0


class InboxError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def root() -> Path:
    return Path(os.environ.get("HOME") or Path.home()) / ".gov-os" / "inbox"


def check(address) -> str:
    """The address, or ``InboxError("MSG_ADDRESS_INVALID")``: never a path out of the inbox root."""
    if not isinstance(address, str) or not ADDRESS.match(address) or ".." in address:
        raise InboxError("MSG_ADDRESS_INVALID", f"{address!r} is not an inbox address "
                         f"({ADDRESS.pattern}, with no '..')")
    return address


def folder(address: str) -> Path:
    return root() / check(address)


def now_stamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _whole_lines(data: bytes) -> tuple[list[dict], int]:
    """The parsed whole lines of ``data`` and the bytes they span; a line that is no JSON object is skipped."""
    end = data.rfind(b"\n") + 1
    out = []
    for line in data[:end].splitlines():
        try:
            item = json.loads(line)
        except ValueError:
            continue
        if isinstance(item, dict):
            out.append(item)
    return out, end


def send(to: str, kind: str, text: str, *, sender: str | None = None, message_id: str | None = None,
         data: dict | None = None) -> dict:
    """Append one message to ``to``'s inbox: ``{"sent", "duplicate", "id", "to"}``. An id already there is not
    appended again (``sent`` false, ``duplicate`` true)."""
    place = folder(to)
    if kind not in KINDS and not (kind == "watch" and to == RUNTIME):
        raise InboxError("MSG_KIND_INVALID", f"{kind!r} is not a message kind ({', '.join(KINDS)})")
    if data is not None and not isinstance(data, dict):
        raise InboxError("MSG_DATA_INVALID", "the message's data must be a JSON object")
    message_id = message_id or uuid.uuid4().hex
    message = {"id": message_id, "at": now_stamp(), "from": sender or os.environ.get("GOV_MSG_ADDRESS") or "unknown",
               "to": to, "kind": kind, "text": str(text)}
    if data is not None:
        message["data"] = data
    line = (json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8")
    place.mkdir(parents=True, exist_ok=True)
    fd = os.open(place / MESSAGES, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        with open(fd, "rb", closefd=False) as handle:
            held, _ = _whole_lines(handle.read())
        if any(item.get("id") == message_id for item in held):
            return {"sent": False, "duplicate": True, "id": message_id, "to": to}
        os.write(fd, line)
    finally:
        os.close(fd)  # the lock goes with the descriptor
    return {"sent": True, "duplicate": False, "id": message_id, "to": to}


def _mark(place: Path) -> int:
    try:
        text = (place / MARK).read_text(encoding="ascii").strip()
        return int(text) if text else 0
    except (OSError, ValueError, UnicodeDecodeError):
        return 0


def _past(place: Path, mark: int) -> tuple[list[dict], int]:
    """The messages past ``mark`` and the offset after the last whole line (the mark read from 0 when the file is now
    shorter than the mark: it was replaced)."""
    try:
        with open(place / MESSAGES, "rb") as handle:
            size = os.fstat(handle.fileno()).st_size
            mark = 0 if mark > size else mark
            handle.seek(mark)
            data = handle.read()
    except FileNotFoundError:
        return [], mark
    found, span = _whole_lines(data)
    return found, mark + span


def pending(address: str) -> tuple[list[dict], int, int]:
    """``(messages, mark, end)``: the unread messages, the mark, and the offset a read would move the mark to."""
    place = folder(address)
    mark = _mark(place)
    found, end = _past(place, mark)
    return found, mark, end


def _write_mark(place: Path, offset: int) -> None:
    with tempfile.NamedTemporaryFile("w", dir=place, prefix=".mark-", delete=False) as handle:
        handle.write(f"{offset}\n")
    os.replace(handle.name, place / MARK)


def _locked_mark(place: Path) -> int:
    """A descriptor on ``mark`` holding its lock, the file at the path still being the one locked (a writer replaces
    it whole)."""
    while True:
        fd = os.open(place / MARK, os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            if os.stat(place / MARK).st_ino == os.fstat(fd).st_ino:
                return fd
        except FileNotFoundError:
            pass
        os.close(fd)


def advance(address: str, offset: int) -> None:
    """Move ``address``'s mark forward to ``offset`` (never back), under the mark's lock."""
    place = folder(address)
    place.mkdir(parents=True, exist_ok=True)
    fd = _locked_mark(place)
    try:
        if offset > _mark(place):
            _write_mark(place, offset)
    finally:
        os.close(fd)


def read(address: str, peek: bool = False) -> dict:
    """``{"address", "messages", "mark"}``: the messages past the mark, which moves past them unless ``peek``."""
    place = folder(address)
    if peek or not (place / MESSAGES).exists():
        found, _mark_now, _end = pending(address)
        return {"address": address, "messages": found, "mark": _mark_now}
    fd = _locked_mark(place)
    try:
        found, end = _past(place, _mark(place))
        if end != _mark(place):
            _write_mark(place, end)
    finally:
        os.close(fd)
    return {"address": address, "messages": found, "mark": end}


def wakes(address: str) -> list[dict]:
    return [m for m in pending(address)[0] if m.get("kind") == "wake"]


def wait(address: str, timeout: float, every: float = POLL_S) -> list[dict] | None:
    """The unread wake messages as soon as there is one (the mark unmoved), or None once ``timeout`` has passed."""
    check(address)
    end = time.monotonic() + timeout
    while True:
        found = wakes(address)
        if found:
            return found
        left = end - time.monotonic()
        if left <= 0:
            return None
        time.sleep(min(every, left))
