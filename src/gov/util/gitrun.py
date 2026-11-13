"""The one git runner the close and the store share (DEC-500; W2-150 S6, DEC-1109 (2)).

Moved here from ``gov.close.repo`` unchanged, so that the store's fingerprints (``gov.store.loader``) read git
exactly as the close does without importing a gate: ``gov.close.repo.git`` and ``gov.store.loader._commit_git``
are this ``git``. Nothing here imports the close, the guard or the store.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from gov.cli.errors import GovError
from gov.util.gitenv import git_env

# What the caller's environment says to git (configuration, another repository or index, a base for
# replacement refs) does not reach the git this command asks (DEC-500).
_GIT_VARIABLES = "GIT_"


def git(root: Path, *args: str, ok: tuple = (0,), code: bool = False, given: str | None = None,
        pinned: bool = True):
    """The output of a git command, or its exit code with ``code``; ``GIT_FAILURE`` outside ``ok``. ``given``
    is its standard input.

    The git asked is not the caller's to bend (DEC-500): no variable of the caller's environment that speaks
    to git is passed on, and replacement refs are not followed. Its environment is the helper's for ``root``
    (W2-M161), with the system and the person's configuration unread; a commit of the close passes
    ``pinned=False``, so that the identity it carries is still the configured one.
    """
    env = git_env(root, pinned=pinned,
                  base={key: value for key, value in os.environ.items() if not key.startswith(_GIT_VARIABLES)})
    try:
        done = subprocess.run(["git", "-C", str(root), "--no-replace-objects", *args],
                              capture_output=True, text=True, env=env, input=given,
                              stdin=None if given is not None else subprocess.DEVNULL)
    except OSError as e:
        raise GovError("GIT_FAILURE", f"git {args[0]} cannot run: {e}",
                        {"root": str(root)})
    if done.returncode not in ok:
        raise GovError("GIT_FAILURE",
                        f"git {args[0]} failed: {done.stderr.strip()[:200]}",
                        {"root": str(root), "arguments": list(args)})
    return done.returncode if code else done.stdout
