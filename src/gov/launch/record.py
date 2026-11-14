"""The launch record: one JSON file per launch, written before the session starts (W2-60a; DEC-826 Q1, CAP-36.a lite).

The records lie in ``.gov-runtime/launches/`` of the repository's main checkout,
one folder for every worktree, found by reading ``.git`` (no git is run). A record
is keyed by the session id the launcher gives, created only where no file of that
name is, and removed when the session cannot be started. Whatever cannot be found,
made or written refuses the launch.
"""

from __future__ import annotations

import json
import os
import re
import secrets
from pathlib import Path

from gov.cli.errors import GovError
from gov.guard import runs

RUNTIME, LAUNCHES = ".gov-runtime", "launches"
FORMAT = 1
_VERSION = re.compile(r"\d+(?:\.\d+)+")


def _refuse(reason: str) -> GovError:
    return GovError("LAUNCH_REFUSED", reason)


def main_checkout(root: Path, what: str = "the launch record's folder") -> Path:
    """The main checkout of the repository ``root`` belongs to, found from ``.git`` (no git is run); ``root`` itself
    when it has no ``.git``. ``root`` is a real path; ``what`` names, in a refusal, what the look-up is for."""
    if not os.path.lexists(root / ".git"):
        return root
    common = runs.common_dir(str(root))
    if common is None:
        raise _refuse(f"the tree's .git cannot be read or gives no common directory, so {what} cannot be found")
    if os.path.basename(common) != ".git":
        raise _refuse(f"the tree's git common directory is not named .git (a bare repository), so {what} has no "
                      f"main checkout")
    return Path(os.path.dirname(common))


def folder(root: Path) -> Path:
    """The record folder of the repository ``root`` belongs to, made when it is missing. ``root`` is a real path."""
    here = main_checkout(root)
    for name in (RUNTIME, LAUNCHES):
        here = here / name
        if os.path.lexists(here) and (here.is_symlink() or not here.is_dir()):
            raise _refuse(f"{here} is a link or not a folder, so the launch record cannot be written there")
        try:
            os.makedirs(here, exist_ok=True)
        except OSError:
            raise _refuse(f"the launch record's folder {here} cannot be made") from None
    return here


def deny_rules(records: Path) -> list[str]:
    """The two literal ``Edit`` deny rules that name the record folder to the session."""
    return [f"Edit(/{records})", f"Edit(/{records}/**)"]


def cli_version(cli: Path) -> str:
    """The CLI's version, from the name of the file its link resolves to (``…/versions/2.1.292``); the CLI is not run."""
    if not cli.is_symlink():
        return "not measured: the CLI is not a link to a versions folder"
    target = Path(os.path.realpath(cli))
    if target.parent.name != "versions" or not _VERSION.fullmatch(target.name):
        return "not measured: the CLI's link does not resolve to versions/<version>"
    return target.name


def original(records: Path, session_id: str, role: str, ticket_id: str) -> dict:
    """The record of the session a launch resumes: it must exist and be this launch's role's and ticket's."""
    path = records / f"{session_id}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise _refuse(f"no launch record exists for the session {session_id} given with --resume: a launch resumes "
                      f"only a session it started") from None
    except (OSError, ValueError):
        raise _refuse(f"the launch record of the session {session_id} given with --resume cannot be read") from None
    if not isinstance(data, dict) or data.get("record") != "gov-launch" or not isinstance(data.get("role_text"), dict) \
            or not isinstance(data.get("skills"), list):
        raise _refuse(f"the launch record of the session {session_id} given with --resume is not of the record's form")
    if data.get("role") != role or data.get("ticket") != ticket_id:
        raise _refuse(f"the session {session_id} given with --resume was launched as {data.get('role')} on "
                      f"{data.get('ticket')}, not as {role} on {ticket_id}")
    return data


def write(records: Path, record: dict) -> Path:
    """Write the record atomically, only where no file of its name is (W2-184 R2, interface 10.2).

    The bytes go, written, flushed and fsynced, to ``.<session id>.<unique part>.tmp`` in the same folder (a name no
    reader of ``*.json`` takes), which is then hard-linked to ``<session id>.json`` (a link never overwrites) and
    removed. So a launch killed at any point leaves no record of its name or a whole one, and a leftover ``.tmp`` at
    most; a refusal leaves neither file."""
    session = record["session_id"]
    path = records / f"{session}.json"
    data = (json.dumps(record, indent=2) + "\n").encode()
    cannot = f"the launch record cannot be written in {records}"
    try:
        temporary, descriptor = _temporary(records, session)
    except OSError:
        raise _refuse(cannot) from None
    try:
        try:
            view = memoryview(data)
            while view:
                view = view[os.write(descriptor, view):]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.link(temporary, path, follow_symlinks=False)
    except FileExistsError:
        _discard(temporary)
        raise _refuse(f"a launch record of the session {session} is already there") from None
    except OSError:
        _discard(temporary)
        raise _refuse(cannot) from None
    try:
        os.unlink(temporary)
    except OSError:
        _discard(path)  # the record is whole, but a refusal leaves no file of either name
        _discard(temporary)
        raise _refuse(cannot) from None
    return path


def _temporary(records: Path, session: str) -> tuple[Path, int]:
    """A new hidden temporary file ``.<session>.<unique part>.tmp`` in ``records``, opened for writing only."""
    while True:
        temporary = records / f".{session}.{secrets.token_hex(8)}.tmp"
        try:
            return temporary, os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
        except FileExistsError:
            continue


def remove(path: Path) -> None:
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


def _discard(path: Path) -> None:
    """Remove ``path`` if it can be: a write that refuses removes what it made, and its refusal stands either way."""
    try:
        os.unlink(path)
    except OSError:
        pass
