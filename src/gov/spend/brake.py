"""The rule of the runaway brake: reading the records, the running cost, the projection, the marker, the brake record
and the inbox item (W2-156; DEC-1091 (2), DEC-1119 (5), DEC-655; the CTO's ``spend.py`` is the rule's origin).

Every path is under the project's main checkout (``gov.launch.record.main_checkout``): the session records
``.gov-runtime/sessions/<id>.json``, the launch records ``.gov-runtime/launches/<id>.json``, and, written here,
``.gov-runtime/spend/brakes.jsonl`` (one JSON line per brake or clear), ``.gov-runtime/spend/braked/<ticket>.json``
(the marker of a braked ticket) and one item in ``.gov-runtime/dispatch/inbox/`` (the dispatcher's folder) per brake.
A record that cannot be read or is not of its form is named in ``problems`` and skipped: never counted as zero cost,
never a crash. A cost the session record gives as not measured counts as unknown and adds nothing to the sum.
"""

from __future__ import annotations

import json
import math
import os
import re
import secrets
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from gov.cli.errors import GovError
from gov.launch import record as launches

RUNTIME, SPEND, BRAKED, SESSIONS, LAUNCHES = ".gov-runtime", "spend", "braked", "sessions", launches.LAUNCHES
LOG = "brakes.jsonl"
INBOX = (".gov-runtime", "dispatch", "inbox")
STAMP = "%Y-%m-%dT%H:%M:%SZ"
FACTOR = 2  # the brake: more than twice the latest projection (DEC-1091 (2))
TICKET = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def now() -> str:
    return time.strftime(STAMP, time.gmtime())


def project(root: Path) -> Path:
    """The project's main checkout (a planted project that is its own repository is its own)."""
    return launches.main_checkout(Path(os.path.realpath(root)), "the spend folder")


def folder(root: Path) -> Path:
    return project(root) / RUNTIME / SPEND


def marker_path(root: Path, ticket: str) -> Path:
    if not isinstance(ticket, str) or not TICKET.fullmatch(ticket):
        raise GovError("SPEND_TICKET_INVALID", f"'{ticket}' is not a ticket id (letters, digits, '.', '_' and '-')")
    return folder(root) / BRAKED / f"{ticket}.json"


def _stamp(value) -> datetime | None:
    try:
        return datetime.strptime(value, STAMP)
    except (TypeError, ValueError):
        return None


