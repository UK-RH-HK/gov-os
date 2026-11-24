"""The freeze flag and its mirror (DEC-402, DEC-429), read by ``gov pause``, ``gov status``, ``gov launch`` and the
close's commit check.

Moved from ``gov.guard.decide`` unchanged when the guard was retired (EMERGENCY-2 6.1).
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from gov.util.gitenv import GIT_DIRS, git_binary

FREEZE_FLAG = ".gov-runtime/freeze"
FREEZE_MARKER = b"FROZEN"  # DEC-402: the word of a real flag's marker line
_FREEZE_HEAD = 65536       # the most that is read of a flag


# W2-L160: git from the system's own folders, never whatever comes first on
# the inherited PATH; the helper's folders and resolver, one for every reader.
_GIT_DIRS = GIT_DIRS
# DEC-783 item 2: the look-up's own limit.
_LOOKUP_S = 15


class FreezeLookupUnavailable(Exception):
    """The freeze look-up could not be made: no git resolved, or it passed
    its own limit; a strict reader refuses (DEC-580)."""


def _git_binary() -> str | None:
    return git_binary(_GIT_DIRS)


def _mirror_path(project_root: str) -> Path:
    """The mirror file for this project: ``~/.local/state/gov-os/<key>/freeze``
    where ``<key>`` is ``sha256(realpath(git-common-dir))``.

    Raises ``FreezeLookupUnavailable`` when no git is resolved by absolute
    path or the look-up passes ``_LOOKUP_S``."""
    import hashlib
    import subprocess as _sp
    from gov.util.gitenv import git_env
    git = _git_binary()
    if git is None:
        raise FreezeLookupUnavailable("no git resolved by absolute path")
    try:
        # No inherited GIT_* variable and no system or global configuration
        # (a trace setting there) reaches it (DEC-710).
        raw = _sp.run([git, "-C", project_root, "rev-parse", "--git-common-dir"],
                      capture_output=True, text=True, check=True,
                      stdin=_sp.DEVNULL, timeout=_LOOKUP_S,
                      env=git_env(None, pinned=True)).stdout.strip()
        if not os.path.isabs(raw):
            raw = os.path.join(project_root, raw)
        common = os.path.realpath(raw)
    except _sp.TimeoutExpired:
        raise FreezeLookupUnavailable(
            f"git rev-parse gave no answer within {_LOOKUP_S} s") from None
    except Exception:
        common = os.path.realpath(project_root)
    key = hashlib.sha256(common.encode()).hexdigest()
    return Path.home() / ".local" / "state" / "gov-os" / key / "freeze"


def _mirror_frozen(project_root: str, *, strict: bool = False) -> bool:
    """True when the mirror says frozen or the mirror folder is unreadable (fail closed, DEC-429).

    A look-up that could not be made reads as frozen; with ``strict`` it
    raises ``FreezeLookupUnavailable`` instead, for the caller to refuse."""
    try:
        mirror = _mirror_path(project_root)
    except FreezeLookupUnavailable:
        if strict:
            raise
        return True
    except Exception:
        return True
    try:
        if not mirror.parent.exists():
            return False
        if not os.access(str(mirror.parent), os.R_OK):
            return True
        if not mirror.exists():
            return False
        head = mirror.read_bytes()[:_FREEZE_HEAD]
        return FREEZE_MARKER in head.replace(b"\x00", b"").upper()
    except OSError:
        return True


# -- the freeze flag (DEC-402) -------------------------------------------------

def freeze_state(project_root: str) -> str:
    """Read the freeze flag: ``"absent"``, ``"unmarked"`` or ``"frozen"``.

    Frozen when the flag carries the marker word, in any letter case and
    with its NUL bytes taken out (a near spelling of the marker line, or
    the line in UTF-16 or UTF-32), or when something is at the path that
    cannot be read as a file (DEC-179).  An empty file, text without the
    word and a character device (what the sandbox puts at the path) are an
    unmarked presence, which the hook records.  Only a regular file is
    opened, and only its head is read.
    """
    path = os.path.join(project_root, FREEZE_FLAG)
    try:
        os.lstat(path)
    except FileNotFoundError:
        # A dangling link where the runtime folder should be hides the
        # folder that would hold the flag: no reader can tell.
        runtime = os.path.dirname(path)
        if os.path.islink(runtime) and not os.path.exists(runtime):
            return "frozen"
        return "absent"
    except NotADirectoryError:
        return "absent"
    except OSError:
        return "frozen"
    try:
        st = os.stat(path)
        if stat.S_ISCHR(st.st_mode) or (stat.S_ISREG(st.st_mode)
                                        and st.st_size == 0):
            return "unmarked"
        if not stat.S_ISREG(st.st_mode):
            return "frozen"
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        try:
            head = os.read(fd, _FREEZE_HEAD + 1)
        finally:
            os.close(fd)
    except OSError:
        return "frozen"
    if len(head) > _FREEZE_HEAD:
        return "frozen"  # too large to read whole: no reader can tell
    if FREEZE_MARKER in head.replace(b"\x00", b"").upper():
        return "frozen"
    return "unmarked"




PAUSED = "PAUSED"


def paused_error(*roots):
    """F10 (fixes-015a, CAP-05.a): the ``PAUSED`` error naming the pause when the freeze flag of any of ``roots`` is
    frozen, else None. One reading for ``gov launch``, the dispatch pass and ``gov release --patch``."""
    from gov.cli.errors import GovError

    for each in sorted({str(r) for r in roots}):
        if freeze_state(each) == "frozen":
            return GovError(PAUSED, f"the project is paused (gov pause set {each}/{FREEZE_FLAG}): nothing starts until "
                            f"the owner lifts it with gov pause --off (CAP-05)", {"path": f"{each}/{FREEZE_FLAG}"})
    return None
