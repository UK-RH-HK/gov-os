"""``gov launch``'s check of a lead against the plan (W2-136 S9, DEC-1088 (5)(a), DEC-899).

A lead (a session started as ``GOV_ROLE=orchestrator`` with a ``GOV_TICKET``) is refused for a ticket that is not in
the approved ready list's batches, or whose waits (``depends_on``, ``needs``, ``waits_on``) are not met when checked
now against the current tickets. The refusal names what the ticket waits for: the ticket, the path or the id. A
``plan_override: <DEC-id>`` on the ticket admits it anyway, and the launcher writes the override in the machine-wide
launch log and on standard error (W2-20 S21, review F4).

**The current plan (W2-20 S21, review F2):** the tickets and the approved ready list are the main tree's (the main
worktree of the launch tree's repository, ``gov.launch.store.main_root``), never a lead worktree's own copies, which
can be stale. ``GOV_PLAN_READY`` names the list the dispatcher keeps; a relative value is read against the main tree.

The launcher calls ``check_lead`` once, at its argument checks; nothing else calls it.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from gov.launch.store import main_root
from gov.plan.derive import Context, hard_waits, unknown_waits
from gov.plan.tickets import PlanError, index, load

READY_ENV = "GOV_PLAN_READY"  # the approved ready list, when the project keeps it elsewhere
READY_REL = "governance/project/orchestration/ready.txt"


@dataclass(frozen=True)
class LeadCheck:
    admitted: bool
    reason: str
    override: str | None = None  # the decision id of the plan_override that admitted the lead

    def __iter__(self):  # admitted, reason, override = check_lead(...)
        return iter((self.admitted, self.reason, self.override))

    def __getitem__(self, name):
        return tuple(self)[name] if isinstance(name, int) else getattr(self, name)

    def get(self, name: str, default=None):
        return getattr(self, name, default)

    def __bool__(self) -> bool:
        return self.admitted


def ready_path(root: Path) -> Path:
    """Where the approved ready list is: ``$GOV_PLAN_READY``, else ``READY_REL``; a relative path is read against the
    main tree of ``root``'s repository (P-8), never a worktree's copy."""
    named = os.environ.get(READY_ENV, "").strip()
    path = Path(named) if named else Path(READY_REL)
    return path if path.is_absolute() else main_root(Path(root)) / path


def ready_entries(ready) -> set[str] | None:
    """The ids and WBS ids the ready list names (its ``# batch k`` headers and comments left out); None when the
    file cannot be read. ``ready`` is the file, the list's text, its lines, or the ids themselves."""
    if isinstance(ready, (set, frozenset, list, tuple)):
        items = [str(item) for item in ready]
        return ready_entries("\n".join(items) + "\n") | {item.strip() for item in items if " " not in item.strip()}
    if isinstance(ready, str) and "\n" in ready:
        text = ready
    else:
        try:
            text = Path(ready).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, TypeError):
            return None
    names: set[str] = set()
    for line in text.splitlines():
        fields = line.split("#", 1)[0].split()
        if len(fields) >= 2:
            names.update(fields[:2])  # <W2> <ticket id> <brief> <log>
    return names


def _named(waits, unknown, by: dict) -> str:
    def wbs(name: str) -> str:
        ticket = by.get(name)
        return f" [{ticket.wbs}]" if ticket is not None and ticket.wbs and ticket.wbs != name else ""
    parts = [f"{w.on} ({w.code} {w.what}){wbs(w.on)}" for w in waits]
    parts += [f"{wid} (UNKNOWN_WAIT: it names nothing)" for wid in unknown]
    return "; ".join(parts)


def check_lead(root, ticket_id: str, *, ready=None) -> LeadCheck:
    """Whether a lead for ``ticket_id`` may start now, from the main tree's current tickets. ``ready`` is the
    approved ready list (a file, or its ids); None reads ``ready_path(root)``. Nothing is written."""
    root = main_root(Path(root))
    try:
        tickets = load(root)
    except PlanError as error:
        return LeadCheck(False, f"the plan cannot be checked: {error}")
    ticket = index(tickets).get(ticket_id)
    if ticket is None:
        return LeadCheck(False, f"unknown ticket '{ticket_id}': the plan cannot admit it")
    ctx = Context(root, tickets)
    waits, unknown = hard_waits(ticket, ctx), unknown_waits(ticket, ctx)
    source = ready if ready is not None else ready_path(root)
    entries = ready_entries(source)
    faults = []
    if entries is None:
        faults.append(f"no approved ready list can be read at {source}")
    elif ticket.id not in entries and not (ticket.wbs and ticket.wbs in entries):
        faults.append(f"ticket {ticket.id} is not in the approved ready list's batches ({source})")
    if waits or unknown:
        faults.append(f"ticket {ticket.id} waits for {_named(waits, unknown, ctx.by)}")
    if not faults:
        return LeadCheck(True, f"ticket {ticket.id} is in the approved batches and its waits are met")
    if ticket.override:
        return LeadCheck(True, f"plan_override {ticket.override} admits ticket {ticket.id} despite: "
                               + "; ".join(faults), ticket.override)
    return LeadCheck(False, "; ".join(faults))
