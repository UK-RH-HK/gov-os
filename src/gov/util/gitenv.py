"""The environment of every git call of the Gov OS (W2-05, AR-2; DEC-710, DEC-712).

A hook inherits the ``GIT_*`` variables git exports to it: in a linked worktree ``GIT_DIR`` names the
worktree's git directory and ``GIT_INDEX_FILE`` its index. A git call the hook's check makes in another folder
(a temporary clone) acts on that repository instead of its own, and wrote two foreign commits onto a branch
(DEC-710). ``git_env`` is the one place that clears them, with the trace and configuration variables
(``GIT_TRACE*``, ``GIT_CONFIG_*``) among them, and turns lazy fetching off (``GIT_NO_LAZY_FETCH``).

P-1 (DEC-804 item 3): an inherited ``GIT_INDEX_FILE`` is honoured only for git calls in the project root; a
program that may start git elsewhere gets no index. The one value ``git_env`` keeps is git's own for the call's
repository: a ``GIT_INDEX_FILE`` that names a file directly in the git directory of ``root``. ``git commit -a``
and ``git commit -- <path>`` give the hook such an index (``index.lock``, ``next-index-*.lock``) and what is to
be committed is only there. Any other value is cleared, a linked worktree's index under the main tree's
``.git/worktrees/`` among them. A ``GIT_DIR`` that names the git directory of ``root`` is the one git finds from
``root`` by itself, so clearing it changes nothing. ``program_env`` keeps no index at all: a declared check runs
git where it likes (a temporary repository of its own), and an index kept as an absolute path would be the
project's there (F-A, DEC-807 item 2). ``foreign_index`` names an inherited ``GIT_INDEX_FILE`` that is not kept,
for a caller that must refuse rather than act on the default index in its place (the staged-secrets gate).

``pinned`` also leaves the system and the person's own configuration unread (``~/.gitconfig``, the XDG file):
for the calls that only read, where a setting there (``trace2.eventTarget``) could write or change an answer.

``runner_env`` is the environment of a process that runs the tests (package I (b), DEC-970): ``program_env``'s,
pinned, with ``GIT_CONFIG_GLOBAL`` naming a file generated for the run that holds only the person's
``user.name``, ``user.email`` and ``init.defaultBranch``. A test that commits in a repository of its own without
naming an identity, or that relies on the default branch, works as it does for the person; nothing else of the
person's configuration reaches it.

``git_binary`` is git by absolute path from the system's own folders, never whatever comes first on the inherited
``PATH`` (W2-L160): for the guard's hooks, the freeze look-up and the containment check.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

_PREFIX = "GIT_"
_OWN = "GIT_INDEX_FILE"
# The person's own: who commits (a note of ``gov ci push`` needs it) and how a push reaches its remote. None names
# a repository, a trace, a configuration or a fetch.
_PERSON = frozenset({
    "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL",
    "GIT_COMMITTER_DATE", "GIT_SSH", "GIT_SSH_COMMAND", "GIT_SSH_VARIANT", "GIT_ASKPASS", "GIT_TERMINAL_PROMPT"})
_TIMEOUT_S = 10
_PINNED = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
# The person's settings a test run gets (DEC-970), as git names them in its output.
_RUNNER_KEYS = {"user.name": ("user", "name"), "user.email": ("user", "email"),
                "init.defaultbranch": ("init", "defaultBranch")}
# The system's own folders git is taken from, in this order (W2-L160).
GIT_DIRS = ("/usr/bin", "/bin", "/usr/local/bin", "/opt/homebrew/bin")


def git_binary(dirs: tuple[str, ...] | None = None) -> str | None:
    """git by absolute path from ``dirs`` (default ``GIT_DIRS``), never from the inherited ``PATH``; None when
    none of them holds it. A caller refuses on None rather than run another git (DEC-580)."""
    return shutil.which("git", path=os.pathsep.join(GIT_DIRS if dirs is None else dirs))


def git_env(root: str | Path | None = None, *, pinned: bool = False, base: dict | None = None) -> dict[str, str]:
    """The environment for a git call in the repository at ``root`` (``git -C <root> …``); a program that may
    start git elsewhere takes ``program_env`` instead (P-1).

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


