"""The sandbox block of a worker session's ``--settings`` and its strict check (W2-56; DEC-1112 (1), DEC-1035).

Today's sandbox, not made from the ticket's allowed paths (write scope is the path-map guard's, DEC-820 (4)):

- ``network``: the strict allowlist (today's domains: none, the research allowlist for research) and **one** Unix
  socket, the shared reranker's (``gov.retrieval.rerank``: ``~/.cache/gov-os/rerank.sock``, the service's own
  setting), never a pattern or its folder (S8). On Linux the CLI's sandbox does not open a socket for a one-path
  allow (D-13, measured by the CTO on 2026-11-09): the entry is inert there and honoured where the CLI supports it.
- ``filesystem.allowWrite``: the session's temp folder (DEC-159), its own run folder (DEC-728) and the reranker's log
  file (S11, D-11 (a)), so that a search the service does not answer is counted where ``gov status`` reads it. The
  log file is made here when it is missing (the sandbox cannot bind a file that is not there).

A place under ``~/.cache/gov-os`` that is a link, or a log that is no regular file, is left off: a link followed would
put its target on the list (fail open). ``faults`` names every way a block is wider than this one.
"""

from __future__ import annotations

import fcntl
import os
import re
import stat
from pathlib import Path

from gov.retrieval.rerank import CACHE_REL, LOG, SOCKET

# W2-56 S4 (DEC-402, row W2-I012): the names the CLI's sandbox denies writes to whatever the settings say, and puts a
# placeholder at when nothing is there (shell and git start-up files, editor folders, the CLI's own folders) ...
PLACEHOLDER_NAMES = (".bashrc", ".bash_profile", ".profile", ".zshrc", ".zprofile", ".gitconfig", ".gitmodules",
                     ".ripgreprc", ".mcp.json", ".vscode", ".idea")
PLACEHOLDER_PATHS = (".claude/commands", ".claude/agents", ".claude/skills", ".claude/hooks")
# ... kept out of git's way in the repository's own exclude file, shared by its worktrees, so that neither the session
# nor its caller in the same worktree stages one; a folder of the same name is not ignored (``!<name>/``).
EXCLUDE_MARK = "# gov launch (W2-56 S4, DEC-402): the sandbox's placeholder names; a folder of the same name is kept"
_LITERAL_EDIT = re.compile(r"Edit\(/(/.+)\)")

SANDBOX_KEYS = frozenset({"enabled", "failIfUnavailable", "allowUnsandboxedCommands", "network", "filesystem"})
NETWORK_KEYS = frozenset({"strictAllowlist", "allowedDomains", "allowUnixSockets"})
FILESYSTEM_KEYS = frozenset({"allowWrite", "denyWrite", "denyRead"})
_PATTERN = frozenset("*?[{")


def _home(home: str | Path | None) -> Path:
    return Path(home if home is not None else (os.environ.get("HOME") or Path.home()))


def cache_dir(home: str | Path | None = None) -> Path:
    """The reranker's folder under ``home`` (the launcher's HOME by default), as the service names it."""
    return _home(home) / CACHE_REL


def socket_path(home: str | Path | None = None) -> str:
    """The reranker's socket, as the service names it: ``<HOME>/.cache/gov-os/rerank.sock``."""
    return os.path.normpath(str(cache_dir(home) / SOCKET))


def log_path(home: str | Path | None = None) -> str:
    """The reranker's log, where ``gov.retrieval.rerank.status`` counts the FALLBACK lines."""
    return os.path.normpath(str(cache_dir(home) / LOG))


def _no_link_on_the_way(home: Path) -> bool:
    """True when neither ``.cache`` nor ``.cache/gov-os`` under ``home`` is a link (a missing one is no link)."""
    place = home
    for part in Path(CACHE_REL).parts:
        place = place / part
        if os.path.islink(place):
            return False
    return True


def reranker_socket(home: str | Path | None = None) -> list[str]:
    """``allowUnixSockets``: the reranker's one socket, or nothing when it, or a folder on its way, is a link."""
    home = _home(home)
    path = socket_path(home)
    if not _no_link_on_the_way(home) or os.path.islink(path):
        return []
    return [path]


def reranker_log(home: str | Path | None = None) -> list[str]:
    """The reranker's log for the write list, made (0600, its folder 0700) when missing; nothing when it, or a folder on
    its way, is a link, or when it is no regular file of this user."""
    home = _home(home)
    if not _no_link_on_the_way(home):
        return []
    folder, path = cache_dir(home), log_path(home)
    try:
        folder.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not _no_link_on_the_way(home):  # made by someone else between the check and the mkdir
            return []
        try:
            os.close(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600))
        except FileExistsError:
            pass
        found = os.lstat(path)
    except OSError:
        return []
    if not stat.S_ISREG(found.st_mode) or found.st_uid != os.getuid():
        return []
    return [path]


def network(domains: list[str], home: str | Path | None = None) -> dict:
    """The ``network`` block: the strict allowlist and the reranker's one socket (S8)."""
    return {"strictAllowlist": True, "allowedDomains": list(domains), "allowUnixSockets": reranker_socket(home)}


def filesystem(tmpdir: str, own: str | None, home: str | Path | None = None) -> dict:
    """The ``filesystem`` block: the session's temp folder, its run folder and the reranker's log (S2, S11)."""
    places = [tmpdir, *([own] if own else []), *reranker_log(home)]
    return {"allowWrite": [f"/{place}" for place in places]}


