"""Returns (S4, S8, S9; DEC-1014): every wake the caller gets is an inbox item a pass writes.

- A finished session (its ``logs/<log name>.exit`` exists) becomes ``inbox/<log name>.return.txt``, once: an item of that
  name in ``inbox/`` or ``inbox/read/`` is the record that it was written. Its ``status:`` is the ``status:`` line the log
  holds (the last), else ``exit <code>``. Every commit id (7 to 40 hex) on its ``commits:`` lines and every path on its
  ``files_changed:`` lines is resolved against git in the ticket's worktree; what does not resolve is named on one
  ``unresolved:`` line (none: no such line).
- A start that never ran (in ``started.txt`` past ``never_ran_after_s``, no process of its ticket, no ``.exit``) becomes
  ``inbox/<log name>.never-ran.txt``, once, and a line of ``never-ran.txt``.
- An item unread (still in ``inbox/``) past ``unread_escalate_s`` runs ``notifier_command`` once, the item's path its
  last argument; ``escalated.txt`` records it before the command runs, so it is never raised twice.
"""

from __future__ import annotations

import re
from pathlib import Path

from gov.dispatch import state as states
from gov.dispatch.config import Config, ConfigError
from gov.dispatch.shell import CommandFailed, Runner

LABEL = re.compile(r"^\s*[-*]?\s*\**\s*(status|commits|files_changed)\s*\**\s*:\s*\**\s*(.*?)\s*$", re.I)
LABELLED = re.compile(r"^\s*[-*]?\s*\**\s*[a-z_]+\s*\**\s*:")
BULLET = re.compile(r"^\s+[-*]?\s*(.+?)\s*$")
HEX = re.compile(r"\b[0-9a-f]{7,40}\b")
TAIL_BYTES = 256 * 1024
MAX_NAMED = 200
NOT_PATHS = {"none", "n/a", "-", "and", "the", "(none)", "(see", "tbd"}


def parse(text: str) -> dict:
    """The last ``status:``, ``commits:`` and ``files_changed:`` of a return (a list the label opens runs on over the
    indented or bulleted lines that follow it)."""
    found, lines = {}, text.splitlines()
    for number, line in enumerate(lines):
        match = LABEL.match(line)
        if not match:
            continue
        label, value = match.group(1).lower(), match.group(2)
        more = []
        if label != "status":
            for follow in lines[number + 1:]:
                if not follow.strip() or LABELLED.match(follow) and not follow.lstrip().startswith(("-", "*")):
                    break
                bullet = BULLET.match(follow)
                if not bullet:
                    break
                more.append(bullet.group(1))
        found[label] = (value, more)
    return found


def commit_ids(value: str, more: list[str]) -> list[str]:
    ids = []
    for text in [value, *more]:
        for token in HEX.findall(text):
            if (any(c.isdigit() for c in token) or len(token) >= 12) and token not in ids:
                ids.append(token)
    return ids[:MAX_NAMED]


def file_paths(value: str, more: list[str]) -> list[str]:
    paths = []
    for part in [p for p in value.split(",") if p.strip()] + [m.split(",")[0] for m in more]:
        words = part.strip().strip("`'\"[]").split()
        token = words[0].strip("`'\"[]();,") if words else ""
        if token.startswith("./"):
            token = token[2:]
        if token and token.lower() not in NOT_PATHS and not token.startswith("(") and token not in paths:
            paths.append(token)
    return paths[:MAX_NAMED]


def unresolved(runner: Runner, folder: Path, ids: list[str], paths: list[str]) -> list[str]:
    """What the return names that git (in ``folder``) does not know."""
    missing = []
    for commit in ids:
        if runner.git(folder, "cat-file", "-e", f"{commit}^{{commit}}").code != 0:
            missing.append(commit)
    for path in paths:
        if path.startswith("/"):
            if not Path(path).exists():
                missing.append(path)
        elif runner.git(folder, "cat-file", "-e", f"HEAD:{path}").code != 0 and not (folder / path).exists() \
                and not runner.git(folder, "log", "-1", "--format=%h", "--", path).out.strip():
            missing.append(path)
    return missing


