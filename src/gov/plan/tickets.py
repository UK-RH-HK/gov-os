"""The ticket store as the plan reads it (W2-136 S1, S5): every ``.tickets/*.md`` file, read fresh on every call.

Each ticket gives its writes (``allowed_paths``), ``reads``, ``needs``, ``waits_on``, ``depends_on`` and ``deps``,
its status, priority and WBS id, and an owner exception (``plan_override: <DEC-id>``, DEC-899). Nothing is cached
between calls (S8): an open ticket changed in flight (DEC-1088 (6)) is read as it is now.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from gov.util.frontmatter import FrontmatterError, parse

TICKETS_DIR = ".tickets"
OPEN = ("open", "in_progress")
CLOSED = "closed"
DEFAULT_PRIORITY = 99  # a ticket without a priority comes after every ticket with one
_DEC = re.compile(r"DEC-[0-9]+")
_ID_END = ":,;()[]—–"


class PlanError(Exception):
    """The plan cannot be made (exit code 2): the reason names what could not be read."""


@dataclass(frozen=True)
class Ticket:
    id: str
    wbs: str
    status: str
    priority: int
    writes: tuple[str, ...]
    reads: tuple[str, ...] | None   # None: the field is not declared
    needs: tuple[str, ...] | None   # None: the field is not declared (NEEDS_UNDECLARED)
    waits_on: tuple[str, ...]       # the ids or record paths, each entry's reason left out
    depends_on: tuple[str, ...]
    deps: tuple[str, ...]
    override: str | None            # the decision id of a plan_override
    path: str

    @property
    def unfinished(self) -> bool:
        return self.status != CLOSED


def _strings(value) -> list[str]:
    """A field of paths or ids as a list of non-empty strings: one string as itself, a list's strings."""
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _declared(front: dict, key: str) -> tuple[str, ...] | None:
    if key not in front or front[key] is None:
        return None
    return tuple(_strings(front[key]))


def wait_id(entry) -> str | None:
    """The id or record path of one ``waits_on`` entry: ``"DAEO-x — the reason"``, ``"DEC-12: the reason"``,
    ``{id: DAEO-x, reason: ...}`` or ``{DAEO-x: the reason}``; None when it names nothing."""
    if isinstance(entry, dict):
        for key in ("id", "path", "ref"):
            if isinstance(entry.get(key), str) and entry[key].strip():
                return wait_id(entry[key])
        if len(entry) == 1:
            key = next(iter(entry))
            return wait_id(key) if isinstance(key, str) else None
        return None
    if not isinstance(entry, str) or not entry.strip():
        return None
    first = entry.strip().split()[0].rstrip(_ID_END)
    return first or None


def _waits(value) -> tuple[str, ...]:
    entries = value if isinstance(value, list) else ([value] if value is not None else [])
    found = [wait_id(entry) for entry in entries]
    return tuple(item for item in found if item)


def _priority(value) -> int:
    if isinstance(value, bool):
        return DEFAULT_PRIORITY
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    return DEFAULT_PRIORITY


def _override(value) -> str | None:
    """The decision id of ``plan_override``: ``DEC-899`` or ``DEC-899 — the reason``; None without one."""
    text = value if isinstance(value, str) else (wait_id(value) if isinstance(value, dict) else None)
    match = _DEC.match(text.strip()) if isinstance(text, str) else None
    return match.group(0) if match else None


def from_front(front: dict, path: str) -> Ticket:
    stem = Path(path).stem
    return Ticket(
        id=str(front.get("id") or stem).strip(),
        wbs=str(front.get("wbs_id") or front.get("external-ref") or "").strip(),
        status=str(front.get("status") or "").strip(),
        priority=_priority(front.get("priority")),
        writes=tuple(_strings(front.get("allowed_paths"))),
        reads=_declared(front, "reads"),
        needs=_declared(front, "needs"),
        waits_on=_waits(front.get("waits_on")),
        depends_on=tuple(_strings(front.get("depends_on"))),
        deps=tuple(_strings(front.get("deps"))),
        override=_override(front.get("plan_override")),
        path=path,
    )


def load(root: Path) -> dict[str, Ticket]:
    """Every ticket of the store by id, read now; ``PlanError`` when the store or a ticket cannot be read."""
    folder = Path(root) / TICKETS_DIR
    if not folder.is_dir():
        raise PlanError(f"no ticket store: {TICKETS_DIR}/ is not a folder under {root}")
    tickets: dict[str, Ticket] = {}
    for file in sorted(folder.glob("*.md")):
        rel = f"{TICKETS_DIR}/{file.name}"
        try:
            front = parse(file.read_text(encoding="utf-8"), rstrip=True)
        except (OSError, UnicodeDecodeError) as error:
            raise PlanError(f"{rel} cannot be read: {error}") from None
        except FrontmatterError as error:
            raise PlanError(f"{rel}: its frontmatter cannot be read ({error.kind})") from None
        if front is None:
            continue  # a file of the folder that is not a ticket
        ticket = from_front(front, rel)
        if ticket.id in tickets:
            raise PlanError(f"{rel}: the ticket id {ticket.id} is also {tickets[ticket.id].path}'s")
        tickets[ticket.id] = ticket
    return tickets


def index(tickets: dict[str, Ticket]) -> dict[str, Ticket]:
    """Each ticket under its id and under its WBS id (an id wins over a WBS id that is the same text)."""
    found = {ticket.wbs: ticket for ticket in tickets.values() if ticket.wbs}
    found.update(tickets)
    return found
