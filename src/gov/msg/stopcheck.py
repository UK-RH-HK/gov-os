"""The Stop check (the run-time tool, slice 3: RT-2, the wake carrier; audit 3 D7).

``check(address)`` is what the one Stop hook (``stop.py``) and ``gov msg stop-check`` ask when a turn is about to end:
the Claude Code block decision for an unread ``wake`` message, or None to let the turn end. It blocks only for a wake
message past the address's read mark, **once per message**: the ids it blocked on are recorded in
``~/.gov-os/inbox/<address>/stop-seen`` before it answers, so no message blocks twice, whatever happens next. A
notice or a relay never blocks, a session with no address is never blocked, and nothing is waited on: an idle session
with nothing unread passes (the owner retired inbox waiters and idle wake-ups, DEC-1212 (4)). The read mark is never
moved here: it is ``gov msg read``'s.
"""

from __future__ import annotations

import fcntl
import json
import os

from gov.dispatch import inbox

SEEN = "stop-seen"


def _seen(data: bytes) -> set[str]:
    found = set()
    for line in data.decode("utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except ValueError:
            continue
        if isinstance(item, str):
            found.add(item)
    return found


def _fresh(address: str, wakes: list[dict]) -> list[dict]:
    """The wake messages not blocked on before; their ids are recorded (under a lock) before this returns."""
    fd = os.open(inbox.folder(address) / SEEN, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        with open(fd, "rb", closefd=False) as handle:
            seen = _seen(handle.read())
        fresh, taken = [], set()
        for message in wakes:
            ident = message.get("id")
            if isinstance(ident, str) and ident not in seen and ident not in taken:
                fresh.append(message)
                taken.add(ident)
        if fresh:
            os.write(fd, "".join(json.dumps(m["id"]) + "\n" for m in fresh).encode("utf-8"))
        return fresh
    finally:
        os.close(fd)


def check(address: str | None = None) -> dict | None:
    """``{"decision": "block", "reason": <the unread wake messages' text>}`` for the wake messages of ``address``
    (default ``$GOV_MSG_ADDRESS``) not blocked on before, else None. It never raises: a check that cannot run lets
    the turn end."""
    address = address if address is not None else os.environ.get("GOV_MSG_ADDRESS")
    if not address:
        return None
    try:
        wakes = inbox.wakes(inbox.check(address))
        fresh = _fresh(address, wakes) if wakes else []
    except (OSError, inbox.InboxError):
        return None
    if not fresh:
        return None
    lines = [f"- {message.get('from')}: {message.get('text')}" for message in fresh]
    noun = "message" if len(fresh) == 1 else "messages"
    reason = (f"{len(fresh)} unread wake {noun} for {address} (read with `gov msg read`):\n" + "\n".join(lines))
    return {"decision": "block", "reason": reason}
