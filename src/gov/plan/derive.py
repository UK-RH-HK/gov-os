"""The dependency map and the launch batches (W2-136 S2, S4, S5, S6; DEC-1088 (3), DEC-235, DEC-899).

- **after (hard):** a ``depends_on`` on an unfinished ticket (``DEPENDS_ON``); a ``waits_on`` on what is not closed or
  not ACCEPTED (``WAITS_ON``);
- **after (read-after-write):** a ticket whose ``needs:`` names a path an unfinished ticket writes
  (``NEEDS_WHAT_WRITES``, naming the path);
- **in series:** tickets whose writes overlap (``WRITES_OVERLAP``), the earlier by the fixed key first;
- **in parallel:** the rest, in one batch;
- ``reads:`` orders nothing: a read that overlaps an unfinished ticket's writes is a ``READS_WIDE`` warning naming the
  waits it would have caused;
- **ties and cycles** by the fixed key (priority, then WBS order, then id), a broken cycle named ``CYCLE_TIEBREAK``;
- **findings:** ``NEEDS_UNDECLARED`` (planned on its own writes alone), ``DEPS_DISAGREE``, ``UNKNOWN_WAIT``;
- ``plan_override: <DEC-id>`` lets a ticket share a batch despite an overlap or a wait, shown as ``OVERRIDE``.

A wait on something outside the plan that is not met (a decision not ACCEPTED, an unfinished ticket not planned)
holds the ticket out of every batch, and with it every ticket that waits for it.
"""

from __future__ import annotations

import heapq
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from gov.plan.overlap import Tracked, patterns_overlap
from gov.plan.tickets import OPEN, PlanError, Ticket, index, load
from gov.util.frontmatter import of_file

DEPENDS_ON, WAITS_ON, NEEDS_WHAT_WRITES = "DEPENDS_ON", "WAITS_ON", "NEEDS_WHAT_WRITES"
WRITES_OVERLAP, CYCLE_TIEBREAK, OVERRIDE = "WRITES_OVERLAP", "CYCLE_TIEBREAK", "OVERRIDE"
READS_WIDE = "READS_WIDE"
NEEDS_UNDECLARED, DEPS_DISAGREE, UNKNOWN_WAIT = "NEEDS_UNDECLARED", "DEPS_DISAGREE", "UNKNOWN_WAIT"
WAIT_CODES = (DEPENDS_ON, WAITS_ON, NEEDS_WHAT_WRITES, WRITES_OVERLAP, CYCLE_TIEBREAK)
FINDING_CODES = (NEEDS_UNDECLARED, DEPS_DISAGREE, UNKNOWN_WAIT)  # a plan with any of them ends with exit code 1
REGISTER = "docs/DECISION_REGISTER.md"
_DEC = re.compile(r"DEC-[0-9]+")
_NOT_DONE = frozenset({"open", "in_progress", "draft", "proposed", "pending", "blocked"})


@dataclass(frozen=True)
class Wait:
    ticket: str   # the ticket that waits
    on: str       # the ticket, decision or record it waits for
    code: str
    what: str     # the path or id the wait is on


@dataclass(frozen=True)
class Note:
    ticket: str
    code: str
    detail: str


@dataclass(frozen=True)
class Override:
    ticket: str
    on: str
    decision: str
    code: str     # what the override set aside
    what: str


@dataclass
class Plan:
    tickets: list[Ticket]
    batches: list[list[str]]
    waits: list[Wait]
    held: list[str] = field(default_factory=list)
    overrides: list[Override] = field(default_factory=list)
    warnings: list[Note] = field(default_factory=list)
    findings: list[Note] = field(default_factory=list)

    @property
    def codes(self) -> list[str]:
        found = {w.code for w in self.waits} | {n.code for n in self.warnings + self.findings}
        found |= {OVERRIDE} if self.overrides else set()
        return sorted(found)


def _natural(text: str) -> tuple:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text) if part)


def key(ticket: Ticket) -> tuple:
    """The fixed order of ties and cycles: priority, then WBS order, then id."""
    return (ticket.priority, 0 if ticket.wbs else 1, _natural(ticket.wbs), ticket.id)


