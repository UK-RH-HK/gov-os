"""The backup's logic: one verified bundle of every ref, then the retention rule (W2-198 S1, S2, F1).

``run_backup`` writes ``git bundle create --all`` to a temporary name in the destination (outside the name form),
verifies it with ``git bundle verify`` and only then renames it to ``<name>-<YYYYMMDDTHHMMSSZ>.bundle``. Retention runs
after that, never before, and removes only files of that exact name form for that name; the time is the name's.
git runs with the caller's ``GIT_*`` variables removed (a hook or a cron may set ``GIT_DIR``).
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gov.util.gitenv import git_env

KEEP_DEFAULT, DAYS_DEFAULT = 48, 30
_STAMP = "%Y%m%dT%H%M%SZ"
_STAMP_RE = r"(\d{8}T\d{6}Z)"


class BackupError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def clock(env) -> datetime:
    """``GOV_BACKUP_NOW`` (ISO-8601) when set, else the UTC time now."""
    given = env.get("GOV_BACKUP_NOW")
    if not given:
        return datetime.now(timezone.utc)
    try:
        at = datetime.fromisoformat(given.strip())
    except ValueError:
        raise BackupError("BACKUP_FAILED", f"GOV_BACKUP_NOW {given!r} is not an ISO-8601 time") from None
    return (at if at.tzinfo else at.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def stamp_of(name: str, filename: str) -> datetime | None:
    """The time in ``filename`` when it is exactly ``<name>-<YYYYMMDDTHHMMSSZ>.bundle``, else None."""
    found = re.fullmatch(re.escape(name) + "-" + _STAMP_RE + r"\.bundle", filename)
    if found is None:
        return None
    try:
        return datetime.strptime(found.group(1), _STAMP).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def plan(filenames, name: str, now: datetime, keep: int, days: int, protect: str) -> tuple[list[str], list[str]]:
    """``(kept, removed)`` among the files of the name form: the newest ``keep``, the newest of each of the last
    ``days`` UTC days (today and the ``days - 1`` before it) and ``protect``, the file just written. Files of any
    other form are in neither list."""
    stamped = sorted(((stamp_of(name, f), f) for f in set(filenames) if stamp_of(name, f) is not None), reverse=True)
    kept = {f for _stamp, f in stamped[:max(keep, 0)]}
    window = {(now - timedelta(days=d)).date() for d in range(max(days, 0))}
    seen = set()
    for stamp, f in stamped:  # newest first: the first of a day is that day's newest
        if stamp.date() in window and stamp.date() not in seen:
            seen.add(stamp.date())
            kept.add(f)
    if protect:
        kept.add(protect)
    return ([f for _s, f in stamped if f in kept], [f for _s, f in stamped if f not in kept])


def _env() -> dict:
    return git_env(None, base={k: v for k, v in os.environ.items() if not k.startswith("GIT_")})


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, errors="replace",
                              stdin=subprocess.DEVNULL, env=_env())
    except OSError as error:
        raise BackupError("BACKUP_FAILED", f"git cannot be run: {error.strerror or error}") from None


def _why(done: subprocess.CompletedProcess) -> str:
    return " ".join((done.stderr or done.stdout or f"exit {done.returncode}").split())[:300]


def worktrees(root: Path) -> list[Path]:
    """The worktrees of the repository of ``root``, the main one first."""
    done = _git(root, "worktree", "list", "--porcelain")
    if done.returncode != 0:
        raise BackupError("BACKUP_FAILED", f"{root} is not in a git repository: {_why(done)}")
    return [Path(line[len("worktree "):]) for line in done.stdout.splitlines() if line.startswith("worktree ")]


def _inside(dest: Path, root: Path, trees: list[Path]) -> Path | None:
    done = _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    places = list(trees) + ([Path(done.stdout.strip())] if done.returncode == 0 and done.stdout.strip() else [])
    for place in places:
        real = Path(os.path.realpath(place))
        if dest == real or real in dest.parents:
            return place
    return None


def default_dest(name: str, env) -> Path:
    base = env.get("GOV_BACKUP_ROOT") or "~/.gov-os/backups"
    return Path(os.path.expanduser(base)) / name


def run_backup(root: Path, dest: str | None, name: str | None, keep: int, days: int, env=None) -> dict:
    """The bundle, verified and renamed, then the retention; ``{file, bytes, refs, verified, kept, removed}``.
    Raises ``BackupError`` (``BACKUP_FAILED``, ``BACKUP_VERIFY_FAILED``, ``BACKUP_DEST_INSIDE``) and leaves in
    ``dest`` nothing of this run and no older bundle removed."""
    env = os.environ if env is None else env
    trees = worktrees(root)
    name = name or trees[0].name
    if not name or "/" in name or name in (".", ".."):
        raise BackupError("BACKUP_FAILED", f"{name!r} is not a usable backup name")
    target = Path(dest) if dest else default_dest(name, env)
    target = Path(os.path.realpath(os.path.expanduser(str(target))))
    inside = _inside(target, root, trees)
    if inside is not None:
        raise BackupError("BACKUP_DEST_INSIDE", f"{target} is inside the repository ({inside}); a backup there is lost "
                          "with it")
    now = clock(env)
    if not _git(root, "for-each-ref", "--count=1", "--format=%(refname)").stdout.strip() \
            and _git(root, "rev-parse", "--verify", "-q", "HEAD").returncode != 0:
        raise BackupError("BACKUP_FAILED", f"{root} has no commit to back up")
    home = trees[0] if trees[0].is_dir() else root  # git names the other worktrees' HEADs from the one it runs in
    final = target / f"{name}-{now.strftime(_STAMP)}.bundle"
    temporary = target / f".{name}-{now.strftime(_STAMP)}.{os.getpid()}.partial"
    try:
        target.mkdir(parents=True, exist_ok=True)
        done = _git(home, "bundle", "create", str(temporary), "--all")
        if done.returncode != 0:
            raise BackupError("BACKUP_FAILED", f"git bundle create failed: {_why(done)}")
        done = _git(home, "bundle", "verify", str(temporary))
        if done.returncode != 0:
            raise BackupError("BACKUP_VERIFY_FAILED", f"git bundle verify refused the new bundle: {_why(done)}")
        heads = _git(home, "bundle", "list-heads", str(temporary))
        if heads.returncode != 0:
            raise BackupError("BACKUP_VERIFY_FAILED", f"git bundle list-heads failed: {_why(heads)}")
        refs = len([line for line in heads.stdout.splitlines() if line.strip()])
        os.replace(temporary, final)
    except OSError as error:
        raise BackupError("BACKUP_FAILED", f"{target}: {error.strerror or error}") from None
    finally:
        try:
            temporary.unlink()
        except OSError:
            pass
    kept, removed = plan(os.listdir(target), name, now, keep, days, final.name)
    gone = []
    for victim in removed:
        try:
            (target / victim).unlink()
            gone.append(victim)
        except OSError:
            kept.append(victim)  # still there: kept in fact
    return {"file": str(final), "bytes": final.stat().st_size, "refs": refs, "verified": True, "kept": len(kept),
            "removed": gone}
