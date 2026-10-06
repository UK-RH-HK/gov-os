"""``gov pause`` as a command module (W1-28, CAP-05, DEC-317). The convention is in ``gov.cli.main``.

- ``gov pause`` sets the freeze flag ``.gov-runtime/freeze``, which the guard reads; it writes no record (DEC-367).
  The flag's first line is ``FROZEN <who> <when>`` (DEC-402, DEC-404): an empty file there is no freeze.
- ``gov pause --off`` clears it, for the owner in person only (DEC-409, ``lift``).
- ``gov pause --cancel-agents`` sets the flag and releases every claim lock, with one record commit per released
  ticket (DEC-357, DEC-368, DEC-375). It stops no process and changes no status.
- ``gov pause --rollback <ticket>`` sets the flag first (DEC-378), then reverts the ticket's commits, newest first,
  and records it by one commit to the ticket file (DEC-366, DEC-367). Its reverts write where those commits wrote,
  the flag's path included, so the flag is set again when the rollback has ended, with success or with an error.

The caller is ``GOV_ROLE`` (DEC-365): the orchestrator may set the freeze, every other role is refused, and with
``GOV_ROLE`` unset the caller is the owner. ``--role`` is not read. An unset ``GOV_ROLE`` does not make the owner
for the lift (DEC-409): no Claude Code session among the ancestor processes, a terminal on input and output, and a
one-time code typed back. Nothing outside the process reaches those checks: ``run`` calls ``lift(root)``.
"""

from __future__ import annotations

import os
import random
import re
import subprocess
import tempfile
import time
from pathlib import Path

ACT_PATHS = (".gov-runtime/freeze", ".tickets/**")
OWNER, ORCHESTRATOR = "owner", "orchestrator"
FIRST_PROCESSES = ("init", "systemd")  # the ``comm`` of a system's first process; a sandbox's own is another
_VERSION_FILE = "claude/versions/"     # where the CLI's binary lives, under the version as its name
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


def _freeze(root: Path, flag: Path, caller: str) -> None:
    """Write the marked flag (DEC-402, DEC-404): a temporary file renamed over the flag's path, never through a link
    there, then read back with the guard's own reader."""
    from gov.cli.errors import GovError
    from gov.guard.decide import FREEZE_FLAG, FREEZE_MARKER, freeze_state

    line, tmp = f"{FREEZE_MARKER.decode()} {caller} {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n", None
    try:
        flag.parent.mkdir(parents=True, exist_ok=True)
        handle, tmp = tempfile.mkstemp(dir=flag.parent, prefix="freeze.")
        with os.fdopen(handle, "w", encoding="utf-8") as file:
            file.write(line)
        os.replace(tmp, flag)
    except OSError as error:
        if tmp:
            Path(tmp).unlink(missing_ok=True)
        raise GovError("PAUSE_NOT_SET", f"{FREEZE_FLAG} was not written: {error}", {"path": FREEZE_FLAG})
    if freeze_state(str(root)) != "frozen":
        raise GovError("PAUSE_NOT_SET", f"{FREEZE_FLAG} was written and the guard does not read it as a freeze",
                       {"path": FREEZE_FLAG})


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


def read_ancestry() -> list[dict]:
    """The process chain from ``/proc``: this process first, the system's first process last.

    Each process is ``{"pid", "ppid", "comm", "exe", "cmdline"}``; ``exe`` is None when its link cannot be read. A
    process that cannot be read ends the chain there, and ``lift`` refuses a chain that does not reach process 1.
    """
    chain, pid = [], os.getpid()
    while pid > 0 and len(chain) < 1024:
        try:
            stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8", errors="replace")
            words = Path(f"/proc/{pid}/cmdline").read_bytes().decode("utf-8", "replace").split("\0")
            parent = int(stat.rpartition(")")[2].split()[1])
        except (OSError, ValueError, IndexError):
            break
        try:
            exe = os.readlink(f"/proc/{pid}/exe")
        except OSError:
            exe = None
        chain.append({"pid": pid, "ppid": parent, "comm": stat.partition("(")[2].rpartition(")")[0], "exe": exe,
                      "cmdline": words[:-1] if words[-1] == "" else words})
        pid = parent
    return chain


def _is_session(process: dict) -> bool:
    """A Claude Code session, by one sign: its ``comm``, or a path part of its ``exe``, of the first word of its
    command line or of the first word after it that is no option (the script an interpreter runs)."""
    words = process["cmdline"]
    named = [process["exe"], words[0], next((word for word in words[1:] if not word.startswith("-")), None)]
    return process["comm"] == "claude" or any(
        os.path.basename(word) == "claude" or _VERSION_FILE in word
        or any("claude-code" in part or part == "@anthropic-ai" for part in word.split("/"))
        for word in named if word)


