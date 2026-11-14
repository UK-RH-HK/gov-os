"""``gov rebuild --integration <branch>`` (W2-116 S1, S4; DEC-963, DEC-983, DEC-1014 items 4 and 6, DEC-1087 (3)):
the store of the integration branch's head, double-buffered, so a search is always answered from a complete store.

- **The place:** the link at the absolute path ``integration_store`` of the project's ``governance/project/rebuild.yaml``
  (W2-122's key). The two halves are detached worktrees of the project's repository beside it, ``<link>-a`` and
  ``<link>-b``; the link points at the ready one. A link that is not a symbolic link, or a half that is not a worktree
  of this repository, refuses the refresh: nothing is removed or built.
- **The lock:** ``<link>.lock``, an exclusive ``flock`` held from before the branch's head and the link are read to
  after it is switched (the CTO's ``refresh_integration_store.sh`` and the merge queue's promotion take the same file).
  A refresh that finds it held says so and waits; it reads the head only once it holds the lock, so a refresh that
  waited never builds an older head than the one already built. Searches take no lock.
- **The log:** every line a refresh writes on stderr starts with its date and time (``%Y-%m-%d %H:%M:%S``).
- **Unchanged:** where the ready half is at the branch's head and its stores' record (W2-122) names the running code,
  nothing is done (``status: unchanged``). The command is safe to run after every merge, by a hook or by hand.
- **The build:** the half not in use is checked out at the branch's head and rebuilt there by the code this command
  runs under (never the half's own ``src/``), so the store always matches the code that searches it. It is seeded
  from the ready half (``--seed``, W2-122), so only what changed since is chunked and embedded again; the seed names
  the ready half's head and how it stands to the head built (behind, ahead or diverged). A seed refused (another code, embedder or schema) leaves the
  half's own stores, built incrementally or cold.
- **The switch:** only when the build succeeded: the rebuild raised nothing, the lexical index and the semantic store
  were recreated (a build whose semantic store is not recreated counts as failed, N-2), the half's lexical and
  semantic facets then read fresh, and the half is still at the head it was built for. The link is replaced by an
  atomic rename (``os.replace`` of a new link made beside it). Otherwise the link stays where it was, the failure is
  ``REBUILD_FAILED`` with the build's stores in its details, and the half left behind is never read: the next refresh
  seeds over it.
- **While it builds,** the link points at the ready half, which nothing here writes: searches through the link are
  answered from it, complete, the whole time (F2).

S2, ``--when-due`` (W2-116 pass 2b; P-W2-116-S2-INTERFACE Q1 (a), DEC-1157 (12)): a tick, run every few minutes, that
refreshes only when a refresh is due and otherwise builds nothing.

- **The settings** are ``integration_refresh`` of ``rebuild.yaml``: ``branch``, ``after_nightly`` (``verdict``: a glob
  relative to the project root, default ``DEFAULT_VERDICT``; ``latest``: ``"HH:MM"``) and ``second`` (``"HH:MM"``). A
  time is two digits, a colon, two digits, 24-hour; a missing or invalid time, a missing ``branch`` or no
  ``integration_refresh`` is ``REBUILD_CONFIG_INVALID`` naming the dotted key, with the value read, before anything
  is built. A verdict file *counts* once it holds a line ``verdict:`` or a JSON ``verdict`` key (a nightly still
  running holds neither).
- **The clock** is ``GOV_NOW`` (ISO 8601; no offset: local time) where set, else the real clock; an invalid one is
  ``REBUILD_CONFIG_INVALID`` (key ``GOV_NOW``). ``HH:MM`` times are wall-clock times on ``now``'s date; a verdict
  file's time is its modification time.
- **Due** (``due_reason``), one refresh with the reason ``after_nightly`` where both are: after the nightly, a counting
  verdict file later than the record's ``at`` (any, with no record), or ``now`` at or after today's ``latest`` with no
  scheduled ``after_nightly`` refresh on today's date (the record's ``after_nightly_at``, which a ``second`` refresh
  carries over); ``second``, ``now`` at or after today's ``second`` with no record at or after it. A verdict file
  stamped after ``now`` does not count yet.
- **The record** ``<link>.refresh.json`` (``at``, ``reason``, ``head``, ``status``, ``branch``, and ``after_nightly_at``,
  the ``at`` of the last ``after_nightly`` refresh) is written whole, by
  an atomic replace, after a refresh that switched or found the head built; ``at`` is ``now`` as the decision was
  taken, so a verdict file that lands during the build is later than it. A failed refresh leaves the record, so the
  next tick is due again. Not due: nothing is built or written, the status is ``not_due``.
"""

