"""``gov rebuild --integration <branch>`` (W2-116 S1, S4; DEC-963, DEC-983, DEC-1014 items 4 and 6, DEC-1087 (3)):
the store of the integration branch's head, double-buffered, so a search is always answered from a complete store.

- **The place:** the link at the absolute path ``integration_store`` of the project's ``governance/project/rebuild.yaml``
  (W2-122's key). The two halves are detached worktrees of the project's repository beside it, ``<link>-a`` and
  ``<link>-b``; the link points at the ready one. A link that is not a symbolic link, or a half that is not a worktree
  of this repository, refuses the refresh: nothing is removed or built.
- **The lock:** ``<link>.lock``, an exclusive ``flock`` held from before the link is read to after it is switched (the
  CTO's ``refresh_integration_store.sh`` and the merge queue's promotion take the same file). A refresh that finds it
  held says so and waits. Searches take no lock.
- **Unchanged:** where the ready half is at the branch's head and its stores' record (W2-122) names the running code,
  nothing is done (``status: unchanged``). The command is safe to run after every merge, by a hook or by hand.
- **The build:** the half not in use is checked out at the branch's head and rebuilt there by the code this command
  runs under (never the half's own ``src/``), so the store always matches the code that searches it. It is seeded
  from the ready half (``--seed``, W2-122), so only what changed since is chunked and embedded again; the seed names
  the ready half's head and says that it is behind. A seed refused (another code, embedder or schema) leaves the
  half's own stores, built incrementally or cold.
- **The switch:** only when the build succeeded: the rebuild raised nothing, the lexical index and the semantic store
  were recreated (a build whose semantic store is not recreated counts as failed, N-2), the half's lexical and
  semantic facets then read fresh, and the half is still at the head it was built for. The link is replaced by an
  atomic rename (``os.replace`` of a new link made beside it). Otherwise the link stays where it was, the failure is
  ``REBUILD_FAILED`` with the build's stores in its details, and the half left behind is never read: the next refresh
  seeds over it.
- **While it builds,** the link points at the ready half, which nothing here writes: searches through the link are
  answered from it, complete, the whole time (F2).
"""

from __future__ import annotations

import argparse
import fcntl
import os
import subprocess
import sys
from pathlib import Path

from gov.cli.errors import GovError

HALVES = ("-a", "-b")
LOCK_SUFFIX = ".lock"
UNCHANGED, SWITCHED = "unchanged", "switched"


def _failed(message: str, details: dict) -> GovError:
    return GovError("REBUILD_FAILED", message, details)


def _git(where: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    from gov.util.gitenv import git_binary, git_env

    done = subprocess.run([git_binary() or "git", "-C", str(where), *args], capture_output=True, text=True,
                          env=git_env(where))
    if check and done.returncode != 0:
        raise _failed(f"git {' '.join(args)} failed in {where}: {done.stderr.strip() or done.returncode}",
                      {"where": str(where), "git": list(args)})
    return done


def _common_dir(where: Path) -> Path | None:
    done = _git(where, "rev-parse", "--git-common-dir", check=False)
    if done.returncode != 0 or not done.stdout.strip():
        return None
    return (where / done.stdout.strip()).resolve()


def _head(where: Path) -> str | None:
    done = _git(where, "rev-parse", "--verify", "-q", "HEAD^{commit}", check=False)
    return done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else None


def place(root: Path) -> Path:
    """The link the project configures; ``REBUILD_FAILED`` where none is configured or it cannot be used."""
    from gov.launch.store import StoreSettingError, configured

    try:
        value = configured(root)
    except StoreSettingError as error:
        raise _failed(f"{error}: nothing is built", {"key": "integration_store"}) from None
    if value is None:
        raise _failed("governance/project/rebuild.yaml names no integration_store: there is no place for the "
                      "integration store, so nothing is built", {"key": "integration_store"})
    return Path(value)


def halves(link: Path) -> tuple[Path, Path]:
    return tuple(link.with_name(link.name + suffix) for suffix in HALVES)


def _lock(link: Path) -> int:
    """The refresh's exclusive lock on ``<link>.lock``, waited for when held; its descriptor."""
    path = link.with_name(link.name + LOCK_SUFFIX)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o664)
    except OSError as error:
        raise _failed(f"the integration store's lock {path} cannot be opened: {error}: nothing is built",
                      {"lock": str(path)}) from None
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"rebuild --integration: waiting for the integration store's lock {path}", file=sys.stderr,
                  flush=True)
            fcntl.flock(fd, fcntl.LOCK_EX)
    except OSError as error:
        os.close(fd)
        raise _failed(f"the integration store's lock {path} cannot be taken: {error}: nothing is built",
                      {"lock": str(path)}) from None
    return fd


def _ready(link: Path) -> Path | None:
    """The half the link points at; None where there is no link yet. A link that is no symbolic link refuses."""
    if not os.path.lexists(link):
        return None
    if not link.is_symlink():
        raise _failed(f"{link} is not a symbolic link: the integration store's link is never replaced by a folder "
                      f"or a file, so nothing is built", {"link": str(link)})
    target = Path(os.path.realpath(link))
    return target if target.is_dir() else None


