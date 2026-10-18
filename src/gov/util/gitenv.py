"""The environment of every git call of the Gov OS (W2-05, AR-2; DEC-710, DEC-712).

A hook inherits the ``GIT_*`` variables git exports to it: in a linked worktree ``GIT_DIR`` names the
worktree's git directory and ``GIT_INDEX_FILE`` its index. A git call the hook's check makes in another folder
(a temporary clone) acts on that repository instead of its own, and wrote two foreign commits onto a branch
(DEC-710). ``git_env`` is the one place that clears them, with the trace and configuration variables
(``GIT_TRACE*``, ``GIT_CONFIG_*``) among them, and turns lazy fetching off (``GIT_NO_LAZY_FETCH``).

The one value kept is git's own for the call's repository: a ``GIT_INDEX_FILE`` that names a file directly in
the git directory of ``root``. ``git commit -a`` and ``git commit -- <path>`` give the hook such an index
(``index.lock``, ``next-index-*.lock``) and what is to be committed is only there. Any other value is cleared,
a linked worktree's index under the main tree's ``.git/worktrees/`` among them. A
``GIT_DIR`` that names the git directory of ``root`` is the one git finds from ``root`` by itself, so clearing
it changes nothing.

``pinned`` also leaves the system and the person's own configuration unread (``~/.gitconfig``, the XDG file):
for the calls that only read, where a setting there (``trace2.eventTarget``) could write or change an answer.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

_PREFIX = "GIT_"
_OWN = "GIT_INDEX_FILE"
# The person's own: who commits (a note of ``gov ci push`` needs it) and how a push reaches its remote. None names
# a repository, a trace, a configuration or a fetch.
_PERSON = frozenset({
    "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL",
    "GIT_COMMITTER_DATE", "GIT_SSH", "GIT_SSH_COMMAND", "GIT_SSH_VARIANT", "GIT_ASKPASS", "GIT_TERMINAL_PROMPT"})
_TIMEOUT_S = 10
_PINNED = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}


def git_env(root: str | Path | None = None, *, pinned: bool = False, base: dict | None = None) -> dict[str, str]:
    """The environment for a git call (or a program that starts git) acting on the repository at ``root``.

    ``base`` (default ``os.environ``) without any ``GIT_*`` variable but the person's identity and push transport
    (``GIT_AUTHOR_*``, ``GIT_COMMITTER_*``, ``GIT_SSH*``, ``GIT_ASKPASS``, ``GIT_TERMINAL_PROMPT``), with
    ``GIT_NO_LAZY_FETCH=1``; and, with
    ``pinned``, with the system and global configuration files unread. A ``GIT_INDEX_FILE`` of ``base`` that names
    a file directly in the git directory of ``root`` is kept, as an absolute path. With no ``root`` nothing is kept."""
    source = os.environ if base is None else base
    env = {key: value for key, value in source.items() if not key.startswith(_PREFIX) or key in _PERSON}
    env["GIT_NO_LAZY_FETCH"] = "1"
    if pinned:
        env.update(_PINNED)
    own = _own_index(root, source.get(_OWN), env) if root is not None else None
    if own is not None:
        env[_OWN] = own
    return env


def _own_index(root: str | Path, value: str | None, cleared: dict) -> str | None:
    """``value`` as an absolute path when it names a file directly in the git directory of ``root``, else None."""
    if not value:
        return None
    try:
        # A relative value is read by git from the folder it was given in: the caller's.
        index = os.path.realpath(os.path.join(os.getcwd(), value))
        done = subprocess.run(["git", "-C", str(root), "rev-parse", "--absolute-git-dir"], capture_output=True,
                              text=True, stdin=subprocess.DEVNULL, timeout=_TIMEOUT_S, env={**cleared, **_PINNED})
    except (OSError, subprocess.TimeoutExpired):
        return None
    if done.returncode != 0 or not done.stdout.strip():
        return None
    # Directly in it: a linked worktree's index lies deeper, under the main tree's ``worktrees/<name>/``.
    return index if os.path.dirname(index) == os.path.realpath(done.stdout.rstrip("\n")) else None