def _caller_refusal(ancestry: list[dict]) -> tuple[str, str] | None:
    """Why this ancestry does not lift (DEC-409, rule 1), or None: a chain read whole up to a system's first
    process, with no Claude Code session in it."""
    unreadable = ("ancestry", "the ancestor processes cannot be read up to the system's first process, so the "
                  "caller is not known to be the owner in person: the freeze is as it was")
    try:
        sessions = [process["pid"] for process in ancestry if process["comm"] and process["cmdline"]
                    and _is_session(process)]
        if sessions:
            return "session", (f"a Claude Code session is among the ancestor processes (process {sessions[0]}): "
                               "only the owner lifts a freeze, in person from a plain terminal (DEC-409)")
        last = ancestry[-1]
        whole = (last["pid"] == 1 and last["ppid"] == 0 and last["comm"] in FIRST_PROCESSES
                 and all(isinstance(process["comm"], str) and process["comm"] and process["cmdline"]
                         for process in ancestry)
                 and all(process["ppid"] == parent["pid"] for process, parent in zip(ancestry, ancestry[1:])))
    except Exception:  # a chain that is not in the form above is not read
        return unreadable
    return None if whole else unreadable


def lift(root: Path, ancestry: list[dict] | None = None, terminal: tuple[int, int] | None = None) -> dict:
    """Lift the freeze as the owner in person (DEC-409): the ancestry, the terminal, the code, then the flag.

    ``ancestry`` and ``terminal`` are the seam of the tests: ``run`` passes neither, so the chain is read from
    ``/proc`` and the terminal is ``(0, 1)``. Both descriptors are asked ``os.isatty`` here whatever is passed. The
    code comes from the system's random source and goes to the terminal only; one line is read, once.
    """
    from gov.cli.errors import GovError
    from gov.guard.decide import FREEZE_FLAG

    def refused(reason: str, message: str) -> GovError:
        return GovError("PAUSE_REFUSED", message, {"reason": reason})

    refusal = _caller_refusal(read_ancestry() if ancestry is None else ancestry)
    if refusal:
        raise refused(*refusal)
    no_terminal = refused("terminal", "lifting a freeze needs an interactive terminal: its input and its output "
                          "are not both a TTY, and the freeze is as it was (DEC-409)")
    try:
        source, shown = terminal or (0, 1)
        if not (os.isatty(source) and os.isatty(shown)):
            raise no_terminal
        code, typed = f"LIFT-{random.SystemRandom().randrange(10000):04d}", b""
        os.write(shown, f"type {code} to lift the freeze: ".encode())
        while not typed.endswith(b"\n") and len(typed) < 64:
            chunk = os.read(source, 64)
            if not chunk:
                break
            typed += chunk
    except (OSError, TypeError, ValueError):
        raise no_terminal from None
    if typed.decode("utf-8", "replace").strip() != code:
        raise refused("code", "the code typed back is not the code shown: the freeze is as it was, and the next "
                      "run shows a new code (DEC-409)")
    flag = Path(root) / FREEZE_FLAG
    if flag.parent.is_symlink():  # DEC-404: nothing is removed through it, and the owner repairs the folder
        raise _linked(flag)
    try:
        flag.unlink(missing_ok=True)
    except OSError as error:  # a directory at the path: the guard reads it as a freeze
        raise GovError("PAUSE_NOT_LIFTED", f"{FREEZE_FLAG} cannot be removed, and the tree stays frozen: {error}",
                       {"path": FREEZE_FLAG})
    return {"paused": False}


def _linked(flag: Path):
    from gov.cli.errors import GovError

    return GovError("PAUSE_RUNTIME_LINKED", f"{flag.parent.name} is a symbolic link: nothing is written through "
                    "it, and the pause is as it was", {"path": flag.parent.name})


def run(root: Path, args, config: dict) -> dict:
    from gov.cli.errors import GovError
    from gov.guard.decide import FREEZE_FLAG

    role = os.environ.get("GOV_ROLE")  # DEC-365: the caller; unset, the owner
    if role is not None and (role != ORCHESTRATOR or args.off):
        raise GovError("PAUSE_REFUSED", "only the owner and the orchestrator pause, and only the owner in person "
                       "(GOV_ROLE unset, a plain terminal) lifts a pause", {"caller": role})
    if args.off:
        return lift(root)  # DEC-409: nothing from outside the process fills its other parameters
    root, caller = Path(root), role or OWNER
    flag = root / FREEZE_FLAG
    if flag.parent.is_symlink():  # DEC-404: nothing is written through it, and the owner repairs the folder
        raise _linked(flag)
    _freeze(root, flag, caller)
    if args.cancel_agents:
        return {"paused": True, "cancelled": _cancel(root, caller)}
    if not args.rollback:
        return {"paused": True}
    try:
        return {"paused": True, **_rollback(root, args.rollback, caller)}
    finally:  # DEC-378: a revert or the reset may have overwritten or removed the flag, so it is set again
        _freeze(root, flag, caller)
