"""Whether a ready-list entry may start (S2, S7): the checks in their order, the first failure is the reason.

``reason(entry, context)`` returns None for an entry that passes every check of its own, else the text the status
names it with. The checks that are the machine's, not the entry's (the gate, the disk, ``max_leads``, the stagger, the
room for the peak), are the pass's (``gov.dispatch.run``). Every external command is the context's ``runner``'s and so
limited by ``command_timeout_s``: a hung one is a named failed check of the entry.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from gov.dispatch import state as states
from gov.dispatch.config import Config
from gov.dispatch.shell import CommandFailed, Runner

SLOT = re.compile(r"\{[A-Z][A-Z0-9_]*\}")
TICKETS = ".tickets"
REVIEW_LINE = re.compile(r"^\s*run:\s*review\s*$", re.M)
OPEN_ROUNDS = 2  # a third review round is never started: two probe records are two rounds


@dataclass
class Context:
    root: Path
    conf: Config
    state: states.State
    runner: Runner
    started_logs: set = field(default_factory=set)
    running: dict = field(default_factory=dict)       # ticket -> pid, from the processes
    pending: set = field(default_factory=set)         # tickets started lately that show no process yet
    unread: set = field(default_factory=set)          # W2 ids with an item in inbox/

    def worktree(self, w2: str) -> Path:
        return Path(self.root) / self.conf.worktrees_root / w2

    def brief(self, name: str) -> Path:
        return Path(self.root) / self.conf.briefs_dir / name


def _status_of(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        key, _, value = line.partition(":")
        if key.strip() == "status":
            return value.strip().strip("'\"")
    return None


def _claim(entry: states.Entry, ctx: Context) -> str | None:
    path = f"{TICKETS}/{entry.ticket}.md"
    branch = ctx.conf.integration_branch
    tip = ctx.runner.git(ctx.root, "show", f"{branch}:{path}")
    if tip.code != 0:
        return f"claim not committed: {path} is not on the tip of {branch}"
    if _status_of(tip.out) != "in_progress":
        return f"claim not committed: {path} on {branch} is not status: in_progress"
    worktree = ctx.worktree(entry.w2)
    if not worktree.is_dir():
        return f"claim not committed in the worktree: {worktree} does not exist"
    head = ctx.runner.git(worktree, "show", f"HEAD:{path}")
    if head.code != 0 or _status_of(head.out) != "in_progress":
        return f"claim not committed in the worktree: {path} is not status: in_progress at its HEAD"
    return None


def _clean(entry: states.Entry, ctx: Context) -> str | None:
    done = ctx.runner.git(ctx.worktree(entry.w2), "status", "--porcelain", "--untracked-files=no")
    if done.code != 0:
        return f"worktree not clean: git status failed ({done.err.strip().splitlines()[-1:] or done.code})"
    changed = [line for line in done.out.splitlines() if line.strip()]
    return f"worktree not clean: {len(changed)} tracked change(s), e.g. {changed[0].strip()}" if changed else None


def _brief(entry: states.Entry, ctx: Context) -> tuple[str | None, str]:
    path = ctx.brief(entry.brief)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return f"brief incomplete: {path} cannot be read ({error.__class__.__name__})", ""
    if not text.strip():
        return f"brief incomplete: {path} is empty", text
    if "@@" in text:
        return f"brief incomplete: {path} holds @@", text
    slot = SLOT.search(text)
    if slot:
        return f"brief incomplete: {path} holds the unfilled slot {slot.group(0)}", text
    return None, text


def _review(entry: states.Entry, ctx: Context, text: str) -> str | None:
    if not REVIEW_LINE.search(text):
        return None
    folder = ctx.worktree(entry.w2) / ctx.conf.probes_dir / entry.ticket
    try:
        rounds = len([p for p in folder.glob("*.md") if p.is_file()]) if folder.is_dir() else 0
    except OSError:
        rounds = 0
    if rounds < OPEN_ROUNDS:
        return None
    item = ctx.state.write_item(f"{entry.log}.owner.txt", [
        f"log: {entry.log}", f"W2: {entry.w2}", "status: owner", "kind: owner", f"ticket: {entry.ticket}",
        f"time: {states.stamp()}",
        f"The review launch of {entry.ticket} is not started: its probe records already show {rounds} review rounds "
        f"({folder}); a third round is the owner's to allow."])
    return (f"review refused: {rounds} probe records, a third round is the owner's "
            f"({'owner item written' if item else 'owner item already raised'})")


def reason(entry: states.Entry, ctx: Context) -> str | None:
    if entry.problem:
        return entry.problem
    try:
        if entry.log in ctx.started_logs:
            return "already started (its log name is in started.txt)"
        for check in (_claim, _clean):
            why = check(entry, ctx)
            if why:
                return why
        why, text = _brief(entry, ctx)
        if why:
            return why
        if entry.ticket in ctx.running:
            return f"ticket running (process {ctx.running[entry.ticket]})"
        if entry.ticket in ctx.pending:
            return "ticket running (started a moment ago, its process not seen yet)"
        if entry.w2 in ctx.unread:
            return "unread return: an item of this W2 is in the inbox"
        return _review(entry, ctx, text)
    except CommandFailed as failure:
        return f"check failed: {failure}"