def _amount(value) -> float | None:
    """A number of 0 or more (a bool is not one), else None."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        return None
    return float(value)


def _usd(value) -> str:
    return f"{value:.2f}" if isinstance(value, (int, float)) and not isinstance(value, bool) else "unreadable"


# -- the marker, for ``gov launch`` ---------------------------------------------------------------------------------

def _read_marker(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def refusal(root: Path, ticket: str) -> str | None:
    """The text of ``gov launch``'s SPEND_BRAKED refusal for ``ticket``, naming the marker, the cost and the
    projection; None when the ticket has no marker. A marker that exists but cannot be read still refuses (fail
    closed), saying so."""
    try:
        path = marker_path(root, ticket)
    except GovError:
        return None  # not a name a marker can have
    if not os.path.lexists(path):
        return None
    data = _read_marker(path) or {}
    return (f"ticket {ticket} is braked: its cost passed twice its projection (marker {path}: cost "
            f"{_usd(data.get('cost_usd'))} USD, projection {_usd(data.get('projection_usd'))} USD; DEC-1091 (2)); "
            f"no new session starts until `gov spend clear {ticket} --note <why>` lifts it")


# -- reading the records ---------------------------------------------------------------------------------------------

def _json_files(base: Path, problems: list[str]) -> list[tuple[Path, dict]]:
    if not base.is_dir():
        return []
    try:
        names = sorted(name for name in os.listdir(base) if name.endswith(".json") and not name.startswith("."))
    except OSError as error:
        problems.append(f"{base}: cannot be listed ({error.strerror or error})")
        return []
    found = []
    for name in names:
        path = base / name
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            problems.append(f"{path}: cannot be read ({getattr(error, 'strerror', None) or 'not JSON'}), skipped")
            continue
        if not isinstance(data, dict):
            problems.append(f"{path}: not a JSON object, skipped")
            continue
        found.append((path, data))
    return found


def _log(root: Path, problems: list[str]) -> list[dict]:
    path = folder(root) / LOG
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    except OSError as error:
        problems.append(f"{path}: cannot be read ({error.strerror or error}), so no clear is known")
        return []
    entries = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            entry = None
        if isinstance(entry, dict):
            entries.append(entry)
        else:
            problems.append(f"{path} line {number}: not a JSON object, skipped")
    return entries


@dataclass
class Ticket:
    id: str
    cost: float = 0.0       # the measured sum
    unknown: int = 0        # counted sessions whose cost is not measured
    sessions: int = 0
    projection: float | None = None
    braked: bool = False


def survey(root: Path) -> tuple[list[Ticket], list[str]]:
    """Every ticket with a counted session record, sorted by id, and the records skipped (each named)."""
    problems: list[str] = []
    base = project(root) / RUNTIME
    entries = _log(root, problems)
    cleared: dict[str, datetime] = {}
    candidates: dict[str, list[tuple]] = {}  # ticket -> [(time, 0 launch | 1 clear, order, projection)]
    for order, entry in enumerate(entries):
        ticket, moment = entry.get("ticket"), _stamp(entry.get("at"))
        if entry.get("kind") != "clear" or not isinstance(ticket, str) or moment is None:
            continue
        cleared[ticket] = max(cleared.get(ticket, moment), moment)
        if (value := _amount(entry.get("projection_usd"))) is not None and value > 0:
            candidates.setdefault(ticket, []).append((moment, 1, order, value))
    for order, (path, data) in enumerate(_json_files(base / LAUNCHES, problems), len(entries)):
        ticket, moment = data.get("ticket"), _stamp(data.get("started_at"))
        if data.get("record") != "gov-launch" or not isinstance(ticket, str) or moment is None:
            problems.append(f"{path}: not a launch record of the form read here, skipped")
        elif (value := _amount(data.get("projection_usd"))) is not None and value > 0:
            candidates.setdefault(ticket, []).append((moment, 0, order, value))
    tickets: dict[str, Ticket] = {}
    for path, data in _json_files(base / SESSIONS, problems):
        held, moment = data.get("ticket"), _stamp(data.get("started_at"))
        ticket = held.get("value") if isinstance(held, dict) else None
        if data.get("record") != "gov-session" or not isinstance(ticket, str) or not ticket or moment is None:
            problems.append(f"{path}: not a session record of the form read here, skipped")
            continue
        if ticket in cleared and moment < cleared[ticket]:
            continue  # a cost before the last clear is no longer counted
        item = tickets.setdefault(ticket, Ticket(ticket))
        item.sessions += 1
        cost = data.get("cost_usd")
        measured = _amount(cost.get("value")) if isinstance(cost, dict) else None
        if measured is None:
            item.unknown += 1  # never zero: named in the sum
        else:
            item.cost += measured
    for ticket, item in tickets.items():
        if ticket in candidates:
            item.projection = max(candidates[ticket], key=lambda c: c[:3])[3]
        item.braked = TICKET.fullmatch(ticket) is not None and os.path.lexists(marker_path(root, ticket))
    return sorted(tickets.values(), key=lambda item: item.id), problems


def over(item: Ticket) -> bool:
    """More than twice the projection (exactly twice is not): compared to nine decimals, so a sum of floats that is
    twice the projection to the cent is not braked by rounding."""
    return item.projection is not None and round(item.cost, 9) > round(FACTOR * item.projection, 9)


# -- the brake and the clear -----------------------------------------------------------------------------------------

def _append(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def _unique(base: Path, stem: str) -> Path:
    target, number = base / f"{stem}.txt", 1
    while os.path.lexists(target):  # an item is never overwritten
        number += 1
        target = base / f"{stem}-{number}.txt"
    return target


def _inbox_item(root: Path, item: Ticket, marker: Path) -> Path:
    base = project(root).joinpath(*INBOX)
    base.mkdir(parents=True, exist_ok=True)
    target = _unique(base, f"{time.strftime('%Y%m%d-%H%M%S')}-spend-brake-{item.id}")
    status = (f"runaway brake: {item.id} has cost {item.cost:.2f} USD, past twice its projection "
              f"{item.projection:.2f} USD (brake at {FACTOR * item.projection:.2f})")
    text = "\n".join([
        f"log: {LOG}", f"W2: {item.id}", f"status: {status}", "kind: spend-brake", f"ticket: {item.id}",
        f"cost: {item.cost:.2f} USD", f"projection: {item.projection:.2f} USD", f"marker: {marker}", "",
        f"New launches for {item.id} stop (gov launch refuses with SPEND_BRAKED while the marker exists) until it is cleared:",
        f"  gov spend clear {item.id} [--projection-usd <more>] --note '<why>'",
        "Record only: no running session is stopped and nothing goes outside this inbox (DEC-1089 (3)).", ""])
    temporary = base / f".{target.name}.tmp"
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, target)
    return target


def _make_marker(path: Path, data: dict) -> bool:
    """The marker, whole and made once: False when it is there already (a check ending at the same moment)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.{secrets.token_hex(6)}.tmp"
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    try:
        os.link(temporary, path)
    except FileExistsError:
        return False
    finally:
        os.unlink(temporary)
    return True