from __future__ import annotations

import argparse
import fcntl
import glob
import json
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from gov.cli.errors import GovError

HALVES = ("-a", "-b")
LOCK_SUFFIX = ".lock"
UNCHANGED, SWITCHED = "unchanged", "switched"
REFRESH_KEY = "integration_refresh"
RECORD_SUFFIX = ".refresh.json"
NOW_ENV = "GOV_NOW"
AFTER_NIGHTLY, SECOND, NOT_DUE = "after_nightly", "second", "not_due"
DEFAULT_VERDICT = "docs/close/nightly/NR-*.json"
_TIME = re.compile(r"([01]\d|2[0-3]):([0-5]\d)")
_VERDICT_LINE = re.compile(r"^verdict:", re.MULTILINE)


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


class _Dated:
    """``sys.stderr`` while a refresh runs: each line written starts with its date and time, as the CTO's script's
    lines do (review F6), whichever stage writes it."""

    def __init__(self, stream):
        self._stream, self._fresh, self._guard = stream, True, threading.Lock()

    def write(self, text: str) -> int:
        with self._guard:
            out = []
            for piece in text.splitlines(keepends=True):
                if self._fresh:
                    out.append(time.strftime("%Y-%m-%d %H:%M:%S "))
                out.append(piece)
                self._fresh = piece.endswith("\n")
            self._stream.write("".join(out))
        return len(text)

    def flush(self) -> None:
        self._stream.flush()

    def __getattr__(self, name):
        return getattr(self._stream, name)


def refresh(root: Path, branch: str) -> dict:
    """The integration store brought to ``branch``'s head (module docstring); the result, or ``REBUILD_FAILED``. Every
    line it writes on stderr starts with the date and time; a failure is also said there before it is raised."""
    installed = not isinstance(sys.stderr, _Dated)
    if installed:
        sys.stderr = _Dated(sys.stderr)
    try:
        try:
            return _refresh(Path(root), branch)
        except GovError as error:
            print(f"rebuild --integration: {error.code}: {error.message}", file=sys.stderr, flush=True)
            raise
    finally:
        if installed and isinstance(sys.stderr, _Dated):
            sys.stderr = sys.stderr._stream


def _refresh(root: Path, branch: str) -> dict:
    from gov.config.loader import load_config
    from gov.rebuild import command
    from gov.store import STORE_REL

    link = place(root)
    fd = _lock(link)
    try:
        # The head is read under the lock (review F1): a refresh that waited builds the head as it is now, never the
        # one it saw before waiting, so it never moves the link back; at a head already built it does nothing.
        done = _git(root, "rev-parse", "--verify", "-q", f"{branch}^{{commit}}", check=False)
        head = done.stdout.strip()
        if done.returncode != 0 or not head:
            raise _failed(f"the branch {branch!r} is not known in {root}: nothing is built", {"branch": branch})
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


# --- S2: the two daily refresh times, ``--when-due`` -------------------------------------------------------------------


@dataclass(frozen=True)
class Refresh:
    """``integration_refresh`` of ``rebuild.yaml``, checked; the times as (hour, minute)."""

    branch: str
    verdict: str
    latest: tuple[int, int]
    second: tuple[int, int]


def _plain(value):
    """``value`` as a detail of an error: itself where JSON holds it, else its text."""
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return repr(value)
    return value


def _config_invalid(key: str, value, why: str, where: str | None = None) -> GovError:
    from gov.launch.store import SETTINGS_REL

    return GovError("REBUILD_CONFIG_INVALID", f"{where or SETTINGS_REL}: key '{key}': {why}: nothing is built",
                    {"key": key, "value": _plain(value)})


def _hour_minute(key: str, value) -> tuple[int, int]:
    found = _TIME.fullmatch(value) if isinstance(value, str) else None
    if found is None:
        raise _config_invalid(key, value, f"must be a time written \"HH:MM\" (24-hour, 00:00 to 23:59), not {value!r}")
    return int(found.group(1)), int(found.group(2))