class Context:
    """The current tickets and what a wait can name: a ticket (id or WBS id), a decision, a record path."""

    def __init__(self, root: Path, tickets: dict[str, Ticket]):
        self.root, self.tickets, self.by = Path(root), tickets, index(tickets)
        self.tracked = Tracked(self.root)
        self._register: dict[str, str] | None = None

    def decision(self, dec: str) -> str | None:
        """The register's status word of ``dec``; None when the register has no such entry."""
        if self._register is None:
            self._register = {}
            try:
                text = (self.root / REGISTER).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                text = ""
            entries = re.split(r"^(?=### DEC-[0-9]+\b)", text, flags=re.M)
            for entry in entries:
                head = re.match(r"### (DEC-[0-9]+)\b", entry)
                if head is None:
                    continue
                status = re.search(r"\*\*Status:?\*\*:?\s*([A-Za-z_-]+)", entry)
                self._register.setdefault(head.group(1), status.group(1) if status else "")
        return self._register.get(dec)

    def resolve(self, wid: str) -> tuple[str | None, str, bool]:
        """``(kind, target, met)``: kind ``ticket``, ``decision`` or ``record``, None when it names nothing."""
        ticket = self.by.get(wid)
        if ticket is not None:
            return "ticket", ticket.id, not ticket.unfinished
        if _DEC.fullmatch(wid):
            status = self.decision(wid)
            return (None, wid, False) if status is None else ("decision", wid, status.upper().startswith("ACCEPTED"))
        rel = wid.lstrip("./")
        path = self.root / rel
        if rel and not Path(wid).is_absolute() and ".." not in Path(rel).parts and path.exists():
            front = of_file(path) if path.is_file() else None
            status = str((front or {}).get("status") or "").strip().lower()
            return "record", wid, status not in _NOT_DONE
        return None, wid, False


def _first_overlap(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, str] | None:
    for a in sorted(left):
        for b in sorted(right):
            if patterns_overlap(a, b):
                return a, b
    return None


def hard_waits(ticket: Ticket, ctx: Context) -> list[Wait]:
    """Every wait of ``ticket`` not met on the current tickets: its ``depends_on`` on unfinished tickets, its
    ``waits_on`` not closed or not ACCEPTED, and the unfinished tickets that write a path it needs."""
    waits: list[Wait] = []
    for dep in ticket.depends_on:
        other = ctx.by.get(dep)
        if other is not None and other.unfinished and other.id != ticket.id:
            waits.append(Wait(ticket.id, other.id, DEPENDS_ON, other.id))
    for wid in ticket.waits_on:
        kind, target, met = ctx.resolve(wid)
        if kind is not None and not met and target != ticket.id:
            waits.append(Wait(ticket.id, target, WAITS_ON, wid))
    if ticket.needs:
        for other in sorted(ctx.tickets.values(), key=key):
            if other.id == ticket.id or not other.unfinished:
                continue
            pair = _first_overlap(ticket.needs, other.writes)
            if pair is not None:
                waits.append(Wait(ticket.id, other.id, NEEDS_WHAT_WRITES, ctx.tracked.witness(*pair)))
    return waits


def unknown_waits(ticket: Ticket, ctx: Context) -> list[str]:
    return [wid for wid in ticket.waits_on if ctx.resolve(wid)[0] is None]


def _findings(ticket: Ticket, ctx: Context) -> list[Note]:
    notes = []
    if ticket.needs is None:
        notes.append(Note(ticket.id, NEEDS_UNDECLARED, "no needs: declared; planned as needing only its own writes"))
    if set(ticket.deps) != set(ticket.depends_on):
        notes.append(Note(ticket.id, DEPS_DISAGREE, f"deps [{', '.join(sorted(set(ticket.deps)))}] but depends_on "
                                                    f"[{', '.join(sorted(set(ticket.depends_on)))}]"))
    for wid in unknown_waits(ticket, ctx):
        notes.append(Note(ticket.id, UNKNOWN_WAIT, f"waits_on {wid} names nothing"))
    return notes


def _reads_wide(ticket: Ticket, ctx: Context) -> Note | None:
    if not ticket.reads:
        return None
    hit = [other.id for other in sorted(ctx.tickets.values(), key=key)
           if other.id != ticket.id and other.unfinished and _first_overlap(ticket.reads, other.writes)]
    if not hit:
        return None
    return Note(ticket.id, READS_WIDE, f"reads: would have made it wait for {', '.join(hit)}; it orders nothing")


def _select(tickets: dict[str, Ticket], ctx: Context, selected: list[str] | None) -> list[Ticket]:
    if selected is None:
        return [t for t in tickets.values() if t.status in OPEN]
    chosen: dict[str, Ticket] = {}
    for name in selected:
        ticket = ctx.by.get(name)
        if ticket is None:
            raise PlanError(f"unknown ticket '{name}'")
        chosen[ticket.id] = ticket
    return list(chosen.values())