def brake(root: Path, item: Ticket) -> tuple[Path, Path] | None:
    """One brake record, one marker and one inbox item for ``item``; ``(marker, inbox item)``, or None when the marker
    was made by another check meanwhile (then it wrote the rest)."""
    marker, at = marker_path(root, item.id), now()
    data = {"ticket": item.id, "cost_usd": round(item.cost, 4), "projection_usd": item.projection, "at": at}
    try:
        if not _make_marker(marker, data):
            return None
        _append(folder(root) / LOG, {"kind": "brake", **data})
        return marker, _inbox_item(root, item, marker)
    except OSError as error:
        raise GovError("SPEND_WRITE_FAILED", f"the brake on {item.id} cannot be written ({error.strerror or error}); "
                       f"the marker {marker} {'exists' if os.path.lexists(marker) else 'was not made'}") from None


def check(root: Path) -> tuple[list[str], list[str]]:
    """Judge every ticket with a counted session record: the output lines, and the records skipped."""
    lines = []
    tickets, problems = survey(root)
    for item in tickets:
        if item.projection is None:
            lines.append(f"{item.id}: no projection, never braked (cost {item.cost:.2f} USD)")
        elif item.braked:
            lines.append(f"{item.id}: already braked")
        elif over(item):
            made = brake(root, item)
            if made is not None:
                lines.append(f"BRAKE {item.id}: cost {item.cost:.2f} USD, past twice its projection "
                             f"{item.projection:.2f} USD; marker {made[0]}; inbox item {made[1]}")
    return lines or ["spend check: no ticket past twice its projection"], problems


def clear(root: Path, ticket: str, note: str, projection: float | None) -> tuple[str, bool]:
    """Lift ``ticket``'s brake: the clear is recorded first (the count restarts from its time), then the marker is
    removed. ``(the clear's time, whether a marker was removed)``."""
    marker, at = marker_path(root, ticket), now()
    try:
        _append(folder(root) / LOG, {"kind": "clear", "ticket": ticket, "note": note, "projection_usd": projection,
                                     "at": at})
        had = os.path.lexists(marker)
        if had:
            os.unlink(marker)
    except OSError as error:
        raise GovError("SPEND_WRITE_FAILED", f"the clear of {ticket} cannot be written ({error.strerror or error})") \
            from None
    return at, had


def sum_line(item: Ticket) -> str:
    unknown = f", {item.unknown} unknown" if item.unknown else ""
    projection = f"projection {item.projection:.2f} USD" if item.projection is not None else "no projection"
    return f"{item.id}: cost {item.cost:.2f} USD{unknown}; {projection}; {'braked' if item.braked else 'not braked'}"
