"""What ``gov close`` reads of the repository before it measures (DEC-487, DEC-490): the commits with the
paths they bring, the working tree against its commit, and the commit the record store was built from.

Nothing here judges the ticket's work. What cannot be read is a ``GovError`` (exit code 1): the close could
not measure, and that is neither a finding nor a pass.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from gov.cli.errors import GovError

_ENTRY, _FIELD = "\x1e", "\x1f"
# One process for any number of commits. Paths come NUL-separated and unquoted, without rename detection; a
# first commit lists every path it holds and a merge commit the paths it brings to its first parent.
_LOG = ("-c", "core.quotePath=false", "log", "-z", "--no-renames", "--root", "--diff-merges=first-parent",
        "--name-only", f"--format={_ENTRY}%H{_FIELD}%P{_FIELD}%(trailers:only,unfold){_FIELD}")


def git(root: Path, *args: str, ok: tuple = (0,), code: bool = False):
    """The output of a git command, or its exit code with ``code``; ``GIT_FAILURE`` outside ``ok``."""
    try:
        done = subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True)
    except OSError as e:
        raise GovError("GIT_FAILURE", f"git {args[0]} cannot run: {e}",
                        {"root": str(root)})
    if done.returncode not in ok:
        raise GovError("GIT_FAILURE",
                        f"git {args[0]} failed: {done.stderr.strip()[:200]}",
                        {"root": str(root), "arguments": list(args)})
    return done.returncode if code else done.stdout


def read_commits(root: Path, *revisions: str) -> list[dict]:
    """The commits ``git log <revisions>`` walks, newest first: ``sha``, ``parents``, ``trailers`` (as
    written, by key) and ``paths``. Output of another shape is ``GIT_FAILURE``, never fewer commits."""
    commits = []
    for entry in git(root, *_LOG, *revisions).split(_ENTRY)[1:]:
        fields = entry.split(_FIELD)
        if len(fields) != 4 or not fields[0]:
            raise GovError("GIT_FAILURE", "git log gave commits that cannot be read",
                            {"root": str(root), "arguments": list(revisions)})
        sha, parents, block, names = fields
        trailers: dict[str, list[str]] = {}
        for line in block.split("\n"):
            key, _, value = line.partition(":")
            if key.strip() and value.strip():
                trailers.setdefault(key.strip(), []).append(value.strip())
        names = names.removeprefix("\0").removeprefix("\n")
        commits.append({"sha": sha, "parents": parents.split(), "trailers": trailers,
                        "paths": [name for name in names.split("\0") if name.strip("\n")]})
    return commits


def ticket_commits(root: Path, ticket: str) -> list[dict]:
    """The commits of HEAD's history whose trailers hold ``Task: <ticket>``, newest first."""
    return [c for c in read_commits(root, "HEAD", "--fixed-strings", f"--grep=Task: {ticket}")
            if ticket in c["trailers"].get("Task", [])]


def commits_since(root: Path, commits: list[dict]) -> list[dict]:
    """Every commit of HEAD's history that the ticket's first commit does not hold, the ticket's own
    left out: the commits of others in the ticket's range, newest first."""
    if not commits:
        return []
    own = {c["sha"] for c in commits}
    return [c for c in read_commits(root, f"{commits[-1]['sha']}..HEAD") if c["sha"] not in own]


def names_no_task(commit: dict) -> bool:
    return not commit["trailers"].get("Task")


# ---------------------------------------------------------------------------
# The tree a close measures is the commit it records
# ---------------------------------------------------------------------------

def tree_differences(root: Path) -> list[tuple[str, str]]:
    """``(state, path)`` for every path in which the working tree is not ``HEAD``: a tracked file changed,
    staged or hidden from git's comparison, and an untracked file git does not ignore (``??``)."""
    found = []
    entries = iter(git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                       "--ignore-submodules=none").split("\0"))
    for entry in entries:
        if not entry:
            continue
        state, path = entry[:2], entry[3:]
        if len(entry) < 4 or entry[2] != " ":
            raise GovError("GIT_FAILURE", "git status gave an entry that cannot be read",
                            {"root": str(root)})
        found.append((state, path))
        if "R" in state or "C" in state:  # the path it was renamed or copied from follows
            found.append((state, next(entries, "")))
    # What git was told not to compare (assume-unchanged, skip-worktree) is not known to be the commit's.
    for entry in git(root, "ls-files", "-v", "-z").split("\0"):
        if entry and not entry.startswith("H "):
            found.append((f"hidden from git's comparison ({entry[:1]})", entry[2:]))
    return found


# ---------------------------------------------------------------------------
# The record store against the commit being closed
# ---------------------------------------------------------------------------

def store_is_of_head(root: Path) -> bool | None:
    """Whether the record store was built from ``HEAD``; ``None`` when the project has no store.

    The store keeps the commits of the ``HEAD`` it was loaded from (``gov.store``: its ``commits`` table,
    every commit of that history). It is of this ``HEAD`` when it holds ``HEAD`` and as many commits as
    ``HEAD``'s history has. ``STORE_UNREADABLE`` when the store cannot be asked.
    """
    import sqlite3
    from gov.store import STORE_REL, connect

    head = git(root, "rev-parse", "HEAD").strip()
    history = git(root, "rev-list", "--count", "HEAD").strip()
    try:
        connection = connect(root)
    except GovError as e:
        if e.code == "STORE_MISSING":
            return None
        raise
    try:
        held = connection.execute("SELECT COUNT(*) FROM commits").fetchone()[0]
        holds_head = connection.execute("SELECT COUNT(*) FROM commits WHERE id = ?", (head,)).fetchone()[0]
    except sqlite3.Error as e:
        raise GovError("STORE_UNREADABLE",
                        f"the record store {STORE_REL} cannot be read ({e}); run gov rebuild",
                        {"store": STORE_REL})
    finally:
        connection.close()
    return bool(holds_head) and str(held) == history