def make_plan(root: Path, selected: list[str] | None = None) -> Plan:
    """The plan of every open and in-progress ticket (or of ``selected``), from the tickets as they are now."""
    tickets = load(root)
    ctx = Context(root, tickets)
    planned = sorted(_select(tickets, ctx, selected), key=key)
    ids = {t.id for t in planned}
    rank = {t.id: n for n, t in enumerate(planned)}
    findings = [note for t in planned for note in _findings(t, ctx)]
    warnings = [note for t in planned if (note := _reads_wide(t, ctx)) is not None]

    edges: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)  # (u, v): v after u
    outside: dict[str, list[Wait]] = defaultdict(list)
    overrides: list[Override] = []
    for t in planned:
        for wait in hard_waits(t, ctx):
            if t.override:
                overrides.append(Override(t.id, wait.on, t.override, wait.code, wait.what))
            elif wait.on in ids:
                edges[(wait.on, t.id)].append((wait.code, wait.what))
            else:
                outside[t.id].append(wait)
    conflicts: list[tuple[str, str, str]] = []
    for n, a in enumerate(planned):
        for b in planned[n + 1:]:
            pair = _first_overlap(a.writes, b.writes)
            if pair is None:
                continue
            what = ctx.tracked.witness(*pair)
            owner = b if b.override else (a if a.override else None)
            if owner is not None:
                overrides.append(Override(owner.id, (a if owner is b else b).id, owner.override, WRITES_OVERLAP, what))
            else:
                conflicts.append((a.id, b.id, what))

    held = set(outside)
    grew = True
    while grew:
        grew = False
        for (u, v) in edges:
            if u in held and v not in held:
                held.add(v)
                grew = True

    nodes = [t.id for t in planned if t.id not in held]
    live = {(u, v): why for (u, v), why in edges.items() if u not in held and v not in held}
    order, broken = _order(nodes, live, rank)
    position = {tid: n for n, tid in enumerate(order)}

    preds: dict[str, set[str]] = defaultdict(set)
    waits: list[Wait] = []
    for (u, v), why in live.items():
        if (u, v) in broken:
            continue
        preds[v].add(u)
        waits += [Wait(v, u, code, what) for code, what in why]
    for (u, v), why in broken.items():
        waits += [Wait(u, v, CYCLE_TIEBREAK, f"{code} {what}") for code, what in why]
    for a, b, what in conflicts:
        if a in held or b in held:
            continue
        first, second = (a, b) if position[a] < position[b] else (b, a)
        preds[second].add(first)
        waits.append(Wait(second, first, WRITES_OVERLAP, what))
    level: dict[str, int] = {}
    for tid in order:
        level[tid] = 1 + max((level[u] for u in preds[tid]), default=0)
    batches = [[tid for tid in order if level[tid] == k] for k in range(1, max(level.values(), default=0) + 1)]
    batches = [sorted(batch, key=rank.__getitem__) for batch in batches]

    for tid in held:
        waits += outside.get(tid, [])
    for (u, v), why in edges.items():
        if (u, v) not in live:
            waits += [Wait(v, u, code, what) for code, what in why]

    def wait_order(w: Wait) -> tuple:
        return (level.get(w.ticket, len(batches) + 1), rank.get(w.ticket, len(rank)), rank.get(w.on, len(rank)),
                w.on, WAIT_CODES.index(w.code), w.what)

    return Plan(
        tickets=planned,
        batches=batches,
        waits=sorted(set(waits), key=wait_order),
        held=sorted(held, key=rank.__getitem__),
        overrides=sorted(set(overrides), key=lambda o: (rank[o.ticket], rank.get(o.on, len(rank)), o.on, o.code,
                                                        o.what)),
        warnings=warnings,
        findings=findings,
    )


def _order(nodes: list[str], edges: dict[tuple[str, str], list], rank: dict[str, int]):
    """The nodes in an order that respects the edges, ties by the fixed key; a cycle is broken at its first ticket
    by the key, whose remaining incoming edges are returned as broken."""
    incoming: dict[str, set[str]] = defaultdict(set)
    outgoing: dict[str, set[str]] = defaultdict(set)
    for (u, v) in edges:
        incoming[v].add(u)
        outgoing[u].add(v)
    left = set(nodes)
    ready = [rank[n] for n in nodes if not incoming[n]]
    heapq.heapify(ready)
    by_rank = {rank[n]: n for n in nodes}
    order, broken = [], {}
    while left:
        if not ready:  # a cycle: its first ticket by the key goes first
            node = min(left, key=rank.__getitem__)
            for u in sorted(incoming[node], key=rank.__getitem__):
                broken[(u, node)] = edges[(u, node)]
                outgoing[u].discard(node)
            incoming[node] = set()
            heapq.heappush(ready, rank[node])
        node = by_rank[heapq.heappop(ready)]
        if node not in left:
            continue
        left.discard(node)
        order.append(node)
        for v in sorted(outgoing[node], key=rank.__getitem__):
            incoming[v].discard(node)
            if not incoming[v] and v in left:
                heapq.heappush(ready, rank[v])
    return order, broken