def _complete(half: Path) -> bool:
    """The half's stores were completed by the running code: its W2-122 record is there and names this code."""
    from gov.rebuild import seed

    record = seed._read(half / seed.RECORD_REL)
    return record is not None and record.get("code") == seed.code_fingerprint()


def _checkout(root: Path, half: Path, head: str) -> None:
    """``half`` a detached worktree of ``root``'s repository at ``head``: made where absent, checked out where it is
    one; anything else there refuses."""
    if not os.path.lexists(half):
        _git(root, "worktree", "add", "--force", "--detach", str(half), head)
        return
    if half.is_symlink() or not half.is_dir():
        raise _failed(f"{half} is there and is not a folder: nothing is built", {"half": str(half)})
    if (half / ".git").exists():
        if _common_dir(half) != _common_dir(root):
            raise _failed(f"{half} is a worktree of another repository than {root}'s: nothing is built",
                          {"half": str(half)})
        _git(half, "checkout", "-q", "--force", "--detach", head)
        return
    if any(half.iterdir()):
        raise _failed(f"{half} is a folder that is not a worktree of {root}'s repository: nothing is built",
                      {"half": str(half)})
    _git(root, "worktree", "add", "--force", "--detach", str(half), head)


def _switch(link: Path, half: Path) -> None:
    """The link pointed at ``half`` by one atomic rename."""
    temporary = link.with_name(f".{link.name}.{os.getpid()}.tmp")
    try:
        if os.path.lexists(temporary):
            temporary.unlink()
        os.symlink(half, temporary)
        os.replace(temporary, link)
    except OSError as error:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise _failed(f"the link {link} could not be switched to {half}: {error}; it stays where it was",
                      {"link": str(link), "half": str(half)}) from None


def _faults(half: Path, head: str, result: dict) -> list[str]:
    """Why the build in ``half`` may not be switched to; empty when it may."""
    from gov.retrieval import lexical, semantic

    stores = result.get("stores") or {}
    said = []
    for name in ("lexical", "semantic"):
        status = (stores.get(name) or {}).get("status")
        if status != "recreated":
            said.append(f"the {name} store was not recreated ({(stores.get(name) or {}).get('reason') or status})")
    if not said:
        fresh = lexical.freshness(half)["status"]
        if fresh != "fresh":
            said.append(f"the lexical index reads {fresh} after the build")
        else:
            reason = semantic._status(half)
            if reason is not None:
                said.append(f"the semantic facet reads {reason} after the build")
    if _head(half) != head:
        said.append(f"the half moved off {head[:12]} during the build")
    return said


def refresh(root: Path, branch: str) -> dict:
    """The integration store brought to ``branch``'s head (module docstring); the result, or ``REBUILD_FAILED``."""
    from gov.config.loader import load_config
    from gov.rebuild import command
    from gov.store import STORE_REL

    root = Path(root)
    link = place(root)
    done = _git(root, "rev-parse", "--verify", "-q", f"{branch}^{{commit}}", check=False)
    head = done.stdout.strip()
    if done.returncode != 0 or not head:
        raise _failed(f"the branch {branch!r} is not known in {root}: nothing is built", {"branch": branch})
    fd = _lock(link)
    try:
        ready = _ready(link)
        first, second = halves(link)
        summary = {"branch": branch, "head": head, "link": str(link), "ready": None if ready is None else str(ready)}
        if ready is not None and _head(ready) == head and _complete(ready):
            print(f"rebuild --integration: {link} is at {head[:12]} already ({ready.name}): nothing to do",
                  file=sys.stderr, flush=True)
            return {"integration": summary | {"status": UNCHANGED}}
        building = second if ready is not None and ready == first.resolve() else first  # never the ready half
        _checkout(root, building, head)
        seeded_from = ready if ready is not None and (ready / STORE_REL).is_file() else None
        print(f"rebuild --integration: building {building.name} at {head[:12]}"
              + (f", seeded from {ready.name}" if seeded_from else "") + f"; {link} stays at "
              + (ready.name if ready else "nothing") + " until it succeeds", file=sys.stderr, flush=True)
        args = argparse.Namespace(no_embeddings=False, seed=None if seeded_from is None else str(seeded_from),
                                  integration=None)
        try:
            config = load_config(building)
            result = command.run(building, args, config)
        except GovError as error:
            raise _failed(f"the build of {building} at {head[:12]} failed: {error.message}; {link} stays at "
                          f"{summary['ready']}", summary | {"building": str(building), "error": error.code,
                                                            "details": error.details}) from None
        faults = _faults(building, head, result)
        if faults:
            raise _failed(f"the build of {building} at {head[:12]} is not switched to: {'; '.join(faults)}; {link} "
                          f"stays at {summary['ready']}", summary | {"building": str(building),
                                                                     "stores": result.get("stores"),
                                                                     "seed": result.get("seed"), "faults": faults})
        _switch(link, building)
        print(f"rebuild --integration: {link} -> {building.name} at {head[:12]}", file=sys.stderr, flush=True)
        return result | {"integration": summary | {"status": SWITCHED, "ready": str(building),
                                                   "previous": summary["ready"]}}
    finally:
        os.close(fd)
