"""The checkpoint record: writing one, the resume brief of the latest one, and the watchdog's verdict (W1-25).

A checkpoint is ``docs/checkpoints/<ticket>/CP-<ticket>-<number>.md`` (DEC-320): a markdown record whose
frontmatter conforms to the kernel checkpoint schema (DEC-279). The highest number is the latest. The brief and
the watchdog read that one file and refuse it when a key, an input's version or an input's hash is missing.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from gov.checkpoint.command import EXIT_UNHEALTHY, TRIGGERS
from gov.cli.errors import GovError
from gov.tasks.tickets import TICKETS_REL, frontmatter

CHECKPOINTS_REL = "docs/checkpoints"
STALE, MISSING, INVALID = "CHECKPOINT_STALE", "CHECKPOINT_MISSING", "CHECKPOINT_INVALID"
TICKET_ID = re.compile(r"[A-Za-z0-9]+-[a-z0-9]{4}")  # the kernel's ticket_id grammar (common.schema.json)
NAME = re.compile(r"CP-.+-(\d+)\.md")
HASH = re.compile(r"sha256:[0-9a-f]{64}")


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if done.returncode != 0:  # never a silent "no commits": the watchdog does not pass what it could not count
        raise GovError("GIT_FAILED", f"git {args[0]} failed: {done.stderr.strip()}", {"args": list(args)})
    return done.stdout.strip()


def _ticket_status(root: Path, ticket: str | None) -> str:
    """The status of the ticket; a GovError when ``--ticket`` is missing or names no ticket of the project."""
    if not ticket:
        raise GovError("CHECKPOINT_ARGUMENT_MISSING", "gov checkpoint needs --ticket", {"missing": ["--ticket"]})
    front = frontmatter(root / TICKETS_REL / f"{ticket}.md") if TICKET_ID.fullmatch(ticket) else None
    if front is None:
        raise GovError("TICKET_UNKNOWN", f"{ticket} is not a ticket of this project", {"ticket": ticket})
    return str(front.get("status"))


def _input(root: Path, named: str, ident: str | None = None) -> dict:
    path = (root / named).resolve()
    if not path.is_file() or not path.is_relative_to(root.resolve()):
        raise GovError("CHECKPOINT_INPUT_UNREADABLE", f"{named} is not a file of this project: it has no hash",
                       {"input": named})
    rel = path.relative_to(root.resolve()).as_posix()
    return {"id": ident or rel, "version": _git(root, "log", "-1", "--format=%h", "--", rel) or "untracked",
            "hash": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()}


def _numbered(folder: Path) -> list[tuple[int, Path]]:
    """The checkpoints of a ticket's folder, by number; the last is the latest."""
    return sorted((int(match.group(1)), path) for path in folder.glob("CP-*.md")
                  if (match := NAME.fullmatch(path.name)))


def write(root: Path, ticket: str | None, trigger: str | None, next_action: str | None, inputs: list[str]) -> dict:
    """Write a checkpoint of ``ticket``; everything is checked before anything is written."""
    import yaml

    missing = [name for name, value in (("--ticket", ticket), ("--trigger", trigger), ("--next", next_action))
               if not (value or "").strip()]
    if missing:
        raise GovError("CHECKPOINT_ARGUMENT_MISSING", f"gov checkpoint needs {', '.join(missing)}",
                       {"missing": missing})
    if trigger not in TRIGGERS:
        raise GovError("CHECKPOINT_TRIGGER_UNKNOWN", f"--trigger is one of {', '.join(TRIGGERS)}",
                       {"trigger": trigger})
    status = _ticket_status(root, ticket)
    recorded = [_input(root, f"{TICKETS_REL}/{ticket}.md", ticket), *(_input(root, named) for named in inputs)]
    folder = root / CHECKPOINTS_REL / ticket
    ident = f"CP-{ticket}-{max((number for number, _ in _numbered(folder)), default=0) + 1:04d}"
    front = {"id": ident, "type": "checkpoint", "status": "ACTIVE", "state_class": "NARRATIVE",
             "title": f"{ticket} at {trigger}", "task": ticket, "task_status": status, "trigger": trigger,
             "next_action": next_action, "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "inputs": recorded}
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{ident}.md").write_text(
        "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n\n"
        f"# {ident} — {ticket} at {trigger}\n\n## Next action\n\n{next_action}\n", encoding="utf-8")
    return {"path": f"{CHECKPOINTS_REL}/{ticket}/{ident}.md", "id": ident}