def _text(path: Path) -> str:
    try:
        with open(path, "rb") as handle:
            handle.seek(0, 2)
            handle.seek(max(0, handle.tell() - TAIL_BYTES))
            return handle.read().decode("utf-8", "replace")
    except OSError:
        return ""


def finished(ctx, problems: list[str]) -> list[str]:
    """One item for each finished session that has none; the names of the items written."""
    written = []
    for start in ctx.state.started():
        exit_file = ctx.state.exit_file(start.log)
        if not exit_file.exists():
            continue
        name = f"{start.log}.return.txt"
        if (ctx.state.inbox / name).exists() or (ctx.state.read / name).exists():
            continue
        code = _text(exit_file).strip() or "unknown"
        log = parse(_text(ctx.state.logs / start.log))
        status = log["status"][0] if log.get("status") and log["status"][0] else f"exit {code}"
        ids = commit_ids(*log["commits"]) if "commits" in log else []
        paths = file_paths(*log["files_changed"]) if "files_changed" in log else []
        lines = [f"log: {start.log}", f"W2: {start.w2}", f"status: {status[:120]}", "kind: return",
                 f"ticket: {start.ticket}", f"exit: {code}", f"time: {states.stamp()}"]
        if "commits" in log:
            lines.append("commits: " + " ".join(ids))
        if "files_changed" in log:
            lines.append("files_changed: " + " ".join(paths))
        if ids or paths:
            folder = ctx.root / ctx.conf.worktrees_root / start.w2
            folder = folder if folder.is_dir() else ctx.root
            try:
                missing = unresolved(ctx.runner, folder, ids, paths)
            except CommandFailed as failure:
                missing = ids + paths
                problems.append(f"{start.log}: its commits and paths could not be checked: {failure}")
            if missing:
                lines.append("unresolved: " + " ".join(missing))
        if ctx.state.write_item(name, lines):
            written.append(name)
    return written


def never_ran(ctx, now) -> list[str]:
    written = []
    running = ctx.running
    for start in ctx.state.started():
        if ctx.state.exit_file(start.log).exists() or start.ticket in running:
            continue
        if (now - start.at).total_seconds() <= ctx.conf.never_ran_after_s:
            continue
        name = f"{start.log}.never-ran.txt"
        item = ctx.state.write_item(name, [
            f"log: {start.log}", f"W2: {start.w2}", "status: never-ran", "kind: never-ran", f"ticket: {start.ticket}",
            f"time: {states.stamp(now)}",
            f"The start of {start.log} (at {states.stamp(start.at)}) has no process of its ticket and no exit file "
            f"after {ctx.conf.never_ran_after_s:g} s: it never ran."])
        if item:
            ctx.state.append("never-ran.txt", f"{start.log} {states.stamp(now)} {start.w2} {start.ticket}")
            written.append(name)
    return written


def escalate(ctx, conf: Config, problems: list[str]) -> list[str]:
    """Run the notifier once for each item unread past ``unread_escalate_s``."""
    done = {line.split()[0] for line in ctx.state.lines("escalated.txt")}
    raised = []
    for item in ctx.state.items():
        if item.age_s <= conf.unread_escalate_s or item.path.name in done:
            continue
        if conf.notifier_command is None:
            raise ConfigError(f"notifier_command: needed to escalate {item.path.name}, unread for {item.age_s:.0f} s")
        ctx.state.append("escalated.txt", f"{item.path.name} {states.stamp()}")
        try:
            result = ctx.runner.run([*conf.notifier_command, str(item.path)], cwd=ctx.root)
        except CommandFailed as failure:
            problems.append(f"escalation of {item.path.name}: {failure}")
            continue
        if result.code != 0:
            problems.append(f"escalation of {item.path.name}: the notifier ended with {result.code}")
        raised.append(item.path.name)
    return raised