def placeholder_lines(root: Path, deny: list[str]) -> list[str]:
    """The exclude lines for the placeholders of a session at ``root``: the CLI's fixed names (anywhere), its fixed
    paths, and each literal ``Edit`` deny rule under ``root`` that names nothing at launch (the sandbox puts a
    placeholder there, DEC-402: the prefixes of ``scratch`` in ``.gov-runtime/``). Each line with its folder
    exception."""
    root = Path(root)
    rels = [f"/{rel}" for rel in PLACEHOLDER_PATHS]
    for rule in deny:
        found = _LITERAL_EDIT.fullmatch(rule)
        if found is None or _PATTERN & set(found.group(1)):
            continue
        path = Path(os.path.normpath(found.group(1)))
        if path != root and path.is_relative_to(root) and not os.path.lexists(path):
            rels.append(f"/{path.relative_to(root).as_posix()}")
    lines = []
    for name in (*PLACEHOLDER_NAMES, *dict.fromkeys(rels)):
        lines += [name, f"!{name}/"]
    return lines


def exclude_file(root: Path) -> Path | None:
    """The exclude file git reads for the worktree at ``root`` (``git rev-parse --git-path info/exclude``): in the
    repository's common git folder, shared by its worktrees. None when no ``.git`` stands at ``root`` or above it.
    Read from the files, without starting git."""
    for place in (Path(root), *Path(root).parents):
        dot = place / ".git"
        if dot.is_dir():
            gitdir = dot
        elif dot.is_file():
            first = dot.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
            if not first.startswith("gitdir:"):
                return None
            gitdir = (place / first[len("gitdir:"):].strip()).resolve()
        else:
            continue
        common = gitdir / "commondir"
        if common.is_file():
            gitdir = (gitdir / common.read_text(encoding="utf-8", errors="replace").strip()).resolve()
        return gitdir / "info" / "exclude"
    return None


def exclude_placeholders(root: Path, deny: list[str]) -> None:
    """Keep the placeholders out of every commit made in ``root``'s repository (W2-56 S4): the lines missing from its
    exclude file (``exclude_file``) are added under ``EXCLUDE_MARK``. Nothing for a root that is not in a git
    repository; an ``OSError`` when the file cannot be written."""
    path = exclude_file(root)
    if path is None or not path.parent.parent.is_dir():
        return  # no repository: nothing is committed there
    wanted = placeholder_lines(root, deny)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW | os.O_CLOEXEC, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        with open(path, encoding="utf-8", errors="replace") as text:
            have = {line.rstrip("\n") for line in text}
        missing = [line for line in wanted if line not in have]
        if missing:
            head = "" if EXCLUDE_MARK in have else f"{EXCLUDE_MARK}\n"
            ending = os.pread(fd, 1, os.fstat(fd).st_size - 1) if os.fstat(fd).st_size else b"\n"
            gap = "" if ending == b"\n" else "\n"
            os.write(fd, (gap + head + "".join(f"{line}\n" for line in missing)).encode())
    finally:
        os.close(fd)


def _one_slash(entry: str) -> str:
    """A path entry read with one leading slash: ``//<absolute>`` and ``/<absolute>`` are the same."""
    return "/" + entry.lstrip("/") if entry.startswith("/") else entry


def _socket_faults(sockets, home: str | Path | None) -> list[str]:
    if sockets is None:
        return []
    if not isinstance(sockets, list) or not all(isinstance(entry, str) for entry in sockets):
        return ["sandbox.network.allowUnixSockets is not a list of paths"]
    faults = []
    if len(sockets) > 1:
        faults.append("sandbox.network.allowUnixSockets names more than one socket (DEC-1035)")
    wanted = socket_path(home)
    for entry in sockets:
        if _PATTERN & set(entry):
            faults.append(f"sandbox.network.allowUnixSockets holds a pattern: {entry}")
        elif os.path.normpath(_one_slash(entry)) != wanted:
            faults.append(f"sandbox.network.allowUnixSockets names a socket other than the reranker's: {entry}")
    return faults


def faults(settings: dict, home: str | Path | None = None) -> list[str]:
    """Why the settings are not on, strict and fail-closed, or are wider than the launcher's (CAP-61.a, DEC-164,
    DEC-1035); empty when they are as built. ``home`` (the launcher's HOME by default) names the reranker's socket."""
    block = settings.get("sandbox")
    block = block if isinstance(block, dict) else {}
    net = block.get("network")
    net = net if isinstance(net, dict) else None
    files = block.get("filesystem")
    checks = {
        "sandbox.enabled is not true": block.get("enabled") is True,
        "sandbox.failIfUnavailable is not true": block.get("failIfUnavailable") is True,
        "sandbox.allowUnsandboxedCommands is not false": block.get("allowUnsandboxedCommands") is False,
        "sandbox.network.strictAllowlist is not true": net is not None and net.get("strictAllowlist") is True,
        "sandbox.excludedCommands is set (DEC-164)": "excludedCommands" not in block,
    }
    found = [fault for fault, holds in checks.items() if not holds]
    found += [f"sandbox.{key} is set: not a key of the launcher's sandbox" for key in sorted(set(block) - SANDBOX_KEYS)
              if key != "excludedCommands"]
    if net is not None:
        found += [f"sandbox.network.{key} is set: no other socket, port or binding (DEC-1035)"
                  for key in sorted(set(net) - NETWORK_KEYS)]
        found += _socket_faults(net.get("allowUnixSockets"), home)
    if files is not None:
        if not isinstance(files, dict):
            found.append("sandbox.filesystem is not a map")
        else:
            found += [f"sandbox.filesystem.{key} is set: not a key of the launcher's sandbox"
                      for key in sorted(set(files) - FILESYSTEM_KEYS)]
    return found