def refresh_settings(root: Path) -> Refresh:
    """``integration_refresh`` as the project's ``rebuild.yaml`` states it; ``REBUILD_CONFIG_INVALID`` naming the dotted
    key where it is absent or any part of it is missing or invalid."""
    from gov.config.loader import read_yaml
    from gov.launch.store import SETTINGS_REL

    path = Path(root) / SETTINGS_REL
    document = None
    if path.is_file():
        try:
            document = read_yaml(path, "REBUILD_CONFIG_INVALID", SETTINGS_REL)
        except (GovError, OSError) as error:
            raise _config_invalid(REFRESH_KEY, None, f"{getattr(error, 'message', error)}") from None
    block = document.get(REFRESH_KEY) if isinstance(document, dict) else None
    if not isinstance(block, dict):
        raise _config_invalid(REFRESH_KEY, block, "is required with --when-due and must be a map of branch, "
                                                  "after_nightly and second")
    branch = block.get("branch")
    if not isinstance(branch, str) or not branch.strip():
        raise _config_invalid(f"{REFRESH_KEY}.branch", branch, "must name the integration branch")
    nightly = block.get("after_nightly")
    if nightly is not None and not isinstance(nightly, dict):
        raise _config_invalid(f"{REFRESH_KEY}.after_nightly", nightly, "must be a map of verdict and latest")
    nightly = nightly or {}
    verdict = nightly.get("verdict", DEFAULT_VERDICT)
    if not isinstance(verdict, str) or not verdict.strip():
        raise _config_invalid(f"{REFRESH_KEY}.after_nightly.verdict", verdict, "must be a glob, relative to the "
                                                                              "project root")
    return Refresh(branch, verdict,
                   _hour_minute(f"{REFRESH_KEY}.after_nightly.latest", nightly.get("latest")),
                   _hour_minute(f"{REFRESH_KEY}.second", block.get("second")))


def now() -> datetime:
    """The time the decisions are taken at: ``GOV_NOW`` (ISO 8601; without an offset it is local time) where set, else
    the real clock to the second. Always with an offset. An invalid ``GOV_NOW`` is ``REBUILD_CONFIG_INVALID``."""
    given = os.environ.get(NOW_ENV)
    if given is None:
        return datetime.now().astimezone().replace(microsecond=0)
    try:
        parsed = datetime.fromisoformat(given.strip())
    except ValueError:
        raise _config_invalid(NOW_ENV, given, "must be an ISO 8601 date and time (2026-11-13T09:30:00+01:00)",
                              where="the environment") from None
    return parsed if parsed.tzinfo is not None else parsed.astimezone()  # an offset keeps its wall clock


def at_time(day: datetime, hour_minute: tuple[int, int], days_back: int = 0) -> datetime:
    """The wall-clock time ``hour_minute`` on ``day``'s date, ``days_back`` days earlier, in ``day``'s offset."""
    return (day - timedelta(days=days_back)).replace(hour=hour_minute[0], minute=hour_minute[1], second=0,
                                                     microsecond=0)


def hhmm(hour_minute: tuple[int, int]) -> str:
    return f"{hour_minute[0]:02d}:{hour_minute[1]:02d}"


def _counts(text: str) -> bool:
    """A verdict file counts once it holds a line ``verdict:`` or is JSON with a ``verdict`` key."""
    if _VERDICT_LINE.search(text):
        return True
    try:
        document = json.loads(text)
    except ValueError:
        return False
    return isinstance(document, dict) and "verdict" in document


def verdict_times(root: Path, pattern: str) -> list[datetime]:
    """The modification time of every counting verdict file the glob (relative to ``root``) matches, oldest first."""
    found = []
    for name in glob.glob(os.path.join(str(root), pattern), recursive=True):
        try:
            path = Path(name)
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if _counts(text):
                found.append(datetime.fromtimestamp(path.stat().st_mtime).astimezone())
        except OSError:
            continue  # a file that cannot be read has no verdict that counts
    return sorted(found)


def record_path(link: Path) -> Path:
    return link.with_name(link.name + RECORD_SUFFIX)


