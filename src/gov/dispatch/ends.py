"""The end events and their gaps (the run-time tool, slice 3: RT-2; audit 3 D4).

Every end of a lead, a worker or a heavy job is one ``end`` event in the runtime log (``~/.gov-os/runtime/log.jsonl``)::

    {"at", "event": "end", "id", "kind": "lead"|"worker"|"job", "to", "ended_at", "ticket"|"job", ["estimated": true]}

``id`` is the id of the wake message that tells the end (``end:...`` for a session, ``job:<job>`` for a job), ``to`` the
address it goes to, ``ended_at`` an ISO-8601 time. The launcher (``_end_message``) and ``admission.wake`` write it
with ``ended_at`` = now; the watch pass writes it for an end it detects, with ``estimated: true``. An id already
there writes no second event.

``gov dispatch waits --ends`` reads them: the gap of an end is the ``at`` of the first message with its id in the inbox
``to``, less ``ended_at``; an end with no message yet has the gap to now and is ``unsent``. A gap over ``OVER_S`` is a
finding.
"""

from __future__ import annotations

import datetime
import json
import os

from gov.dispatch import admission, inbox

OVER_S = 120.0
KINDS = ("lead", "worker", "job")


def stamp(epoch: float | None = None) -> str:
    """A whole-second UTC time (the inbox's own form), of ``epoch`` or now."""
    when = datetime.datetime.now(datetime.timezone.utc) if epoch is None else \
        datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc)
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch(text) -> float | None:
    try:
        when = datetime.datetime.fromisoformat(str(text).strip().replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=datetime.timezone.utc)
        return when.timestamp()
    except ValueError:
        return None


def known(ident: str) -> bool:
    """Whether the runtime log already holds an ``end`` event with this id."""
    return bool(admission.events(newest=1, want=lambda e: e.get("event") == "end" and e.get("id") == ident))


def event(ident: str, kind: str, to: str, ended_at: str, *, ticket: str | None = None, job: str | None = None,
          estimated: bool = False) -> dict:
    found = {"at": admission.stamp(), "event": "end", "id": ident, "kind": kind, "to": to, "ended_at": ended_at}
    if ticket is not None:
        found["ticket"] = ticket
    if job is not None:
        found["job"] = job
    if estimated:
        found["estimated"] = True
    return found


def record(ident: str, kind: str, to: str, ended_at: str, **fields) -> bool:
    """Append one ``end`` event to the runtime log (``O_APPEND``); False for an id already there, and for a log that
    cannot be written (a log that cannot be written never fails the end it records)."""
    if known(ident):
        return False
    line = (json.dumps(event(ident, kind, to, ended_at, **fields)) + "\n").encode("utf-8")
    try:
        path = admission.log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_CLOEXEC, 0o644)
        try:
            os.write(fd, line)
        finally:
            os.close(fd)
    except OSError:
        return False
    return True


def analyse(log: list[dict], now: float) -> list[dict]:
    """One row per ``end`` event, in the log's order: ``{id, kind, to, ended_at, sent_at, gap_s, unsent}``."""
    firsts: dict[tuple[str, str], str | None] = {}
    rows = []
    for item in log:
        ident, to, ended = item.get("id"), item.get("to"), epoch(item.get("ended_at"))
        if item.get("event") != "end" or not isinstance(ident, str) or not isinstance(to, str) or ended is None:
            continue
        if (to, ident) not in firsts:
            try:
                firsts[(to, ident)] = inbox.sent_at(to, ident)
            except inbox.InboxError:  # an address that is none: nothing was sent to it
                firsts[(to, ident)] = None
        sent = firsts[(to, ident)]
        sent_epoch = None if sent is None else epoch(sent)
        unsent = sent_epoch is None
        rows.append({"id": ident, "kind": item.get("kind"), "to": to, "ended_at": item.get("ended_at"),
                     "sent_at": sent, "gap_s": round(max(0.0, (now if unsent else sent_epoch) - ended), 3),
                     "unsent": unsent})
    return rows


def findings(rows: list[dict], over: float = OVER_S) -> list[dict]:
    """The ends whose gap passed ``over`` seconds (strictly: a gap of exactly ``over`` is none)."""
    return [row for row in rows if row["gap_s"] > over]


def _shown(seconds: float) -> str:
    return str(int(seconds)) if seconds == int(seconds) else f"{seconds:.1f}"


def render(rows: list[dict], found: list[dict], over: float) -> str:
    lines = [f"{row['id']} {row['kind']} {row['to']} gap {_shown(row['gap_s'])} s" + (" unsent" if row["unsent"] else "")
             for row in rows] or ["no end has been recorded yet"]
    lines += [f"finding: {row['id']} {'unsent, ' if row['unsent'] else ''}gap {_shown(row['gap_s'])} s is over "
              f"{_shown(over)} s" for row in found]
    return "\n".join(lines) + "\n"
