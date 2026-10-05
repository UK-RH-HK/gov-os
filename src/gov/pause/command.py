"""``gov pause`` as a command module (W1-28, CAP-05, DEC-317). The convention is in ``gov.cli.main``.

- ``gov pause`` sets the freeze flag ``.gov-runtime/freeze``, which the guard reads; it writes no record (DEC-367).
- ``gov pause --off`` clears it.
- ``gov pause --cancel-agents`` sets the flag and releases every claim lock, with one record commit per released
  ticket (DEC-357, DEC-368, DEC-375). It stops no process and changes no status.
- ``gov pause --rollback <ticket>`` sets the flag first (DEC-378), then reverts the ticket's commits, newest first,
  and records it by one commit to the ticket file (DEC-366, DEC-367). Its reverts write where those commits wrote.

The caller is ``GOV_ROLE`` (DEC-365): the orchestrator may set the freeze, every other role is refused, and with
``GOV_ROLE`` unset the caller is the owner, who alone lifts it. ``--role`` is not read.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ACT_PATHS = (".gov-runtime/freeze", ".tickets/**")
OWNER, ORCHESTRATOR = "owner", "orchestrator"
MERGE_NOTE = "a merge commit is skipped: its own conflict resolutions stay (DEC-366)"
_LOG_FORMAT = ("--format=%H%x1f%P%x1f%cs%x1f%(trailers:key=Task,valueonly,unfold)%x1f"
               "%(trailers:key=Reverts-Task,valueonly,unfold)%x1f%B%x1e")


def add_arguments(parser) -> None:
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--off", action="store_true", help="lift the freeze (the owner only)")
    mode.add_argument("--cancel-agents", action="store_true", help="freeze, and release every claim")
    mode.add_argument("--rollback", metavar="<ticket>", help="freeze, and revert the commits of the ticket")


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def _record(root: Path, ticket: str, caller: str, line: str) -> None:
    """Append ``line`` to the ticket file and commit that file alone (DEC-367)."""
    from gov.cli.errors import GovError
    from gov.tasks.tickets import TICKETS_REL

    rel = f"{TICKETS_REL}/{ticket}.md"
    text = (root / rel).read_text(encoding="utf-8")
    (root / rel).write_text(f"{text}{'' if text.endswith(chr(10)) else chr(10)}\n- {line}\n", encoding="utf-8")
    done = _git(root, "commit", "-m", f"gov pause: {line}", "--trailer", f"Task: {ticket}", "--trailer",
                f"Role: {caller}", "--trailer", f"Reverts-Task: {ticket}", "--", rel)
    if done.returncode != 0:
        raise GovError("PAUSE_RECORD_FAILED", f"the record of {ticket} was not committed: {done.stderr.strip()}",
                       {"ticket": ticket})


def _cancel(root: Path, caller: str) -> list[dict]:
    from gov.tasks.claims import CLAIMS_REL, holder, release

    folder, cancelled = root / CLAIMS_REL, []
    for ticket in sorted(os.listdir(folder)) if folder.is_dir() else []:
        entry = release(root, ticket, holder(root, ticket))
        _record(root, ticket, caller, f"--cancel-agents by {caller} released the claim of session {entry['holder']}")
        cancelled.append(entry)
    return cancelled


def _rollback(root: Path, ticket: str, caller: str) -> dict:
    from gov.cli.errors import GovError
    from gov.store.loader import TRAILER_RULE_DATE
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    if frontmatter(root / TICKETS_REL / f"{ticket}.md") is None:
        raise GovError("TICKET_NOT_FOUND", f"{ticket}: no such ticket", {"ticket": ticket})
    status = _git(root, "status", "--porcelain", "--untracked-files=no")
    log = _git(root, "log", "--topo-order", _LOG_FORMAT)
    if status.returncode != 0 or log.returncode != 0 or status.stdout.strip():
        raise GovError("PAUSE_DIRTY_TREE", "the working tree has uncommitted changes, or git cannot read it: "
                       "nothing is reverted", {"ticket": ticket})
    mine, merges, undone = [], [], set()
    for entry in log.stdout.split("\x1e")[:-1]:
        commit, parents, date, final_block, reverts, message = entry.strip("\n").split("\x1f")
        if ticket in reverts.split():  # a revert or a record of an earlier rollback or cancel: never reverted itself
            undone.update(re.findall(r"^This reverts commit ([0-9a-f]+)", message, re.MULTILINE))
            continue
        # DEC-182, as gov.store reads a commit's ticket: the final block, or the whole message before the rule's date
        tasks = final_block if date >= TRAILER_RULE_DATE else "\n".join(re.findall(r"^Task:[ \t]*(.*)$", message, re.M))
        if ticket in re.split(r"[,\s]+", tasks):
            (merges if len(parents.split()) > 1 else mine).append(commit)
    start, reverted = _git(root, "rev-parse", "HEAD").stdout.strip(), [c for c in mine if c not in undone]
    for commit in reverted:  # newest first: the order of history
        done = _git(root, "revert", "--no-edit", "--no-commit", commit)
        if done.returncode == 0:
            done = _git(root, "commit", "--no-edit", "--trailer", f"Role: {caller}", "--trailer",
                        f"Reverts-Task: {ticket}")
        if done.returncode != 0:
            _git(root, "revert", "--quit")
            _git(root, "reset", "--hard", start)
            raise GovError("PAUSE_ROLLBACK_ABORTED", f"the revert of {commit} failed, and nothing is reverted: "
                           f"{(done.stderr or done.stdout).strip()}", {"ticket": ticket, "commit": commit})
    if reverted:
        _record(root, ticket, caller, f"--rollback by {caller} reverted {', '.join(reverted)}")
    return {"ticket": ticket, "reverted": reverted, "skipped_merges": merges, **({"note": MERGE_NOTE} if merges else {})}


def run(root: Path, args, config: dict) -> dict:
    from gov.cli.errors import GovError
    from gov.guard.decide import FREEZE_FLAG

    role = os.environ.get("GOV_ROLE")  # DEC-365: the caller; unset, the owner
    if role is not None and (role != ORCHESTRATOR or args.off):
        raise GovError("PAUSE_REFUSED", "only the owner and the orchestrator pause, and only the owner (GOV_ROLE "
                       "unset) lifts a pause", {"caller": role})
    root, caller = Path(root), role or OWNER
    flag = root / FREEZE_FLAG
    if args.off:
        flag.unlink(missing_ok=True)
        return {"paused": False}
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.touch()
    if args.cancel_agents:
        return {"paused": True, "cancelled": _cancel(root, caller)}
    return {"paused": True, **(_rollback(root, args.rollback, caller) if args.rollback else {})}