def read_record(link: Path) -> dict | None:
    """The scheduled refreshes' record beside ``link``; None where there is none or it is no JSON map."""
    try:
        document = json.loads(record_path(link).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return document if isinstance(document, dict) else None


def _instant(text) -> datetime | None:
    try:
        return datetime.fromisoformat(text).astimezone() if isinstance(text, str) else None
    except ValueError:
        return None


def _after_nightly_text(record: dict | None) -> str | None:
    """The ``at`` as written of the last scheduled refresh with the reason ``after_nightly``: the record's
    ``after_nightly_at`` (a ``second`` refresh carries it over), else its own ``at`` where it is one; None where
    there is none or none can be read."""
    if not record:
        return None
    if _instant(record.get("after_nightly_at")) is not None:
        return record["after_nightly_at"]
    if record.get("reason") == AFTER_NIGHTLY and _instant(record.get("at")) is not None:
        return record["at"]
    return None


def after_nightly_at(record: dict | None) -> datetime | None:
    """``_after_nightly_text`` as an instant."""
    return _instant(_after_nightly_text(record))


def due_reason(settings: Refresh, when: datetime, record: dict | None, verdicts: list[datetime]) -> str | None:
    """Why a refresh is due at ``when`` (``AFTER_NIGHTLY`` before ``SECOND`` where both), or None (module docstring)."""
    last = _instant(record.get("at")) if record else None  # a record with no readable ``at`` is none
    if any((last is None or seen > last) and seen <= when for seen in verdicts):  # a file stamped after now: not yet
        return AFTER_NIGHTLY
    if when >= at_time(when, settings.latest):
        nightly = after_nightly_at(record) if last is not None else None
        if not (nightly is not None and nightly.astimezone(when.tzinfo).date() == when.date()):
            return AFTER_NIGHTLY
    second = at_time(when, settings.second)
    if when >= second and (last is None or last < second):
        return SECOND
    return None


def last_due(settings: Refresh, when: datetime, verdicts: list[datetime]) -> tuple[datetime, str] | None:
    """The last time at or before ``when`` that a refresh fell due, with what made it so: the newest counting verdict
    file, ``second`` today and yesterday, and ``latest`` today and yesterday where no counting verdict file's time
    falls on that date before it; None where none is at or before ``when``."""
    found: list[tuple[datetime, str]] = []
    seen = [at for at in verdicts if at <= when]
    if seen:
        found.append((max(seen), "the nightly's newest verdict file"))
    for back in (0, 1):
        second = at_time(when, settings.second, back)
        if second <= when:
            found.append((second, f"the second time {hhmm(settings.second)}"))
        latest = at_time(when, settings.latest, back)
        if latest <= when and not any(at < latest and at.astimezone(latest.tzinfo).date() == latest.date()
                                      for at in verdicts):
            found.append((latest, f"the nightly's latest time {hhmm(settings.latest)} with no verdict before it"))
    return max(found) if found else None


def _write_record(link: Path, record: dict) -> None:
    """The record written whole, by an atomic replace beside it."""
    path = record_path(link)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    except OSError as error:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise _failed(f"the refresh's record {path} could not be written: {error}; the next tick is due again",
                      {"record": str(path)}) from None


def refresh_when_due(root: Path, branch: str) -> dict:
    """``gov rebuild --integration <branch> --when-due`` (module docstring): the refresh where one is due, its result with
    ``integration.reason`` and the record written; else ``integration.status`` ``not_due`` and nothing built or written."""
    root = Path(root)
    settings = refresh_settings(root)
    when = now()
    link = place(root)
    record = read_record(link)
    reason = due_reason(settings, when, record, verdict_times(root, settings.verdict))
    if reason is None:
        return {"integration": {"status": NOT_DUE, "branch": branch, "link": str(link), "last_refresh": record}}
    result = refresh(root, branch)
    result["integration"]["reason"] = reason
    nightly = when.isoformat() if reason == AFTER_NIGHTLY else _after_nightly_text(record)
    written = {"at": when.isoformat(), "reason": reason, "head": result["integration"]["head"],
               "status": result["integration"]["status"], "branch": branch}
    if nightly is not None:
        written["after_nightly_at"] = nightly
    _write_record(link, written)
    return result