def _latest(root: Path, ticket: str) -> tuple[str, dict]:
    """``(path, frontmatter)`` of the ticket's latest checkpoint; a GovError when there is none or it is incomplete."""
    found = _numbered(root / CHECKPOINTS_REL / ticket) if TICKET_ID.fullmatch(ticket) else []
    if not found:
        raise GovError(MISSING, f"{ticket} has no checkpoint", {"ticket": ticket}, exit_code=EXIT_UNHEALTHY)
    rel = f"{CHECKPOINTS_REL}/{ticket}/{found[-1][1].name}"
    front = frontmatter(found[-1][1]) or {}
    faults = [key for key in ("next_action", "created") if not str(front.get(key) or "").strip()]
    inputs = front.get("inputs")
    if front.get("task") != ticket:
        faults.append("task")
    if not isinstance(inputs, list) or not inputs or not all(
            isinstance(item, dict) and str(item.get("id") or "").strip() and str(item.get("version") or "").strip()
            and HASH.fullmatch(str(item.get("hash"))) for item in inputs):
        faults.append("inputs")
    if faults:
        raise GovError(INVALID, f"{rel} gives no resume brief: {', '.join(faults)} missing or incomplete",
                       {"path": rel, "keys": faults})
    return rel, front


def brief(root: Path, ticket: str) -> dict:
    """What a fresh session needs to resume ``ticket``, from its latest checkpoint alone (DEC-282)."""
    rel, front = _latest(root, ticket)
    return {"ticket": ticket, "next_action": front["next_action"], "inputs": front["inputs"], "path": rel,
            "id": front.get("id"), "trigger": front.get("trigger"), "created": str(front["created"])}


def briefs(root: Path) -> list[dict]:
    """The brief of every ticket that has a checkpoint: the fresh-agent-reconstruction family check."""
    return [brief(root, folder.name) for folder in sorted((root / CHECKPOINTS_REL).glob("*")) if _numbered(folder)]


def watch(root: Path, ticket: str | None, max_age_minutes: float, max_commits: int, max_context: float,
          context_utilisation: float | None) -> dict:
    """Fresh, or a ``CHECKPOINT_STALE`` GovError with its reasons (DEC-280, DEC-281). Only reads."""
    status = _ticket_status(root, ticket)
    rel, front = _latest(root, ticket)
    try:
        created = front["created"]
        if not isinstance(created, datetime):
            created = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
    except ValueError:
        raise GovError(INVALID, f"{rel}: 'created' is not a time", {"path": rel, "keys": ["created"]}) from None
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - created).total_seconds() / 60
    carrier = _git(root, "log", "-1", "--format=%H", "--diff-filter=A", "--", rel)  # empty: not committed yet
    commits = int(_git(root, "rev-list", "--count", f"{carrier}..HEAD")) if carrier else 0
    judged = (("age", age > max_age_minutes), ("commits", commits > max_commits),
              ("context", context_utilisation is not None and context_utilisation > max_context),
              ("ticket-transition", front.get("task_status") != status))
    measured = {"path": rel, "ticket": ticket, "age_minutes": round(age), "commits": commits}
    reasons = [reason for reason, violated in judged if violated]
    if reasons:
        raise GovError(STALE, f"the latest checkpoint of {ticket} is stale: {', '.join(reasons)}",
                       {**measured, "reasons": reasons}, exit_code=EXIT_UNHEALTHY)
    return {"stale": False, **measured}
