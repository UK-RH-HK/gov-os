"""The two checks, each a reminder that blocks at most once a turn: ``waiter`` (S1) and ``idle`` (S2).

Each returns a ``Verdict(decision, case, detail, output)``: ``decision`` is ``block`` or ``through`` (the log's words),
``output`` the one JSON object the hook prints (or None, to say nothing). A block is recorded in the state file before
it is answered, so a failure to record it ends the turn (S4) rather than trapping it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from gov.session_watch import items as items_mod
from gov.session_watch import running, status
from gov.session_watch.config import Config
from gov.session_watch.state import now, record, standby_age

SHOW_MAX = 50


class Verdict(NamedTuple):
    decision: str
    case: str
    detail: str
    output: dict | None


@dataclass
class Context:
    root: Path
    config: Config
    state: dict
    data: dict
    session: str
    turn: str | None
    reason: str | None


def bounded(ctx: Context, check: str) -> bool:
    """Never when ``stop_hook_active`` is set (the turn already continued for a Stop hook), never twice for one turn."""
    last = ctx.state.get(check, {})
    return bool(ctx.data.get("stop_hook_active")) or bool(
        ctx.turn and last.get("session") == ctx.session and last.get("turn") == ctx.turn)


def block(ctx: Context, check: str, reason: str, case: str, detail: str = "") -> Verdict:
    record(ctx.root, ctx.state, check, {"session": ctx.session, "turn": ctx.turn, "at": now()})
    return Verdict("block", case, detail, {"decision": "block", "reason": reason})


def waiter(ctx: Context) -> Verdict:
    config = ctx.config
    if not config.waiter_commands:
        return Verdict("through", "no waiter configured", "", None)
    age = standby_age(ctx.root)
    if age is not None and age < config.standby_max_age_h * 3600:
        return Verdict("through", "a stand-by note is younger than its limit", f"{int(age // 60)} min", None)
    if running.waiter_alive(running.processes(), config.waiter_commands):
        return Verdict("through", "the waiter is running", "", None)
    if bounded(ctx, "waiter"):
        return Verdict("through", "bound: blocked once this turn", "", None)
    reason = ("The inbox waiter is not armed (DEC-1027): returns and landings would sit unread. Arm it now with the Bash "
              f"tool's own background run: `{config.waiter_arm}`; then end the turn.")
    return block(ctx, "waiter", reason, "the inbox waiter is not armed", config.waiter_arm)


def _through(case: str, detail: str, message: str) -> Verdict:
    return Verdict("through", case, detail, {"systemMessage": f"Idle check (DEC-1110): {message}"})


def _list(names: list) -> str:
    return ", ".join(names[:SHOW_MAX]) + (f" and {len(names) - SHOW_MAX} more" if len(names) > SHOW_MAX else "")


def idle(ctx: Context) -> Verdict:
    if ctx.reason:
        return _through("the stated reason", ctx.reason, f"let through on the stated reason, recorded: {ctx.reason}")
    if bounded(ctx, "idle"):
        return Verdict("through", "bound: blocked once this turn", "", None)
    root, config, notes, stale = ctx.root, ctx.config, [], []
    dispatcher = status.read(root, notes)
    procs = running.processes()
    agents, tasks = running.folders(ctx.data)
    live = (running.agents(agents, notes) + running.tasks(tasks, procs, config.waiter_commands, stale)
            + running.pid_files(root, config.pid_globs, procs, stale) + status.running(dispatcher))
    past = f"over the 3 h bound, stale and not counted: {', '.join(stale)}" if stale else ""
    detail = "; ".join(notes + ([past] if past else []))
    tail = f" ({past[0].upper()}{past[1:]}; check it is work.)" if past else ""
    if live:
        return _through(f"running: {len(live)}", "; ".join(live + [detail] if detail else live),
                        f"let through, something of yours is running: {_list(live)}.{tail}")
    wait = status.legitimate_wait(dispatcher)
    if wait:
        return _through(wait, detail, f"nothing running; let through: {wait}.{tail}")
    found = items_mod.load(root, config.items, status.running_tickets(dispatcher))
    unblocked = [i.id for i in found if i.state == "open"]
    if not unblocked:
        owner, other = (sum(1 for i in found if i.state == s) for s in ("owner", "job"))
        case = ("the list of open items is empty" if not owner + other else
                f"every remaining item waits on the owner ({owner})" if not other else
                f"every remaining item waits ({owner} on the owner, {other} on a running job or another wait)")
        return _through(case, detail, f"nothing running; let through: {case}.{tail}")
    seen = "none of the session's agents or tasks, no launched work" + (f"; {past}" if past else "")
    reason = (f"Idle check (DEC-1110 (1), DEC-1109 (3)): nothing of yours is running ({seen}) while {len(unblocked)} "
              f"unblocked item(s) remain: {_list(unblocked)}. Start them now within the machine's limits (or move each "
              "to its true state), then end the turn. If none can move, write one line `IDLE-REASON: <why>` "
              "(recorded in the check's log, shown to the owner) and end the turn.")
    return block(ctx, "idle", reason, f"{len(unblocked)} unblocked",
                 "; ".join([_list(unblocked)] + ([detail] if detail else [])))