def program_env(*, pinned: bool = False, base: dict | None = None) -> dict[str, str]:
    """The environment for a program that may start git outside the project root (a declared check, P-1).

    ``git_env``'s, with no ``GIT_INDEX_FILE`` kept whatever ``base`` holds: no inherited ``GIT_DIR``,
    ``GIT_WORK_TREE``, ``GIT_COMMON_DIR`` or index reaches it, so its git in a folder of its own acts on that
    folder's repository only, and its git in the root finds the root's own index by itself."""
    return git_env(None, pinned=pinned, base=base)


@contextmanager
def runner_env(*, base: dict | None = None) -> Iterator[dict[str, str]]:
    """The environment of a process that runs the tests, for the time of the ``with`` (DEC-970).

    ``program_env(pinned=True, base=base)`` with ``GIT_CONFIG_GLOBAL`` naming a file in a folder of this process's
    temporary folder, made on entry and removed on exit. It holds the person's ``user.name``, ``user.email`` and
    ``init.defaultBranch``, each only when set, taken from the person's global files as ``base``'s ``HOME`` and
    ``XDG_CONFIG_HOME`` name them (the XDG file, then ``~/.gitconfig``, the later winning). Each file is read as
    data under the pinned environment (``git config --file``: no include followed, no setting of it acting)."""
    source = os.environ if base is None else base
    env = program_env(pinned=True, base=source)
    with tempfile.TemporaryDirectory(prefix="gov-gitconfig-") as folder:
        found = {}
        for path in _global_files(source):
            found.update(_read_keys(path, folder))
        sections: dict[str, list[str]] = {}
        for key, (section, name) in _RUNNER_KEYS.items():
            if key in found:
                sections.setdefault(section, []).append(f"\t{name} = {_quoted(found[key])}\n")
        env["GIT_CONFIG_GLOBAL"] = os.path.join(folder, "config")
        Path(env["GIT_CONFIG_GLOBAL"]).write_text(
            "".join(f"[{section}]\n" + "".join(lines) for section, lines in sections.items()), encoding="utf-8")
        yield env


def _global_files(source: dict) -> list[str]:
    """The person's global configuration files in the order git reads them."""
    home, xdg = source.get("HOME"), source.get("XDG_CONFIG_HOME")
    xdg = xdg or (os.path.join(home, ".config") if home else None)
    return [path for path in (xdg and os.path.join(xdg, "git", "config"), home and os.path.join(home, ".gitconfig"))
            if path and os.path.isfile(path)]


def _read_keys(path: str, folder: str) -> dict[str, str]:
    """The runner's keys set in the file at ``path``, read with no configuration of git's own and in ``folder``
    (no repository around it); nothing when git cannot read it."""
    git = git_binary()
    env = {"PATH": os.pathsep.join(GIT_DIRS), "GIT_CEILING_DIRECTORIES": os.path.dirname(folder), **_PINNED}
    try:
        done = subprocess.run([git, "config", "--file", path, "--null", "--get-regexp",
                               r"^(user\.(name|email)|init\.defaultbranch)$"], capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=_TIMEOUT_S, env=env, cwd=folder) if git else None
    except (OSError, subprocess.TimeoutExpired):
        return {}
    if done is None or done.returncode != 0:
        return {}
    found = {}
    for item in filter(None, done.stdout.split("\0")):
        key, _sep, value = item.partition("\n")
        found[key] = value
    return found


def _quoted(value: str) -> str:
    """``value`` as a git configuration value in double quotes."""
    for plain, escaped in (("\\", "\\\\"), ('"', '\\"'), ("\n", "\\n"), ("\t", "\\t")):
        value = value.replace(plain, escaped)
    return f'"{value}"'


def foreign_index(root: str | Path, *, base: dict | None = None) -> str | None:
    """The ``GIT_INDEX_FILE`` of ``base`` (default ``os.environ``) as given, when ``git_env(root)`` would not keep it
    (it is not git's own index of ``root``); None when it is git's own or none is set. A caller that must act on
    the index being committed refuses on it rather than act on the default index (review F1, DEC-580)."""
    source = os.environ if base is None else base
    value = source.get(_OWN)
    if not value:
        return None
    return None if _own_index(root, value, git_env(None, base=source)) is not None else value


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
